import os

from . import core
from . import icc
import collections

class Image(core.Image):
    def __init__(self, *args, **kwargs):
        if not os.path.exists(args[0]):
            raise FileNotFoundError("Unable to locate {}.".format(args[0]))
        super().__init__(*args, **kwargs)
        self.metadata = collections.ChainMap(self.exif, self.iptc, self.xmp)

    def icc(self):
        unpacked =icc.unpack_binary(self.get_icc_profile_data())

        return unpacked._asdict()