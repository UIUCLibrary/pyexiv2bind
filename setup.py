from skbuild import setup

setup(
    name="py3exiv2bind",
    version="0.0.1",
    packages=['py3exiv2bind'],
    # package_data={'py3exiv2bind': ['*.pyd', '*.so']},
    setup_requires=[
        "pytest-runner"
    ],
    test_suite="tests",
    tests_require=['pytest'],
    zip_safe=False,
    url="https://github.com/UIUCLibrary/pyexiv2bind",

)
