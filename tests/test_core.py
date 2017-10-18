# print("Running {}".format(__file__))
import os
from py3exiv2bind import core

def test_exiv_version():
    exiv2_version = core.exiv2_version()
    assert isinstance(exiv2_version, str)
