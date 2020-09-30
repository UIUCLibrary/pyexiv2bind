import os

from conans import ConanFile, CMake

class pyexiv2bind(ConanFile):
    requires = [
        "zlib/1.2.11",
        "expat/2.2.9"
    ]
    settings = "os", "arch", "compiler", "build_type"

    generators = ["cmake_paths"]
    default_options = {
    }

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin") # From bin to bin
    #     self.copy("*.dylib*", dst="bin", src="lib") # From lib to bin
    #
    # def configure(self):
    #     if self.settings.os == "Linux":
    #         self.options["ffmpeg"].vorbis = False
    #
    # def build(self):
    #     cmake = CMake(self)
    #     cmake_toolchain_file = os.path.join(self.build_folder, "conan_paths.cmake")
    #     assert os.path.exists(cmake_toolchain_file)
    #     cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = cmake_toolchain_file
    #     cmake.configure()
    #     cmake.build()

