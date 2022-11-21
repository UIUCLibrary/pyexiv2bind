import logging
import os
import re
import subprocess
import sys
import shutil
import abc
from typing import Iterable, Any, Dict, List, Union, Optional
import setuptools
import platform
from distutils import ccompiler
from pathlib import Path
from builders.deps import get_win_deps
from builders.compiler_info import get_compiler_version, get_compiler_name
import json
from distutils.dist import Distribution


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
            names = []
            for value in data.keys():
                if not value.startswith("name_"):
                    continue
                names.append(value.replace("name_", ""))
            # print(names)
            libsmetadata = {}
            for library_name in names:
                version = data.get(f"version_{library_name}", None)
                libsmetadata[library_name] = {
                    "libs": data.get(f"libs_{library_name}", []),
                    "includedirs": data.get(f"includedirs_{library_name}", []),
                    "libdirs": data.get(f"libdirs_{library_name}", []),
                    "bindirs": data.get(f"bindirs_{library_name}", []),
                    "resdirs": data.get(f"resdirs_{library_name}", []),
                    "builddirs": data.get(f"builddirs_{library_name}", []),
                    "system_libs": data.get(f"system_libs_{library_name}", []),
                    "defines": data.get(f"defines_{library_name}", []),
                    "cppflags": data.get(f"cppflags_{library_name}", []),
                    "cxxflags": data.get(f"cxxflags_{library_name}", []),
                    "cflags": data.get(f"cflags_{library_name}", []),
                    "sharedlinkflags": data.get(f"sharedlinkflags_{library_name}", []),
                    "exelinkflags": data.get(f"exelinkflags_{library_name}", []),
                    "sysroot": data.get(f"sysroot_{library_name}", []),
                    "frameworks": data.get(f"frameworks_{library_name}", []),
                    "frameworkdirs": data.get(f"frameworkdirs_{library_name}", []),
                    "rootpath": data.get(f"rootpath_{library_name}", []),
                    "name": library_name,
                    "version": version[0] if version else None,
                    "generatornames": data.get(f"generatornames_{library_name}", []),
                    "generatorfilenames": data.get(f"generatorfilenames_{library_name}", []),
                }
        return {
            "definitions": definitions,
            "include_paths": list(include_paths),
            "lib_paths": list(lib_paths),
            "bin_paths": list(bin_paths),
            "libs": list(libs),
            "metadata": libsmetadata

        }


class AbsResultTester(abc.ABC):
    def __init__(self, compiler=None) -> None:
        self.compiler = compiler or ccompiler.new_compiler()

    def test_shared_libs(self, libs_dir):
        """Make sure all shared libraries in directory are linked"""
        for lib in os.scandir(libs_dir):
            if not lib.name.endswith(self.compiler.shared_lib_extension):
                continue
            self.test_binary_dependents(Path(lib.path))

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

        deps = get_win_deps(
            str(file_path.resolve()),
            output_file=f"{file_path.stem}.depends",
            compiler=self.compiler
        )

        system_path = os.getenv('PATH')
        for dep in deps:
            print(f"{file_path} requires {dep}")
            locations = list(filter(os.path.exists, system_path.split(";")))
            locations.append(str(file_path.parent.absolute()))
            for location in locations:
                dep_path = os.path.join(location, dep)
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
            if lib not in self._place_to_add.libraries and \
                    lib not in extension_deps:
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


def update_extension(extension, metadata):
    updated_libs = []
    include_dirs = []
    library_dirs = []
    define_macros = []
    for extension_lib in extension.libraries:
        if extension_lib in metadata.deps():
            dep_metadata = metadata.dep(extension_lib)
            updated_libs += dep_metadata.get('libs', [])
            include_dirs += dep_metadata.get('include_paths', [])
            library_dirs += dep_metadata.get('lib_paths', [])
            define_macros += [
                (d, None) for d in dep_metadata.get('definitions', [])
            ]
        else:
            updated_libs.append(extension_lib)
    extension.libraries = updated_libs
    extension.include_dirs = include_dirs + extension.include_dirs
    extension.library_dirs = library_dirs + extension.library_dirs
    extension.define_macros = define_macros + extension.define_macros


