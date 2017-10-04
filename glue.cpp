//
// Created by hborcher on 9/15/2017.
//

#include "glue.h"
#include <iostream>
#include <pybind11/pybind11.h>
#include <exiv2/exiv2.hpp>


std::string exiv2_version() {
    return Exiv2::version();
}

PYBIND11_MODULE(glue, m){
    m.doc() = "Glue code";
    m.def("exiv2_version", &exiv2_version, "Just a exiv2_version check");
}