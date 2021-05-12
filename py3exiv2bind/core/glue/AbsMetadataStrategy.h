//
// Created by hborcher on 10/11/2017.
//

#ifndef PYEXIV2BIND_ABSMETADATASTRATEGY_H
#define PYEXIV2BIND_ABSMETADATASTRATEGY_H


#include <exiv2/image.hpp>

class AbsMetadataStrategy {
public:
    virtual std::map<std::string, std::string> load(const std::unique_ptr<Exiv2::Image> &image) = 0;
};


#endif //PYEXIV2BIND_ABSMETADATASTRATEGY_H
