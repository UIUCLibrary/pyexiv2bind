#add_library(py3exiv2bind MODULE py3exiv2bind.cpp glue.cpp glue.h)
#target_link_libraries(py3exiv2bind PRIVATE pybind11::module)
#set_target_properties(py3exiv2bind PROPERTIES PREFIX "${PYTHON_MODULE_PREFIX}"
#        SUFFIX "${PYTHON_MODULE_EXTENSION}")

pybind11_add_module(core core.cpp)
add_library(glue STATIC glue.cpp glue.h)
target_include_directories(glue PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
set_target_properties(glue PROPERTIES
        CXX_STANDARD 14)
target_link_libraries(core PUBLIC glue)
set_target_properties(core PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/py3exiv2bind
        RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/py3exiv2bind
        )
target_link_libraries(glue PUBLIC libexiv2)
add_dependencies(core libexiv2)
add_custom_command(TARGET core PRE_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/setup.py $<TARGET_FILE_DIR:core>/..
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/setup.cfg $<TARGET_FILE_DIR:core>/..
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/tox.ini $<TARGET_FILE_DIR:core>/..
        )
add_custom_command(TARGET core PRE_BUILD
#        COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}/py3exiv2bind $<TARGET_FILE_DIR:core>
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/py3exiv2bind/__init__.py $<TARGET_FILE_DIR:core>
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/py3exiv2bind/metadata.py $<TARGET_FILE_DIR:core>
        )
add_custom_command(TARGET core PRE_BUILD
#        COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}/py3exiv2bind $<TARGET_FILE_DIR:core>
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/py3exiv2bind/image.py $<TARGET_FILE_DIR:core>
        )