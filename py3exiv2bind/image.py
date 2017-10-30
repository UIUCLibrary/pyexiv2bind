import os

from . import core
from . import icc
import collections


class Image(core.Image):
    INVALID_FORMATS_FOR_ICC = [".jp2"]

    def __init__(self, *args, **kwargs):
        """
        Loads the file to get information about it.
        Args:
            *args:
            **kwargs:
        """
        if not os.path.exists(args[0]):
            raise FileNotFoundError("Unable to locate {}.".format(args[0]))
        super().__init__(*args, **kwargs)
        self.metadata = collections.ChainMap(self.exif, self.iptc, self.xmp)

    def icc(self):
        extension = os.path.splitext(self.filename)[1].lower()
        if extension in Image.INVALID_FORMATS_FOR_ICC:
            raise AttributeError("{} files not currently supported for ICC data".format(extension))
        unpacked = icc.unpack_binary(self.get_icc_profile_data())

        return unpacked._asdict()
