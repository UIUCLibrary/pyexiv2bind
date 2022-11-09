import abc
import sys
from typing import Optional
import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext
from . import conan_libs
from distutils.ccompiler import CCompiler
import os


class BuildPybind11Extension(build_ext):
    user_options = build_ext.user_options + [
        ('cxx-standard=', None, "C++ version to use. Default:11")
    ]

    def initialize_options(self):
        self.cxx_standard = None
        super().initialize_options()

    def finalize_options(self):
        super().finalize_options()

        # self.inplace keeps getting reset by the time it is needed so
        # capture it here
        self._inplace = self.inplace
        self.cxx_standard = self.cxx_standard or "14"

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

    def find_missing_libraries(self, ext, strategies=None):
        strategies = strategies or [
            UseSetuptoolsCompilerFileLibrary(
                compiler=self.compiler,
                dirs=self.library_dirs + ext.library_dirs
            ),
        ]
        conanfileinfo_locations = [
            self.get_finalized_command("build_clib").build_temp
        ]
        conan_info_dir = os.environ.get('CONAN_BUILD_INFO_DIR')
        if conan_info_dir:
            conanfileinfo_locations.insert(0, conan_info_dir)
        conanbuildinfo = conan_libs.locate_conanbuildinfo(conanfileinfo_locations)
        if conanbuildinfo:
            strategies.insert(
                0,
                UseConanFileBuildInfo(path=os.path.dirname(conanbuildinfo))
            )
        missing_libs = set(ext.libraries)
        for lib in ext.libraries:
            for strategy in strategies:
                if strategy.locate(lib) is not None:
                    missing_libs.remove(lib)
                    break
        return list(missing_libs)

    def build_extension(self, ext: Pybind11Extension):
        self._add_conan_libs_to_ext(ext)
        self.compiler: CCompiler
        if self.compiler.compiler_type == "unix":
            ext.extra_compile_args.append(f"-std=c++{self.cxx_standard}")
        else:
            ext.extra_compile_args.append(f"/std:c++{self.cxx_standard}")
        super().build_extension(ext)
        fullname = self.get_ext_fullname(ext.name)
        created_extension = os.path.join(
            self.build_lib,
            self.get_ext_filename(fullname)
        )
        if sys.platform == "darwin":
            self.spawn(['otool', "-L", created_extension])
        if sys.platform == "linux":
            self.spawn(['ldd', created_extension])

    def get_pybind11_include_path(self) -> str:
        return pybind11.get_include()

    def _add_conan_libs_to_ext(self, ext: Pybind11Extension):
        conan_build_info = os.path.join(
            self.get_finalized_command("build_clib").build_temp,
            "conanbuildinfo.txt"
        )
        if not os.path.exists(conan_build_info):
            return
        # libraries must retain order and put after existing libs
        for lib in _parse_conan_build_info(conan_build_info, "libs"):
            if lib not in ext.libraries:
                ext.libraries.append(lib)

        lib_output = os.path.abspath(os.path.join(self.build_temp, "lib"))

        build_py = self.get_finalized_command("build_py")
        package_path = build_py.get_package_dir(build_py.packages[0])
        if os.path.exists(lib_output) and not self._inplace:
            dest = os.path.join(self.build_lib, package_path)
            self.copy_tree(lib_output, dest)

        if sys.platform == "linux":
            if not self._inplace:
                ext.runtime_library_dirs.append("$ORIGIN")
            else:
                ext.runtime_library_dirs.append(os.path.abspath(lib_output))
                ext.library_dirs.insert(0, os.path.abspath(lib_output))
        ext.library_dirs = list(_parse_conan_build_info(conan_build_info, "libdirs")) + ext.library_dirs
        ext.include_dirs = list(_parse_conan_build_info(conan_build_info, "includedirs")) + ext.include_dirs
        defines = _parse_conan_build_info(conan_build_info, "defines")
        ext.define_macros = [(d, None) for d in defines] + ext.define_macros


class AbsFindLibrary(abc.ABC):
    @abc.abstractmethod
    def locate(self, library_name) -> Optional[str]:
        """Abstract method for locating a library."""


class UseSetuptoolsCompilerFileLibrary(AbsFindLibrary):
    def __init__(self, compiler, dirs):
        self.compiler = compiler
        self.dirs = dirs

    def locate(self, library_name) -> Optional[str]:
        return self.compiler.find_library_file(self.dirs, library_name)


class UseConanFileBuildInfo(AbsFindLibrary):

    def __init__(self, path) -> None:
        super().__init__()
        self.path = path

    def locate(self, library_name) -> Optional[str]:
        conan_build_info = os.path.join(self.path, "conanbuildinfo.txt")
        if not os.path.exists(conan_build_info):
            return None
        libs = _parse_conan_build_info(conan_build_info, "libs")
        return library_name if library_name in libs else None


def _parse_conan_build_info(conan_build_info_file, section):
    items = set()
    with open(conan_build_info_file, encoding="utf-8") as f:
        found = False
        while True:
            line = f.readline()
            if not line:
                break
            if line.strip() == f"[{section}]":
                found = True
                continue
            if found:
                if line.strip() == "":
                    found = False
                    continue
                if found:
                    items.add(line.strip())
    return items
