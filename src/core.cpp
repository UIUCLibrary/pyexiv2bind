//
// Created by hborcher on 9/15/2017.
//

#include <pybind11/pybind11.h>
#include <glue.h>


PYBIND11_MODULE(core, m){
    m.doc() = "Glue code";
    m.def("exiv2_version", &exiv2_version, "Just a exiv2_version check");
    m.def("get_exif_metadata", &get_exif_metadata, "Get the exif metadata of a file");
}