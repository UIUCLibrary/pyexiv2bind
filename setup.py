import abc
import os

import sys
import shutil
from typing import Optional, List

from distutils.sysconfig import customize_compiler
import subprocess
import pathlib
import platform
from setuptools import setup
try:
    from pybind11.setup_helpers import Pybind11Extension
except ImportError:
    from setuptools import Extension as Pybind11Extension
from setuptools.command.build_clib import build_clib

sys.path.insert(0, os.path.dirname(__file__))
cmd_class = {}
extension_modules = []

try:
    from builders.conan_libs import BuildConan, locate_conanbuildinfo, ConanBuildInfoTXT
    cmd_class["build_conan"] = BuildConan
    from builders.pybind11_builder import BuildPybind11Extension, parse_conan_build_info
    cmd_class["build_ext"] = BuildPybind11Extension
    exiv2_extension = Pybind11Extension(
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
            # "expat"
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


class AbsCMakePlatform(abc.ABC):

    def __init__(self, clib_builder) -> None:
        super().__init__()
        self.clib_builder = clib_builder

    @abc.abstractmethod
    def platform_specific_configs(self) -> List[str]:
        """Get cmake arguments specifically for a given platform"""


class WinCMakelib(AbsCMakePlatform):

    def platform_specific_configs(self) -> List[str]:
        return ['-DEXIV2_BUILD_EXIV2_COMMAND:BOOL=ON']


class UnixCMakePlatform(AbsCMakePlatform):
    def platform_specific_configs(self) -> List[str]:
        return ['-DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=ON']


class OSXCMakelib(UnixCMakePlatform):
    def platform_specific_configs(self):
        configs: List[str] = super().platform_specific_configs()
        sys_root = self.get_cmake_osx_sysroot()
        if sys_root is not None:
            configs.append(sys_root)
        configs.append('-DEXIV2_BUILD_EXIV2_COMMAND:BOOL=ON')
        return configs

    @staticmethod
    def get_cmake_osx_sysroot() -> Optional[str]:
        if os.getenv('HOMEBREW_SDKROOT'):
            return f"-DCMAKE_OSX_SYSROOT={os.getenv('HOMEBREW_SDKROOT')}"
        return None


class LinuxCMakePlatform(UnixCMakePlatform):

    def platform_specific_configs(self) -> List[str]:
        configs: List[str] = super().platform_specific_configs()
        if platform.system() == "Linux":
            configs.append('-DEXIV2_BUILD_EXIV2_COMMAND:BOOL=OFF')
        return configs


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

        self._cmake_platform: AbsCMakePlatform = {
            "Windows": WinCMakelib,
            "Darwin": OSXCMakelib,
            "Linux": LinuxCMakePlatform
        }[platform.system()](self)

    def finalize_options(self):
        super().finalize_options()
        import cmake
        self.cmake_exec = shutil.which("cmake", path=cmake.CMAKE_BIN_DIR)

        self.cmake_api_dir = \
            os.path.join(self.build_temp, "deps", ".cmake", "api", "v1")

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


    def configure_cmake(self, extension: Pybind11Extension):
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
        pathlib.Path(codemodel_file).touch()

        toolchain_locations = [
            self.build_temp,
            os.path.join(self.build_temp, "conan"),
            os.path.join(self.build_temp, "Release"),
            os.path.join(self.build_temp, "Release", "conan"),
        ]
        cmake_toolchain = locate_file("conan_paths.cmake", toolchain_locations)
        if cmake_toolchain is None:
            raise FileNotFoundError("Missing toolchain file conan_paths.cmake")

        configure_command = [
            self.cmake_exec, f'-S{source_dir}'
        ]
        ninja = shutil.which("ninja")
        if ninja:
            configure_command += [
                "-G", "Ninja",
                f"-DCMAKE_MAKE_PROGRAM:FILEPATH={ninja}",
            ]
        configure_command += [
            f'-B{dep_build_path}',
            f"-DCMAKE_TOOLCHAIN_FILE={cmake_toolchain}",
            f'-DCMAKE_BUILD_TYPE={build_configuration_name}',
            f'-DCMAKE_INSTALL_PREFIX={os.path.abspath(self.build_clib)}',
        ]
        configure_command += extension[1].get('CMAKE_CONFIG', [])
        configure_command += self._cmake_platform.platform_specific_configs()
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

    def build_cmake(self, extension: Pybind11Extension):
        dep_build_path = os.path.join(self.build_temp, "deps")
        build_command = [
            self.cmake_exec,
            "--build", dep_build_path,
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

    def build_install_cmake(self, extension: Pybind11Extension):
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
        ext: Pybind11Extension
        for ext in build_ext_cmd.extensions:
            ext.library_dirs.insert(
                0,
                os.path.abspath(os.path.join(build_ext_cmd.build_lib, "py3exiv2bind"))
            )
            print(f"ext = {ext}: ext.library_dirs = {ext.library_dirs}")
            print(f"ext = {ext}: ext.libraries = {ext.libraries}")
        # raise Exception("ok")
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

        install_manifest = os.path.join(self.build_temp, "deps", "install_manifest.txt")
        self.add_cmake_built_libraries(install_manifest)
        lib_dirs = list(self.locate_cmake_installed_lib_dirs(install_manifest))
        ext: Pybind11Extension
        for ext in build_ext_cmd.extensions:
            ext.library_dirs = lib_dirs + ext.library_dirs
            if sys.platform == "darwin":
                if "@loader_path" not in ext.runtime_library_dirs:
                    ext.runtime_library_dirs.append("@loader_path")
            elif sys.platform == "linux":
                if "$ORIGIN" not in ext.runtime_library_dirs:
                    ext.runtime_library_dirs.append("$ORIGIN")

    def add_cmake_built_libraries(self, install_manifest):
        if not os.path.exists(install_manifest):
            raise FileNotFoundError(f"Missing {install_manifest}")
        with open(install_manifest, "r", encoding="utf8") as f:
            build_py = self.get_finalized_command("build_py")
            install_dir = os.path.abspath(
                os.path.join(
                    build_py.build_lib,
                    build_py.get_package_dir(build_py.packages[0]))
            )
            for line in f.readlines():
                file_path = line.strip()
                if ".dylib" not in file_path:
                    continue
                shutil.copy(file_path, install_dir, follow_symlinks=False)

    def locate_cmake_installed_lib_dirs(self, install_manifest):
        with open(install_manifest, "r", encoding="utf8") as f:
            file_paths = set()
            # don't return any dup paths
            for line in f.readlines():
                file_path = line.strip()
                if platform.system() == "Windows":
                    if ".lib" not in file_path:
                        continue
                else:
                    if ".a" not in file_path:
                        continue
                path = str(pathlib.Path(file_path).parent)
                if path not in file_paths:
                    file_paths.add(path)
                    yield path


def locate_file(file_name, search_locations):
    for location in search_locations:
        file_candidate = os.path.join(location, file_name)
        if os.path.exists(file_candidate):
            return file_candidate


class BuildExiv2(BuildCMakeLib):

    def __init__(self, dist):

        super().__init__(dist)
        self.extra_cmake_options += [
            "-DBUILD_SHARED_LIBS:BOOL=OFF",
            "-DBUILD_TESTING:BOOL=OFF",
        ]

    def run(self):
        conan_cmd = self.get_finalized_command("build_conan")
        build_clib = self.get_finalized_command("build_clib")
        conan_cmd.run()
        toolchain_locations = [
            self.build_temp,
            os.path.join(self.build_temp, "conan"),
            os.path.join(self.build_temp, "Release"),
            os.path.join(self.build_temp, "Release", "conan"),
        ]
        cmake_toolchain = locate_file("conan_paths.cmake", toolchain_locations)
        if cmake_toolchain is None:
            raise FileNotFoundError(
                f"Missing toolchain file conan_paths.cmake. "
                f"Searching in {toolchain_locations}",
            )
        self.extra_cmake_options.append(
            f'-DCMAKE_TOOLCHAIN_FILE={cmake_toolchain}'
        )

        super().run()
        ext_command = self.get_finalized_command("build_ext")

        core_ext = ext_command.ext_map['py3exiv2bind.core']
        build_locations = [
            build_clib.build_temp,
            os.path.join(build_clib.build_temp, "conan"),
            os.path.join(build_clib.build_temp, "conan", "Release"),
            os.path.join(build_clib.build_temp, "Release"),
        ]
        conanbuildinfotext = locate_conanbuildinfo(build_locations)
        metadata_strategy = ConanBuildInfoTXT()
        text_md = metadata_strategy.parse(conanbuildinfotext)
        for lib in text_md["libs"]:
            core_ext.libraries.append(lib)
        for path in text_md["lib_paths"]:
            core_ext.library_dirs.append(path)

        core_ext.include_dirs.append(os.path.join(self.build_temp, "include"))
        if os.name == 'nt':
            core_ext.libraries.append("shell32")
            core_ext.libraries.append("psapi")
            core_ext.libraries.append("Ws2_32")

        core_ext.libraries.append("exiv2-xmp")

        temp_lib_dir = os.path.join(self.build_temp, "lib")

        if temp_lib_dir not in core_ext.library_dirs:
            core_ext.library_dirs.insert(0, temp_lib_dir)


exiv2 = ("exiv2", {
    "sources": [],
    "CMAKE_SOURCE_DIR": os.path.dirname(__file__),
    "CMAKE_CONFIG": [
        '-Dpyexiv2bind_generate_python_bindings:BOOL=NO',
        '-DEXIV2_ENABLE_NLS:BOOL=NO',
        '-DEXIV2_ENABLE_VIDEO:BOOL=OFF',
        '-DEXIV2_ENABLE_PNG:BOOL=OFF'
    ],
})


cmd_class['build_clib'] = BuildExiv2

exiv2_extension = Pybind11Extension(
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
        "py3exiv2bind/core/glue"
    ],
    language='c++',

)

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