def update_extension2(extension, text_md):
    include_dirs = text_md['include_paths']
    library_dirs = text_md['lib_paths']
    define_macros = [(d, None) for d in text_md.get('definitions', [])]
    libs = extension.libraries.copy()

    for original_lib_name in extension.libraries:
        metadata = text_md['metadata']
        if original_lib_name not in metadata:
            continue
        conan_libs = metadata[original_lib_name]["libs"]
        index = libs.index(original_lib_name)
        libs[index:index+1] = conan_libs

    extension.libraries = libs
    for lib in text_md['libs']:
        if lib not in extension.libraries:
            extension.libraries.append(lib)

    extension.include_dirs = include_dirs + extension.include_dirs
    extension.library_dirs = library_dirs + extension.library_dirs
    extension.define_macros = define_macros + extension.define_macros


def get_conan_options():
    pyproject_toml_data = get_pyproject_toml_data()
    if 'localbuilder' not in pyproject_toml_data:
        return []

    local_builder_settings = pyproject_toml_data['localbuilder']
    platform_settings = local_builder_settings.get(sys.platform)
    if platform_settings is None:
        return []
    return platform_settings.get('conan_options', [])


class BuildConan(setuptools.Command):
    user_options = [
        ('conan-cache=', None, 'conan cache directory'),
        ('compiler-version=', None, 'Compiler version'),
        ('compiler-libcxx=', None, 'Compiler libcxx')
    ]

    description = "Get the required dependencies from a Conan package manager"

    def initialize_options(self):
        self.conan_cache = None
        self.compiler_version = None
        self.compiler_libcxx = None

    def __init__(self, dist, **kw):
        self.install_libs = True
        self.build_libs = ['outdated']
        super().__init__(dist, **kw)

    def finalize_options(self):
        if self.conan_cache is None:
            build_ext_cmd = self.get_finalized_command("build_ext")
            build_dir = build_ext_cmd.build_temp

            self.conan_cache = \
                os.path.join(
                    os.environ.get("CONAN_USER_HOME", build_dir),
                    ".conan"
                )
        if self.compiler_libcxx is None:
            self.compiler_libcxx = os.getenv("CONAN_COMPILER_LIBCXX")
        if self.compiler_version is None:
            self.compiler_version = \
                os.getenv("CONAN_COMPILER_VERSION", get_compiler_version())

    def getConanBuildInfo(self, root_dir):
        for root, dirs, files in os.walk(root_dir):
            for f in files:
                if f == "conanbuildinfo.json":
                    return os.path.join(root, f)
        return None

    def add_deps_to_compiler(self, metadata) -> None:
        build_ext_cmd = self.get_finalized_command("build_ext")
        compiler_adder = CompilerInfoAdder(build_ext_cmd)

        include_dirs = metadata['include_paths']
        compiler_adder.add_include_dirs(include_dirs)
        self.announce(
            f"Added the following paths to include "
            f"path {', '.join(include_dirs)} ",
            5
        )

        lib_paths = metadata['lib_paths']

        compiler_adder.add_lib_dirs(lib_paths)
        self.announce(
            f"Added the following paths to library "
            f"path {', '.join(metadata['lib_paths'])} ",
            5
        )

        for extension in build_ext_cmd.extensions:
            for lib in metadata['libs']:
                if lib not in extension.libraries:
                    extension.libraries.append(lib)

    def run(self):

        build_clib = self.get_finalized_command("build_clib")
        build_ext = self.get_finalized_command("build_ext")
        if self.install_libs:
            if build_ext._inplace:
                install_dir = os.path.abspath(build_ext.build_temp)
            else:
                build_py = self.get_finalized_command("build_py")
                install_dir = os.path.abspath(
                    os.path.join(
                        build_py.build_lib,
                        build_py.get_package_dir(build_py.packages[0]))
                )
        else:
            install_dir = build_ext.build_temp
        build_dir = os.path.join(build_clib.build_temp, "conan")
        build_dir_full_path = os.path.abspath(build_dir)
        conan_cache = self.conan_cache
        if not os.path.exists(conan_cache):
            self.mkpath(conan_cache)
            self.announce(f"Created {conan_cache} for conan cache", 5)
        if not os.path.exists(build_dir_full_path):
            self.mkpath(build_dir_full_path)
        self.announce(f"Using {conan_cache} for conan cache", 5)
        build_deps_with_conan(
            build_dir,
            install_dir=os.path.abspath(install_dir),
            compiler_libcxx=self.compiler_libcxx,
            compiler_version=self.compiler_version,
            conan_options=get_conan_options(),
            conan_cache=conan_cache,
            install_libs=self.install_libs
        )
        conaninfotext = os.path.join(build_dir, "conaninfo.txt")
        if os.path.exists(conaninfotext):
            with open(conaninfotext) as r:
                self.announce(r.read(), 5)
        build_locations = [
            build_dir,
            os.path.join(build_dir, "Release")
        ]
        conanbuildinfotext = locate_conanbuildinfo(build_locations)
        if conanbuildinfotext is None:
            raise AssertionError("Missing conanbuildinfo.txt")
        metadata_strategy = ConanBuildInfoTXT()
        text_md = metadata_strategy.parse(conanbuildinfotext)
        build_ext_cmd = self.get_finalized_command("build_ext")
        for extension in build_ext_cmd.extensions:
            if build_ext._inplace:
                extension.runtime_library_dirs.append(
                    os.path.abspath(install_dir)
                )
            update_extension2(extension, text_md)
            extension.library_dirs.insert(0, install_dir)
            if sys.platform == "darwin":
                extension.runtime_library_dirs.append("@loader_path")
            elif sys.platform == "linux":
                if "$ORIGIN" not in extension.runtime_library_dirs:
                    extension.runtime_library_dirs.append("$ORIGIN")
            # else:
            #     pprint(text_md)
            #     raise Exception(text_md)
            # if sys.platform == "Windows":


