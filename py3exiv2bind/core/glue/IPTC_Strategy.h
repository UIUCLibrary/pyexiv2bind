//
// Created by hborcher on 10/11/2017.
//

#ifndef PYEXIV2BIND_IPTC_STRATEGY_H
#define PYEXIV2BIND_IPTC_STRATEGY_H


#include "AbsMetadataStrategy.h"

class IPTC_Strategy : public AbsMetadataStrategy {
    std::map<std::string, std::string> load(const std::unique_ptr<Exiv2::Image> &image) override;
//    std::map<std::string, std::string> load(const Exiv2::Image::AutoPtr &image) override;
};


#endif //PYEXIV2BIND_IPTC_STRATEGY_H
