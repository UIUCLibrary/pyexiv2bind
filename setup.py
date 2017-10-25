import os
from skbuild import setup
cmake_args = []
if "EXIV2_DIR" in os.environ:
    if os.path.exists(os.environ['EXIV2_DIR']):
        print("Detected that the environment variable EXIV2_DIR is set to {}.".format(os.environ['EXIV2_DIR']))
        cmake_args.append('-DEXIV2_DIR:PATH={}'.format(os.environ['EXIV2_DIR']))
setup(
    name="py3exiv2bind",
    version="0.0.3b1",
    # author="University of Illinois at Urbana Champaign",
    maintainer="Henry Borchers",
    maintainer_email="hborcher@illinois.edu",
    packages=['py3exiv2bind'],
    setup_requires=[
        "pytest-runner"
    ],
    cmake_args=cmake_args,
    test_suite="tests",
    tests_require=['pytest'],
    zip_safe=False,
    url="https://github.com/UIUCLibrary/pyexiv2bind",

)
