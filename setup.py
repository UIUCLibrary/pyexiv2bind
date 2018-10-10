import os
import sys
import shutil
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import platform
import subprocess

# CMAKE = shutil.which("cmake")

class CMakeExtension(Extension):
    def __init__(self, name, sources=None):
        # don't invoke the original build_ext for this special extension
        super().__init__(name, sources=sources if sources is not None else [])


class BuildCMakeExt(build_ext):
    user_options = build_ext.user_options + [
        ('cmake-exec=', None,
         "Location of CMake. Defaults of CMake located on path")
    ]

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
            'GCC': "Unix Makefiles",
            'Clang': "Unix Makefiles",
        }

        return cmake_build_systems_lut[python_compiler]

    def run(self):
        for extension in self.extensions:
            self.configure_cmake(extension)
            self.build_cmake(extension)
            self.build_install_cmake(extension)
            self.bundle_shared_library_deps(extension)

    def bundle_shared_library_deps(self, extension: Extension):
        print("bundling")
        pass

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
            f'-G{self.get_build_generator_name()}'
        ]

        package_source = os.path.join(source_dir, "py3exiv2bind")

        if self.inplace == 1:
            configure_command.append(
                f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{build_configuration_name.upper()}={package_source}')

        configure_command.append(
            f'-DCMAKE_BUILD_TYPE={build_configuration_name}')

        configure_command.append(f'-DCMAKE_INSTALL_PREFIX={self.build_lib}')

        configure_command += self.extra_cmake_options

        if sys.gettrace():
            print("Running as a debug", file=sys.stderr)
            subprocess.check_call(configure_command)
        else:
            self.spawn(configure_command)
        # self.spawn(configure_command)

    def build_cmake(self, extension: Extension):
        self.announce("Building binaries", level=3)

        build_command = [
            self.cmake_exec,
            "--build",
            self.build_temp,
        ]

        # Add config
        build_command.append("--config")
        if self.debug:
            build_command.append("Debug")
        else:
            build_command.append("Release")

        if self.parallel:
            build_command.extend(["-j", str(self.parallel)])

        if "Visual Studio" in self.get_build_generator_name():
            build_command += ["--", "/NOLOGO", "/verbosity:minimal"]

        if sys.gettrace():
            subprocess.check_call(build_command)
        else:
            self.spawn(build_command)

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

        install_command += ["--target", "INSTALL"]

        if self.parallel:
            install_command.extend(["-j", str(self.parallel)])

        if "Visual Studio" in self.get_build_generator_name():
            install_command += ["--", "/NOLOGO", "/verbosity:quiet"]

        if sys.gettrace():
            print("Running as a debug", file=sys.stderr)
            subprocess.check_call(install_command)
        else:
            self.spawn(install_command)


class Exiv2Ext(BuildCMakeExt):

    def __init__(self, dist):
        super().__init__(dist)
        self.extra_cmake_options += [
            "-Dpyexiv2bind_generate_venv:BOOL=OFF",
            "-DBUILD_SHARED_LIBS:BOOL=OFF",
            "-DEXIV2_VERSION_TAG:STRING=11e66c6c9eceeddd2263c3591af6317cbd05c1b6",
            "-DBUILD_TESTING:BOOL=OFF",
        ]


exiv2_extension = CMakeExtension("exiv2_wrapper")

setup(
    packages=['py3exiv2bind'],
    python_requires=">=3.6",
    setup_requires=['pytest-runner'],
    test_suite="tests",
    tests_require=['pytest'],
    ext_modules=[exiv2_extension],
    cmdclass={
        "build_ext": Exiv2Ext,
    },

)
