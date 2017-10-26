include(ExternalProject)
if(pyexiv2bind_png)
    ExternalProject_Add(project_zlib
            URL https://zlib.net/zlib-1.2.11.tar.gz
            URL_HASH SHA256=c3e5e9fdd5004dcb542feda5ee4f0ff0744628baf8ed2dd5d66f8ca1197cb1a1
            CMAKE_ARGS
                -DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>
                -DCMAKE_BUILD_TYPE=Release

            BUILD_BYPRODUCTS
                <INSTALL_DIR>/lib/zlib${CMAKE_STATIC_LIBRARY_SUFFIX}
                <INSTALL_DIR>/lib/zlibstatic${CMAKE_STATIC_LIBRARY_SUFFIX}
                <INSTALL_DIR>/bin/zlibs${CMAKE_SHARED_LIBRARY_SUFFIX}
            )
    ExternalProject_Get_Property(project_zlib install_dir)
    add_library(zlib::zlib STATIC IMPORTED)
    add_dependencies(zlib::zlib project_zlib)
    set_target_properties(zlib::zlib PROPERTIES
            INCLUDE_DIRECTORIES ${install_dir}/include
            IMPORTED_LOCATION_RELEASE ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}zlibstatic${CMAKE_STATIC_LIBRARY_SUFFIX}
            )
endif()


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

list(APPEND google_test_args -DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>)
list(APPEND google_test_args -DBUILD_GMOCK=OFF)
list(APPEND google_test_args -DBUILD_GTEST=ON)

list(APPEND google_test_args -DCMAKE_BUILD_TYPE=$<CONFIG>)

if(MSVC)
    list(APPEND google_test_args -DBUILD_SHARED_LIBS=ON)
    list(APPEND google_test_byproducts <INSTALL_DIR>/lib/gtest${CMAKE_SHARED_LIBRARY_SUFFIX})
    list(APPEND google_test_byproducts <INSTALL_DIR>/lib/gtest${CMAKE_LINK_LIBRARY_SUFFIX})
    list(APPEND google_test_byproducts <INSTALL_DIR>/lib/gtest_main${CMAKE_SHARED_LIBRARY_SUFFIX})
    list(APPEND google_test_byproducts <INSTALL_DIR>/lib/gtest_main${CMAKE_LINK_LIBRARY_SUFFIX})
    add_library(googletest::googletest SHARED IMPORTED)
    add_library(googletest::googletest_main SHARED IMPORTED)
else()
    add_library(googletest::googletest STATIC IMPORTED)
    add_library(googletest::googletest_main STATIC IMPORTED)
    list(APPEND google_test_args -DBUILD_SHARED_LIBS=OFF)
    list(APPEND google_test_byproducts <INSTALL_DIR>/lib/${CMAKE_STATIC_LIBRARY_PREFIX}gtest${CMAKE_STATIC_LIBRARY_SUFFIX})
    list(APPEND google_test_byproducts <INSTALL_DIR>/lib/${CMAKE_STATIC_LIBRARY_PREFIX}gtest_main${CMAKE_STATIC_LIBRARY_SUFFIX})
endif()


ExternalProject_Add(project_gtest
        URL https://github.com/google/googletest/archive/release-1.8.0.tar.gz
        CMAKE_ARGS ${google_test_args}
        #        -Dgtest_force_shared_crt=ON
        BUILD_BYPRODUCTS ${google_test_byproducts}
        )

ExternalProject_Get_Property(project_gtest install_dir)
if(MSVC)
    set_target_properties(googletest::googletest PROPERTIES
            INCLUDE_DIRECTORIES ${install_dir}/include
            IMPORTED_IMPLIB ${install_dir}/lib/gtest${CMAKE_IMPORT_LIBRARY_SUFFIX}
            IMPORTED_LOCATION ${install_dir}/lib/gtest${CMAKE_SHARED_LIBRARY_SUFFIX}
            )
    set_target_properties(googletest::googletest_main PROPERTIES
            INCLUDE_DIRECTORIES ${install_dir}/include
            IMPORTED_IMPLIB ${install_dir}/lib/gtest_main${CMAKE_IMPORT_LIBRARY_SUFFIX}
            IMPORTED_LOCATION ${install_dir}/lib/gtest_main${CMAKE_SHARED_LIBRARY_SUFFIX}
            )
else()
    set_target_properties(googletest::googletest PROPERTIES
            INCLUDE_DIRECTORIES ${install_dir}/include
            IMPORTED_LOCATION ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}gtest${CMAKE_STATIC_LIBRARY_SUFFIX}
            )
    set_target_properties(googletest::googletest_main PROPERTIES
            INCLUDE_DIRECTORIES ${install_dir}/include
            IMPORTED_LOCATION ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}gtest_main${CMAKE_STATIC_LIBRARY_SUFFIX}
            )
endif()
set(googletest_root ${install_dir})
add_dependencies(googletest::googletest project_gtest)

