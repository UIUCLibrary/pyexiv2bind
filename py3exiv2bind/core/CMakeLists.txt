include(GenerateExportHeader)
pybind11_add_module(core core.cpp)

add_library(glue STATIC glue/glue.cpp glue/glue.h glue/Image2.cpp glue/Image2.h)

target_include_directories(glue PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
set_target_properties(glue PROPERTIES
        CXX_STANDARD 14)
GENERATE_EXPORT_HEADER(glue)

target_include_directories(glue PUBLIC ${CMAKE_CURRENT_BINARY_DIR})
target_link_libraries(core PUBLIC glue)
set_target_properties(core PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/py3exiv2bind
        RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/py3exiv2bind
        )


target_link_libraries(glue PUBLIC exiv2lib)
install(TARGETS core DESTINATION py3exiv2bind)