//
// Created by hborcher on 10/4/2017.
//
#include "glue.h"
#include <exiv2/exiv2.hpp>
using Exiv2::Image;
using Exiv2::ImageFactory;
std::string exiv2_version() {
    return Exiv2::versionString();
}


void set_dpi(const std::string &filename, int x, int y){
    try{

        std::unique_ptr<Exiv2::Image> image = ImageFactory::open(filename);

        image->readMetadata();

        Exiv2::ExifData metadata = image->exifData();

        metadata["Exif.Image.XResolution"] = Exiv2::URational(x, 1);
        metadata["Exif.Image.YResolution"] = Exiv2::URational(y, 1);
        metadata["Exif.Image.ResolutionUnit"] = 2;
        image->setExifData(metadata);
        image->writeMetadata();
        image->readMetadata();

    }catch (const Exiv2::Error &e) {
        throw;
    }
}
