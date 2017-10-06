//
// Created by hborcher on 10/4/2017.
//
#include <exiv2/exiv2.hpp>
#include <iostream>
#include <assert.h>
#include "glue.h"
std::string exiv2_version() {
    return Exiv2::version();
}

const std::vector<metadata_chunk> get_exif_metadata(const std::string &filename) {
    std::cout << "getting exif metadata of " << filename << std::endl;
    std::vector<metadata_chunk> metadata;
    try{
//        TODO: get metadata from filename
        using namespace Exiv2;
        Image::AutoPtr image = ImageFactory::open(filename);
        assert(image.get() != 0); // Make sure it's able to read the file
        image->readMetadata();
        ExifData &exifData = image->exifData();
        if(exifData.empty()){
            std::string error(filename);
            error += ": no Exif data found in file";
            throw Error(1, error);
        }

        auto end = exifData.end();
        for (auto md = exifData.begin(); md != end; md++){
            std::cout << md->key() << std::endl;
            metadata_chunk chunk = {md->key(), std::string(md->typeName()), std::string(md->value().toString().c_str())};
            metadata.push_back(chunk);
        }

    }catch (Exiv2::AnyError &e){
//        TODO: Handle errors
        std::cerr << e.what() <<std::endl;
        throw;
    }
//    TODO: return the metadata a vector
    std::cout << "Returning\n";
    return metadata;
}
