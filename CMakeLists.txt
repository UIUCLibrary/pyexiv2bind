cmake_minimum_required(VERSION 3.8)
project(pyexiv2bind)

option( build_tests     "build test suite"  ON  )

include(ExternalProject)
include(external_exiv2.cmake)

add_executable(runme main.cpp)


if(build_tests)
    add_dependencies(runme add_tests)
endif()
target_link_libraries(runme PRIVATE libexiv2)
add_dependencies(runme libexiv2)
include_directories(${install_dir}/include)
add_subdirectory(thirdparty/pybind11)
add_subdirectory(src)
enable_testing()
add_subdirectory(tests)
