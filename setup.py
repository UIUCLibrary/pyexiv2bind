import abc
import json
import os
import re
import sys
import shutil
import tempfile
from typing import List, Optional, Tuple, Iterable, Dict, Any, Union
# import ninja
import setuptools

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import platform
import subprocess
from setuptools.command.build_clib import build_clib
from distutils.sysconfig import customize_compiler
from functools import reduce

sys.path.insert(0, os.path.dirname(__file__))
from builders.deps import get_win_deps
cmd_class = {}
try:
    from builders.conan_libs import BuildConan
    cmd_class["build_conan"] = BuildConan
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


class ConanBuildInfoParser:
    def __init__(self, fp):
        self._fp = fp

    def parse(self) -> Dict[str, List[str]]:
        data = dict()
        for subject_chunk in self.iter_subject_chunk():
            subject_title = subject_chunk[0][1:-1]

            data[subject_title] = subject_chunk[1:]
        return data

    def iter_subject_chunk(self) -> Iterable[Any]:
        buffer = []
        for line in self._fp:
            line = line.strip()
            if len(line) == 0:
                continue
            if line.startswith("[") and line.endswith("]") and len(buffer) > 0:
                yield buffer
                buffer.clear()
            buffer.append(line)
        yield buffer
        buffer.clear()


class ConanImportManifestParser:
    def __init__(self, fp):
        self._fp = fp

    def parse(self) -> List[str]:
        libs = set()
        for line in self._fp:
            t = line.split()[0].strip(":\n")
            if os.path.exists(t):
                libs.add(t)
        return list(libs)


class BuildConan(setuptools.Command):
    user_options = [
        ('conan-exec=', "c", 'conan executable')
    ]

    description = "Get the required dependencies from a Conan package manager"

    def get_from_txt(self, conanbuildinfo_file):
        definitions = []
        include_paths = []
        lib_paths = []
        bin_paths = []
        libs = []

        with open(conanbuildinfo_file, "r") as f:
            parser = ConanBuildInfoParser(f)
            data = parser.parse()
            definitions = data['defines']
            include_paths = data['includedirs']
            lib_paths = data['libdirs']
            bin_paths = data['bindirs']
            libs = data['libs']

        return {
            "definitions": definitions,
            "include_paths": list(include_paths),
            "lib_paths": list(lib_paths),
            "bin_paths": list(bin_paths),
            "libs": list(libs),

        }

    def initialize_options(self):
        self.conan_exec = None
        self.conan_cache = None

    def finalize_options(self):
        if self.conan_exec is None:
            self.conan_exec = shutil.which("conan")
            if self.conan_exec is None:
                raise Exception("missing conan_exec")
        if self.conan_cache is None:
            build_ext_cmd = self.get_finalized_command("build_ext")
            build_dir = build_ext_cmd.build_temp

            self.conan_cache = \
                os.path.join(
                    os.environ.get("CONAN_USER_HOME", build_dir),
                    ".conan"
                )

    def getConanBuildInfo(self, root_dir):
        for root, dirs, files in os.walk(root_dir):
            for f in files:
                if f == "conanbuildinfo.json":
                    return os.path.join(root, f)
        return None

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

        text_md = self.get_from_txt(conanbuildinfotext)
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

    def find_conan_paths_cmake(self) -> Optional[str]:
        search_dirs = []
        build_ext_cmd = self.get_finalized_command("build_ext")
        search_dirs.append(build_ext_cmd.build_temp)
        for f in search_dirs:
            potential = os.path.join(f, "conan_paths.cmake")
            if os.path.exists(potential):
                return potential
        return None
    # conan_paths = os.path.join(self.build_temp, "conan_paths.cmake")

    def get_import_paths_from_import_manifest(self, manifest_file) -> \
            List[str]:

        lib_dirs = set()
        for lib in self.get_libraries_from_import_manifest(manifest_file):
            lib_dirs.add(os.path.dirname(lib))
        return list(lib_dirs)

    def get_libraries_from_import_manifest(self, manifest_file) -> List[str]:
        with open(manifest_file, "r") as f:
            parser = ConanImportManifestParser(f)
            return parser.parse()

    def get_from_json(self, conanbuildinfo_file) -> \
            Dict[str, List[Union[str, Tuple[str, Optional[str]]]]]:

        if conanbuildinfo_file is None:
            raise FileNotFoundError("Unable to locate conanbuildinfo.json")
        self.announce(f"Reading from {conanbuildinfo_file}", 5)
        with open(conanbuildinfo_file) as f:
            conan_build_info = json.loads(f.read())

        def reduce_dups(a, b, key):

            if isinstance(a, set):
                collection = a
            else:
                collection = set(a[key])
            collection = collection.union(b[key])
            return collection

        libs = reduce(lambda a, b: reduce_dups(a, b, key="libs"),
                      conan_build_info['dependencies'])
        include_paths = reduce(
            lambda a, b: reduce_dups(a, b, key="include_paths"),
            conan_build_info['dependencies'])
        self.announce(f"Adding [{','.join(include_paths)}] to include path", 4)
        lib_paths = reduce(lambda a, b: reduce_dups(a, b, key="lib_paths"),
                           conan_build_info['dependencies'])
        self.announce(
            f"Adding [{', '.join(lib_paths)}] to library search path", 4)

        definitions = list()
        for dep in conan_build_info['dependencies']:
            definitions += [(d,) for d in dep['defines']]

        return {
            "definitions": definitions,
            "include_paths": list(include_paths),
            "lib_paths": list(lib_paths),
            "libs": list(libs)
        }


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
        ext_command.ext_map['py3exiv2bind.core'].libraries.append("xmp")
        ext_command.ext_map['py3exiv2bind.core'].library_dirs.insert(
            0, os.path.join(self.build_temp, "lib")
        )



