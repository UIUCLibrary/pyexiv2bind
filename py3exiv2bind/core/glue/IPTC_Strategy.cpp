//
// Created by hborcher on 10/11/2017.
//

#include "IPTC_Strategy.h"

std::map<std::string, std::string> IPTC_Strategy::load(const Exiv2::Image::AutoPtr &image) {
    std::map<std::string, std::string> metadata;
    try{
        Exiv2::IptcData &iptcData = image->iptcData();

        if(iptcData.empty()){

            return std::map<std::string, std::string>();
        }

        auto end = iptcData.end();
        for (auto md = iptcData.begin(); md != end; md++){
            metadata[md->key()] = md->value().toString();
        }

    }catch (Exiv2::AnyError &e){
//        TODO: Handle errors
        std::cerr << e.what() <<std::endl;
        throw;
    }
//    TODO: return the metadata a vector
    return metadata;
}
