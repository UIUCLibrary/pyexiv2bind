import re
from typing import List

DEPS_REGEX = \
    r'(?<=(Image has the following dependencies:(\n){2}))((?<=\s).*\.dll\n)*'


def parse_dumpbin_deps(file) -> List[str]:

    dlls = []
    dep_regex = re.compile(DEPS_REGEX)

    with open(file) as f:
        d = dep_regex.search(f.read())
        for x in d.group(0).split("\n"):
            if x.strip() == "":
                continue
            dll = x.strip()
            dlls.append(dll)
    return dlls


def remove_system_dlls(dlls):
    non_system_dlls = []
    for dll in dlls:
        if dll.startswith("api-ms-win-crt"):
            continue

        if dll.startswith("python"):
            continue

        if dll == "KERNEL32.dll":
            continue
        non_system_dlls.append(dll)
    return non_system_dlls


def get_win_deps(dll_name, output_file, compiler):
    compiler.spawn(
        [
            'dumpbin',
            '/dependents',
            dll_name,
            f'/out:{output_file}'
        ]
    )
    deps = parse_dumpbin_deps(file=output_file)
    deps = remove_system_dlls(deps)
    return deps
