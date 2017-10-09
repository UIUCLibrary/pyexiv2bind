from py3exiv2bind import image

def test_pixelHeight():
    sample_file = "tests/sample_images/dummy.jp2"
    my_image = image.Image(sample_file)
    assert isinstance(my_image.pixelHeight, int)
    assert my_image.pixelHeight == 785


def test_pixelWidth():
    sample_file = "tests/sample_images/dummy.jp2"
    my_image = image.Image(sample_file)
    assert isinstance(my_image.pixelWidth, int)
    assert my_image.pixelWidth == 4000