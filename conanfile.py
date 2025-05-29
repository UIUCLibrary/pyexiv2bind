import os
from platform import platform

from conans import ConanFile, CMake

class pyexiv2bind(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    generators = ["cmake_find_package", "cmake_paths", "json"]
    default_options = {
        "expat:shared": False,
    }

    def requirements(self):
        self.requires("brotli/1.0.9")
        self.requires("expat/2.5.0")
        self.requires("zlib/1.3.1")
        if self.settings.os in ["Macos", "Linux"]:
            self.requires("libiconv/1.17")
    def imports(self):
        self.copy("*.dll", dst="bin", src="bin") # From bin to bin
        self.copy("*.dylib*", dst=".", src="lib") # From lib to bin
