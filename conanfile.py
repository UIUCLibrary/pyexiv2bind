import os
from platform import platform

from conans import ConanFile, CMake

class pyexiv2bind(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    generators = ["cmake_paths"]
    default_options = {
        "expat:shared": False
    }

    def requirements(self):
        # if self.settings.os == "Windows":
        #     self.requires("Expat/2.2.9@pix4d/stable")
        # else:
        self.requires("expat/2.2.9")
        self.requires("zlib/1.2.11")
    def imports(self):
        self.copy("*.dll", dst="bin", src="bin") # From bin to bin
    #     self.copy("*.dylib*", dst="bin", src="lib") # From lib to bin
    #
    # def configure(self):
    #
    # #         self.options["ffmpeg"].vorbis = False
    #
    # def build(self):
    #     cmake = CMake(self)
    #     cmake_toolchain_file = os.path.join(self.build_folder, "conan_paths.cmake")
    #     assert os.path.exists(cmake_toolchain_file)
    #     cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = cmake_toolchain_file
    #     cmake.configure()
    #     cmake.build()

