"""For extracting the ICC data."""
from collections import namedtuple
import struct
import copy
from typing import Optional, Union, Tuple, Any


class ICC_data:
    """ICC data container."""

    def __init__(self) -> None:
        """Create a ICC data container."""
        self.friendly_name = None
        self.value: Optional[Any] = None
        self.raw_data: Optional[bytes] = None

    def __str__(self) -> str:
        """Provide a friendly name keys if possible."""
        if self.friendly_name:
            return self.friendly_name
        if self.value:
            return str(self.value, encoding="ascii")
        return str(self.raw_data)


def build_ICC_data(value: bytes, lookup_table: dict = None,
                   restrict=False) -> ICC_data:
    """Build an ICC_data object."""
    new_value = ICC_data()
    new_value.value = value
    if lookup_table:
        if value in lookup_table:
            new_value.friendly_name = lookup_table[value]
        else:
            if restrict:
                raise LookupError("Invalid signature: {}".format(str(value)))
    return new_value


def build_ICC_friendly_names(icc_data: ICC_data, lookup_table=None,
                             restrict=False) -> ICC_data:
    """Update the keys to display easier to read names."""
    new_icc = copy.deepcopy(icc_data)
    if lookup_table:
        if icc_data.value in lookup_table:
            new_icc.friendly_name = lookup_table[icc_data.value]
        else:
            if restrict:
                raise LookupError("Invalid signature: {}".format(
                    str(icc_data.value))
                )

    return new_icc


def build_ICC_empty_data(raw_data: bytes) -> ICC_data:
    """Create an empty ICC data set from raw data.

    Args:
        raw_data:

    Returns:
        New ICC data set

    """
    new_value = ICC_data()
    new_value.raw_data = raw_data
    return new_value


def add_decoded_value(icc_data: ICC_data, data: tuple):
    """Include decoded values."""
    new_data = copy.deepcopy(icc_data)
    new_data.value = data
    return new_data


ICC_Profile_Header = namedtuple("ICC_Profile_Header", (
    "size",
    "pref_ccm",
    "version_number",
    "device_class",
    "color_space",
    "PCS",
    "creation_date",
    "acsp",
    "primary_plaform_sig",
    "flags",
    "device_manufacture",
    "device_model",
    "device_attr",
    "rendering_intent",
    "nCIEXYZ",
    "creator_sig",
    "id",
    "reserved"
))

color_spaces = {
    b"XYZ ": "nCIEXYZ or PCSXYZa",
    b"Lab ": "CIELAB or PCSLABb",
    b"Luv ": "CIELUV",
    b"YCbr": "YCbCr",
    b"Yxy ": "CIEYxy",
    b"RGB ": "RGB",
    b"GRAY": "Gray",
    b"HSV ": "HSV",
    b"HLS ": "HLS",
    b"CMYK": "CMYK",
    b"CMY ": "CMY",
    b"2CLR": "2 colour",
    b"3CLR": "3 colour",
    b"4CLR": "4 colour (other than CMYK)",
    b"5CLR": "5 colour",
    b"6CLR": "6 colour",
    b"7CLR": "7 colour",
    b"8CLR": "8 colour",
    b"9CLR": "9 colour",
    b"ACLR": "10 colour",
    b"BCLR": "11 colour",
    b"CCLR": "12 colour",
    b"DCLR": "13 colour",
    b"ECLR": "14 colour",
    b"FCLR": "15 colour",
}

profile_classes = {
    b"scnr": "Input device profile",
    b"mntr": "Display device profile",
    b"prtr": "Output device profile",
    b"link": "DeviceLink profile",
    b"spac": "ColorSpace profile",
    b"abst": "Abstract profile",
    b"nmcl": "NamedColor profile",
}

primary_platforms = {
    b"APPL": "Apple Computer, Inc.",
    b"MSFT": "Microsoft Corporation",
    b"SGI ": "Silicon Graphics, Inc.",
    b"SUNW": "Sun Microsystems, Inc.",
}


def unpack_binary(data) -> ICC_Profile_Header:
    """Unpack binary data into a a ICC profile header."""
    return unpack_header(data[:128])


def _parse_header(raw_data: bytes) -> ICC_Profile_Header:
    return ICC_Profile_Header(
        size=build_ICC_empty_data(raw_data[:4]),
        pref_ccm=build_ICC_empty_data(raw_data[4:8]),
        version_number=build_ICC_empty_data(raw_data[8:12]),
        device_class=build_ICC_empty_data(raw_data[12:16]),
        color_space=build_ICC_empty_data(raw_data[16:20]),
        PCS=build_ICC_empty_data(raw_data[20:24]),
        creation_date=build_ICC_empty_data(raw_data[24:36]),
        acsp=build_ICC_empty_data(raw_data[36:40]),
        primary_plaform_sig=build_ICC_empty_data(raw_data[40:44]),
        flags=build_ICC_empty_data(raw_data[44:48]),
        device_manufacture=build_ICC_empty_data(raw_data[48:52]),
        device_model=build_ICC_empty_data(raw_data[52:56]),
        device_attr=build_ICC_empty_data(raw_data[56:64]),
        rendering_intent=build_ICC_empty_data(raw_data[64:68]),
        nCIEXYZ=build_ICC_empty_data(raw_data[68:80]),
        creator_sig=build_ICC_empty_data(raw_data[80:84]),
        id=build_ICC_empty_data(raw_data[84:100]),
        reserved=build_ICC_empty_data(raw_data[100:128])
    )


