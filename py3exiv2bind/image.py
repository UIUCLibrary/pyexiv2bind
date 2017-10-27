import os

from . import core
import collections

class Image(core.Image):
    def __init__(self, *args, **kwargs):
        if not os.path.exists(args[0]):
            raise FileNotFoundError("Unable to locate {}.".format(args[0]))
        super().__init__(*args, **kwargs)
        self.metadata = collections.ChainMap(self.exif, self.iptc, self.xmp)
