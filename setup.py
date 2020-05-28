import os
import re
import sys
import shutil
import tarfile
from typing import List
from urllib import request

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import platform
import subprocess
import sysconfig
from setuptools.command.build_clib import build_clib
from distutils.sysconfig import customize_compiler
from ctypes.util import find_library
# CMAKE = shutil.which("cmake")
PACKAGE_NAME = "py3exiv2bind"
PYBIND11_DEFAULT_URL = \
    "https://github.com/pybind/pybind11/archive/v2.5.0.tar.gz"

class CMakeExtension(Extension):
    def __init__(self, name, sources=None, language=None):
        # don't invoke the original build_ext for this special extension
        super().__init__(name,
                         sources=sources if sources is not None else [],
                         language=language)


class BuildCMakeExt(build_clib):
    user_options = [
        ('cmake-exec=', None, "Location of CMake. Defaults of CMake located on path")
    ]

    @property
    def package_dir(self):
        build_py = self.get_finalized_command('build_py')
        return build_py.get_package_dir(PACKAGE_NAME)

    def initialize_options(self):
        super().initialize_options()
        self.cmake_exec = shutil.which("cmake")
        pass

    def __init__(self, dist):
        super().__init__(dist)
        self.extra_cmake_options = []

    def finalize_options(self):
        super().finalize_options()

        if self.cmake_exec is None:

            raise Exception("CMake path not located on path")

        if not os.path.exists(self.cmake_exec):
            raise Exception("CMake path not located at {}".format(self.cmake_exec))

    @staticmethod
    def get_build_generator_name():
        python_compiler = platform.python_compiler()

        if "GCC" in python_compiler:
            python_compiler = "GCC"

        if "Clang" in python_compiler:
            python_compiler = "Clang"

        cmake_build_systems_lut = {
            'MSC v.1900 64 bit (AMD64)': "Visual Studio 14 2015 Win64",
            'MSC v.1900 32 bit (Intel)': "Visual Studio 14 2015",
            'MSC v.1915 64 bit (AMD64)': "Visual Studio 14 2015 Win64",
            'MSC v.1915 32 bit (Intel)': "Visual Studio 14 2015",
            'MSC v.1916 64 bit (AMD64)': "Visual Studio 14 2015 Win64",
            'MSC v.1916 32 bit (Intel)': "Visual Studio 14 2015",
            'MSC v.1924 64 bit (AMD64)': "Visual Studio 14 2015 Win64",
            'MSC v.1924 32 bit (Intel)': "Visual Studio 14 2015",
            'MSC v.1925 64 bit (AMD64)': "Visual Studio 14 2015 Win64",
            'MSC v.1925 32 bit (Intel)': "Visual Studio 14 2015",
            'GCC': "Unix Makefiles",
            'Clang': "Unix Makefiles",
        }

        return cmake_build_systems_lut[python_compiler]

    def run(self):

        if not self.libraries:
            return

        # Yech -- this is cut 'n pasted from build_ext.py!
        from distutils.ccompiler import new_compiler
        self.compiler = new_compiler(compiler=self.compiler,
                                     dry_run=self.dry_run,
                                     force=self.force)
        customize_compiler(self.compiler)

        if self.include_dirs is not None:
            self.compiler.set_include_dirs(self.include_dirs)
        if self.define is not None:
            # 'define' option is a list of (name,value) tuples
            for (name,value) in self.define:
                self.compiler.define_macro(name, value)
        if self.undef is not None:
            for macro in self.undef:
                self.compiler.undefine_macro(macro)

        for library in self.libraries:
            self.build_extension(library)


    def build_extension(self, ext):
        if self.compiler.compiler_type != "unix":
            if not self.compiler.initialized:
                self.compiler.initialize()

        self.configure_cmake(ext)
        self.build_cmake(ext)
        self.build_install_cmake(ext)

    def configure_cmake(self, extension: Extension):
        source_dir = os.path.abspath(os.path.dirname(__file__))

        self.announce("Configuring CMake Project", level=3)
        os.makedirs(self.build_temp, exist_ok=True)

        if self.debug:
            build_configuration_name = 'Debug'
        else:
            build_configuration_name = 'Release'

        configure_command = [
            self.cmake_exec,
            f'-H{source_dir}',
            f'-B{self.build_temp}',
            # f'-G{self.get_build_generator_name()}'
        ]


        configure_command.append(
            f'-DCMAKE_BUILD_TYPE={build_configuration_name}')
        build_ext_cmd = self.get_finalized_command("build_ext")
        configure_command.append(f'-DCMAKE_INSTALL_PREFIX={os.path.abspath(build_ext_cmd.build_temp)}')
        configure_command.append(f'-DPYTHON_EXECUTABLE:FILEPATH={sys.executable}')
        configure_command.append(f'-DPYTHON_INCLUDE_DIR={sysconfig.get_path("include")}')
        configure_command.append(f'-DPython_ADDITIONAL_VERSIONS={sys.version_info.major}.{sys.version_info.minor}')

        configure_command.append('-Dpyexiv2bind_generate_python_bindings:BOOL=NO')
        configure_command.append('-DEXIV2_ENABLE_NLS:BOOL=NO')
        configure_command.append('-DEXIV2_ENABLE_VIDEO:BOOL=OFF')
        configure_command.append('-DEXIV2_ENABLE_PNG:BOOL=OFF')

        configure_command += self.extra_cmake_options

        if sys.gettrace():
            print("Running as a debug", file=sys.stderr)
            subprocess.check_call(configure_command)
        else:
            self.compiler.spawn(configure_command)

    def build_cmake(self, extension: Extension):

        build_command = [
            self.cmake_exec,
            "--build",
            self.build_temp,
            # "--target", "exiv2lib"
        ]

        self.announce("Building binaries", level=3)

        # Add config
        build_command.append("--config")
        if self.debug:
            build_command.append("Debug")
        else:
            build_command.append("Release")

        build_ext_cmd = self.get_finalized_command("build_ext")
        if build_ext_cmd.parallel:
            build_command.extend(["-j", str(build_ext_cmd.parallel)])

        if "Visual Studio" in self.get_build_generator_name():
            build_command += ["--", "/NOLOGO", "/verbosity:minimal"]

        if sys.gettrace():
            subprocess.check_call(build_command)
        else:
            self.compiler.spawn(build_command)

    def build_install_cmake(self, extension: Extension):

        install_command = [
            self.cmake_exec,
            "--build", self.build_temp
        ]

        self.announce("Adding binaries to Python build path", level=3)

        install_command.append("--config")
        if self.debug:
            install_command.append("Debug")
        else:
            install_command.append("Release")

        install_command += ["--target", "install"]
        build_ext_cmd = self.get_finalized_command("build_ext")

        if build_ext_cmd.parallel:
            install_command.extend(["-j", str(build_ext_cmd.parallel)])

        if "Visual Studio" in self.get_build_generator_name():
            install_command += ["--", "/NOLOGO", "/verbosity:quiet"]

        build_ext_cmd.include_dirs.insert(0, os.path.abspath(os.path.join(build_ext_cmd.build_temp, "include")))
        build_ext_cmd.library_dirs.insert(0, os.path.abspath(os.path.join(build_ext_cmd.build_temp, "lib")))
        if self.compiler.compiler_type != "unix":
            build_ext_cmd.libraries.append("shell32")
        if sys.gettrace():
            print("Running as a debug", file=sys.stderr)
            subprocess.check_call(install_command)
        else:
            self.compiler.spawn(install_command)


