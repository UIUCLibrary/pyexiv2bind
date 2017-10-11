import py3exiv2bind
import os


def test_get_exif():
    sample_file = "tests/sample_images/dummy.jp2"
    assert os.path.exists(sample_file)
    print("Found test file")
    metadata = py3exiv2bind.get_exif(filename=sample_file)
    assert isinstance(metadata, dict)
