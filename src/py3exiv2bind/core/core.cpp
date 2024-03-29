//
// Created by hborcher on 9/15/2017.
//

#include "glue/glue.h"
#include "glue/Image.h"
#include "glue/glue_execeptions.h"
#include <exiv2/error.hpp>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

// PyBind11 library generates warnings for clang-tidy that I can't do anything about
// NOLINTNEXTLINE
PYBIND11_MODULE(core, m) {
    pybind11::options options;
    options.enable_function_signatures();
    m.doc() = R"pbdoc(
        .. currentmodule:: core
    )pbdoc";

    m.def("exiv2_version", &exiv2_version, "Version of exiv2 that is built with");
    pybind11::class_<Image>(m, "Image", "The c++ binding for libexiv2")
            .def(pybind11::init<const std::string &>())
            .def_property_readonly("filename", [](const Image &i) {
                return pybind11::str(i.getFilename());
            },                                                                 "Name of file loaded")
            .def_property_readonly("pixelHeight",   &Image::get_pixelHeight,   "Number of pixels high")
            .def_property_readonly("pixelWidth",    &Image::get_pixelWidth,    "Number of pixels wide")
            .def_property_readonly("exif",          &Image::get_exif_metadata, "Embedded Exif metadata")
            .def_property_readonly("iptc",          &Image::get_iptc_metadata, "Embedded IPTC metadata")
            .def_property_readonly("xmp",           &Image::get_xmp_metadata,  "Embedded XMP metadata")
            .def_property_readonly("error_logs",    &Image::getError_logs,     "Errors produced by Exiv2 library")
            .def_property_readonly("warnings_logs", &Image::getWarning_logs,   "Warnings produced by Exiv2 library")
            .def("get_icc_profile_data",            [](const Image &i) {
                     return pybind11::bytes(i.get_icc_profile());
                 },                                                            "Get the icc profile data")
            .def("is_good",                  &Image::is_good,     "Check if a file is loaded.")
            ;
    pybind11::register_exception<NoIccError>(m, "NoICCError");
    pybind11::register_exception<Exiv2::Error>(m, "Exiv2Error");
    m.def("set_dpi", &set_dpi,
            pybind11::arg("image"),
            pybind11::arg("x"),
            pybind11::arg("y"),
            "set the DPI for a given image file"
            );
}
