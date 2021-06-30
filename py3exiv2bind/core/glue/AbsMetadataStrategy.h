//
// Created by hborcher on 10/11/2017.
//

#ifndef PYEXIV2BIND_ABSMETADATASTRATEGY_H
#define PYEXIV2BIND_ABSMETADATASTRATEGY_H


#include <exiv2/image.hpp>
#include <unordered_map>
class AbsMetadataStrategy {
public:
    virtual std::unordered_map<std::string, std::string> load(const Exiv2::Image &image) = 0;
    virtual ~AbsMetadataStrategy() = default;
};


#endif //PYEXIV2BIND_ABSMETADATASTRATEGY_H
