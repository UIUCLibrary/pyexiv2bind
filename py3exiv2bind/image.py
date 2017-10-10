from . import core


class Image:
    def __init__(self, filename):
        self.filename = filename

    @property
    def exif(self):
        return core.get_exif_metadata(self.filename)

    @property
    def pixelHeight(self):
        return core.get_pixelHeight(self.filename)

    @property
    def pixelWidth(self):
        return core.get_pixelWidth(self.filename)
