include(FetchContent)
include(ExternalProject)

set(EXIV2_VERSION_TAG "" CACHE STRING "Git tag of version of exiv2 to build")

function(patch_tiff_resolution root)
    list(APPEND LINES_TO_BE_REMOVED "{ 0x011a, ifd0Id }, // Exif.Image.XResolution")
    list(APPEND LINES_TO_BE_REMOVED "{ 0x011b, ifd0Id }, // Exif.Image.YResolution")
    list(APPEND LINES_TO_BE_REMOVED "{ 0x0128, ifd0Id }, // Exif.Image.ResolutionUnit")

    find_file(
        tiffimage_int
        NAMES
            tiffimage_int.cpp
        PATHS
            ${root}/src
        NO_DEFAULT_PATH
        NO_CMAKE_PATH
    )
    file(READ "${tiffimage_int}" data)
    foreach(line ${LINES_TO_BE_REMOVED})
        string(REPLACE "${line}" "" data "${data}")
    endforeach()
    file(WRITE  "${libexiv2_BINARY_DIR}/tiffimage_int.cpp" "${data}")
    execute_process(COMMAND ${CMAKE_COMMAND} -E copy_if_different "${libexiv2_BINARY_DIR}/tiffimage_int.cpp" "${tiffimage_int}")
endfunction()

###########################################################################################
# Google ZLIB
###########################################################################################

FetchContent_Declare(zlib
        URL https://zlib.net/zlib-1.2.11.tar.gz
        URL_HASH SHA256=c3e5e9fdd5004dcb542feda5ee4f0ff0744628baf8ed2dd5d66f8ca1197cb1a1
        PATCH_COMMAND ${CMAKE_COMMAND} -P ${PROJECT_BINARY_DIR}/patch_zlib.cmake
        )
FetchContent_GetProperties(zlib)
configure_file(${PROJECT_SOURCE_DIR}/patches/patch_zlib.cmake patch_zlib.cmake @ONLY)

if (NOT zlib_POPULATED)
    FetchContent_Populate(zlib)
    set(SKIP_INSTALL_LIBRARIES YES CACHE BOOL "")
    set(BUILD_examples NO CACHE BOOL "")
#
    add_subdirectory(${zlib_SOURCE_DIR} ${zlib_BINARY_DIR} EXCLUDE_FROM_ALL)
    get_directory_property(zlib_targets DIRECTORY ${zlib_SOURCE_DIR} BUILDSYSTEM_TARGETS )
    foreach(target ${zlib_targets})
        if(${target} STREQUAL example)
            message(FATAL_ERROR "ZLib imported the \"${target}\" Target.")
        endif()
    endforeach()
#    set_tests_properties(example PROPERTIES DISABLED ON)
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
#    option(INSTALL "" NO)

    add_subdirectory(${expat_SOURCE_DIR}/expat ${expat_BINARY_DIR})
endif ()
FetchContent_Declare(
        libexiv2
        URL https://github.com/Exiv2/exiv2/archive/0.27.tar.gz
#            GIT_REPOSITORY https://github.com/Exiv2/exiv2.git
#            GIT_TAG ${EXIV2_VERSION_TAG}
#        PATCH_COMMAND
#            COMMAND git apply ${PROJECT_SOURCE_DIR}/patches/tiff_resolution_path.patch
)
#if(EXIV2_VERSION_TAG)
#
#else()
#    message(STATUS "Using version 0.27")
#    FetchContent_Declare(
#            libexiv2
#            GIT_REPOSITORY https://github.com/Exiv2/exiv2.git
#            GIT_TAG "0.27"
#            PATCH_COMMAND
#                COMMAND git apply ${PROJECT_SOURCE_DIR}/patches/tiff_resolution_path.patch
#    )
#endif()

FetchContent_GetProperties(libexiv2)
if (NOT libexiv2_POPULATED)
    FetchContent_Populate(libexiv2)
    patch_tiff_resolution("${libexiv2_SOURCE_DIR}")

    option(BUILD_SHARED_LIBS "" OFF)
    set(BUILD_SHARED_LIBS OFF CACHE BOOL "")
    set(EXIV2_BUILD_SAMPLES OFF CACHE BOOL "")
    option(EXIV2_BUILD_UNIT_TESTS "" OFF)

    if(MSVC)
        option(EXIV2_ENABLE_DYNAMIC_RUNTIME "" ON)
    endif()

    set(EXPAT_LIBRARY $<TARGET_FILE:expat>)
    set(EXPAT_INCLUDE_DIR $<TARGET_PROPERTY:expat,INCLUDE_DIRECTORIES>)
    set(ZLIB_INCLUDE_DIR $<TARGET_PROPERTY:zlibstatic,INCLUDE_DIRECTORIES>)
    set(ZLIB_LIBRARY $<TARGET_FILE:zlibstatic>)
    set(EXIV2_BUILD_SAMPLES OFF)
    option(EXIV2_BUILD_SAMPLES "" OFF)
    include_directories(${libexiv2_BINARY_DIR})
    add_subdirectory(${libexiv2_SOURCE_DIR} ${libexiv2_BINARY_DIR} EXCLUDE_FROM_ALL)
#    target_include_directories(exiv2lib PRIVATE ${libexiv2_BINARY_DIR})
#    include_directories(${libexiv2_BINARY_DIR})
    add_dependencies(exiv2lib zlibstatic)
endif ()
add_dependencies(exiv2lib expat)
install(DIRECTORY ${libexiv2_SOURCE_DIR}/include/ DESTINATION include)

