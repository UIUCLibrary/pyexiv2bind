import platform
import re
import sys
from builders.errors import PlatformError, ExecError
import subprocess
import os
__all__ = [
    'get_compiler_version',
    'get_compiler_name'
]


def get_compiler_name() -> str:
    groups = re.match(
        '^(GCC|Clang|MSVC|MSC)',
        platform.python_compiler()
    )
    try:
        if "Clang" in groups[1]:
            if platform.system() == "Darwin":
                return 'apple-clang'
        elif "GCC" in groups[1]:
            return 'gcc'
        elif groups[1] in ['MSVC', 'MSC']:
            return 'Visual Studio'
        else:
            return groups[1]
    except TypeError:
        print(
            f"python compiler = {platform.python_compiler()}",
            file=sys.stderr
        )
        raise


if sys.platform == 'darwin':
    _cfg_target = None
    _cfg_target_split = None


def get_visual_studio_version():
    import winreg
    possible_versions = [
        "8.0", "9.0", "10.0", "11.0", "12.0", "14.0", "15.0", "16.0"
    ]
    installed_versions = []
    key = "SOFTWARE\Microsoft\VisualStudio\%s"

    for v in possible_versions:
        try:
            winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key % v, 0,
                            winreg.KEY_ALL_ACCESS)
            installed_versions.append(v)
        except Exception as e:
            pass
    sorted_values = sorted(installed_versions, key=lambda value: float(value))
    print(sorted_values)
    return sorted_values[-1].split(".")[0]


def get_clang_version():
    cmd = ['cc', '--version']

    env = None
    if sys.platform == 'darwin':
        global _cfg_target, _cfg_target_split
        if _cfg_target is None:
            from distutils import sysconfig
            _cfg_target = sysconfig.get_config_var(
                'MACOSX_DEPLOYMENT_TARGET') or ''
            if _cfg_target:
                _cfg_target_split = [int(x) for x in _cfg_target.split('.')]
        if _cfg_target:
            # Ensure that the deployment target of the build process is not
            # less than 10.3 if the interpreter was built for 10.3 or later.
            # This ensures extension modules are built with correct
            # compatibility values, specifically LDSHARED which can use
            # '-undefined dynamic_lookup' which only works on >= 10.3.
            cur_target = os.environ.get('MACOSX_DEPLOYMENT_TARGET', _cfg_target)
            cur_target_split = [int(x) for x in cur_target.split('.')]
            if _cfg_target_split[:2] >= [10, 3] and cur_target_split[:2] < [10,
                                                                            3]:
                my_msg = ('$MACOSX_DEPLOYMENT_TARGET mismatch: '
                          'now "%s" but "%s" during configure;'
                          'must use 10.3 or later'
                          % (cur_target, _cfg_target))
                raise PlatformError(my_msg)
            env = dict(os.environ,
                       MACOSX_DEPLOYMENT_TARGET=cur_target)

    try:
        proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE)
        proc.wait()
        exitcode = proc.returncode
        clang_version_regex = re.compile(
            r'(?<=Apple clang version )((\d+[.]){1,2}\d+)')
        compiler_response = proc.stdout.read().decode('utf-8')
        try:
            env_version = clang_version_regex.search(
                compiler_response
            )[0]
        except TypeError as result_error:
            print(compiler_response, file=sys.stderr)
            raise TypeError(
                "Unable to parse compiler version response"
            ) from result_error

        parts = env_version.split('.')
        if exitcode:
            raise ExecError(f"command {cmd} failed with exit code {exitcode}")

        return f"{parts[0]}.{parts[1]}"
    except OSError as exc:
        raise ExecError("command %r failed: %s" % (cmd, exc.args[-1])) from exc


def get_gcc_version():
    cmd = ['cc', '-dumpfullversion', '-dumpversion']
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        proc.wait()
        exitcode = proc.returncode
        compiler_response = proc.stdout.read().decode('utf-8')
        if exitcode:
            raise ExecError(f"command {cmd} failed with exit code {exitcode}")
        compiler_version = compiler_response.strip()
        version_comps = compiler_version.split(".")

        if len(version_comps) == 1:
            return version_comps[0]
        return f"{version_comps[0]}.{version_comps[1]}"
    except OSError as exc:
        raise ExecError("command %r failed: %s" % (cmd, exc.args[-1])) from exc


def get_compiler_version():
    """
    Examples of compiler data:
        GCC 10.2.1 20210110
        GCC 9.4.0
        MSC v.1916 64 bit (AMD64)
        Clang 13.1.6 (clang-1316.0.21.2)
    """
    full_version = re.search(
        r"^(?:[A-Za-z]+ )(?:v[.])?(([0-9]+[.]?)+)",
        platform.python_compiler()
    ).groups()[0]
    compiler_name = get_compiler_name()
    if compiler_name == "msvc":
        # MSVC compiler uses versions like 1916 but conan wants it as 191
        return full_version[:3]
    elif compiler_name == "Visual Studio":
        return get_visual_studio_version()
    elif compiler_name == "apple-clang":
        return get_clang_version()
    elif compiler_name == "gcc":
        return get_gcc_version()

    parsed_version = re.findall("([0-9]+)(?:[.]?)", full_version)
    if len(parsed_version) <= 2:
        return full_version
    return f"{parsed_version[0]}.{parsed_version[1]}"