#########################################################################################
if(pyexiv2bind_png)
    list(APPEND libexiv2_args -DEXIV2_ENABLE_PNG:BOOL=ON)
    list(APPEND libexiv2_args -DZLIB_LIBRARY=$<TARGET_FILE:zlib::zlib>)
    list(APPEND libexiv2_args -DZLIB_INCLUDE_DIR=$<TARGET_PROPERTY:zlib::zlib,INCLUDE_DIRECTORIES>)
    list(APPEND libexiv2_depends project_zlib)
else()
    list(APPEND libexiv2_args -DEXIV2_ENABLE_PNG:BOOL=OFF)
endif()
if(WIN32)
    list(APPEND libexiv2_args -DEXIV2_ENABLE_WIN_UNICODE:BOOL=ON)
endif()
list(APPEND libexiv2_args -DCMAKE_BUILD_TYPE=$<CONFIG>)
list(APPEND libexiv2_args -DEXIV2_BUILD_EXIV2_COMMAND:BOOL=ON)
list(APPEND libexiv2_args -DEXIV2_ENABLE_DYNAMIC_RUNTIME=ON)
list(APPEND libexiv2_args -DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>)
list(APPEND libexiv2_args -DBUILD_SHARED_LIBS:BOOL=OFF)
list(APPEND libexiv2_args -DEXIV2_BUILD_SAMPLES:BOOL=OFF)
list(APPEND libexiv2_args -DEXIV2_ENABLE_XMP:BOOL=ON)
list(APPEND libexiv2_args -DEXIV2_BUILD_UNIT_TESTS=ON)
list(APPEND libexiv2_args -DGTEST_ROOT="${googletest_root}")
list(APPEND libexiv2_args -DGTEST_INCLUDE_DIR=$<TARGET_PROPERTY:googletest::googletest,INCLUDE_DIRECTORIES>)
list(APPEND libexiv2_args -DGTEST_LIBRARY=$<TARGET_LINKER_FILE:googletest::googletest>)
list(APPEND libexiv2_args -DEXPAT_INCLUDE_DIR=$<TARGET_PROPERTY:libexpat::libexpat,INCLUDE_DIRECTORIES>)
list(APPEND libexiv2_args -DGTEST_MAIN_LIBRARY=$<TARGET_LINKER_FILE:googletest::googletest_main>)
list(APPEND libexiv2_args -DEXPAT_LIBRARY=$<TARGET_FILE:libexpat::libexpat>)
list(APPEND libexiv2_args -DICONV_INCLUDE_DIR="")
list(APPEND libexiv2_args -DICONV_LIBRARY="")
list(APPEND libexiv2_depends project_gtest)
list(APPEND libexiv2_depends project_libexpat)


ExternalProject_Add(project_libexiv2
        GIT_REPOSITORY https://github.com/Exiv2/exiv2.git

        CMAKE_ARGS ${libexiv2_args}
        DEPENDS ${libexiv2_depends}
        BUILD_BYPRODUCTS
            <INSTALL_DIR>/lib/${CMAKE_STATIC_LIBRARY_PREFIX}exiv2${CMAKE_DEBUG_POSTFIX}${CMAKE_STATIC_LIBRARY_SUFFIX}
            <INSTALL_DIR>/lib/${CMAKE_STATIC_LIBRARY_PREFIX}xmp${CMAKE_DEBUG_POSTFIX}${CMAKE_STATIC_LIBRARY_SUFFIX}
        )
ExternalProject_Add_Step(project_libexiv2 add_gtest_libs
        COMMENT "Adding GoogleTest libraries to BUILD PATH"
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${googletest_root}/lib/ <BINARY_DIR>/bin/
        DEPENDEES build
        )
ExternalProject_Add_Step(project_libexiv2 run_gtest
        COMMENT "Running googletest"
        COMMAND ./unit_tests${CMAKE_EXECUTABLE_SUFFIX}
        WORKING_DIRECTORY <BINARY_DIR>/bin
        ALWAYS 1
        DEPENDEES add_gtest_libs
        DEPENDERS install
        )
add_library(exiv2lib STATIC IMPORTED)

ExternalProject_Get_Property(project_libexiv2 install_dir)

set_target_properties(exiv2lib PROPERTIES
        INCLUDE_DIRECTORIES ${install_dir}/include
        IMPORTED_LOCATION_DEBUG ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}exiv2${CMAKE_DEBUG_POSTFIX}${CMAKE_STATIC_LIBRARY_SUFFIX}
        IMPORTED_LOCATION_RELEASE ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}exiv2${CMAKE_STATIC_LIBRARY_SUFFIX}
        INTERFACE_LINK_LIBRARIES "${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}xmp$<$<CONFIG:Debug>:${CMAKE_DEBUG_POSTFIX}>${CMAKE_STATIC_LIBRARY_SUFFIX};$<TARGET_FILE:libexpat::libexpat>"
        CXX_STANDARD 98
        )

add_dependencies(exiv2lib project_libexiv2)
#add_library(exiv2lib ALIAS exiv2::exiv2)