exiv2 = ("exiv2", {
    "sources": [],
    "CMAKE_SOURCE_DIR": os.path.dirname(__file__)
})


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


class BuildPybind11Extension(build_ext):

    def initialize_options(self):
        super().initialize_options()

    def finalize_options(self):
        super().finalize_options()

    def run(self):
        self.include_dirs.insert(
            0, os.path.abspath(os.path.join(self.build_temp, "include"))
        )

        lib_dir = os.path.abspath(os.path.join(self.build_temp, "lib"))
        if os.path.exists(lib_dir):
            self.library_dirs.insert(0, lib_dir)
        lib64_dir = os.path.abspath(os.path.join(self.build_temp, "lib64"))
        if os.path.exists(lib64_dir):
            self.library_dirs.insert(0, lib64_dir)

        import pybind11
        self.include_dirs.insert(0, pybind11.get_include())
        super().run()

        for e in self.extensions:
            dll_name = \
                os.path.join(self.build_lib, self.get_ext_filename(e.name))
            search_dirs = self.get_library_paths()
            search_dirs.insert(0, self.build_temp)
            self.resolve_shared_library(dll_name, search_dirs)

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

    def _get_path_dirs(self):
        if platform.system() == "Windows":
            paths = os.environ['path'].split(";")
        else:
            paths = os.environ['PATH'].split(":")
        return [path for path in paths if os.path.exists(path)]

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
            if self.compiler.find_library_file(self.library_dirs, lib) is None:
                missing_libs.append(lib)
        return missing_libs

    def build_extension(self, ext):
        missing = self.find_missing_libraries(ext)
        if self.compiler.compiler_type == "unix":
            ext.extra_compile_args.append("-std=c++14")
        else:
            ext.extra_compile_args.append("/std:c++14")

        if len(missing) > 0:
            self.announce(f"missing required deps [{', '.join(missing)}]. "
                          f"Trying to build them", 5)
            self.run_command("build_clib")
            build_clib_cmd = self.get_finalized_command("build_clib")

            ext.include_dirs.append(os.path.abspath(
                os.path.join(build_clib_cmd.build_clib, "include"))
            )

        build_clib_cmd = self.get_finalized_command("build_clib")

        new_libs = []
        for lib in ext.libraries:
            if self.compiler.compiler_type != "unix":
                if self.debug is None:
                    build_configuration = "Release"
                else:
                    build_configuration = "Debug"
                lib_path = self.compiler.find_library_file(
                    [
                        os.path.abspath(build_clib_cmd.build_clib),
                        os.path.abspath(
                            os.path.join(build_clib_cmd.build_clib, "lib")
                        ),
                    ],
                    lib
                )
                if lib_path is not None:
                    ext.library_dirs.append(os.path.dirname(lib_path))

            else:
                build_configuration = None
            t = build_clib_cmd.find_target(lib, build_configuration)

            res = build_clib_cmd.find_dep_libs_from_cmake(
                ext, t, remove_prefix=self.compiler.compiler_type == "unix")

            if res is not None:
                deps, flags = res
                if deps is not None:
                    if lib in deps:
                        deps.remove(lib)
                    new_libs += deps
        ext.libraries += new_libs

        super().build_extension(ext)

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
        "py3exiv2bind/core/glue"
    ],
    language='c++',

)
cmd_class['build_clib'] = BuildExiv2
cmd_class['build_conan'] =BuildConan
cmd_class["build_ext"] =  BuildPybind11Extension
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
    ext_modules=[exiv2_extension],
    package_data={"py3exiv2bind": ["py.typed"]},
    cmdclass=cmd_class
    # cmdclass={
    #     "build_ext": BuildPybind11Extension,
    #     "build_clib": BuildExiv2,
    #     "build_conan": BuildConan
    # },

)
