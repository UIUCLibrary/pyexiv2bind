//
// Created by hborcher on 10/20/2017.
//

#include "XmpStrategy.h"

std::map<std::string, std::string> XmpStrategy::load(const Exiv2::Image::AutoPtr &image) {
    std::map<std::string, std::string> metadata;
    try{
        Exiv2::XmpData &xmpData = image->xmpData();

        if(xmpData.empty()){

            return std::map<std::string, std::string>();
        }

        auto end = xmpData.end();
        for (auto md = xmpData.begin(); md != end; md++){
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
