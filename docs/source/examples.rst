Examples
========

Getting simple embedded metadata is easy to do. Just load a file in an Image object and request the metadata by name with the :attr:`Image.metadata` attribute.

.. code-block:: python

    from py3exiv2bind import Image

    # Load the image file into an Image object.
    my_image = Image("dummy.jp2")

    # This will print the number of pixels wide the image is.
    print(my_image.pixelWidth)

    # This will print the artist information stored in the embedded
    # exif metadata.
    print(my_image.metadata['Exif.Image.Artist']

To get ICC based metadata, you need to call the :meth:`Image.icc` method

.. code-block:: python

    from py3exiv2bind import Image

    # Load the image file into an Image object.
    my_image = Image("dummy.tif")

    icc_data = my_image.icc())

    # This will print out the color space of the icc profile
    print(icc("color_space"))

This method will try to provide the most human friendly data for this value.

For example, if the metadata for the
"device_class" is requested, the friendly name is known and the default string value will be close to english, such as
the value "Display device profile".

However, if a value has an unknown friendly name, the string representation will by the decoded value. If that's not
available, at least the raw data will be used.

Do explicitly use one of these representations use the dot notation followed by "friendly_name", "value", or "raw_data".