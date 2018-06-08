include(GenerateExportHeader)
#pybind11_add_module(core core.cpp)
add_library(glue OBJECT
        glue/glue.cpp
        glue/glue.h
        glue/Image.cpp
        glue/Image.h
        glue/MetadataStrategies.h
        glue/MetadataProcessor.cpp
        glue/MetadataProcessor.h
        glue/IPTC_Strategy.cpp
        glue/IPTC_Strategy.h
        glue/ExifStrategy.cpp
        glue/ExifStrategy.h
        glue/AbsMetadataStrategy.h
        glue/XmpStrategy.cpp
        glue/XmpStrategy.h
        glue/make_dictionary.h
        )
#exiv2lib
target_include_directories(glue PUBLIC ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR}
        PRIVATE
        $<TARGET_PROPERTY:exiv2lib,INCLUDE_DIRECTORIES>
        )
set_target_properties(glue PROPERTIES
        CXX_STANDARD 14
        )
#GENERATE_EXPORT_HEADER(glue)
#add_custom_target(d COMMAND ${CMAKE_COMMAND} -E echo "the anser is $<TARGET_PROPERTY:exiv2lib,INCLUDE_DIRECTORIES>")
#target_include_directories(glue PUBLIC ${CMAKE_CURRENT_BINARY_DIR})
#target_link_libraries(glue PUBLIC exiv2lib)

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