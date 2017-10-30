import os
from skbuild import setup


def get_metadata():
    about = {}

    metadata_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'py3exiv2bind', '__version__.py')

    with open(metadata_file, 'r', encoding='utf-8') as f:
        exec(f.read(), about)

    return about


metadata = get_metadata()

with open('README.rst', 'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()

cmake_args = []
if "EXIV2_DIR" in os.environ:
    if os.path.exists(os.environ['EXIV2_DIR']):
        print("Detected that the environment variable EXIV2_DIR is set to {}.".format(os.environ['EXIV2_DIR']))
        cmake_args.append('-DEXIV2_DIR:PATH={}'.format(os.environ['EXIV2_DIR']))
setup(
    name=metadata["__title__"],
    version=metadata["__version__"],
    # author="University of Illinois at Urbana Champaign",
    maintainer=metadata["__maintainer__"],
    maintainer_email=metadata["__maintainer_email__"],
    packages=['py3exiv2bind'],
    setup_requires=[
        "pytest-runner"
    ],
    cmake_args=cmake_args,
    test_suite="tests",
    tests_require=['pytest'],
    zip_safe=False,
    url=metadata["__url__"],
    description=metadata["__description__"],
    long_description=readme,

)
