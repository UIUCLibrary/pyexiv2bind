import logging
import os
import sys
import shutil
import abc
from typing import Iterable, Any, Dict, List, Union
import setuptools
from distutils import ccompiler
from pathlib import Path
from builders.deps import get_win_deps
import json


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


class AbsConanBuildInfo(abc.ABC):
    @abc.abstractmethod
    def parse(self, filename: str) -> Dict[str, str]:
        pass


class ConanBuildInfoTXT(AbsConanBuildInfo):

    def parse(self, filename: str) -> Dict[str, Union[str, List[str]]]:
        with open(filename, "r") as f:
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


class AbsResultTester(abc.ABC):
    def __init__(self, compiler=None) -> None:
        self.compiler = compiler or ccompiler.new_compiler()

    def test_shared_libs(self, libs_dir):
        """Make sure all shared libraries in directory are linked"""
        for lib in os.scandir(libs_dir):
            if not lib.name.endswith(self.compiler.shared_lib_extension):
                continue
            self.test_binary_dependents(lib.path)

    @abc.abstractmethod
    def test_binary_dependents(self, file_path: Path):
        """Make sure shared library is linked"""


class MacResultTester(AbsResultTester):
    def test_binary_dependents(self, file_path: Path):
        otool = shutil.which("otool")
        self.compiler.spawn([otool, '-L', str(file_path.resolve())])


class WindowsResultTester(AbsResultTester):
    def test_binary_dependents(self, file_path: Path):
        self.compiler.initialize()
        deps = get_win_deps(str(file_path.resolve()), output_file="tesseract.depends", compiler=self.compiler)
        path = os.getenv('PATH')
        for dep in deps:
            print(f"{file_path} requires {dep}")
            locations = list(filter(os.path.exists, path.split(";")))
            for l in locations:
                dep_path = os.path.join(l, dep)
                if os.path.exists(dep_path):
                    print("Found requirement: {}".format(dep_path))
                    break
            else:
                print(f"Couldn't find {dep}")


class LinuxResultTester(AbsResultTester):
    def test_binary_dependents(self, file_path: Path):
        ldd = shutil.which("ldd")
        self.compiler.spawn([ldd, str(file_path.resolve())])


class CompilerInfoAdder:

    def __init__(self, build_ext_cmd) -> None:
        super().__init__()
        self._build_ext_cmd = build_ext_cmd
        if build_ext_cmd.compiler is None:
            self._place_to_add = build_ext_cmd
        else:
            self._place_to_add = build_ext_cmd.compiler

    def add_libs(self, libs: List[str]):
        extension_deps = set()
        for lib in reversed(libs):
            if lib not in self._place_to_add.libraries and lib not in extension_deps:
                self._place_to_add.libraries.insert(0, lib)

    def add_lib_dirs(self, lib_dirs: List[str]):
        for path in reversed(lib_dirs):
            assert os.path.exists(path)
            if path not in self._place_to_add.library_dirs:
                self._place_to_add.library_dirs.insert(0, path)

    def add_include_dirs(self, include_dirs: List[str]):
        for path in reversed(include_dirs):
            if path not in self._place_to_add.include_dirs:
                self._place_to_add.include_dirs.insert(0, path)
            else:
                self._place_to_add.compiler.include_dirs.insert(0, path)


class BuildConan(setuptools.Command):
    user_options = [
        ('conan-cache=', None, 'conan cache directory')
    ]

    description = "Get the required dependencies from a Conan package manager"

    def initialize_options(self):
        self.conan_cache = None

    def __init__(self, dist, **kw):
        super().__init__(dist, **kw)
        self.output_library_name = "exiv2"

    def finalize_options(self):
        if self.conan_cache is None:
            build_ext_cmd = self.get_finalized_command("build_ext")
            build_dir = build_ext_cmd.build_temp

            self.conan_cache = \
                os.path.join(
                    os.environ.get("CONAN_USER_HOME", build_dir),
                    ".conan"
                )

    @staticmethod
    def getConanBuildInfo(root_dir):
        for root, dirs, files in os.walk(root_dir):
            for f in files:
                if f == "conanbuildinfo.json":
                    return os.path.join(root, f)
        return None

    def _get_deps(self, build_dir=None, conan_cache=None):
        build_dir = build_dir or self.get_finalized_command("build_clib").build_temp
        from conans.client import conan_api, conf
        conan = conan_api.Conan(cache_folder=os.path.abspath(conan_cache))
        if sys.platform == "win32":
            conan_options = ['tesseract:shared=True']
        else:
            conan_options = []
        build = ['outdated']

        build_ext_cmd = self.get_finalized_command("build_ext")
        settings = []
        logger = logging.Logger(__name__)
        conan_profile_cache = os.path.join(build_dir, "profiles")
        for name, value in conf.detect.detect_defaults_settings(logger, conan_profile_cache):
            settings.append(f"{name}={value}")

        if build_ext_cmd.debug is not None:
            settings.append("build_type=Debug")
        else:
            settings.append("build_type=Release")
        #     FIXME: This should be the setup.py file dir
        conanfile_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )


        build_dir_full_path = os.path.abspath(build_dir)
        conan.install(
            options=conan_options,
            cwd=build_dir,
            settings=settings,
            build=build if len(build) > 0 else None,
            path=conanfile_path,
            install_folder=build_dir_full_path,
            # profile_build=profile
        )

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

        conanfile_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )

        conan.install(
            options=conan_options,
            cwd=build_dir,
            build=['missing'],
            path=conanfile_path,
            install_folder=build_dir_full_path
        )

        conanbuildinfotext = os.path.join(build_dir, "conanbuildinfo.txt")
        assert os.path.exists(conanbuildinfotext)
        text_md = ConanBuildInfoTXT().parse(conanbuildinfotext)
        for path in text_md['bin_paths']:
            if path not in build_ext_cmd.library_dirs:
                build_ext_cmd.library_dirs.insert(0, path)

        definition_macro = [(d, None) for d in text_md.get('definitions', [])]
        if build_ext_cmd.define is None:
            build_ext_cmd.define = definition_macro
        else:
            build_ext_cmd.define += definition_macro

        for extension in build_ext_cmd.extensions:
            update_extension4(extension, text_md)

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


def update_extension4(extension, text_md):
    definition_macro = [(d, None) for d in text_md.get('definitions', [])]
    if definition_macro not in extension.define_macros:
        extension.define_macros += definition_macro

    for path in text_md['lib_paths']:
        if path not in extension.library_dirs:
            extension.library_dirs.insert(0, path)


def update_extension3(extension, text_md):
    for path in text_md['lib_paths']:
        if path not in extension.library_dirs:
            extension.library_dirs.insert(0, path)

    for path in text_md['lib_paths']:
        if path not in extension.library_dirs:
            extension.library_dirs.insert(0, path)


class ConanBuildMetadata:
    def __init__(self, filename) -> None:
        super().__init__()
        self.filename = filename
        with open(self.filename) as f:
            self._data = json.loads(f.read())

    def deps(self):
        return [a['name'] for a in self._data['dependencies']]

    def dep(self, dep: str):
        deps = self._data['dependencies']
        return [d for d in deps if d['name'] == dep][0]
