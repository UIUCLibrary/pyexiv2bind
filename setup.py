import os
import sys
try:
    from skbuild import setup
except ImportError:
    print("scikit-build required to install")
    raise

needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []


cmake_args = []
cmake_args.append("-DBUILD_SHARED_LIBS:BOOL=NO")
cmake_args.append('-DEXIV2_VERSION_TAG:STRING=0d6abb5b5130fbce8bdc398b6728d225838bb382')

# cmake_args = ["-Dpyexiv2bind_experimental_jp2_support=ON"]

if "EXIV2_DIR" in os.environ:
    if os.path.exists(os.environ['EXIV2_DIR']):
        print("Detected that the environment variable EXIV2_DIR is set to {}.".format(os.environ['EXIV2_DIR']))
        cmake_args.append('-DEXIV2_DIR:PATH={}'.format(os.environ['EXIV2_DIR']))

setup(
    packages=['py3exiv2bind'],
    python_requires=">=3.6",
    setup_requires=pytest_runner,
    cmake_args=cmake_args,
    test_suite="tests",
    tests_require=['pytest'],

)
