//
// Created by hborcher on 10/4/2017.
//

#ifndef SUPERBUILD_GLUE_H
#define SUPERBUILD_GLUE_H

#include <string>
#include <map>

struct metadata_chunk {

    const std::string key;
    const std::string data_type;
    const std::string value;


};

std::string exiv2_version();

void set_dpi(const std::string &filename, int x, int y);

#endif //SUPERBUILD_GLUE_H
