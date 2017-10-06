include(ExternalProject)
include(external_zlib.cmake)
include(external_expat.cmake)
message(STATUS "zlibsource install_dir = ${install_dir}")

ExternalProject_Add(project_libexiv2
#        URL https://github.com/henryborchers/exiv2/archive/v0.26_deps.tar.gz
        URL https://github.com/henryborchers/exiv2/archive/v0.26.1_deps.tar.gz
#        GIT_REPOSITORY https://github.com/Exiv2/exiv2.git
        CMAKE_ARGS
        -DEXIV2_ENABLE_DYNAMIC_RUNTIME=ON
        -DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>
        -DBUILD_SHARED_LIBS:BOOL=OFF
#        -DBUILD_SHARED_LIBS:BOOL=OFF
        -DEXIV2_BUILD_SAMPLES:BOOL=OFF
        -DEXIV2_ENABLE_TOOLS:BOOL=ON
        -DEXIV2_ENABLE_CURL:BOOL=ON
        -DEXIV2_ENABLE_PNG:BOOL=OFF
        -DEXIV2_ENABLE_XMP:BOOL=OFF
        -DEXPAT_INCLUDE_DIR=$<TARGET_PROPERTY:libexpat,INCLUDE_DIRECTORIES>
        -DEXPAT_LIBRARY=$<TARGET_FILE:libexpat>
        -DZLIB_INCLUDE_DIR=$<TARGET_PROPERTY:zlib,INCLUDE_DIRECTORIES>
        -DZLIB_LIBRARY=$<TARGET_FILE:zlib>
        -DICONV_INCLUDE_DIR=""
        -DICONV_LIBRARY=""
        DEPENDS libexpat zlib
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

add_library(libxmp STATIC IMPORTED)
add_dependencies(libxmp project_libexiv2)

set_target_properties(libxmp PROPERTIES
        IMPORTED_LOCATION_DEBUG ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}xmpd${CMAKE_STATIC_LIBRARY_SUFFIX}
        IMPORTED_LOCATION_RELEASE ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}xmp${CMAKE_STATIC_LIBRARY_SUFFIX}
#        CXX_STANDARD 98
        )

add_custom_target(dummy_xmp)
add_custom_command(TARGET dummy_xmp
        COMMENT "adfasdfasdddddddddddddf $<TARGET_FILE:libxmp>"
        COMMAND ${CMAKE_COMMAND} -E echo $<TARGET_FILE:libxmp>
        COMMAND ${CMAKE_COMMAND} -E echo $<TARGET_PROPERTY:libxmp,INCLUDE_DIRECTORIES>
        )