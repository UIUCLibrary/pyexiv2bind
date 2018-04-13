include(FetchContent)
include(ExternalProject)

###########################################################################################
# Google ZLIB
###########################################################################################

FetchContent_Declare(zlib
        URL https://zlib.net/zlib-1.2.11.tar.gz
        URL_HASH SHA256=c3e5e9fdd5004dcb542feda5ee4f0ff0744628baf8ed2dd5d66f8ca1197cb1a1
)

FetchContent_GetProperties(zlib)
if (NOT zlib_POPULATED)
    FetchContent_Populate(zlib)
    add_subdirectory(${zlib_SOURCE_DIR} ${zlib_BINARY_DIR})
endif ()


###########################################################################################
# libexpat build
###########################################################################################

list(APPEND expat_args -DBUILD_examples=off)
list(APPEND expat_args -DBUILD_shared=off)
list(APPEND expat_args -DBUILD_tests=off)
list(APPEND expat_args -DBUILD_tools=off)
list(APPEND expat_args -DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>)
list(APPEND expat_args -DCMAKE_BUILD_TYPE=$<CONFIG>)

ExternalProject_Add(project_libexpat
        URL https://github.com/libexpat/libexpat/archive/R_2_2_4.zip
        SOURCE_SUBDIR expat
        CMAKE_ARGS ${expat_args}
        # -DBUILD_tests=$<$<CONFIG:Debug>:1, 0>
        # TEST_BEFORE_INSTALL $<$<CONFIG:Debug>1, 0>
        LOG_CONFIGURE 1
        BUILD_BYPRODUCTS
        <INSTALL_DIR>/lib/${CMAKE_STATIC_LIBRARY_PREFIX}expat${CMAKE_DEBUG_POSTFIX}${CMAKE_STATIC_LIBRARY_SUFFIX}
        )

ExternalProject_Get_Property(project_libexpat install_dir)
add_library(libexpat::libexpat STATIC IMPORTED)
add_dependencies(libexpat::libexpat project_libexpat)
set_target_properties(libexpat::libexpat PROPERTIES
        INCLUDE_DIRECTORIES ${install_dir}/include
        IMPORTED_LOCATION_DEBUG ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}expat${CMAKE_DEBUG_POSTFIX}${CMAKE_STATIC_LIBRARY_SUFFIX}
        IMPORTED_LOCATION_RELEASE ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}expat${CMAKE_STATIC_LIBRARY_SUFFIX}
        )

###########################################################################################
# Google test build
###########################################################################################

FetchContent_Declare(
        googletest
        GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG release-1.8.0
)
FetchContent_GetProperties(googletest)
if (NOT googletest_POPULATED)
    FetchContent_Populate(googletest)
    option(BUILD_GTEST "" ON)
    option(BUILD_GMOCK "" FALSE)
    option(BUILD_SHARED_LIBS "" ON)
    option(gtest_disable_pthreads "" TRUE)
    option(gtest_force_shared_crt "" TRUE)
    add_subdirectory(${googletest_SOURCE_DIR} ${googletest_BINARY_DIR})
endif ()

FetchContent_Declare(
        libexiv2
        GIT_REPOSITORY https://github.com/UIUCLibrary/exiv2.git
)
FetchContent_GetProperties(libexiv2)
if (NOT libexiv2_POPULATED)
    FetchContent_Populate(libexiv2)
    set(BUILD_SHARED_LIBS OFF)
    option(EXIV2_BUILD_UNIT_TESTS "" ON)
    option(EXIV2_ENABLE_DYNAMIC_RUNTIME "" ON)
    set(EXPAT_LIBRARY ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}expat${CMAKE_DEBUG_POSTFIX}${CMAKE_STATIC_LIBRARY_SUFFIX})

    set(EXPAT_INCLUDE_DIR $<TARGET_PROPERTY:libexpat::libexpat,INCLUDE_DIRECTORIES>)
    set(ZLIB_INCLUDE_DIR $<TARGET_PROPERTY:zlibstatic,INCLUDE_DIRECTORIES>)
    set(ZLIB_LIBRARY "$<TARGET_FILE:zlibstatic>")
    set(GTEST_INCLUDE_DIR $<TARGET_PROPERTY:gtest,INCLUDE_DIRECTORIES>)
    set(GTEST_LIBRARY $<TARGET_LINKER_FILE:gtest>)
    set(GTEST_MAIN_LIBRARY $<TARGET_LINKER_FILE:gtest_main>)
    add_subdirectory(${libexiv2_SOURCE_DIR} ${libexiv2_BINARY_DIR})
    include_directories(${libexiv2_BINARY_DIR})
        add_dependencies(exiv2lib zlibstatic)
    add_dependencies(unit_tests gtest gtest_main)
endif ()
add_dependencies(xmp project_libexpat)


