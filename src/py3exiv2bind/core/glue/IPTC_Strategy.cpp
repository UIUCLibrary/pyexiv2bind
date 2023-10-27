//
// Created by hborcher on 10/11/2017.
//

#include "IPTC_Strategy.h"
#include "make_dictionary.h"
#include <exiv2/error.hpp>
#include <iostream>

std::unordered_map<std::string, std::string> IPTC_Strategy::load(const Exiv2::Image &image){
    return make_dictionary(image.iptcData());
}
