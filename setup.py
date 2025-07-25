import abc
import json
import os

import sys
import shutil
from typing import Optional, List, Dict
import contextlib
import platform
import cmake
from pybind11.setup_helpers import Pybind11Extension

from setuptools import setup, errors, Distribution
from setuptools.command.build_clib import build_clib

from uiucprescon.build.conan.files import read_conan_build_info_json
from uiucprescon.build.pybind11_builder import BuildPybind11Extension

MIN_MACOSX_DEPLOYMENT_TARGET = '10.15'
PACKAGE_NAME = "py3exiv2bind"

class BuildExtension(BuildPybind11Extension):

    def build_extension(self, ext: Pybind11Extension) -> None:
        build_clib_cmd = self.get_finalized_command('build_clib')
        ext.include_dirs.insert(0, os.path.join(build_clib_cmd.installed_prefix, "include"))
        ext.library_dirs.insert(0, os.path.join(build_clib_cmd.installed_prefix, "lib"))
        super().build_extension(ext)



class AbsCMakePlatform(abc.ABC):

    def __init__(self, clib_builder) -> None:
        super().__init__()
        self.clib_builder = clib_builder

    @abc.abstractmethod
    def platform_specific_configs(self) -> List[str]:
        """Get cmake arguments specifically for a given platform"""


class WinCMakelib(AbsCMakePlatform):

    def platform_specific_configs(self) -> List[str]:
        return []


class UnixCMakePlatform(AbsCMakePlatform):
    def platform_specific_configs(self) -> List[str]:
        return ['-DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=ON']

@contextlib.contextmanager
def set_compiler_env(envvars: Dict[str, str]):
    og_env = os.environ.copy()
    os.environ.update(**envvars)

    yield

    # Do not assign os.environ to og_env because it makes os.environ
    # case-sensitive, even on OSs that have case-insensitive environment
    # variables such as windows. When this happens it makes it hard to use
    # os.environ and breaks setuptools trying to find Visual Studio.

    # Remove any keys that were set since entering the context
    for k in [
        k for k in os.environ.keys()
        if k not in og_env
    ]:
        del os.environ[k]

    # set the values of environment variables before entering the context
    for k, v in og_env.items():
        os.environ[k] = v


class OSXCMakelib(UnixCMakePlatform):
    def platform_specific_configs(self):
        configs: List[str] = super().platform_specific_configs()
        sys_root = self.get_cmake_osx_sysroot()
        if sys_root is not None:
            configs.append(sys_root)
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
        self.installed_prefix = None
        self.cmake_build_path = None

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
        self.cmake_exec = shutil.which("cmake", path=cmake.CMAKE_BIN_DIR)
        self.cmake_build_path = os.path.join(self.build_temp, "cmake_builds")
        self.installed_prefix = os.path.join(self.build_temp, "cmake_deps")

    @staticmethod
    def _get_new_compiler():
        build_ext = Distribution().get_command_obj("build_ext")
        build_ext.finalize_options()
        # register an extension to ensure a compiler is created
        build_ext.extensions = [Pybind11Extension("ignored", ["ignored.c"])]
        # disable building fake extensions
        build_ext.build_extensions = lambda: None
        # run to populate self.compiler
        build_ext.run()
        return build_ext.compiler

    def run(self):

        if not self.libraries:
            return

        self.compiler = self._get_new_compiler()

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
        dep_build_path = os.path.join(self.cmake_build_path, str(extension[0]))
        if not os.path.exists(dep_build_path):
            self.mkpath(dep_build_path)

        if self.debug:
            build_configuration_name = 'Debug'
        else:
            build_configuration_name = 'Release'
        build_conan = self.get_finalized_command("build_conan")
        toolchain_locations = [
            build_conan.build_temp,
            os.path.join(self.build_temp, "conan"),
            os.path.join(self.build_temp, "Release"),
            os.path.join(self.build_temp, "Release", "conan"),
        ]
        cmake_toolchain_file_name = "conan_toolchain.cmake"
        cmake_toolchain = locate_file(cmake_toolchain_file_name, toolchain_locations)
        if cmake_toolchain is None:
            raise FileNotFoundError(f"Missing toolchain file {cmake_toolchain_file_name}")

        configure_command = [
            self.cmake_exec, f'-S{source_dir}'
        ]
        configure_command += [
            f'-B{dep_build_path}',
            f"-DCMAKE_TOOLCHAIN_FILE={cmake_toolchain}",
            f'-DCMAKE_BUILD_TYPE={build_configuration_name}',
            f'-DCMAKE_INSTALL_PREFIX={os.path.abspath(self.installed_prefix)}',
        ]
        configure_command += extension[1].get('CMAKE_CONFIG', [])
        configure_command += self._cmake_platform.platform_specific_configs()
        configure_command += self.extra_cmake_options

        if platform.system() == "Darwin":
            env_vars = {
                'MACOSX_DEPLOYMENT_TARGET':
                    os.environ.get(
                        'MACOSX_DEPLOYMENT_TARGET',
                        MIN_MACOSX_DEPLOYMENT_TARGET
                    )
            }
        else:
            env_vars = {}
        if platform.system() == "Windows":
            if not self.compiler.initialized:
                self.compiler.initialize()
        with set_compiler_env(env_vars):
            try:
                self.compiler.spawn(configure_command)
            except errors.ExecError:
                print("Failed at CMake config time", file=sys.stderr)
                raise

    def build_cmake(self, extension: Pybind11Extension):
        build_command = [
            self.cmake_exec,
            "--build", os.path.join(self.cmake_build_path, str(extension[0])),
        ]
        if self.verbose == 1:
            build_command.append("--verbose")

        # Add config
        build_command.append("--config")
        if self.debug:
            build_command.append("Debug")
        else:
            build_command.append("Release")

        build_ext_cmd = self.get_finalized_command("build_ext")
        if build_ext_cmd.parallel:
            build_command.extend(["-j", str(build_ext_cmd.parallel)])

        try:
            if platform.system() == "Darwin":
                env_vars = {
                    'MACOSX_DEPLOYMENT_TARGET':
                        os.environ.get(
                            'MACOSX_DEPLOYMENT_TARGET',
                            MIN_MACOSX_DEPLOYMENT_TARGET
                        )
                }
            else:
                env_vars = {}
            with set_compiler_env(env_vars):
                self.compiler.spawn(build_command)
        except errors.ExecError:
            print(f"Conan failed when running {build_command}", file=sys.stderr)
            raise

    def build_install_cmake(self, extension: Pybind11Extension):
        dep_build_path = os.path.join(self.cmake_build_path, str(extension[0]))
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

        try:
            self.compiler.spawn(install_command)
        except errors.ExecError:
            print("CMake failed at install time")
            raise