#########################################################################################
#if(pyexiv2bind_png)
#    list(APPEND libexiv2_args -DEXIV2_ENABLE_PNG:BOOL=ON)
#    list(APPEND libexiv2_args -DZLIB_LIBRARY=$<TARGET_FILE:zlib::zlib>)
#    list(APPEND libexiv2_args -DZLIB_INCLUDE_DIR=$<TARGET_PROPERTY:zlib::zlib,INCLUDE_DIRECTORIES>)
#    list(APPEND libexiv2_depends project_zlib)
#else()
#    list(APPEND libexiv2_args -DEXIV2_ENABLE_PNG:BOOL=OFF)
#endif()
#if(WIN32)
#    list(APPEND libexiv2_args -DEXIV2_ENABLE_WIN_UNICODE:BOOL=ON)
#endif()
#list(APPEND libexiv2_args -DCMAKE_BUILD_TYPE=$<CONFIG>)
#list(APPEND libexiv2_args -DEXIV2_BUILD_EXIV2_COMMAND:BOOL=ON)
#list(APPEND libexiv2_args -DEXIV2_ENABLE_DYNAMIC_RUNTIME=ON)
#list(APPEND libexiv2_args -DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>)
#list(APPEND libexiv2_args -DBUILD_SHARED_LIBS:BOOL=ON)
#list(APPEND libexiv2_args -DEXIV2_BUILD_SAMPLES:BOOL=OFF)
#list(APPEND libexiv2_args -DEXIV2_ENABLE_XMP:BOOL=ON)
#list(APPEND libexiv2_args -DEXIV2_BUILD_UNIT_TESTS=ON)
##list(APPEND libexiv2_args -DGTEST_ROOT="${googletest_root}")
#
##list(APPEND libexiv2_args -DGTEST_INCLUDE_DIR=<TARGET_PROPERTY:gtest_main,INCLUDE_DIRECTORIES>)
#list(APPEND libexiv2_args -DGTEST_INCLUDE_DIR=${googletest_SOURCE_DIR}/googletest/include)
##list(APPEND libexiv2_args -DGTEST_INCLUDE_DIR=$<TARGET_PROPERTY:googletest::googletest,INCLUDE_DIRECTORIES>)
##list(APPEND libexiv2_args -DGTEST_LIBRARY=$<TARGET_LINKER_FILE:googletest::googletest>)
#list(APPEND libexiv2_args -DGTEST_LIBRARY=$<TARGET_LINKER_FILE:gtest>)
#list(APPEND libexiv2_args -DGTEST_MAIN_LIBRARY=$<TARGET_LINKER_FILE:gtest_main>)
#list(APPEND libexiv2_args -DEXPAT_INCLUDE_DIR=$<TARGET_PROPERTY:libexpat::libexpat,INCLUDE_DIRECTORIES>)
##list(APPEND libexiv2_args -DGTEST_MAIN_LIBRARY=$<TARGET_LINKER_FILE:googletest::googletest_main>)
#list(APPEND libexiv2_args -DEXPAT_LIBRARY=$<TARGET_FILE:libexpat::libexpat>)
#list(APPEND libexiv2_args -DICONV_INCLUDE_DIR="")
#list(APPEND libexiv2_args -DICONV_LIBRARY="")
#list(APPEND libexiv2_depends gtest gtest_main)
##list(APPEND libexiv2_depends project_gtest)
#list(APPEND libexiv2_depends project_libexpat)

#set(exiv2_git_url https://github.com/Exiv2/exiv2.git)

#
#ExternalProject_Add(project_libexiv2
#        GIT_REPOSITORY ${exiv2_git_url}
#        GIT_TAG ${exiv2_git_tag}
#        CMAKE_ARGS ${libexiv2_args}
#        DEPENDS ${libexiv2_depends}
#        BUILD_BYPRODUCTS
#            <INSTALL_DIR>/lib/${CMAKE_STATIC_LIBRARY_PREFIX}exiv2${CMAKE_DEBUG_POSTFIX}${CMAKE_STATIC_LIBRARY_SUFFIX}
#            <INSTALL_DIR>/lib/${CMAKE_STATIC_LIBRARY_PREFIX}xmp${CMAKE_DEBUG_POSTFIX}${CMAKE_STATIC_LIBRARY_SUFFIX}
#        )
#ExternalProject_Add_Step(project_libexiv2 add_gtest_libs
#        COMMENT "Adding GoogleTest libraries to BUILD PATH"
#        COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:gtest> <BINARY_DIR>/bin/
#        DEPENDEES build
#        )
#ExternalProject_Add_Step(project_libexiv2 run_gtest
#        COMMENT "Running googletest"
#        COMMAND <BINARY_DIR>/bin/unit_tests${CMAKE_EXECUTABLE_SUFFIX}
#        WORKING_DIRECTORY <BINARY_DIR>/bin
#        ALWAYS 1
#        DEPENDEES add_gtest_libs
#        DEPENDERS install
#        )
#add_library(exiv2lib_ STATIC IMPORTED)

#ExternalProject_Get_Property(project_libexiv2 install_dir)
#
#set_target_properties(exiv2lib_ PROPERTIES
#        INCLUDE_DIRECTORIES ${install_dir}/include
#        IMPORTED_LOCATION_DEBUG ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}exiv2${CMAKE_DEBUG_POSTFIX}${CMAKE_STATIC_LIBRARY_SUFFIX}
#        IMPORTED_LOCATION_RELEASE ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}exiv2${CMAKE_STATIC_LIBRARY_SUFFIX}
#        INTERFACE_LINK_LIBRARIES "${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}xmp$<$<CONFIG:Debug>:${CMAKE_DEBUG_POSTFIX}>${CMAKE_STATIC_LIBRARY_SUFFIX};$<TARGET_FILE:libexpat::libexpat>"
#        CXX_STANDARD 11
#        )

#add_dependencies(exiv2lib_ project_libexiv2)
#add_library(exiv2lib ALIAS exiv2::exiv2)