import json
import os

import setuptools
import sys
import shutil
from typing import Optional, Tuple, Dict, List, Iterable, Any, Union

from setuptools import setup, Extension
import platform
import subprocess
from setuptools.command.build_clib import build_clib
from distutils.sysconfig import customize_compiler
from functools import reduce

sys.path.insert(0, os.path.dirname(__file__))
cmd_class = {}
extension_modules = []
try:
    from builders.conan_libs import BuildConan
    cmd_class["build_conan"] = BuildConan
    from builders.pybind11_builder import BuildPybind11Extension
    cmd_class["build_ext"] = BuildPybind11Extension
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
        ],
        include_dirs=[
            "py3exiv2bind/core/glue",
        ],
        language='c++',

    )
    extension_modules.append(exiv2_extension)
except ImportError:
    pass

PACKAGE_NAME = "py3exiv2bind"


class CMakeExtension(Extension):
    def __init__(self, name, sources=None, language=None):
        # don't invoke the original build_ext for this special extension
        super().__init__(name,
                         sources=sources if sources is not None else [],
                         language=language)


class BuildCMakeLib(build_clib):
    user_options = [
        (
            'cmake-exec=',
            None,
            "Location of CMake. Defaults of CMake located on path"
        )
    ]

    @property
    def package_dir(self):
        build_py = self.get_finalized_command('build_py')
        return build_py.get_package_dir(PACKAGE_NAME)

    def initialize_options(self):
        super().initialize_options()
        self.cmake_exec = None

    def __init__(self, dist):
        super().__init__(dist)
        self.extra_cmake_options = []
        self.cmake_api_dir = None

    def finalize_options(self):
        super().finalize_options()
        import cmake
        self.cmake_exec = shutil.which("cmake", path=cmake.CMAKE_BIN_DIR)

        self.cmake_api_dir = \
            os.path.join(self.build_temp, "deps", ".cmake", "api", "v1")

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
            'MSC v.1927 64 bit (AMD64)': "Visual Studio 14 2015 Win64",
            'MSC v.1927 32 bit (Intel)': "Visual Studio 14 2015",
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
            for (name, value) in self.define:
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
        if self.cmake_exec is None:
            raise FileNotFoundError("CMake path not located on path")
        self.configure_cmake(ext)
        self.build_cmake(ext)
        self.build_install_cmake(ext)

    def configure_cmake(self, extension: Extension):
        source_dir = os.path.abspath(os.path.dirname(__file__))

        self.announce("Configuring CMake Project", level=3)
        dep_build_path = os.path.join(self.build_temp, "deps")
        self.mkpath(dep_build_path)

        if self.debug:
            build_configuration_name = 'Debug'
        else:
            build_configuration_name = 'Release'

        self.mkpath(os.path.join(self.cmake_api_dir, "query"))

        codemodel_file = \
            os.path.join(self.cmake_api_dir, "query", "codemodel-v2")

        with open(codemodel_file, "w"):
            pass

        configure_command = [
            self.cmake_exec, f'-S{source_dir}',
            "-G", "Ninja",
            f'-B{dep_build_path}',
            f"-DCMAKE_TOOLCHAIN_FILE={dep_build_path}/conan_paths.cmake",
            f'-DCMAKE_BUILD_TYPE={build_configuration_name}',
            f'-DCMAKE_INSTALL_PREFIX={os.path.abspath(self.build_clib)}',
            '-Dpyexiv2bind_generate_python_bindings:BOOL=NO',
            '-DEXIV2_ENABLE_NLS:BOOL=NO',
            '-DEXIV2_ENABLE_VIDEO:BOOL=OFF',
            '-DEXIV2_ENABLE_PNG:BOOL=OFF'
        ]
        if os.getenv('HOMEBREW_SDKROOT'):
            configure_command.append(
                f"-DCMAKE_OSX_SYSROOT={os.getenv('HOMEBREW_SDKROOT')}",
            )

        if platform.system() == "Linux":
            configure_command.append('-DEXIV2_BUILD_EXIV2_COMMAND:BOOL=OFF')
        else:
            configure_command.append('-DEXIV2_BUILD_EXIV2_COMMAND:BOOL=ON')

        if self.compiler.compiler_type == "unix":
            configure_command.append(
                '-DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=ON'
            )

        configure_command += self.extra_cmake_options

        if sys.gettrace():
            print("Running as a debug", file=sys.stderr)
            subprocess.check_call(configure_command)
        else:
            self.compiler.spawn(configure_command)

    def find_target(self, target_name: str, build_type=None) -> Optional[str]:
        for f in os.scandir(os.path.join(self.cmake_api_dir, "reply")):
            if f"target-{target_name}-" not in f.name:
                continue
            if build_type is not None:
                if build_type not in f.name:
                    continue
            return f.path

        return None

    def find_dep_libs_from_cmake(self, ext, target_json,
                                 remove_prefix) -> Optional[Tuple[list, list]]:

        if target_json is not None:
            with open(target_json) as f:
                t = json.load(f)
                link = t.get("link")
                if link is not None:
                    cf = link['commandFragments']
                    flags = reduce(
                        lambda a, b: {**b, **a},
                        filter(lambda fragment: fragment['role'] == "flags", cf)
                    )['fragment'].split()

                    deps = map(lambda i: os.path.split(i)[-1],
                               map(lambda z: z['fragment'],
                                   filter(lambda fragment: fragment['role'] == "libraries", cf)
                                   )
                               )

                    splitted = []
                    for d in deps:
                        splitted += d.split(" ")

                    prefix_removed = []
                    for d in splitted:
                        if d in ext.libraries:
                            continue

                        for l in ext.libraries:
                            if d.startswith(l):
                                continue

                        if d.startswith("-Wl"):
                            ext.extra_link_args.append(d)
                            continue
                        if d == "-l:":
                            continue
                        if d.startswith("-l"):
                            prefix_removed.append(d.replace("-l", ""))
                        else:
                            prefix_removed.append(d)
                    deps = map(lambda i: os.path.splitext(i)[0], prefix_removed)
                    if remove_prefix:
                        return list(map(lambda i: i.replace("lib", "") if i.startswith("lib") else i, deps)), flags
                    return list(deps), flags
            return [], []
        return None

    def build_cmake(self, extension: Extension):
        dep_build_path = os.path.join(self.build_temp, "deps")
        build_command = [
            self.cmake_exec,
            "--build", dep_build_path,
            # "--target", "exiv2lib"
        ]
        if self.verbose == 1:
            build_command.append("--verbose")
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

        if sys.gettrace():
            subprocess.check_call(build_command)
        else:
            self.compiler.spawn(build_command)

    def build_install_cmake(self, extension: Extension):
        dep_build_path = os.path.join(self.build_temp, "deps")
        install_command = [
            self.cmake_exec,
            "--build", dep_build_path
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

        # if "Visual Studio" in self.get_build_generator_name():
        #     install_command += ["--", "/NOLOGO", "/verbosity:quiet"]

        build_ext_cmd.include_dirs.insert(
            0,
            os.path.abspath(
                os.path.join(build_ext_cmd.build_temp, "include")
            )
        )

        build_ext_cmd.library_dirs.insert(
            0, os.path.abspath(os.path.join(build_ext_cmd.build_temp, "lib"))
        )

        self.mkpath(os.path.join(self.build_clib, "bin"))
        if sys.gettrace():
            print("Running as a debug", file=sys.stderr)
            subprocess.check_call(install_command)
        else:
            self.compiler.spawn(install_command)


class BuildConan(setuptools.Command):
    user_options = [
        ('conan-exec=', "c", 'conan executable')
    ]

    description = "Get the required dependencies from a Conan package manager"

    def initialize_options(self):
        self.conan_cache = None

    def finalize_options(self):
        if self.conan_cache is None:
            build_ext_cmd = self.get_finalized_command("build_ext")
            build_dir = build_ext_cmd.build_temp

            self.conan_cache = \
                os.path.join(
                    os.environ.get("CONAN_USER_HOME", build_dir),
                    ".conan"
                )

    def run(self):
        build_ext_cmd = self.get_finalized_command("build_ext")
        build_dir = build_ext_cmd.build_temp

        build_dir_full_path = os.path.abspath(build_dir)
        conan_cache = self.conan_cache
        if not os.path.exists(conan_cache):
            self.mkpath(conan_cache)
            self.mkpath(build_dir_full_path)
            self.mkpath(os.path.join(build_dir_full_path, "lib"))

        from conans.client import conan_api
        conan = conan_api.Conan(cache_folder=os.path.abspath(conan_cache))
        conan_options = []

        conan.install(
            options=conan_options,
            cwd=build_dir,
            build=['missing'],
            path=os.path.abspath(os.path.dirname(__file__)),
            install_folder=build_dir_full_path
        )

        conanbuildinfotext = os.path.join(build_dir, "conanbuildinfo.txt")
        assert os.path.exists(conanbuildinfotext)
        from builders.conan_libs import ConanBuildInfoTXT
        text_md = ConanBuildInfoTXT().parse(conanbuildinfotext)
        for path in text_md['bin_paths']:
            if path not in build_ext_cmd.library_dirs:
                build_ext_cmd.library_dirs.insert(0, path)

        for extension in build_ext_cmd.extensions:
            for path in text_md['lib_paths']:
                if path not in extension.library_dirs:
                    extension.library_dirs.insert(0, path)

            for path in text_md['lib_paths']:
                if path not in extension.library_dirs:
                    extension.library_dirs.insert(0, path)

        extension_deps = set()
        all_libs = [lib.libraries for lib in build_ext_cmd.ext_map.values()]
        for library_deps in all_libs:
            extension_deps = extension_deps.union(library_deps)

        for lib in text_md['libs']:
            if lib in build_ext_cmd.libraries:
                continue

            if lib in extension_deps:
                continue

            build_ext_cmd.libraries.insert(0, lib)


class BuildExiv2(BuildCMakeLib):

    def __init__(self, dist):

        super().__init__(dist)
        self.extra_cmake_options += [
            "-DBUILD_SHARED_LIBS:BOOL=OFF",
            "-DBUILD_TESTING:BOOL=OFF",
        ]

    def run(self):
        conan_cmd = self.get_finalized_command("build_conan")
        conan_cmd.run()
        build_ext_cmd = self.get_finalized_command("build_ext")


        cmake_toolchain = os.path.join(build_ext_cmd.build_temp, "conan_paths.cmake")
        if not os.path.exists(cmake_toolchain):
            raise FileNotFoundError("Missing toolchain file conan_paths.cmake")
        self.extra_cmake_options.append(
            f'-DCMAKE_TOOLCHAIN_FILE={cmake_toolchain}'
        )

        super().run()
        ext_command = self.get_finalized_command("build_ext")

        ext_command.ext_map['py3exiv2bind.core'].include_dirs.append(
            os.path.join(self.build_temp, "include")
        )

        ext_command.ext_map['py3exiv2bind.core'].libraries.append("xmp")
        ext_command.ext_map['py3exiv2bind.core'].library_dirs.insert(
            0, os.path.join(self.build_temp, "lib")
        )


exiv2 = ("exiv2", {
    "sources": [],
    "CMAKE_SOURCE_DIR": os.path.dirname(__file__)
})

cmd_class['build_clib'] = BuildExiv2
cmd_class['build_conan'] = BuildConan
setup(
    packages=['py3exiv2bind'],
    python_requires=">=3.6",
    setup_requires=[
        'pytest-runner',
        "pybind11",
        "cmake"
    ],
    test_suite="tests",
    tests_require=['pytest'],
    libraries=[exiv2],
    ext_modules=extension_modules,
    package_data={"py3exiv2bind": ["py.typed"]},
    cmdclass=cmd_class
)
