import pybind11
from setuptools.command.build_ext import build_ext
import os

DEFAULT_CPP_STANDARD = "14"


class BuildPybind11Extension(build_ext):
    user_options = build_ext.user_options + [
        ('cxx-standard=', None, f"C++ version to use. Default: {DEFAULT_CPP_STANDARD}")
    ]

    def initialize_options(self):
        super().initialize_options()
        self.cxx_standard = None

    def finalize_options(self):

        self.cxx_standard = self.cxx_standard or DEFAULT_CPP_STANDARD
        super().finalize_options()

    def find_deps(self, lib, search_paths=None):
        search_paths = search_paths or os.environ['path'].split(";")

        search_paths.append(
            self.get_finalized_command("build_clib").build_temp
        )

        for path in search_paths:
            if not os.path.exists(path):
                self.announce(f"Skipping invalid path: {path}", 5)
                continue
            for f in os.scandir(path):
                if f.name.lower() == lib.lower():
                    return f.path

    def find_missing_libraries(self, ext):
        missing_libs = []
        for lib in ext.libraries:
            if self.compiler.find_library_file(self.library_dirs + ext.library_dirs, lib) is None:
                missing_libs.append(lib)
        return missing_libs

    def build_extension(self, ext):
        self.announce("adsfadsf", level=3)
        if self.compiler.compiler_type == "unix":
            ext.extra_compile_args.append(f"-std=c++{self.cxx_standard}")
        else:
            ext.extra_compile_args.append(f"/std:c++{self.cxx_standard}")
        ext.include_dirs.append(self.get_pybind11_include_path())
        super().build_extension(ext)

    def get_pybind11_include_path(self) -> str:
        return pybind11.get_include()
