include(GenerateExportHeader)
#pybind11_add_module(core core.cpp)

#GENERATE_EXPORT_HEADER(glue)
#add_custom_target(d COMMAND ${CMAKE_COMMAND} -E echo "the anser is $<TARGET_PROPERTY:exiv2lib,INCLUDE_DIRECTORIES>")
#target_include_directories(glue PUBLIC ${CMAKE_CURRENT_BINARY_DIR})
#target_link_libraries(glue PUBLIC exiv2lib)
add_subdirectory(glue)
add_library(core MODULE core.cpp $<TARGET_OBJECTS:glue>)


if (SKBUILD)
    python_extension_module(core)
endif()
set_target_properties(core PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/py3exiv2bind
        RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/py3exiv2bind
        PREFIX "${PYTHON_MODULE_PREFIX}"
        SUFFIX "${PYTHON_MODULE_EXTENSION}"
        )
target_link_libraries(core pybind11::module exiv2lib)


#target_link_libraries(core glue)
install(TARGETS core LIBRARY DESTINATION py3exiv2bind)