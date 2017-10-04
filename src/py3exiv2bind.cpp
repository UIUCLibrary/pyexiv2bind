//
// Created by hborcher on 9/15/2017.
//

#include <pybind11/pybind11.h>
#include "glue.h"


PYBIND11_MODULE(py3exiv2bind, m){
    m.doc() = "Glue code";
    m.def("exiv2_version", &exiv2_version, "Just a exiv2_version check");
}