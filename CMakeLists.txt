cmake_minimum_required(VERSION 3.16)
project(pyexiv2bind)

#find_package(PythonInterp 3)
#find_package(PythonLibs)
find_package(Python3 COMPONENTS Development)

if (WIN32 AND CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(CMAKE_DEBUG_POSTFIX "d")
endif ()

option(pyexiv2bind_build_exiv2 "Build Exiv2 from source" ON)
#option(pyexiv2bind_png "Build support for the png format" OFF)
option(pyexiv2bind_generate_venv "Generate python virtual environment" ON)
option(pyexiv2bind_generate_python_bindings "Generate python bindings" ON)

include(cmake_scripts/external_exiv22.cmake)
#if (pyexiv2bind_build_exiv2)
#else ()
#    find_package(EXIV2 REQUIRED)
#endif ()

if(pyexiv2bind_generate_venv)
    include(cmake_scripts/build_python_module.cmake)

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
#    add_tox_tests(TOXPATH ${VENV_TOX})
    add_python_wheel()
endif(pyexiv2bind_generate_venv)

option(pyexiv2bind_build_tests "build test suite" ON)
include_directories(${CMAKE_BINARY_DIR})
#include_directories(${install_dir}/include)
include(FetchContent)
FetchContent_Declare(libpybind11
        URL https://github.com/pybind/pybind11/archive/v2.2.3.tar.gz
        URL_HASH SHA1=0acaeb967f09dbef53a1e2a4366780548597beba
        )

FetchContent_Declare(catch2
        URL https://github.com/catchorg/Catch2/archive/v2.12.2.tar.gz
        )
FetchContent_MakeAvailable(catch2)

if(pyexiv2bind_generate_python_bindings)
    if (NOT libpybind11_POPULATED)
        FetchContent_Populate(libpybind11)
    #    option(BUILD_examples "" OFF)
    #    option(BUILD_shared "" OFF)
    #    option(BUILD_tests "" NO)
    #    option(BUILD_tools "" NO)

        add_subdirectory(${libpybind11_SOURCE_DIR} ${libpybind11_BINARY_DIR} EXCLUDE_FROM_ALL)
    endif ()
endif(pyexiv2bind_generate_python_bindings)
#add_subdirectory(thirdparty/pybind11)
add_subdirectory(py3exiv2bind/core)
#target_compile_options(DEBUG)
#add_definitions(DEBUG)
#target_compile_definitions(exiv2lib PRIVATE -DDEBUG)
set_directory_properties(PROPERTIES ADDITIONAL_MAKE_CLEAN_FILES ${PROJECT_SOURCE_DIR}/_skbuild)
#enable_testing()
include(CTest)
add_subdirectory(tests)
#message(WARNING "CMAKE_DEBUG_POSTFIX = ${CMAKE_DEBUG_POSTFIX}")
