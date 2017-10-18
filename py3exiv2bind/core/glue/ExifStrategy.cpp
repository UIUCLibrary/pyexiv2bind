//
// Created by hborcher on 10/11/2017.
//

#include "ExifStrategy.h"

std::map<std::string, std::string> ExifStrategy::load(const Exiv2::Image::AutoPtr &image) {
    std::map<std::string, std::string> metadata;
    try{
        Exiv2::ExifData &exifData = image->exifData();

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
