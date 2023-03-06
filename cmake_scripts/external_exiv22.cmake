include(FetchContent)
include(ExternalProject)

set(EXIV2_VERSION_TAG "" CACHE STRING "Git tag of version of exiv2 to build")

function(patch_exiv2_cmake root)
#    Removes the need to install exiv2.pc even especially important when it's not needed
    find_file(exiv_cmakefile
            NAMES "CMakeLists.txt"
            PATHS ${root}
            NO_DEFAULT_PATH
            NO_CMAKE_PATH
            )
    file(READ "${exiv_cmakefile}" data)
    set(line_to_remove "install(FILES \${CMAKE_BINARY_DIR}/exiv2.pc DESTINATION \${CMAKE_INSTALL_LIBDIR}/pkgconfig)")
    string(REPLACE "${line_to_remove}" "" data "${data}")

    file(WRITE  "${PROJECT_BINARY_DIR}/temp_cmake.txt" "${data}")
    execute_process(COMMAND ${CMAKE_COMMAND} -E copy_if_different "${PROJECT_BINARY_DIR}/temp_cmake.txt" "${exiv_cmakefile}")

endfunction()

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

FetchContent_Declare(
        libexiv2
        URL https://github.com/Exiv2/exiv2/archive/refs/tags/v0.27.6.tar.gz
#            GIT_REPOSITORY https://github.com/Exiv2/exiv2.git
#            GIT_TAG ${EXIV2_VERSION_TAG}
#        PATCH_COMMAND
#            COMMAND git apply ${PROJECT_SOURCE_DIR}/patches/tiff_resolution_path.patch
)

FetchContent_GetProperties(libexiv2)
if (NOT libexiv2_POPULATED)
    FetchContent_Populate(libexiv2)
    patch_tiff_resolution("${libexiv2_SOURCE_DIR}")
    patch_exiv2_cmake("${libexiv2_SOURCE_DIR}")
    set(EXIV2_BUILD_SAMPLES OFF CACHE BOOL "")
    option(EXIV2_BUILD_SAMPLES "" OFF)
    if(MSVC)
        option(EXIV2_ENABLE_DYNAMIC_RUNTIME "" ON)
    endif()

    include_directories(${libexiv2_BINARY_DIR})
    add_subdirectory(${libexiv2_SOURCE_DIR} ${libexiv2_BINARY_DIR})
endif ()

