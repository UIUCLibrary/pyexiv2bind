//
// Created by hborcher on 10/4/2017.
//
#include <exiv2/exiv2.hpp>
#include <iostream>
#include <cassert>
#include "glue.h"
using Exiv2::Image;
using Exiv2::ImageFactory;
std::string exiv2_version() {
    return Exiv2::versionString();
}


void set_dpi(const std::string &filename, int x, int y){
    try{
        auto image = ImageFactory::open(filename);

        image->readMetadata();

        Exiv2::ExifData metadata = image->exifData();

        metadata["Exif.Image.XResolution"] = create_DPI_string(x);
        metadata["Exif.Image.YResolution"] = create_DPI_string(y);
        metadata["Exif.Image.ResolutionUnit"] = 2;
        image->setExifData(metadata);
        image->writeMetadata();

    }catch (Exiv2::AnyError &e) {
        throw;
    }
}

std::string create_DPI_string(int value){
    std::ostringstream response;
    response << value;
    response << "/1";
    return response.str();
}