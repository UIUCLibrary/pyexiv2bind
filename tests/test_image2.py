import os

from py3exiv2bind import Image2


def test_image2_filename():
    sample_file = os.path.join(os.path.dirname(__file__), "sample_images/dummy.jp2")
    my_image = Image2(sample_file)
    assert my_image.filename == sample_file


def test_image2_pixelHeight():
    sample_file = os.path.join(os.path.dirname(__file__), "sample_images/dummy.jp2")
    my_image = Image2(sample_file)
    assert isinstance(my_image.pixelHeight, int)
    assert my_image.pixelHeight == 785


def test_image2_pixelWidth():
    sample_file = os.path.join(os.path.dirname(__file__), "sample_images/dummy.jp2")
    my_image = Image2(sample_file)
    assert isinstance(my_image.pixelWidth, int)
    assert my_image.pixelWidth == 4000

def test_image2_exif():

    sample_file = os.path.join(os.path.dirname(__file__), "sample_images/dummy.jp2")
    my_image = Image2(sample_file)
    exivf_metadata = my_image.exif
    assert isinstance(exivf_metadata, dict)
    print(exivf_metadata)
    assert exivf_metadata['Exif.Image.Artist'] == "University of Illinois Library"
