//
// Created by hborcher on 10/11/2017.
//

#ifndef PYEXIV2BIND_METADATA_PROCESSOR_H
#define PYEXIV2BIND_METADATA_PROCESSOR_H


#include <memory>
#include <string>
#include <unordered_map>

#include "AbsMetadataStrategy.h"
#include "MetadataStrategies.h"

struct MetadataProcessor {
private:
    std::unique_ptr<AbsMetadataStrategy> metadata_strategy;
    std::unordered_map<std::string, std::string> metadata;
public:
    void build(const Exiv2::Image &image);
    const std::unordered_map<std::string, std::string> &getMetadata() const;
    void set_output_format(MetadataStrategies metadata_type);
};


#endif //PYEXIV2BIND_METADATA_PROCESSOR_H
