//
// Created by hborcher on 10/11/2017.
//

#include "Image.h"

#include "MetadataProcessor.h"
#include "MetadataStrategies.h"
#include "glue_execeptions.h"

#include <exiv2/error.hpp>
#include <exiv2/image.hpp>
#include <exiv2/types.hpp>

#include <cassert>
#include <iostream>
#include <list>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>

namespace {
    std::ostringstream warning_log;
    std::ostringstream error_log;
} // namespace

Image::Image(const std::string &filename) : filename(filename) {
    warning_log.clear();
    error_log.clear();
    warning_log.str("");
    error_log.str("");
    try {
        Exiv2::LogMsg::setHandler([](int level, const char *msg) {
            switch(static_cast<Exiv2::LogMsg::Level>(level)){

                case Exiv2::LogMsg::debug:
                case Exiv2::LogMsg::info:
                case Exiv2::LogMsg::mute:
                    break;
                case Exiv2::LogMsg::warn:
                    warning_log << msg;
                    break;
                case Exiv2::LogMsg::error:
                    error_log << msg;
                    break;
                default: break;
            }
        });
        image = std::unique_ptr<Exiv2::Image>(Exiv2::ImageFactory::open(filename));
        assert(image); // Make sure it's able to read the file
        image->readMetadata();
    } catch (const Exiv2::Error &e) {
        std::cerr << e.what() << std::endl;
        throw std::runtime_error(e.what());
    }
    const std::string warning_msg = warning_log.str();
    const std::string error_msg = error_log.str();

    if(!warning_msg.empty()){
        warning_logs.push_back(warning_msg);
    }
    if(!error_msg.empty()){
        error_logs.push_back(error_log.str());
    }
    warning_log.clear();
    error_log.clear();

}

const std::string &Image::getFilename() const {
    return filename;
}

int Image::get_pixelHeight() const {
    return image->pixelHeight();
}

int Image::get_pixelWidth() const {
    return image->pixelWidth();
}

std::unordered_map<std::string, std::string> Image::get_exif_metadata() const {
    MetadataProcessor processor;
    processor.set_output_format(MetadataStrategies::EXIF);
    processor.build(*image);
    return processor.getMetadata();
}

std::unordered_map<std::string, std::string> Image::get_iptc_metadata() const {
    MetadataProcessor processor;
    processor.set_output_format(MetadataStrategies::IPTC);
    processor.build(*image);
    return processor.getMetadata();
}

std::unordered_map<std::string, std::string> Image::get_xmp_metadata() const {
    MetadataProcessor processor;
    processor.set_output_format(MetadataStrategies::XMP);
    processor.build(*image);
    return processor.getMetadata();
}

bool Image::is_good() const {
    return image->good();
}

std::string Image::get_icc_profile() const {
    std::stringstream data;
    if (!image->iccProfileDefined()) {
        throw NoIccError();
    }
    Exiv2::DataBuf buffer = image->iccProfile();
    for( auto const & byte: buffer){
        data << byte;
    }

    data << std::endl;
    return data.str();

}

const std::list<std::string> &Image::getWarning_logs() const {
    return warning_logs;
}

const std::list<std::string> &Image::getError_logs() const {
    return error_logs;
}