class BuildExiv2(BuildCMakeExt):

    def __init__(self, dist):

        super().__init__(dist)
        self.extra_cmake_options += [
            "-Dpyexiv2bind_generate_venv:BOOL=OFF",
            "-DBUILD_SHARED_LIBS:BOOL=OFF",
            # "-DEXIV2_VERSION_TAG:STRING=11e66c6c9eceeddd2263c3591af6317cbd05c1b6",
            # "-DEXIV2_VERSION_TAG:STRING=0.27",
            "-DBUILD_TESTING:BOOL=OFF",
        ]


# exiv2 = CMakeExtension("exiv2_wrapper")

exiv2 = ("exiv2", {
    "sources": [],
    "CMAKE_SOURCE_DIR": os.path.dirname(__file__)
})

DEPS_REGEX = \
    r'(?<=(Image has the following dependencies:(\n){2}))((?<=\s).*\.dll\n)*'

def parse_dumpbin_deps(file) -> List[str]:

    dlls = []
    dep_regex = re.compile(DEPS_REGEX)

    with open(file) as f:
        d = dep_regex.search(f.read())
        for x in d.group(0).split("\n"):
            if x.strip() == "":
                continue
            dll = x.strip()
            dlls.append(dll)
    return dlls


def remove_system_dlls(dlls):
    non_system_dlls = []
    for dll in dlls:
        if dll.startswith("api-ms-win-crt"):
            continue

        if dll.startswith("python"):
            continue

        if dll == "KERNEL32.dll":
            continue
        non_system_dlls.append(dll)
    return non_system_dlls


