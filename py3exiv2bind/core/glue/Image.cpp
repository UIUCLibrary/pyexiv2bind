//
// Created by hborcher on 10/11/2017.
//

#include <string>
#include <sstream>
#include <cassert>
#include "Image.h"
#include "glue.h"
#include "MetadataProcessor.h"
#include <exiv2/error.hpp>

std::ostringstream warning_log;
std::ostringstream error_log;

Image::Image(const std::string &filename) : filename(filename) {
    warning_log.clear();
    error_log.clear();
    warning_log.str("");
    error_log.str("");
    try {
        Exiv2::LogMsg::setHandler([](int level, const char *msg) {
            switch((Exiv2::LogMsg::Level)level){

                case Exiv2::LogMsg::debug:break;
                case Exiv2::LogMsg::info:break;
                case Exiv2::LogMsg::warn:
                    warning_log << msg;
                    break;
                case Exiv2::LogMsg::error:
                    error_log << msg;
                    break;
                case Exiv2::LogMsg::mute:break;
            }
        });
        image = Exiv2::ImageFactory::open(filename);
        assert(image.get() != 0); // Make sure it's able to read the file
        image->readMetadata();
    } catch (Exiv2::AnyError &e) {
        std::cerr << e.what() << std::endl;
        throw std::runtime_error(e.what());
    }
    std::string warning_msg = warning_log.str();
    std::string error_msg = error_log.str();

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

std::map<std::string, std::string> Image::get_exif_metadata() const {
    MetadataProcessor processor;
    processor.set_output_format(MetadataStrategies::EXIF);
    processor.build(image);
    return processor.getMetadata();
};

std::map<std::string, std::string> Image::get_iptc_metadata() const {
    MetadataProcessor processor;
    processor.set_output_format(MetadataStrategies::IPTC);
    processor.build(image);
    return processor.getMetadata();
}

std::map<std::string, std::string> Image::get_xmp_metadata() const {
    MetadataProcessor processor;
    processor.set_output_format(MetadataStrategies::XMP);
    processor.build(image);
    return processor.getMetadata();
}

bool Image::is_good() const {
    return image->good();
}

std::string Image::get_icc_profile() const {
    std::string profile;
    std::stringstream data;
    if (!image->iccProfileDefined()) {
        throw std::exception();

    }
    const Exiv2::DataBuf *f = image->iccProfile();
    data.write(reinterpret_cast<char *>(f->pData_), f->size_);
    data << std::endl;
    return data.str();

}

const std::list<std::string> &Image::getWarning_logs() const {
    return warning_logs;
}

const std::list<std::string> &Image::getError_logs() const {
    return error_logs;
}
