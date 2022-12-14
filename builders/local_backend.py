import os

import setuptools.build_meta
from . import conan_libs
from pathlib import Path
from setuptools import Distribution

pyproj_toml = Path('pyproject.toml')


def build_sdist(sdist_directory, config_settings=None):
    return setuptools.build_meta.build_sdist(sdist_directory, config_settings)


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    if config_settings is not None and config_settings.get('conan_cache') is not None:
        if "CONAN_USER_HOME" in os.environ:
            config_settings['conan_cache'] = os.path.join(os.environ["CONAN_USER_HOME"], ".conan")

    conan_libs.build_conan(
        wheel_directory,
        config_settings,
        metadata_directory,
        install_libs=False
    )
    original_conan_user_home = os.getenv("CONAN_USER_HOME")

    try:
        if config_settings is not None and "conan_cache" in config_settings:
            os.environ["CONAN_USER_HOME"] = os.path.normpath(os.path.join(config_settings['conan_cache'], ".."))
        return setuptools.build_meta.build_wheel(wheel_directory, config_settings, metadata_directory)
    finally:
        if original_conan_user_home:
            os.environ["CONAN_USER_HOME"] = original_conan_user_home
        else:
            os.unsetenv("CONAN_USER_HOME")


def get_requires_for_build_sdist(config_settings=None):
    return []


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    return setuptools.build_meta.prepare_metadata_for_build_wheel(metadata_directory, config_settings)


def get_requires_for_build_wheel(config_settings=None):
    return ["wheel >= 0.25", "setuptools", 'pybind11>=2.5', 'toml']
