//
// Created by hborcher on 10/4/2017.
//
#include <exiv2/exiv2.hpp>
#include <iostream>
#include <cassert>
#include "glue.h"
using Exiv2::Image;
using Exiv2::ImageFactory;
std::string exiv2_version() {
    return Exiv2::versionString();
}

//
//const std::vector<metadata_chunk> get_exif_metadata(const std::string &filename) {
////    std::cout << "getting exif metadata of " << filename << std::endl;
//    std::vector<metadata_chunk> metadata;
//    try{
////        TODO: get metadata from filename
//        using namespace Exiv2;
//        Image::AutoPtr image = ImageFactory::open(filename);
//        assert(image.get() != 0); // Make sure it's able to read the file
//        image->readMetadata();
//        ExifData &exifData = image->exifData();
//        if(exifData.empty()){
//            std::string error(filename);
//            error += ": no Exif data found in file";
//            throw Error(1, error);
//        }
//
//        auto end = exifData.end();
//        for (auto md = exifData.begin(); md != end; md++){
////            std::cout << md->key() << std::endl;
//            metadata.push_back({md->key(), std::string(md->typeName()), std::string(md->value().toString().c_str())});
//        }
//
//    }catch (Exiv2::AnyError &e){
////        TODO: Handle errors
//        std::cerr << e.what() <<std::endl;
//        throw;
//    }
////    TODO: return the metadata a vector
//    std::cout << "Returning\n";
//    return metadata;
//}
//
//const std::map<std::string, std::string> get_exif_metadata2(const std::string &filename) {
//    std::cout << "getting exif metadata of " << filename << std::endl;
//    std::map<std::string, std::string> metadata;
//    try{
////        TODO: get metadata from filename
//        using namespace Exiv2;
//        Image::AutoPtr image = ImageFactory::open(filename);
//        assert(image.get() != 0); // Make sure it's able to read the file
//        image->readMetadata();
//        ExifData &exifData = image->exifData();
//        if(exifData.empty()){
//            std::string error(filename);
//            error += ": no Exif data found in file";
//            return std::map<std::string, std::string>();
////            throw Error(1, error);
//        }
//
//        auto end = exifData.end();
//        for (auto md = exifData.begin(); md != end; md++){
//            metadata[md->key()] = md->value().toString();
//        }
//
//    }catch (Exiv2::AnyError &e){
////        TODO: Handle errors
//        std::cerr << e.what() <<std::endl;
//        throw;
//    }
////    TODO: return the metadata a vector
////    std::cout << "Returning\n";
//    return metadata;
//}

int get_pixelHeight(const std::string &filename){
    try {
        auto image = ImageFactory::open(filename);
        assert(image.get() != nullptr); // Make sure it's able to read the file
        image->readMetadata();
        return image->pixelHeight();

    }catch (Exiv2::AnyError &e){
//        TODO: Handle errors
        std::cerr << e.what() <<std::endl;
        throw;
    }

}

int get_pixelWidth(const std::string &filename){
    try {
//        using namespace Exiv2;
        auto image = ImageFactory::open(filename);
        assert(image.get() != nullptr); // Make sure it's able to read the file
        image->readMetadata();
        return image->pixelWidth();

    }catch (Exiv2::AnyError &e) {
//        TODO: Handle errors
        std::cerr << e.what() << std::endl;
        throw;
    }
}


void set_dpi(const std::string &filename, int x, int y){
    try{
        auto image = ImageFactory::open(filename);

        image->readMetadata();

        Exiv2::ExifData metadata = image->exifData();

        metadata["Exif.Image.XResolution"] = create_DPI_string(x);
        metadata["Exif.Image.YResolution"] = create_DPI_string(y);
        metadata["Exif.Image.ResolutionUnit"] = 2;
        image->setExifData(metadata);
        image->writeMetadata();

    }catch (Exiv2::AnyError &e) {
        throw;
    }
}

std::string create_DPI_string(int value){
    std::ostringstream response;
    response << value;
    response << "/1";
    return response.str();
}