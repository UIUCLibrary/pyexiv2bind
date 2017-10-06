//
// Created by hborcher on 10/4/2017.
//
#include <exiv2/exiv2.hpp>
#include <iostream>
#include "glue.h"
std::string exiv2_version() {
    return Exiv2::version();
}

int get_exif_metadata() {
    std::cout << "getting exif metadata\n";
    return 0;
}
