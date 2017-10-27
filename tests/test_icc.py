import os
from pprint import pprint

from py3exiv2bind import Image

def test_icc_file():
    sample_file = os.path.join(os.path.dirname(__file__), "sample_images/dummy.tif")
    my_image = Image(sample_file)
    icc = my_image.icc()
    pprint(icc)