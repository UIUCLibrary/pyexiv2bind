#add_library(py3exiv2bind MODULE py3exiv2bind.cpp glue.cpp glue.h)
#target_link_libraries(py3exiv2bind PRIVATE pybind11::module)
#set_target_properties(py3exiv2bind PROPERTIES PREFIX "${PYTHON_MODULE_PREFIX}"
#        SUFFIX "${PYTHON_MODULE_EXTENSION}")

pybind11_add_module(py3exiv2bind py3exiv2bind.cpp glue.cpp glue.h)
set_target_properties(py3exiv2bind PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}
        RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}
        )
target_link_libraries(py3exiv2bind PUBLIC libexiv2)