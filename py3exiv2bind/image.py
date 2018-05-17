import os

from . import core # type: ignore
from . import icc
import collections
import typing

class Image(core.Image):
    _INVALID_FORMATS_FOR_ICC: typing.List[str] = []

    def __init__(self, *args, **kwargs):
        """Loads the file to get information about it."""
        if not os.path.exists(args[0]):
            raise FileNotFoundError("Unable to locate {}.".format(args[0]))
        super().__init__(*args, **kwargs)

    @property
    def metadata(self) -> dict:
        """Extracts embedded metadata stored in exif, iptc, and xmp."""
        return dict(collections.ChainMap(self.exif, self.iptc, self.xmp))

    def icc(self):
        """
        Extract the ICC profile

        Returns:

        """
        extension = os.path.splitext(self.filename)[1].lower()
        if extension in Image._INVALID_FORMATS_FOR_ICC:
            raise AttributeError("{} files not currently supported for ICC data".format(extension))
        unpacked = icc.unpack_binary(self.get_icc_profile_data())

        return unpacked._asdict()