def build_conan(
        wheel_directory,
        config_settings=None,
        metadata_directory=None,
        install_libs=True
):
    dist = Distribution()
    dist.parse_config_files()
    command = BuildConan(dist)
    command.install_libs = install_libs
    build_ext_cmd = command.get_finalized_command("build_ext")
    if config_settings:
        command.conan_cache = config_settings.get(
            'conan_cache',
            os.path.join(build_ext_cmd.build_temp, ".conan")
        )
        command.compiler_libcxx = config_settings.get('conan_compiler_libcxx')
        command.compiler_version = config_settings.get(
            'conan_compiler_version',
            get_compiler_version()
        )
    else:
        command.conan_cache = \
            os.path.join(build_ext_cmd.build_temp, ".conan")

    command.finalize_options()
    command.run()


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


def get_pyproject_toml_data():
    import toml
    pyproj_toml = Path('pyproject.toml')
    with open(pyproj_toml) as f:
        return toml.load(f)


def build_deps_with_conan(
        build_dir: str,
        install_dir: str,
        compiler_libcxx: str,
        compiler_version: str,
        conan_cache: Optional[str] = None,
        conan_options: Optional[List[str]] = None,
        debug: bool = False,
        install_libs=True,
        build=None
):
    from conans.client import conan_api, conf
    conan = conan_api.Conan(cache_folder=os.path.abspath(conan_cache))
    settings = []
    logger = logging.Logger(__name__)
    conan_profile_cache = os.path.join(build_dir, "profiles")
    build = build or ['outdated']
    for name, value in conf.detect.detect_defaults_settings(
            logger,
            conan_profile_cache
    ):
        settings.append(f"{name}={value}")
    if debug is True:
        settings.append("build_type=Debug")
    else:
        settings.append("build_type=Release")
    try:
        compiler_name = get_compiler_name()
        settings.append(f"compiler={compiler_name}")
        if compiler_libcxx is not None:
            if 'compiler.libcxx=libstdc' in settings:
                settings.remove('compiler.libcxx=libstdc')
            settings.append(f'compiler.libcxx={compiler_libcxx}')
        settings.append(f"compiler.version={compiler_version}")
        if compiler_name == 'gcc':
            pass
        elif compiler_name == "msvc":
            settings.append("compiler.cppstd=14")
            settings.append("compiler.runtime=dynamic")
        elif compiler_name == "Visual Studio":
            settings.append("compiler.runtime=MD")
            settings.append("compiler.toolset=v142")
    except AttributeError:
        print(
            f"Unable to get compiler information "
            f"for {platform.python_compiler()}"
        )
        raise

    conanfile_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )

    ninja = shutil.which("ninja")
    env = []
    if ninja:
        env.append(f"NINJA={ninja}")
    conan.install(
        options=conan_options,
        cwd=os.path.abspath(build_dir),
        settings=settings,
        build=build if len(build) > 0 else None,
        path=conanfile_path,
        env=env,
        no_imports=not install_libs,
    )
    if install_libs:
        import_manifest = os.path.join(
            build_dir,
            'conan_imports_manifest.txt'
        )
        if os.path.exists(import_manifest):
            add_conan_imports(
                import_manifest,
                path=build_dir,
                dest=install_dir
            )


