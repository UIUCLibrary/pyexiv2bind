from . import core
import collections

class Image(core.Image):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metadata = collections.ChainMap(self.exif, self.iptc, self.xmp)
