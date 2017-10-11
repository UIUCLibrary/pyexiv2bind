//
// Created by hborcher on 10/11/2017.
//

#include <string>
#include <cassert>
#include "Image2.h"
#include "glue.h"


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
    std::map<std::string, std::string> metadata;
    try{
        using namespace Exiv2;
        ExifData &exifData = image->exifData();
        if(exifData.empty()){
            return std::map<std::string, std::string>();
        }

        auto end = exifData.end();
        for (auto md = exifData.begin(); md != end; md++){
            metadata[md->key()] = md->value().toString();
        }

    }catch (Exiv2::AnyError &e){
//        TODO: Handle errors
        std::cerr << e.what() <<std::endl;
        throw;
    }
//    TODO: return the metadata a vector
    return metadata;
}
