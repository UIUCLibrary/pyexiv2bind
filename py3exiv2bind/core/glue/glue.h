//
// Created by hborcher on 10/4/2017.
//

#ifndef SUPERBUILD_GLUE_H
#define SUPERBUILD_GLUE_H

#include <string>
#include <map>
#include "glue_export.h"

struct metadata_chunk {

//    metadata_chunk() {};
//    metadata_chunk &operator=(const metadata_chunk &m) {
//        metadata_chunk tmp(m);
//
////        *this = std::move(tmp);
////        *this = std::mov
//        return *this;
//    }

//    metadata_chunk(const metadata_chunk &m) : key(m.key), data_type(m.data_type), value(m.value) {};
    const std::string key;
    const std::string data_type;
    const std::string value;

//    metadata_chunk(const std::string &key, const std::string &data_type, const std::string &value) : key(key),
//                                                                                                     data_type(
//                                                                                                             data_type),
//                                                                                                     value(value) {}

};

std::string exiv2_version();

GLUE_DEPRECATED const std::vector<metadata_chunk> get_exif_metadata(const std::string &filename);

const std::map<std::string, std::string> get_exif_metadata2(const std::string &filename);

int get_pixelHeight(const std::string &filename);

int get_pixelWidth(const std::string &filename);

#endif //SUPERBUILD_GLUE_H
