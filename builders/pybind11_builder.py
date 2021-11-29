from typing import List

import pybind11
from setuptools.command.build_ext import build_ext
import os
import abc
import shutil
import re
# from sys import platform
import platform
import tempfile
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

    def _get_path_dirs(self):
        if platform.system() == "Windows":
            paths = os.environ['path'].split(";")
        else:
            paths = os.environ['PATH'].split(":")
        return [path for path in paths if os.path.exists(path)]

    def get_library_paths(self):
        search_paths = []
        library_search_paths = \
            self.compiler.library_dirs + \
            self.compiler.runtime_library_dirs + \
            self.library_dirs + \
            self._get_path_dirs()

        for lib_path in library_search_paths:
            if not os.path.exists(lib_path):
                continue
            if lib_path in search_paths:
                continue
            search_paths.append(lib_path)

        return search_paths

    def run(self):
        super().run()
        for e in self.extensions:
            dll_name = \
                os.path.join(self.build_lib, self.get_ext_filename(e.name))
            search_dirs = self.get_library_paths()
            search_dirs.insert(0, self.build_temp)
            self.resolve_shared_library(dll_name, search_dirs)

    def resolve_shared_library(self, dll_name, search_paths=None):
        dll_dumper = get_so_handler(dll_name, self)
        dll_dumper.set_compiler(self.compiler)
        try:
            dll_dumper.resolve(search_paths)
        except FileNotFoundError:
            if search_paths is not None:
                self.announce(
                    "Error: Not all required shared libraries were resolved. "
                    "Searched:\n{}".format('\n'.join(search_paths)), 5
                )
            raise

    def find_missing_libraries(self, ext):
        missing_libs = []
        for lib in ext.libraries:
            if self.compiler.find_library_file(self.library_dirs + ext.library_dirs, lib) is None:
                missing_libs.append(lib)
        return missing_libs

    def build_extension(self, ext):
        if self.compiler.compiler_type == "unix":
            ext.extra_compile_args.append(f"-std=c++{self.cxx_standard}")
        else:
            ext.extra_compile_args.append(f"/std:c++{self.cxx_standard}")
        ext.include_dirs.append(self.get_pybind11_include_path())
        super().build_extension(ext)

    def get_pybind11_include_path(self) -> str:
        return pybind11.get_include()


class AbsSoHandler(abc.ABC):
    def __init__(self, library_file, context):
        self.library_file = library_file
        self._compiler = None
        self.context = context

    def set_compiler(self, compiler):
        self._compiler = compiler

    @classmethod
    def is_system_file(cls, filename) -> bool:
        return False

    @abc.abstractmethod
    def get_deps(self) -> List[str]:
        pass

    def resolve(self, search_paths=None) -> None:
        dest = os.path.dirname(self.library_file)
        for dep in filter(lambda x: not self.is_system_file(x),
                          self.get_deps()):

            if os.path.exists(os.path.join(dest, dep)):
                continue
            if search_paths is None:
                if platform.system() == "Windows":
                    search_paths = self.context.compiler.library_dirs + \
                                   os.environ['path'].split(";")
                else:
                    search_paths = self.context.compiler.library_dirs + \
                                   os.environ['PATH'].split(":")

            dll = self.context.find_deps(dep, search_paths)
            if dll is None:
                raise FileNotFoundError(f"Unable to locate {dep} for "
                                        f"{self.library_file}")
            if not self.is_system_file(dll):
                type(self)(dll, self.context).resolve(search_paths)



class NullHandlerStrategy(AbsSoHandler):

    def get_deps(self) -> List[str]:
        return []

class MacholibStrategy(AbsSoHandler):
    _system_files = []

    @classmethod
    def get_system_files(cls):
        if len(cls._system_files) == 0:
            cls._system_files = os.listdir("/usr/lib")
        return cls._system_files

    def get_deps(self) -> List[str]:
        from macholib import MachO
        libs = set()
        for header in MachO.MachO(self.library_file).headers:
            for _idx, _name, other in header.walkRelocatables():
                libs.add(os.path.split(other)[-1])
        return list(libs)

    @classmethod
    def is_system_file(cls, filename) -> bool:
        if filename in [
            "libsystem_malloc.dylib"
        ]:
            return True

        if filename in cls.get_system_files():
            return True
        return False

    def resolve(self, search_path=None) -> None:
        from macholib import MachOStandalone
        if self.is_system_file(os.path.split(self.library_file)[1]):
            return

        d = MachOStandalone.MachOStandalone(
            os.path.abspath(os.path.dirname(self.library_file)))

        d.dest = os.path.abspath(os.path.dirname(self.library_file))
        libraries = []
        for dep in self.get_deps():
            if self.is_system_file(dep):
                continue
            found_dep = self.context.find_deps(dep, search_path)
            c_dep = d.copy_dylib(found_dep)
            dep_file = d.mm.locate(c_dep)
            if dep_file is None:
                raise FileNotFoundError(f"Unable to locate {dep}, "
                                        f"required by {self.library_file}")

            self.context.announce(f"Fixing up {dep}")

            libraries.append(dep_file)
            type(self)(dep_file, self.context).resolve(search_path)
        libraries.append(self.library_file)
        d.run(platfiles=libraries, contents="@rpath/..")


