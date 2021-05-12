//
// Created by hborcher on 10/20/2017.
//

#include "XmpStrategy.h"
#include "make_dictionary.h"
#include <exiv2/error.hpp>
#include <iostream>
std::map<std::string, std::string> XmpStrategy::load(const Exiv2::Image &image){
    try{
        return make_dictionary(image.xmpData());

    }catch (Exiv2::AnyError &e){
//        TODO: Handle errors
        std::cerr << e.what() <<std::endl;
        throw;
    }
}
