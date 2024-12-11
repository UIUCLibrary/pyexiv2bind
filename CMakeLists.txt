cmake_minimum_required(VERSION 3.24)
project(pyexiv2bind)

find_package(Python3 COMPONENTS Interpreter Development)

if (WIN32 AND CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(CMAKE_DEBUG_POSTFIX "d")
endif ()

option(pyexiv2bind_build_exiv2 "Build Exiv2 from source" ON)
option(pyexiv2bind_generate_python_bindings "Generate python bindings" OFF)

include(cmake_scripts/external_exiv22.cmake)

option(pyexiv2bind_build_tests "build test suite" ON)
include_directories(${CMAKE_BINARY_DIR})
include(FetchContent)
FetchContent_Declare(libpybind11
        URL https://github.com/pybind/pybind11/archive/refs/tags/v2.10.4.tar.gz
        URL_HASH SHA1=5c366a92fc4b3937bcc3389405edbe362b1f3cbd
        DOWNLOAD_EXTRACT_TIMESTAMP TRUE
        EXCLUDE_FROM_ALL
        )

FetchContent_Declare(libcatch2
        URL https://github.com/catchorg/Catch2/archive/v3.4.0.tar.gz
        URL_HASH SHA1=4c308576c856a43dc88949a8f64ef90ebf94ae1b
        DOWNLOAD_EXTRACT_TIMESTAMP TRUE
        )

if(pyexiv2bind_generate_python_bindings)
    FetchContent_MakeAvailable(libpybind11)
endif(pyexiv2bind_generate_python_bindings)
add_subdirectory(src/py3exiv2bind/core)
set_directory_properties(PROPERTIES ADDITIONAL_MAKE_CLEAN_FILES ${PROJECT_SOURCE_DIR}/_skbuild)
include(CTest)
add_subdirectory(tests)
