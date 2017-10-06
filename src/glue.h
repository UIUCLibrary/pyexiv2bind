//
// Created by hborcher on 10/4/2017.
//

#ifndef SUPERBUILD_GLUE_H
#define SUPERBUILD_GLUE_H

#include <string>

struct  metadata_chunk{
    const std::string key;
    const std::string data_type;
    const std::string value;
};

std::string exiv2_version();
const std::vector<metadata_chunk> get_exif_metadata(const std::string &filename);

#endif //SUPERBUILD_GLUE_H
