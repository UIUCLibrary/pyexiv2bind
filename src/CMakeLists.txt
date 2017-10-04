pybind11_add_module(py3exiv2bind py3exiv2bind.cpp py3exiv2bind.h)
set_target_properties(py3exiv2bind PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
target_link_libraries(py3exiv2bind PUBLIC libexiv2)