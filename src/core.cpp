//
// Created by hborcher on 9/15/2017.
//

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <glue.h>
#include <map>

std::map<std::string, std::string> exif_metadata(const std::string &filename) {
    std::map<std::string, std::string> metadata;
    return get_exif_metadata2(filename);
}

PYBIND11_MODULE(core, m) {
    m.doc() = "Glue code";
    m.def("exiv2_version", &exiv2_version, "Just a exiv2_version check");
    m.def("get_exif_metadata", &exif_metadata, "Get the exif metadata of a file", pybind11::arg("filename"));
}