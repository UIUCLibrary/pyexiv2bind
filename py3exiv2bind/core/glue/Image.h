//
// Created by hborcher on 10/11/2017.
//

#ifndef PYEXIV2BIND_IMAGE2_H
#define PYEXIV2BIND_IMAGE2_H
#include <exiv2/exiv2.hpp>
#include <unordered_map>
struct Image {
private:
    std::string filename;
    std::unique_ptr<Exiv2::Image> image;
    std::list<std::string> warning_logs;
    std::list<std::string> error_logs;
public:
    explicit Image(const std::string &filename);

    const std::string &getFilename() const;
    int get_pixelHeight() const;
    int get_pixelWidth() const;
    bool is_good() const;
    std::unordered_map<std::string, std::string> get_exif_metadata() const;
    std::unordered_map<std::string, std::string> get_iptc_metadata() const;
    std::unordered_map<std::string, std::string> get_xmp_metadata() const;
    std::string get_icc_profile() const;

    const std::list<std::string> &getWarning_logs() const;

    const std::list<std::string> &getError_logs() const;

};


#endif //PYEXIV2BIND_IMAGE2_H
