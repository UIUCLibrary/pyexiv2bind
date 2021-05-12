//
// Created by hborcher on 10/11/2017.
//

#include "IPTC_Strategy.h"
#include "make_dictionary.h"
#include <exiv2/error.hpp>
#include <iostream>

std::map<std::string, std::string> IPTC_Strategy::load(const std::unique_ptr<Exiv2::Image> &image){
    try{
        return make_dictionary(image->iptcData());
    }catch (Exiv2::AnyError &e){
//        TODO: Handle errors
        std::cerr << e.what() <<std::endl;
        throw;
    }
}
