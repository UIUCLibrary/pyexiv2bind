//
// Created by hborcher on 9/15/2017.
//

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "glue/glue.h"
#include <glue/Image.h>



PYBIND11_MODULE(core, m) {
    m.doc() = "Glue code";
    m.def("exiv2_version", &exiv2_version, "Just a exiv2_version check");
    pybind11::class_<Image>(m, "Image")
            .def(pybind11::init<const std::string &>())
            .def_property_readonly("filename", &Image::getFilename)
            .def_property_readonly("pixelHeight", &Image::get_pixelHeight)
            .def_property_readonly("pixelWidth", &Image::get_pixelWidth)
            .def_property_readonly("exif", &Image::get_exif_metadata)
            .def_property_readonly("iptc", &Image::get_iptc_metadata)
            .def_property_readonly("xmp", &Image::get_xmp_metadata)
            ;
}