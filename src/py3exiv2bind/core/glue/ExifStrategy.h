//
// Created by hborcher on 10/11/2017.
//

#ifndef PYEXIV2BIND_EXIFSTRATEGY_H
#define PYEXIV2BIND_EXIFSTRATEGY_H


#include "AbsMetadataStrategy.h"

class ExifStrategy : public AbsMetadataStrategy{
public:
    std::unordered_map<std::string, std::string> load(const Exiv2::Image &image) override;
};


#endif //PYEXIV2BIND_EXIFSTRATEGY_H
