//
// Created by hborcher on 9/15/2017.
//

#include <pybind11/pybind11.h>
#include <glue.h>
void exif_metadata(const std::string &filename){
    auto metadata = get_exif_metadata(filename);
}

PYBIND11_MODULE(core, m){
    m.doc() = "Glue code";
    m.def("exiv2_version", &exiv2_version, "Just a exiv2_version check");
    m.def("get_exif_metadata", &exif_metadata, "Get the exif metadata of a file");
}