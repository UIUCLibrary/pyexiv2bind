# This is a simple script to test the state of the latest version of Exiv2 to
# see if can be fully built for the purposes of creating bindings for this
# project.

include(FetchContent)
include(ProcessorCount)

set(CTEST_PROJECT_NAME superbuild)
set(CTEST_SOURCE_DIRECTORY .)
set(CTEST_BINARY_DIRECTORY build)
set(CTEST_CONFIGURATION_TYPE Debug)
set(CTEST_CMAKE_GENERATOR "Visual Studio 15 2017 Win64")
#set(CTEST_CMAKE_GENERATOR "Unix Makefiles")

ProcessorCount(N)
if(NOT N EQUAL 0)
    if(CTEST_CMAKE_GENERATOR MATCHES "Visual Studio")
        set(CTEST_BUILD_FLAGS /maxcpucount:${N})
    elseif(CTEST_CMAKE_GENERATOR MATCHES "Makefile")
        set(CTEST_BUILD_FLAGS -j${N})
    endif()

endif()

ctest_start(Experimental)
# ####################################################
# Google Test 
# ####################################################

FetchContent_Populate(gtest
    URL             https://github.com/google/googletest/archive/release-1.8.0.tar.gz
    URL_HASH        SHA256=58a6f4277ca2bc8565222b3bbd58a177609e9c488e8a72649359ba51450db7d8
    BINARY_DIR      ${CTEST_BINARY_DIRECTORY}/gtest-build
    SUBBUILD_DIR    ${CTEST_BINARY_DIRECTORY}/gtest-subbuild
    SOURCE_DIR      deps/gtest-source
)

list(APPEND GTEST_OPTIONS "-DBUILD_GTEST:BOOL=ON")
list(APPEND GTEST_OPTIONS "-DBUILD_GMOCK:BOOL=OFF")
list(APPEND GTEST_OPTIONS "-DBUILD_SHARED_LIBS:BOOL=ON")
list(APPEND GTEST_OPTIONS "-Dgtest_disable_pthreads:BOOL=ON")
list(APPEND GTEST_OPTIONS "-Dgtest_force_shared_crt:BOOL=ON")
list(APPEND GTEST_OPTIONS "-DCMAKE_INSTALL_PREFIX=./installed")

if (CTEST_CMAKE_GENERATOR STREQUAL "Visual Studio 15 2017 Win64")
    list(APPEND GTEST_OPTIONS "-DCMAKE_CXX_FLAGS=/D_SILENCE_TR1_NAMESPACE_DEPRECATION_WARNING")
endif()




# list(APPEND GTEST_OPTIONS "-DCMAKE_CXX_FLAGS=_CRT_SECURE_NO_WARNINGS")
# 

ctest_configure(
    BUILD ${gtest_BINARY_DIR} 
    SOURCE ${gtest_SOURCE_DIR}
    OPTIONS "${GTEST_OPTIONS}"
)

ctest_build(
    PROJECT_NAME gtest
    BUILD ${gtest_BINARY_DIR}
    TARGET install
    )


find_library(GTEST_MAIN_LIBRARY 
    NAMES 
        gtest_main 
    HINTS ${gtest_BINARY_DIR}/installed/lib
)

find_library(GTEST_LIBRARY 
    NAMES 
        gtest 
    HINTS ${gtest_BINARY_DIR}/installed/lib
)
find_path(GTEST_INCLUDE_DIR 
    NAMES gtest/gtest.h 
    PATHS ${gtest_BINARY_DIR}/installed/include
    # PATH_SUFFIXES gtest
)
# TODO: find thise files instead of hard coding them
#find_library(GTEST)
if(WIN32)
    find_file(GTEST_DLL
            NAMES gtest.dll
            PATHS ${gtest_BINARY_DIR}/installed/lib
            NO_DEFAULT_PATH
            )
    find_file(GTEST_MAIN_DLL
            NAMES gtest_main.dll
            PATHS ${gtest_BINARY_DIR}/installed/lib
            NO_DEFAULT_PATH
            )
#    set(GTEST_MAIN_DLL ${gtest_BINARY_DIR}/installed/lib/gtest_main.dll)
endif()
# find_package(GTest)
# message(FATAL_ERROR "GTEST_INCLUDE_DIR = ${GTEST_INCLUDE_DIR}")

# ####################################################
# ZLIB
# ####################################################

FetchContent_Populate(zlib
    URL             https://zlib.net/zlib-1.2.11.tar.gz
    URL_HASH        SHA256=c3e5e9fdd5004dcb542feda5ee4f0ff0744628baf8ed2dd5d66f8ca1197cb1a1
    SOURCE_DIR      deps/zlib-source
    BINARY_DIR      ${CTEST_BINARY_DIRECTORY}/zlib-build
    SUBBUILD_DIR    ${CTEST_BINARY_DIRECTORY}/zlib-subbuild

        )

list(APPEND zlib_OPTIONS "-DCMAKE_INSTALL_PREFIX=${zlib_BINARY_DIR}/installed")
ctest_configure(
    BUILD ${zlib_BINARY_DIR} 
    SOURCE ${zlib_SOURCE_DIR}
    OPTIONS "${zlib_OPTIONS}"
    )

ctest_build(
    BUILD ${zlib_BINARY_DIR}
    PROJECT_NAME zlib
    TARGET install
    )


