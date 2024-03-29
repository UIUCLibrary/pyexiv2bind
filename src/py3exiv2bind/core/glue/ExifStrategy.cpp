//
// Created by hborcher on 10/11/2017.
//

#include "ExifStrategy.h"
#include "make_dictionary.h"
#include <iostream>

std::unordered_map<std::string, std::string> ExifStrategy::load(const Exiv2::Image &image){
    return make_dictionary(image.exifData());
}