def locate_file(file_name, search_locations):
    for location in search_locations:
        file_candidate = os.path.join(location, file_name)
        if os.path.exists(file_candidate):
            return file_candidate

def add_conan_build_info(core_ext, build_temp):

    build_locations = [
        build_temp,
        os.path.join(build_temp, "conan"),
        os.path.join(build_temp, "conan", "Release"),
        os.path.join(build_temp, "Release"),
    ]
    for location in build_locations:
        build_info = os.path.join(location, "conan_build_info.json")
        if os.path.exists(build_info):
            break
    else:
        raise FileNotFoundError(
            f"conan_build_info.json not found, searched {*build_locations,}"
        )

    with open(build_info, 'r', encoding="utf-8") as f:
        build_info = read_conan_build_info_json(f)

    for lib in build_info['libs']:
        if lib not in core_ext.libraries:
            core_ext.libraries.append(lib)

    for path in reversed(build_info['lib_paths']):
        if path not in core_ext.libraries:
            core_ext.library_dirs.insert(0, path)
    return core_ext

def get_conan_preset_name(conan_build_folder: str) -> str:
    cmake_presets_json_file = os.path.join(conan_build_folder, "CMakePresets.json")
    if not os.path.exists(cmake_presets_json_file):
        raise FileNotFoundError(f"Missing {cmake_presets_json_file}")
    with open(cmake_presets_json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    configure_presets = data.get('configurePresets')
    if configure_presets is None:
        raise KeyError(f"configurePresets key missing from {cmake_presets_json_file}")
    for preset in configure_presets:
        if "conan" in preset['name']:
            return preset['name']
    raise ValueError("Unable to locate a conan config preset")


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
        self.extra_cmake_options.append(
            f"--preset={get_conan_preset_name(conan_cmd.build_temp)}"
        )

        super().run()
        ext_command = self.get_finalized_command("build_ext")


        core_ext = \
            add_conan_build_info(
                ext_command.ext_map['py3exiv2bind.core'],
                conan_cmd.build_temp
            )

        core_ext.include_dirs.insert(0, os.path.join(self.build_temp, "include"))
        if os.name == 'nt':
            core_ext.libraries.append("shell32")
            core_ext.libraries.append("psapi")
            core_ext.libraries.append("Ws2_32")

        temp_lib_dir = os.path.join(self.build_temp, "lib")

        if temp_lib_dir not in core_ext.library_dirs:
            core_ext.library_dirs.insert(0, temp_lib_dir)



setup(
    libraries=[
        ("exiv2", {
            "sources": [],
            "CMAKE_SOURCE_DIR": os.path.dirname(__file__),
            "CMAKE_CONFIG": [
                '-Dpyexiv2bind_generate_python_bindings:BOOL=NO',
                '-DEXIV2_ENABLE_NLS:BOOL=NO',
                '-DEXIV2_ENABLE_VIDEO:BOOL=OFF',
                '-DEXIV2_ENABLE_PNG:BOOL=OFF',
                '-DEXIV2_BUILD_EXIV2_COMMAND:BOOL=OFF',
                "-DCMAKE_CXX_STANDARD=17"
            ],
        })
    ],
    ext_modules=[
        Pybind11Extension(
            "py3exiv2bind.core",
            sources=[
                "src/py3exiv2bind/core/core.cpp",
                "src/py3exiv2bind/core/glue/ExifStrategy.cpp",
                "src/py3exiv2bind/core/glue/glue.cpp",
                "src/py3exiv2bind/core/glue/Image.cpp",
                "src/py3exiv2bind/core/glue/IPTC_Strategy.cpp",
                "src/py3exiv2bind/core/glue/XmpStrategy.cpp",
                "src/py3exiv2bind/core/glue/MetadataProcessor.cpp",
            ],
            libraries=[
                "exiv2",
            ],
            include_dirs=[
                "src/py3exiv2bind/core/glue",
            ],
            language='c++',
            cxx_std=17
        )
    ],
    cmdclass={
        "build_ext": BuildExtension,
        "build_clib": BuildExiv2,
    }
)
