cmake_minimum_required(VERSION 3.8)
project(pyexiv2bind)
include(ExternalProject)


find_package(PythonLibs 3 REQUIRED)
#find_package(Boost COMPONENTS python3 REQUIRED)

ExternalProject_Add(zlibsource
        URL https://zlib.net/zlib-1.2.11.tar.gz
        CMAKE_ARGS
        -DINSTALL_BIN_DIR=""
        -DINSTALL_LIB_DIR=${CMAKE_BINARY_DIR}/thirdparty/zlib/lib
        -DINSTALL_INC_DIR=${CMAKE_BINARY_DIR}/thirdparty/zlib/include
        -DINSTALL_MAN_DIR=""
        -DINSTALL_PKGCONFIG_DIR=""

        )
ExternalProject_Get_Property(zlibsource install_dir)
message(STATUS "zlibsource install_dir = ${install_dir}")
ExternalProject_Add(project_libexpat
        URL https://github.com/libexpat/libexpat/archive/R_2_2_4.tar.gz
        SOURCE_SUBDIR expat
        CMAKE_ARGS
        -DBUILD_examples=off
        -DBUILD_shared=off
        -DBUILD_tests=off
        -DBUILD_tools=off
        -DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>
#        -DCMAKE_INSTALL_PREFIX=${CMAKE_BINARY_DIR}/thirdparty/expat
        )
ExternalProject_Get_Property(project_libexpat install_dir)
set(libexpat_install_dir ${install_dir})
message(STATUS "libexpat_install_dir = ${libexpat_install_dir}")
ExternalProject_Add(project_libexiv2
        URL https://github.com/henryborchers/exiv2/archive/v0.26_deps.tar.gz
#        GIT_REPOSITORY https://github.com/henryborchers/exiv2.git
        CMAKE_ARGS
        -DEXIV2_ENABLE_DYNAMIC_RUNTIME=ON
        -DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>
#        -DCMAKE_INSTALL_PREFIX=${CMAKE_BINARY_DIR}/thirdparty/exiv2
        -DBUILD_SHARED_LIBS:BOOL=OFF
        -DEXIV2_ENABLE_BUILD_SAMPLES:BOOL=OFF
        -DEXIV2_ENABLE_TOOLS:BOOL=ON
        -DEXIV2_ENABLE_CURL:BOOL=ON
        -DEXIV2_ENABLE_PNG:BOOL=OFF
        -DEXIV2_ENABLE_XMP:BOOL=OFF
        -DEXPAT_INCLUDE_DIR=${libexpat_install_dir}/include
        -DEXPAT_LIBRARY=${libexpat_install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}expat${CMAKE_STATIC_LIBRARY_SUFFIX}
        -DZLIB_INCLUDE_DIR=${CMAKE_BINARY_DIR}/thirdparty/zlib/include
        -DZLIB_LIBRARY=${CMAKE_BINARY_DIR}/thirdparty/zlib/lib/${CMAKE_STATIC_LIBRARY_PREFIX}zlibstatic${CMAKE_STATIC_LIBRARY_SUFFIX}
        -DICONV_INCLUDE_DIR=""
        -DICONV_LIBRARY=""
        )
add_dependencies(project_libexiv2 zlibsource project_libexpat)
ExternalProject_Get_Property(project_libexiv2 install_dir)
message(STATUS "project_libexiv2 install_dir = ${install_dir}")
add_library(libexiv2 STATIC IMPORTED)
add_dependencies(libexiv2 project_libexiv2)


set_property(TARGET libexiv2 PROPERTY INCLUDE_DIRECTORIES ${install_dir}/include)

set_target_properties(libexiv2 PROPERTIES
        IMPORTED_LOCATION_DEBUG ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}exiv2d${CMAKE_STATIC_LIBRARY_SUFFIX}
        IMPORTED_LOCATION_RELEASE ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}exiv2${CMAKE_STATIC_LIBRARY_SUFFIX}
        CXX_STANDARD 98
        )

add_executable(runme main.cpp)
target_link_libraries(runme PRIVATE libexiv2)
add_dependencies(runme libexiv2)
include_directories(${install_dir}/include)
add_subdirectory(thirdparty/pybind11)
add_subdirectory(src)

enable_testing()
add_subdirectory(tests)