find_library(ZLIB_LIBRARY 
    NAMES 
        zlibstatic 
        zlibstaticd
        zlib.a
    HINTS ${zlib_BINARY_DIR}/installed/lib
    NO_DEFAULT_PATH
    )

find_path(ZLIB_INCLUDE 
    NAMES zlib.h 
    PATHS ${zlib_BINARY_DIR}/installed/include
    )
# message(STATUS "ZLIB_LIBRARY = ${ZLIB_LIBRARY}")
if(NOT ZLIB_LIBRARY)
    message(FATAL_ERROR "ZLIB_LIBRARY not found")
endif()

# ####################################################
# EXPAT
# ####################################################

FetchContent_Populate(expat
    URL             https://github.com/libexpat/libexpat/archive/R_2_2_4.zip
    URL_HASH        SHA256=4e73aaacb035afea64f1d0a11ad017aff15e6ec04feabc45241f1f5d30771b80
    SOURCE_DIR      deps/expat-source
    BINARY_DIR      ${CTEST_BINARY_DIRECTORY}/expat-build
    SUBBUILD_DIR    ${CTEST_BINARY_DIRECTORY}/expat-subbuild
)

list(APPEND EXPAT_OPTIONS "-DBUILD_examples:BOOL=OFF")
list(APPEND EXPAT_OPTIONS "-DBUILD_tests:BOOL=OFF")
list(APPEND EXPAT_OPTIONS "-DBUILD_shared:BOOL=OFF")
list(APPEND EXPAT_OPTIONS "-DBUILD_tools:BOOL=OFF")
list(APPEND EXPAT_OPTIONS "-DCMAKE_INSTALL_PREFIX=./installed")

ctest_configure(
    BUILD ${expat_BINARY_DIR} 
    SOURCE ${expat_SOURCE_DIR}/expat
    OPTIONS "${EXPAT_OPTIONS}"
    )

ctest_build(
    BUILD ${expat_BINARY_DIR}
    TARGET install
    PROJECT_NAME expat
    )

find_library(EXPAT_LIBRARY
    NAMES 
        expat 
        expatd
    HINTS ${expat_BINARY_DIR}/installed/lib
    )
find_path(EXPAT_INCLUDE 
    NAMES expat.h
    PATHS ${expat_BINARY_DIR}/installed/include
    )



# ####################################################
# Exiv2 
# ####################################################
find_file(SUBPROJECT_PATCH
    NAMES Make_Subproject_possible.patch
    HINTS ${CTEST_SOURCE_DIRECTORY}/patches
    )
message(WARNING "Using ${SUBPROJECT_PATCH}")

FetchContent_Populate(exiv2
    GIT_REPOSITORY  https://github.com/Exiv2/exiv2.git
    SOURCE_DIR      deps/exiv2-source
    BINARY_DIR      ${CTEST_BINARY_DIRECTORY}/exiv2-build
    SUBBUILD_DIR    ${CTEST_BINARY_DIRECTORY}/exiv2-subbuild
    PATCH_COMMAND   git apply ${SUBPROJECT_PATCH}
)

list(APPEND EXIV2_OPTIONS "-DZLIB_INCLUDE_DIR=${ZLIB_INCLUDE}")
list(APPEND EXIV2_OPTIONS "-DZLIB_LIBRARY=${ZLIB_LIBRARY}")
list(APPEND EXIV2_OPTIONS "-DBUILD_SHARED_LIBS:BOOL=OFF")
list(APPEND EXIV2_OPTIONS "-DEXIV2_ENABLE_DYNAMIC_RUNTIME:BOOL=ON")
list(APPEND EXIV2_OPTIONS "-DEXPAT_LIBRARY=${EXPAT_LIBRARY}")
list(APPEND EXIV2_OPTIONS "-DEXPAT_INCLUDE_DIR=${EXPAT_INCLUDE}")
list(APPEND EXIV2_OPTIONS "-DCMAKE_INSTALL_PREFIX=installed")
list(APPEND EXIV2_OPTIONS "-DGTEST_MAIN_LIBRARY=${GTEST_MAIN_LIBRARY}")
list(APPEND EXIV2_OPTIONS "-DGTEST_LIBRARY=${GTEST_LIBRARY}")
list(APPEND EXIV2_OPTIONS "-DGTEST_INCLUDE_DIR=${GTEST_INCLUDE_DIR}")
list(APPEND EXIV2_OPTIONS "-DEXIV2_BUILD_UNIT_TESTS:BOOL=ON")



ctest_configure(
    BUILD ${exiv2_BINARY_DIR} 
    SOURCE ${exiv2_SOURCE_DIR}
    OPTIONS "${EXIV2_OPTIONS}"
    
    )

ctest_build(
    PROJECT_NAME exiv2
    BUILD ${exiv2_BINARY_DIR} 
    )

if (WIN32)
    file(COPY ${GTEST_DLL} ${GTEST_MAIN_DLL} DESTINATION "${exiv2_BINARY_DIR}/bin")
endif ()

find_program(UNIT_TESTS
        NAMES unit_tests
        PATHS ${exiv2_BINARY_DIR}/bin
        NO_DEFAULT_PATH)

execute_process(
        COMMAND ${UNIT_TESTS}
        RESULT_VARIABLE return_code
        WORKING_DIRECTORY ${exiv2_BINARY_DIR}/bin
)

message(STATUS "return_code = ${return_code}")
