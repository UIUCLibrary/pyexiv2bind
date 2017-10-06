# print("Running {}".format(__file__))
import py3exiv2bind
# exiv2_version = py3exiv2bind.exiv2_version()
# print("Bound to exiv2, version {}".format(exiv2_version))
# print("{} run succesfully".format(__file__))
print("HEre")
def test_exiv_version():
    exiv2_version = py3exiv2bind.exiv2_version()
    assert isinstance(exiv2_version, str)