include(ExternalProject)

option( pyexiv2bind_build_libexpat  "build libexpat"    OFF)
option( pyexiv2bind_build_zlib      "build zlib"        OFF)

if (pyexiv2bind_build_libexpat)
    include(external_expat.cmake)
endif ()

if (pyexiv2bind_build_zlib)
    include(external_zlib.cmake)
endif ()

if (MSVC)
    set(EXIV2_ENABLE_WIN_UNICODE ON)
else ()
    set(EXIV2_ENABLE_WIN_UNICODE OFF)
endif ()

ExternalProject_Add(project_libexiv2
        #        URL https://github.com/henryborchers/exiv2/archive/v0.26_deps.tar.gz
        URL https://github.com/henryborchers/exiv2/archive/v0.26.1_deps.tar.gz
        #        GIT_REPOSITORY https://github.com/Exiv2/exiv2.git
        CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=$<CONFIG>
        -DEXIV2_BUILD_EXIV2_COMMAND:BOOL=ON
        -DEXIV2_ENABLE_DYNAMIC_RUNTIME=ON
        -DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>
        -DBUILD_SHARED_LIBS:BOOL=OFF
        -DEXIV2_BUILD_SAMPLES:BOOL=OFF
        -DEXIV2_ENABLE_TOOLS:BOOL=OFF
        -DEXIV2_ENABLE_CURL:BOOL=ON
        -DEXIV2_ENABLE_PNG:BOOL=OFF
        -DEXIV2_ENABLE_XMP:BOOL=OFF
        -DEXIV2_ENABLE_WIN_UNICODE:BOOL=${EXIV2_ENABLE_WIN_UNICODE}
        #            -DEXPAT_INCLUDE_DIR=$<TARGET_PROPERTY:libexpat,INCLUDE_DIRECTORIES>
        #            -DEXPAT_LIBRARY=$<TARGET_FILE:libexpat>
        #            -DZLIB_INCLUDE_DIR=$<TARGET_PROPERTY:zlib,INCLUDE_DIRECTORIES>
        #            -DZLIB_LIBRARY=$<TARGET_FILE:zlib>
        -DICONV_INCLUDE_DIR=""
        -DICONV_LIBRARY=""
        #        DEPENDS
        #            libexpat
        #            zlib

        )
#add_dependencies(project_libexiv2 zlibsource project_libexpat)
ExternalProject_Get_Property(project_libexiv2 install_dir)
message(STATUS "project_libexiv2 install_dir = ${install_dir}")
add_library(exiv2lib STATIC IMPORTED)


#set_property(TARGET libexiv2 )

set_target_properties(exiv2lib PROPERTIES
        INCLUDE_DIRECTORIES ${install_dir}/include
        IMPORTED_LOCATION_DEBUG ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}exiv2d${CMAKE_STATIC_LIBRARY_SUFFIX}
        IMPORTED_LOCATION_RELEASE ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}exiv2${CMAKE_STATIC_LIBRARY_SUFFIX}
        CXX_STANDARD 98
        )
add_dependencies(exiv2lib project_libexiv2)
