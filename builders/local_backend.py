import setuptools.build_meta


def build_sdist(sdist_directory, config_settings=None):
    return setuptools.build_meta.build_sdist(sdist_directory, config_settings)


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    return setuptools.build_meta.build_wheel(wheel_directory, config_settings, metadata_directory)


def get_requires_for_build_sdist(config_settings=None):
    return []


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    return setuptools.build_meta.prepare_metadata_for_build_wheel(metadata_directory, config_settings)


def get_requires_for_build_wheel(config_settings=None):
    return ['pybind11>=2.5']
