import os
import pytest
from py3exiv2bind import Image, core



def test_icc_file(sample_images):
    sample_file = os.path.join(sample_images, "dummy.tif")
    my_image = Image(sample_file)
    icc = my_image.icc()
    assert str(icc["color_space"]) == "RGB"
    assert str(icc["device_model"]) == "sRGB"


def test_icc_on_jp2_file(sample_images):
    sample_file = os.path.join(sample_images, "dummy.jp2")
    my_image = Image(sample_file)
    with pytest.raises(core.NoICCError):
        icc = my_image.icc()
        print(icc)