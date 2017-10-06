# print("Running {}".format(__file__))
import os
import py3exiv2bind

# exiv2_version = py3exiv2bind.exiv2_version()
# print("Bound to exiv2, version {}".format(exiv2_version))
# print("{} run succesfully".format(__file__))
print("HEre")


def test_exiv_version():
    exiv2_version = py3exiv2bind.exiv2_version()
    assert isinstance(exiv2_version, str)


def test_exif_metadata():
    sample_file = r"tests\sample_images\dummy.jp2"
    assert os.path.exists(sample_file)
    print("Found test file")
    print("Testing {}".format(sample_file))
    foo = py3exiv2bind.get_exif_metadata(sample_file)
