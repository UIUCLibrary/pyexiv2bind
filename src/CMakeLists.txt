#add_library(py3exiv2bind MODULE py3exiv2bind.cpp glue.cpp glue.h)
#target_link_libraries(py3exiv2bind PRIVATE pybind11::module)
#set_target_properties(py3exiv2bind PROPERTIES PREFIX "${PYTHON_MODULE_PREFIX}"
#        SUFFIX "${PYTHON_MODULE_EXTENSION}")

pybind11_add_module(py3exiv2bind py3exiv2bind.cpp glue.cpp glue.h)
set_target_properties(py3exiv2bind PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/py3exiv2bind
        RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/py3exiv2bind
        )
target_link_libraries(py3exiv2bind PUBLIC libexiv2)

add_custom_command(TARGET py3exiv2bind PRE_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/setup.py $<TARGET_FILE_DIR:py3exiv2bind>/..
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/setup.cfg $<TARGET_FILE_DIR:py3exiv2bind>/..
        )
add_custom_command(TARGET py3exiv2bind PRE_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}/py3exiv2bind $<TARGET_FILE_DIR:py3exiv2bind>
        )