//
// Created by hborcher on 10/20/2017.
//

#include "XmpStrategy.h"
#include "make_dictionary.h"
#include <iostream>
std::unordered_map<std::string, std::string> XmpStrategy::load(const Exiv2::Image &image){
    return make_dictionary(image.xmpData());
}
