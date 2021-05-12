//
// Created by hborcher on 10/11/2017.
//

#include "MetadataProcessor.h"
#include "IPTC_Strategy.h"
#include "ExifStrategy.h"
#include "XmpStrategy.h"

const std::map<std::string, std::string> &MetadataProcessor::getMetadata() const {
    return metadata;
}

void MetadataProcessor::build(const Exiv2::Image &image) {
    metadata = this->metadata_strategy->load(image);
}

void MetadataProcessor::set_output_format(MetadataStrategies metadata_type) {
    switch (metadata_type){
        case MetadataStrategies::IPTC:
            metadata_strategy = std::make_unique<IPTC_Strategy>();
            break;
        case MetadataStrategies::EXIF:
            metadata_strategy = std::make_unique<ExifStrategy>();
            break;
        case MetadataStrategies::XMP:
            metadata_strategy = std::make_unique<XmpStrategy>();
            break;
    }
}
