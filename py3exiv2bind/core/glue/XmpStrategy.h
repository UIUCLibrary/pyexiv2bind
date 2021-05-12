//
// Created by hborcher on 10/20/2017.
//

#ifndef PYEXIV2BIND_XMPSTRATEGY_H
#define PYEXIV2BIND_XMPSTRATEGY_H

#include "AbsMetadataStrategy.h"
class XmpStrategy : public AbsMetadataStrategy {
public:
    std::map<std::string, std::string> load(const std::unique_ptr<Exiv2::Image> &image) override;
//    std::map<std::string, std::string> load(const Exiv2::Image::AutoPtr &image) override;
};


#endif //PYEXIV2BIND_XMPSTRATEGY_H
