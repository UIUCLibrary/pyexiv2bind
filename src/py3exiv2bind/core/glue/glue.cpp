//
// Created by hborcher on 10/4/2017.
//
#include "glue.h"


#include <exiv2/exif.hpp>
#include <exiv2/image.hpp>
#include <exiv2/version.hpp>

#include <memory>
#include <string>

using Exiv2::Image;
using Exiv2::ImageFactory;

std::string exiv2_version() {
    return Exiv2::versionString();
}


void set_dpi(const std::string &filename, int x_res, int y_res){
    const std::unique_ptr<Exiv2::Image> image = ImageFactory::open(filename);

    image->readMetadata();

    Exiv2::ExifData metadata = image->exifData();

    metadata["Exif.Image.XResolution"] = Exiv2::URational(x_res, 1);
    metadata["Exif.Image.YResolution"] = Exiv2::URational(y_res, 1);
    metadata["Exif.Image.ResolutionUnit"] = 2;
    image->setExifData(metadata);
    image->writeMetadata();
    image->readMetadata();

}
