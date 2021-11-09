"""Manage image files."""
import os

import collections
import typing
import warnings

from . import core
from . import icc


class Image(core.Image):
    """Evaluate an image file."""

    _INVALID_FORMATS_FOR_ICC: typing.List[str] = []

    def __init__(self, *args, **kwargs):
        """Load the file to get information about it."""
        if not os.path.exists(args[0]):
            raise FileNotFoundError(f"Unable to locate {args[0]}.")
        super().__init__(*args, **kwargs)
        for warning in self.warnings_logs:  # pylint: disable=not-an-iterable
            warnings.warn(warning.strip(), Warning)

    @property
    def metadata(self) -> dict:
        """Extract embedded metadata stored in exif, iptc, and xmp."""
        return dict(collections.ChainMap(self.exif, self.iptc, self.xmp))

    def icc(self) -> typing.Dict[str, typing.Any]:
        """Extract the ICC profile.

        Returns:
            Dictionary of ICC metadata

        """
        extension = os.path.splitext(self.filename)[1].lower()
        if extension in Image._INVALID_FORMATS_FOR_ICC:
            raise AttributeError(
                "{} files not currently supported for ICC data".format(
                    extension)
            )
        unpacked = icc.unpack_binary(self.get_icc_profile_data())

        return unpacked._asdict()