class AudidWheelsHandlerStrategy(AbsSoHandler):

    def get_deps(self) -> List[str]:
        return []


class DllHandlerStrategy(AbsSoHandler):
    DEPS_REGEX = \
        r'(?<=(Image has the following dependencies:(\n){2}))((?<=\s).*\.dll\n)*'

    def __init__(self, library_file, context):
        super().__init__(library_file, context)
        self._compiler = None

    def resolve(self, search_paths=None) -> None:
        dest = os.path.dirname(self.library_file)
        for dep_name in self.get_deps():
            if self.is_system_file(dep_name):
                self.context.announce(f"Not bundling {dep_name}", 4)
                continue
            dep = self.find_lib(dep_name, search_paths=search_paths)
            if not dep:
                raise FileNotFoundError(
                    f"Unable to locate {dep_name} required by "
                    f"{self.library_file}")

            new_dll = os.path.join(dest, os.path.split(dep)[-1])
            if os.path.exists(new_dll):
                continue
            self.context.copy_file(dep, new_dll)
            DllHandlerStrategy(new_dll, self.context).resolve(search_paths)

    def find_lib(self, lib, search_paths=None):
        if search_paths is None:
            search_paths = os.environ['path'].split(";")

        for path in search_paths:
            if not os.path.exists(path):
                self.context.announce(f"Skipping invalid path: {path}", 5)
                continue
            for f in os.scandir(path):
                if f.name.lower() == lib.lower():
                    return f.path

    @classmethod
    def is_system_file(cls, filename: str) -> bool:
        system_exclusions = [
            "msvcp140.dll",
            "vcruntime140.dll",
            "vcruntime140_1.dll"
        ]
        system_libs = []
        for i in os.listdir(r"c:\Windows\System32"):
            if i.endswith(".dll") and i not in system_exclusions:
                system_libs.append(i.lower())

        if filename.lower() in system_libs:
            return True

        if "api-ms-win-crt" in filename:
            return True

        if "api-ms-win-core" in filename:
            return True

        if "api-ms-win" in filename:
            return True

        if filename.startswith("python"):
            return True
        if filename == "KERNEL32.dll":
            return True
        return False

    def get_deps(self) -> List[str]:
        if not self.context.compiler.initialized:
            self.context.compiler.initialize()
        so_name = os.path.split(self.library_file)[-1]
        with tempfile.TemporaryDirectory() as td:
            output_file = os.path.join(td, f'{so_name}.dependents')
            dumpbin = \
                shutil.which("dumpbin",
                             path=os.path.dirname(self.context.compiler.cc))

            self.context.compiler.spawn(
                [
                    dumpbin,
                    '/dependents',
                    os.path.abspath(self.library_file),
                    f'/out:{output_file}'
                ]
            )
            return DllHandlerStrategy.parse_dumpbin_deps(file=output_file)
    def resolve_shared_library(self, dll_name, search_paths=None):
        dll_dumper = get_so_handler(dll_name, self)
        dll_dumper.set_compiler(self.compiler)
        try:
            dll_dumper.resolve(search_paths)
        except FileNotFoundError:
            if search_paths is not None:
                self.announce(
                    "Error: Not all required shared libraries were resolved. "
                    "Searched:\n{}".format('\n'.join(search_paths)), 5
                )
            raise
    @classmethod
    def parse_dumpbin_deps(cls, file) -> List[str]:

        dlls = []
        dep_regex = re.compile(cls.DEPS_REGEX)

        with open(file) as f:
            d = dep_regex.search(f.read())
            for x in d.group(0).split("\n"):
                if x.strip() == "":
                    continue
                dll = x.strip()
                dlls.append(dll)
        return dlls

def get_so_handler(shared_library: str, context,
                   system_name: str = None) -> AbsSoHandler:

    system_name = system_name or platform.system()
    strategies = {
        # "Darwin": NullHandlerStrategy,
        "Darwin": MacholibStrategy,
        "Linux": AudidWheelsHandlerStrategy,
        "Windows": DllHandlerStrategy,
    }
    strat = strategies.get(
        system_name, NullHandlerStrategy)
    return strat(shared_library, context)
