# print("Running {}".format(__file__))
import os
from py3exiv2bind import core


def test_exiv_version():
    exiv2_version = core.exiv2_version()
    assert isinstance(exiv2_version, str)


def test_set_dpi_on_jp2(sample_images):
    test_jp2 = os.path.join(sample_images, "dummy.jp2")
    sample_image = core.Image(test_jp2)
    assert sample_image.exif['Exif.Image.XResolution'] == "400/1"
    assert sample_image.exif['Exif.Image.YResolution'] == "400/1"
    assert sample_image.exif['Exif.Image.ResolutionUnit'] == "2"

    # core.set_dpi(test_jp2, 300, 300)
    core.set_dpi(image=str(test_jp2), x=300, y=300)
    sample_image2 = core.Image(test_jp2)
    assert sample_image2.exif['Exif.Image.XResolution'] == "300/1"
    assert sample_image2.exif['Exif.Image.YResolution'] == "300/1"
    assert sample_image2.exif['Exif.Image.ResolutionUnit'] == "2"


def test_set_dpi_on_tiff(sample_images):
    test_jp2 = os.path.join(sample_images, "dummy.tif")
    sample_image = core.Image(test_jp2)
    assert sample_image.exif['Exif.Image.XResolution'] != "400/1"
    assert sample_image.exif['Exif.Image.YResolution'] != "400/1"
    assert sample_image.exif['Exif.Image.ResolutionUnit'] == "2"

    # core.set_dpi(test_jp2, 300, 300)
    core.set_dpi(image=str(test_jp2), x=300, y=300)
    sample_image2 = core.Image(test_jp2)
    assert sample_image2.exif['Exif.Image.XResolution'] == "300/1"
    assert sample_image2.exif['Exif.Image.YResolution'] == "300/1"
    assert sample_image2.exif['Exif.Image.ResolutionUnit'] == "2"