def fixup_library(shared_library):
    if sys.platform == "darwin":
        otool = shutil.which("otool")
        install_name_tool = shutil.which('install_name_tool')
        if not all([otool, install_name_tool]):
            raise FileNotFoundError(
                "Unable to fixed up because required tools are missing. "
                "Make sure that otool and install_name_tool are on "
                "the PATH."
            )
        dylib_regex = re.compile(
            r'^(?P<path>([@a-zA-Z./_])+)'
            r'/'
            r'(?P<file>lib[a-zA-Z/.0-9]+\.dylib)'
        )
        for line in subprocess.check_output(
                [otool, "-L", shared_library],
                encoding="utf8"
        ).split("\n"):
            if any(
                [
                    line.strip() == "",  # it's an empty line
                    str(shared_library) in line,  # it's the same library
                    "/usr/lib/" in line,  # it's a system library

                ]
            ):
                continue
            value = dylib_regex.match(line.strip())
            try:
                original_path = value.group("path")
                library_name = value.group("file").strip()
            except AttributeError as e:
                raise ValueError(f"unable to parse {line}") from e
            command = [
                install_name_tool,
                "-change",
                os.path.join(original_path, library_name),
                os.path.join("@loader_path", library_name),
                str(shared_library)
            ]
            subprocess.check_call(command)


def add_conan_imports(import_manifest_file: str, path: str, dest: str):
    libs = []
    with open(import_manifest_file, "r", encoding="utf8") as f:
        for line in f.readlines():
            if ":" not in line:
                continue

            try:
                file_name, hash_value = line.strip().split(": ")
            except ValueError:
                print(f"Failed to parse: {line.strip()}")
                raise
            libs.append(file_name)
    for file_name in libs:
        file_path = Path(os.path.join(path, file_name))
        if not file_path.exists():
            raise FileNotFoundError(f"Missing {file_name}")
        lib = str(file_path)
        fixup_library(lib)
        output = Path(os.path.join(dest, file_path.name))
        if output.exists():
            output.unlink()
        shutil.copy(file_path, dest, follow_symlinks=False)
        if file_path.is_symlink():
            continue


def locate_conanbuildinfo(search_locations):
    for location in search_locations:
        conanbuildinfo = os.path.join(location, "conanbuildinfo.txt")
        if os.path.exists(conanbuildinfo):
            return conanbuildinfo


def locate_conanbuildinfo_json(search_locations):
    for location in search_locations:
        conanbuildinfo = os.path.join(location, "conanbuildinfo.json")
        if os.path.exists(conanbuildinfo):
            return conanbuildinfo
