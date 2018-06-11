include(FetchContent)
include(ExternalProject)

set(EXIV2_VERSION_TAG "" CACHE STRING "Git tag of version of exiv2 to build")

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
    set(SKIP_INSTALL_LIBRARIES YES CACHE BOOL "")
    add_subdirectory(${zlib_SOURCE_DIR} ${zlib_BINARY_DIR})
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
    option(INSTALL "" NO)

    add_subdirectory(${expat_SOURCE_DIR}/expat ${expat_BINARY_DIR})
endif ()

if(EXIV2_VERSION_TAG)
    FetchContent_Declare(
            libexiv2
            GIT_REPOSITORY https://github.com/Exiv2/exiv2.git
            GIT_TAG ${EXIV2_VERSION_TAG}
            PATCH_COMMAND
                COMMAND git apply ${PROJECT_SOURCE_DIR}/patches/Make_Subproject_possible.patch
    )
else()
    message(STATUS "Checking out HEAD from exiv2 source")
    FetchContent_Declare(
            libexiv2
            GIT_REPOSITORY https://github.com/Exiv2/exiv2.git
            PATCH_COMMAND
                COMMAND git apply ${PROJECT_SOURCE_DIR}/patches/Make_Subproject_possible.patch
    )
endif()

FetchContent_GetProperties(libexiv2)
if (NOT libexiv2_POPULATED)
    FetchContent_Populate(libexiv2)
    option(BUILD_SHARED_LIBS "" OFF)
    set(BUILD_SHARED_LIBS OFF CACHE BOOL "")
    set(EXIV2_BUILD_SAMPLES OFF CACHE BOOL "")
    option(EXIV2_BUILD_UNIT_TESTS "" OFF)
    option(EXIV2_ENABLE_DYNAMIC_RUNTIME "" ON)
    set(EXPAT_LIBRARY $<TARGET_FILE:expat>)
    set(EXPAT_INCLUDE_DIR $<TARGET_PROPERTY:expat,INCLUDE_DIRECTORIES>)
    set(ZLIB_INCLUDE_DIR $<TARGET_PROPERTY:zlibstatic,INCLUDE_DIRECTORIES>)
    set(ZLIB_LIBRARY $<TARGET_FILE:zlibstatic>)
    set(EXIV2_BUILD_SAMPLES OFF)
    option(EXIV2_BUILD_SAMPLES "" OFF)
    add_subdirectory(${libexiv2_SOURCE_DIR} ${libexiv2_BINARY_DIR})
    include_directories(${libexiv2_BINARY_DIR})
    add_dependencies(exiv2lib zlibstatic)
endif ()
add_dependencies(xmp expat)

