//
// Created by hborcher on 10/11/2017.
//

#include <string>
#include <cassert>
#include "Image2.h"
#include "glue.h"
#include "MetadataProcessor.h"


Image2::Image2(const std::string &filename) : filename(filename) {
    image = Exiv2::ImageFactory::open(filename);
    assert(image.get() != 0); // Make sure it's able to read the file
    image->readMetadata();
}

const std::string &Image2::getFilename() const {
    return filename;
}

int Image2::get_pixelHeight() const {
    return image->pixelHeight();
}

int Image2::get_pixelWidth() const {
    return image->pixelWidth();
}

std::map<std::string, std::string> Image2::get_exif_metadata() const {
    MetadataProcessor processor;
    processor.set_output_format(MetadataStrategies::EXIF);
    processor.build(image);
    return processor.getMetadata();
};

std::map<std::string, std::string> Image2::get_iptc_metadata() const {
    MetadataProcessor processor;
    processor.set_output_format(MetadataStrategies::IPTC);
    processor.build(image);
    return processor.getMetadata();
}
