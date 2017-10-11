from . import core

def get_exif(filename):
    return core.get_exif_metadata(filename)