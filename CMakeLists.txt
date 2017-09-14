cmake_minimum_required(VERSION 3.8)
project(superbuild)
include(ExternalProject)
set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES main.cpp)

ExternalProject_Add(zlibsource
        URL https://zlib.net/zlib-1.2.11.tar.gz
        CMAKE_ARGS
        -DINSTALL_BIN_DIR=""
        -DINSTALL_LIB_DIR=${CMAKE_BINARY_DIR}/thirdparty/zlib/lib
        -DINSTALL_INC_DIR=${CMAKE_BINARY_DIR}/thirdparty/zlib/include
        -DINSTALL_MAN_DIR=""
        -DINSTALL_PKGCONFIG_DIR=""

        )
ExternalProject_Add(libexpat
        URL https://github.com/libexpat/libexpat/archive/R_2_2_4.tar.gz
        SOURCE_SUBDIR expat
        CMAKE_ARGS
        -DBUILD_examples=off
        -DBUILD_shared=off
        -DBUILD_tests=off
        -DBUILD_tools=off
        -DCMAKE_INSTALL_PREFIX=${CMAKE_BINARY_DIR}/thirdparty/expat
        )
ExternalProject_Add(libexiv2
        GIT_REPOSITORY https://github.com/Exiv2/exiv2.git
        CMAKE_ARGS
        -DEXIV2_ENABLE_DYNAMIC_RUNTIME=ON
        -DCMAKE_INSTALL_PREFIX=${CMAKE_BINARY_DIR}/thirdparty/exiv2
        -DBUILD_SHARED_LIBS=OFF
        -DEXPAT_INCLUDE_DIR=${CMAKE_BINARY_DIR}/thirdparty/expat/include
        -DEXPAT_LIBRARY=${CMAKE_BINARY_DIR}/thirdparty/expat/lib/${CMAKE_STATIC_LIBRARY_PREFIX}expat${CMAKE_STATIC_LIBRARY_SUFFIX}
        -DZLIB_INCLUDE_DIR=${CMAKE_BINARY_DIR}/thirdparty/zlib/include
        -DZLIB_LIBRARY=${CMAKE_BINARY_DIR}/thirdparty/zlib/lib/${CMAKE_STATIC_LIBRARY_PREFIX}zlibstatic${CMAKE_STATIC_LIBRARY_SUFFIX}
        -DICONV_INCLUDE_DIR=""
        -DICONV_LIBRARY=""
        )

add_executable(superbuild ${SOURCE_FILES})
add_dependencies(libexiv2 zlibsource libexpat)
add_dependencies(superbuild libexiv2)