def _decode_header(parsed: ICC_Profile_Header) -> ICC_Profile_Header:
    return ICC_Profile_Header(
        size=add_decoded_value(
            parsed.size,
            struct.unpack("I", parsed.size.raw_data)[0]
        ),
        pref_ccm=add_decoded_value(
            parsed.pref_ccm,
            struct.unpack("4s", parsed.pref_ccm.raw_data)[0]
        ),
        # still needs to accurately parsed. The first value is correctly the
        # major version but afterwards It needs bit extraction
        version_number=add_decoded_value(
            parsed.version_number,
            struct.unpack("4b", parsed.version_number.raw_data)
        ),
        device_class=add_decoded_value(
            parsed.device_class,
            struct.unpack("4s", parsed.device_class.raw_data)[0]
        ),
        color_space=add_decoded_value(
            parsed.color_space,
            struct.unpack("4s", parsed.color_space.raw_data)[0]
        ),
        PCS=add_decoded_value(
            parsed.PCS,
            struct.unpack("4s", parsed.PCS.raw_data)[0]
        ),
        creation_date=add_decoded_value(
            parsed.creation_date,
            struct.unpack("iii", parsed.creation_date.raw_data)
        ),
        acsp=add_decoded_value(
            parsed.acsp,
            struct.unpack("4s", parsed.acsp.raw_data)[0]
        ),
        primary_plaform_sig=add_decoded_value(
            parsed.primary_plaform_sig,
            struct.unpack("4s", parsed.primary_plaform_sig.raw_data)[0]
        ),
        flags=add_decoded_value(
            parsed.flags,
            struct.unpack("4s", parsed.flags.raw_data)
        ),
        device_manufacture=add_decoded_value(
            parsed.device_manufacture,
            struct.unpack("4s", parsed.device_manufacture.raw_data)[0]
        ),
        device_model=add_decoded_value(
            parsed.device_model,
            struct.unpack("4s", parsed.device_model.raw_data)[0]
        ),
        device_attr=add_decoded_value(
            parsed.device_attr,
            struct.unpack("8s", parsed.device_attr.raw_data)
        ),
        rendering_intent=add_decoded_value(
            parsed.rendering_intent,
            struct.unpack("4s", parsed.rendering_intent.raw_data)
        ),
        nCIEXYZ=add_decoded_value(
            parsed.nCIEXYZ,
            struct.unpack("12b", parsed.nCIEXYZ.raw_data)
        ),
        creator_sig=add_decoded_value(
            parsed.creator_sig,
            struct.unpack("4s", parsed.creator_sig.raw_data)[0]
        ),
        id=add_decoded_value(
            parsed.id,
            struct.unpack("16b", parsed.id.raw_data)
        ),
        reserved=add_decoded_value(
            parsed.reserved,
            struct.unpack("28x", parsed.reserved.raw_data)
        )
    )


def _map_header_strings(parsed: ICC_Profile_Header):
    return ICC_Profile_Header(
        size=build_ICC_friendly_names(parsed.size),
        pref_ccm=build_ICC_friendly_names(parsed.pref_ccm),
        version_number=build_ICC_friendly_names(parsed.version_number),
        device_class=build_ICC_friendly_names(
            parsed.device_class, profile_classes, restrict=True),
        color_space=build_ICC_friendly_names(
            parsed.color_space, color_spaces, restrict=True),
        PCS=build_ICC_friendly_names(parsed.PCS),
        creation_date=build_ICC_friendly_names(parsed.creation_date),
        acsp=build_ICC_friendly_names(parsed.acsp),
        primary_plaform_sig=build_ICC_friendly_names(
            parsed.primary_plaform_sig, primary_platforms, restrict=False),
        flags=build_ICC_friendly_names(parsed.flags),
        device_manufacture=build_ICC_friendly_names(parsed.device_manufacture),
        device_model=build_ICC_friendly_names(parsed.device_model),
        device_attr=build_ICC_friendly_names(parsed.device_attr),
        rendering_intent=build_ICC_friendly_names(parsed.rendering_intent),
        nCIEXYZ=build_ICC_friendly_names(parsed.nCIEXYZ),
        creator_sig=build_ICC_friendly_names(parsed.creator_sig),
        id=build_ICC_friendly_names(parsed.id),
        reserved=build_ICC_friendly_names(parsed.reserved)
    )
    # if parsed.color_space


def unpack_header(raw_data: bytes) -> ICC_Profile_Header:
    """Unpack & decode binary information from header of ICC profile data.

    Args:
        raw_data: raw stream of bytes from the ICC Profile header to decode
          into a structure

    Notes: Use this http://www.color.org/specification/ICC1v43_2010-12.pdf
    for parsing the binary information


    """
    assert len(raw_data) == 128
    parsed = _parse_header(raw_data)
    decoded = _decode_header(parsed)
    return _map_header_strings(decoded)
