//
// Created by hborcher on 10/11/2017.
//

#include "ExifStrategy.h"
#include "make_dictionary.h"
std::map<std::string, std::string> ExifStrategy::load(const Exiv2::Image::AutoPtr &image) {
    try{
        return make_dictionary(image->exifData());
    }catch (Exiv2::AnyError &e){
//        TODO: Handle errors
        std::cerr << e.what() <<std::endl;
        throw;
    }
//    TODO: return the metadata a vector
}
