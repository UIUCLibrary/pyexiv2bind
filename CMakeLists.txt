cmake_minimum_required(VERSION 3.11)
project(pyexiv2bind)

find_package(PythonInterp 3 REQUIRED)
find_package(PythonLibs)

if (WIN32 AND CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(CMAKE_DEBUG_POSTFIX "d")
endif ()

option(pyexiv2bind_build_exiv2 "Build Exiv2 from source" ON)
option(pyexiv2bind_png "Build support for the png format" OFF)

if (pyexiv2bind_build_exiv2)
    include(cmake/external_exiv22.cmake)
else ()
    find_package(EXIV2 REQUIRED)
endif ()

if (SKBUILD)
    message(STATUS "USING SCIKIT BUILD")

    find_package(PythonExtensions REQUIRED)

else ()

    include(cmake/build_python_module.cmake)

    create_venv(
            DESTINATION ${PROJECT_BINARY_DIR}/venv
            REQUIREMENTS
                ${PROJECT_SOURCE_DIR}/requirements.txt
                ${PROJECT_SOURCE_DIR}/requirements-dev.txt
    )

    add_custom_target(py3exiv2bind
            DEPENDS ${PYTHON_PACKAGE_SOURCE} core
            )

#    update_python_binary_dir(${CMAKE_SOURCE_DIR}/py3exiv2bind)

     find_program(VENV_TOX
             NAMES tox
             PATHS
                ${PROJECT_BINARY_DIR}/venv/Scripts/
                ${PROJECT_BINARY_DIR}/venv/bin/
             NO_DEFAULT_PATH
             )
    add_tox_tests(TOXPATH ${VENV_TOX})
    add_python_wheel()

endif ()

option(pyexiv2bind_build_tests "build test suite" ON)
include_directories(${CMAKE_BINARY_DIR})
#include_directories(${install_dir}/include)


FetchContent_Declare(libpybind11
        URL https://github.com/pybind/pybind11/archive/v2.2.3.tar.gz
        URL_HASH SHA1=0acaeb967f09dbef53a1e2a4366780548597beba
        )

FetchContent_GetProperties(libpybind11)
if (NOT libpybind11_POPULATED)
    FetchContent_Populate(libpybind11)
#    option(BUILD_examples "" OFF)
#    option(BUILD_shared "" OFF)
#    option(BUILD_tests "" NO)
#    option(BUILD_tools "" NO)

    add_subdirectory(${libpybind11_SOURCE_DIR} ${libpybind11_BINARY_DIR})
endif ()

#add_subdirectory(thirdparty/pybind11)
add_subdirectory(py3exiv2bind/core)
set_directory_properties(PROPERTIES ADDITIONAL_MAKE_CLEAN_FILES ${PROJECT_SOURCE_DIR}/_skbuild)
#enable_testing()
include(CTest)
add_subdirectory(tests)
#message(WARNING "CMAKE_DEBUG_POSTFIX = ${CMAKE_DEBUG_POSTFIX}")