class BuildPybind11Extension(build_ext):
    user_options = build_ext.user_options + [
        ('pybind11-url=', None,
         "Url to download Pybind11")
    ]

    def initialize_options(self):
        super().initialize_options()
        self.pybind11_url = None

    def finalize_options(self):
        self.pybind11_url = self.pybind11_url or PYBIND11_DEFAULT_URL
        super().finalize_options()

    def run(self):
        pybind11_include_path = self.get_pybind11_include_path()
        if pybind11_include_path is not None:
            self.include_dirs.insert(0, pybind11_include_path)

        super().run()

        for e in self.extensions:
            dll_name = \
                os.path.join(self.build_lib, self.get_ext_filename(e.name))

            output_file = os.path.join(self.build_temp, f'{e.name}.dependents')
            if self.compiler.compiler_type != "unix":
                if not self.compiler.initialized:
                    self.compiler.initialize()
                self.compiler.spawn(
                    [
                        'dumpbin',
                        '/dependents',
                        dll_name,
                        f'/out:{output_file}'
                    ]
                )
                deps = parse_dumpbin_deps(file=output_file)
                deps = remove_system_dlls(deps)
                dest = os.path.dirname(dll_name)
                for dep in deps:
                    dll = self.find_deps(dep)
                    shutil.copy(dll, dest)

    def find_deps(self, lib):

        for path in os.environ['path'].split(";"):
            for f in os.scandir(path):
                if f.name.lower() == lib.lower():
                    return f.path

    def find_missing_libraries(self, ext):
        missing_libs = []
        for lib in ext.libraries:
            if self.compiler.find_library_file(self.library_dirs, lib) is None:
                missing_libs.append(lib)
        return missing_libs

    def build_extension(self, ext):
        if self.compiler.compiler_type == "unix":
            ext.extra_compile_args.append("-std=c++14")
        else:
            ext.extra_compile_args.append("/std:c++14")

            # self.compiler.add_library("shell32")
            # ext.libraries.append("shell32")

        missing = self.find_missing_libraries(ext)

        if len(missing) > 0:
            self.announce(f"missing required deps [{', '.join(missing)}]. "
                          f"Trying to build them", 5)
            self.run_command("build_clib")
        super().build_extension(ext)

    def get_pybind11_include_path(self):
        pybind11_archive_filename = os.path.split(self.pybind11_url)[1]

        pybind11_archive_downloaded = os.path.join(self.build_temp,
                                                   pybind11_archive_filename)

        pybind11_source = os.path.join(self.build_temp, "pybind11")
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        if not os.path.exists(pybind11_source):
            if not os.path.exists(pybind11_archive_downloaded):
                self.announce("Downloading pybind11", level=5)
                request.urlretrieve(
                    self.pybind11_url, filename=pybind11_archive_downloaded)
                self.announce("pybind11 Downloaded", level=5)
            with tarfile.open(pybind11_archive_downloaded, "r") as tf:
                for f in tf:
                    if "pybind11.h" in f.name:
                        self.announce("Extract pybind11.h to include path")

                    tf.extract(f, pybind11_source)
        for root, dirs, files in os.walk(pybind11_source):
            for f in files:
                if f == "pybind11.h":
                    return os.path.abspath(os.path.relpath(
                        os.path.join(root, ".."),
                        os.path.dirname(__file__)
                    ))



exiv2_extension = Extension(
    "py3exiv2bind.core",
    sources=[
        "py3exiv2bind/core/core.cpp",
        "py3exiv2bind/core/glue/ExifStrategy.cpp",
        "py3exiv2bind/core/glue/glue.cpp",
        "py3exiv2bind/core/glue/Image.cpp",
        "py3exiv2bind/core/glue/IPTC_Strategy.cpp",
        "py3exiv2bind/core/glue/XmpStrategy.cpp",
        "py3exiv2bind/core/glue/MetadataProcessor.cpp",
    ],
    libraries=[
        "exiv2",
        "xmp",
        "expat",
        # "z",
    ],
    include_dirs=[
        "py3exiv2bind/core/glue"
    ],
    language='c++',
    # extra_compile_args=['-std=c++14'],

)

setup(
    packages=['py3exiv2bind'],
    python_requires=">=3.6",
    setup_requires=['pytest-runner'],
    test_suite="tests",
    tests_require=['pytest'],
    libraries=[exiv2],
    ext_modules=[exiv2_extension],
    cmdclass={
        "build_ext": BuildPybind11Extension,
        "build_clib": BuildExiv2,
    },

)
