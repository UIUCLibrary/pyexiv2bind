//
// Created by hborcher on 10/4/2017.
//

#ifndef SUPERBUILD_GLUE_H
#define SUPERBUILD_GLUE_H

#include <string>
#include <map>
//#include "glue_export.h"

struct metadata_chunk {

    const std::string key;
    const std::string data_type;
    const std::string value;


};

std::string exiv2_version();


int get_pixelHeight(const std::string &filename);

int get_pixelWidth(const std::string &filename);

#endif //SUPERBUILD_GLUE_H
