//
// Created by hborcher on 10/11/2017.
//

#ifndef PYEXIV2BIND_IMAGE2_H
#define PYEXIV2BIND_IMAGE2_H
#include <exiv2/exiv2.hpp>

struct Image {
private:
    std::string filename;
    Exiv2::Image::AutoPtr image;
public:
    Image(const std::string &filename);

    const std::string &getFilename() const;
    int get_pixelHeight() const;
    int get_pixelWidth() const;
    bool is_good() const;
    std::map<std::string, std::string> get_exif_metadata() const;
    std::map<std::string, std::string> get_iptc_metadata() const;
    std::map<std::string, std::string> get_xmp_metadata() const;

};


#endif //PYEXIV2BIND_IMAGE2_H
