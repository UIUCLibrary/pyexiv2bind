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
    list(APPEND LINES_TO_BE_REMOVED "case 0x011a:  // Exif.Image.XResolution")
    list(APPEND LINES_TO_BE_REMOVED "case 0x011b:  // Exif.Image.YResolution")
    list(APPEND LINES_TO_BE_REMOVED "case 0x0128:  // Exif.Image.ResolutionUnit")

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
        message(STATUS "Removing line \"${line}\" from tiffimage_int.cpp")
    endforeach()
    file(WRITE  "${libexiv2_BINARY_DIR}/tiffimage_int.cpp" "${data}")
    message(STATUS "Modified the following source file to allow editing of Exif.Image.XResolution, Exif.Image.YResolution, and Exif.Image.ResolutionUnit:  ${tiffimage_int}")
    execute_process(COMMAND ${CMAKE_COMMAND} -E copy_if_different "${libexiv2_BINARY_DIR}/tiffimage_int.cpp" "${tiffimage_int}")
endfunction()

FetchContent_Declare(
        libexiv2
#        URL https://github.com/Exiv2/exiv2/archive/refs/tags/v0.28.1.tar.gz
#        URL_HASH SHA256=3078651f995cb6313b1041f07f4dd1bf0e9e4d394d6e2adc6e92ad0b621291fa
            GIT_REPOSITORY https://github.com/Exiv2/exiv2.git
            GIT_TAG v0.28.1
        #            GIT_REPOSITORY https://github.com/Exiv2/exiv2.git
#            GIT_TAG ${EXIV2_VERSION_TAG}
        PATCH_COMMAND
            COMMAND git cherry-pick 71bb2b193aad369c4d6ed9cab813c2042f626afe --no-commit
#            COMMAND git apply ${PROJECT_SOURCE_DIR}/patches/tiff_resolution_path.patch
)

FetchContent_GetProperties(libexiv2)
if (NOT libexiv2_POPULATED)
    option(EXIV2_ENABLE_INIH "" OFF)
    option(EXIV2_BUILD_EXIV2_COMMAND "" OFF)
    set(CMAKE_SKIP_TEST_ALL_DEPENDENCY OFF CACHE BOOL "")
    set(EXIV2_BUILD_EXIV2_COMMAND OFF CACHE BOOL "")
    set(EXIV2_BUILD_SAMPLES OFF CACHE BOOL "")
    option(EXIV2_BUILD_SAMPLES "" OFF)
    if(MSVC)
        option(EXIV2_ENABLE_DYNAMIC_RUNTIME "" ON)
    endif()
    FetchContent_MakeAvailable(libexiv2)

    patch_tiff_resolution("${libexiv2_SOURCE_DIR}")
    patch_exiv2_cmake("${libexiv2_SOURCE_DIR}")
    list(APPEND CMAKE_MODULE_PATH "${libexiv2_SOURCE_DIR}/cmake")
    include_directories(${libexiv2_BINARY_DIR})
endif ()
