import os
from skbuild import setup


cmake_args = ["-Dpyexiv2bind_experimental_jp2_support=ON"]
if "EXIV2_DIR" in os.environ:
    if os.path.exists(os.environ['EXIV2_DIR']):
        print("Detected that the environment variable EXIV2_DIR is set to {}.".format(os.environ['EXIV2_DIR']))
        cmake_args.append('-DEXIV2_DIR:PATH={}'.format(os.environ['EXIV2_DIR']))
setup(
    setup_requires=[
        "pytest-runner"
    ],
    cmake_args=cmake_args,
    test_suite="tests",
    tests_require=['pytest'],

)
