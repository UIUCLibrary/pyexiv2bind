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
#        set_target_properties(zlib PROPERTIES EXCLUE_FROM_ALL YES)
#    get_target_property(is_all zlib TYPE)
#    message(WARNING "is_all =${is_all}")
endif ()


###########################################################################################
# libexpat build
###########################################################################################

FetchContent_Declare(expat
        URL https://github.com/libexpat/libexpat/archive/R_2_2_4.zip
        )

FetchContent_GetProperties(expat)
if (NOT expat_POPULATED)
    FetchContent_Populate(expat)
    option(BUILD_examples "" OFF)
    option(BUILD_shared "" OFF)
    option(BUILD_tests "" NO)
    option(BUILD_tools "" NO)

    add_subdirectory(${expat_SOURCE_DIR}/expat ${expat_BINARY_DIR})
endif ()


###########################################################################################
# Google test build
###########################################################################################
#
#FetchContent_Declare(
#        googletest
#        GIT_REPOSITORY https://github.com/google/googletest.git
#        GIT_TAG release-1.8.0
#)
#FetchContent_GetProperties(googletest)
#if (NOT googletest_POPULATED)
#    FetchContent_Populate(googletest)
#    option(BUILD_GTEST "" ON)
#    option(BUILD_GMOCK "" FALSE)
#    option(BUILD_SHARED_LIBS "" ON)
#    option(gtest_disable_pthreads "" TRUE)
#    option(gtest_force_shared_crt "" TRUE)
#    add_subdirectory(${googletest_SOURCE_DIR} ${googletest_BINARY_DIR})
#endif ()

FetchContent_Declare(
        libexiv2
        GIT_REPOSITORY https://github.com/Exiv2/exiv2.git
#        GIT_REPOSITORY https://github.com/UIUCLibrary/exiv2.git
        PATCH_COMMAND
            COMMAND git apply ${PROJECT_SOURCE_DIR}/patches/Make_Subproject_possible.patch
)
FetchContent_GetProperties(libexiv2)
if (NOT libexiv2_POPULATED)
    FetchContent_Populate(libexiv2)
    option(BUILD_SHARED_LIBS "" OFF)
#    set(BUILD_SHARED_LIBS OFF)
    option(EXIV2_BUILD_UNIT_TESTS "" OFF)
    option(EXIV2_ENABLE_DYNAMIC_RUNTIME "" ON)
    set(EXPAT_LIBRARY $<TARGET_FILE:expat>)
    set(EXPAT_INCLUDE_DIR $<TARGET_PROPERTY:expat,INCLUDE_DIRECTORIES>)
    set(ZLIB_INCLUDE_DIR $<TARGET_PROPERTY:zlibstatic,INCLUDE_DIRECTORIES>)
    set(ZLIB_LIBRARY $<TARGET_FILE:zlibstatic>)
    set(EXIV2_BUILD_SAMPLES OFF)
    option(EXIV2_BUILD_SAMPLES "" OFF)
#    set(GTEST_INCLUDE_DIR $<TARGET_PROPERTY:gtest,INCLUDE_DIRECTORIES>)
#    set(GTEST_LIBRARY $<TARGET_LINKER_FILE:gtest>)
#    set(GTEST_LIBRARY_DEBUG $<TARGET_LINKER_FILE:gtest>)
#    set(GTEST_MAIN_LIBRARY $<TARGET_LINKER_FILE:gtest_main>)
#    set(GTEST_MAIN_LIBRARY_DEBUG $<TARGET_LINKER_FILE:gtest_main>)
    add_subdirectory(${libexiv2_SOURCE_DIR} ${libexiv2_BINARY_DIR})
    include_directories(${libexiv2_BINARY_DIR})
    add_dependencies(exiv2lib zlibstatic)
#    add_dependencies(unit_tests gtest gtest_main)
endif ()
add_dependencies(xmp expat)

