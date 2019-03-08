import os
import pytest
from py3exiv2bind import Image


def test_invalid_file(sample_images):
    bad_file = os.path.join(sample_images, "not_a_real_file.jp2")
    with pytest.raises(FileNotFoundError):
        my_image = Image(bad_file)


def test_image2_filename(sample_images):
    sample_file = os.path.join(sample_images, "dummy.jp2")
    my_image = Image(sample_file)
    assert my_image.filename == sample_file


def test_image2_pixelHeight(sample_images):
    sample_file = os.path.join(sample_images, "dummy.jp2")
    my_image = Image(sample_file)
    assert isinstance(my_image.pixelHeight, int)
    assert my_image.pixelHeight == 785


def test_image2_pixelWidth(sample_images):
    sample_file = os.path.join(sample_images, "dummy.jp2")
    my_image = Image(sample_file)
    assert isinstance(my_image.pixelWidth, int)
    assert my_image.pixelWidth == 4000


def test_image2_exif(sample_images):
    sample_file = os.path.join(sample_images, "dummy.jp2")
    my_image = Image(sample_file)
    exivf_metadata = my_image.exif
    assert isinstance(exivf_metadata, dict)
    assert exivf_metadata['Exif.Image.Artist'] == "University of Illinois Library"


def test_image2_iptc(sample_images):
    sample_file = os.path.join(sample_images, "dummy.jp2")
    my_image = Image(sample_file)
    iptc_metadata = my_image.iptc
    assert isinstance(iptc_metadata, dict)
    assert iptc_metadata['Iptc.Application2.ObjectName'] == "Mapping History - University Archives"


def test_image_get_icc_data(sample_images):
    sample_file = os.path.join(sample_images, "dummy.tif")
    my_image = Image(sample_file)
    icc_data = my_image.get_icc_profile_data()
    assert isinstance(icc_data, bytes)
