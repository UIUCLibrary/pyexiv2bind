include(ExternalProject)
ExternalProject_Add(zlibsource
        URL https://zlib.net/zlib-1.2.11.tar.gz
        CMAKE_ARGS
            -DINSTALL_BIN_DIR=""
            -DINSTALL_LIB_DIR=<INSTALL_DIR>/lib
            -DINSTALL_INC_DIR=<INSTALL_DIR>/include
            -DINSTALL_MAN_DIR=<INSTALL_DIR>/man
            -DINSTALL_PKGCONFIG_DIR=<INSTALL_DIR>/share/pkgconfig

        )
ExternalProject_Get_Property(zlibsource install_dir)

add_library(zlib STATIC IMPORTED )
add_dependencies(zlib zlibsource)
set_target_properties(zlib PROPERTIES
        INCLUDE_DIRECTORIES ${install_dir}/include
        IMPORTED_LOCATION_DEBUG ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}zlibstaticd${CMAKE_STATIC_LIBRARY_SUFFIX}
        IMPORTED_LOCATION_RELEASE ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}zlibstatic{CMAKE_STATIC_LIBRARY_SUFFIX}
        )
#add_custom_target(dummy
#        COMMENT ""
#        DEPENDS zlib
#        )
#add_custom_command(TARGET dummy
#        COMMENT "adfasdfasdddddddddddddf $<TARGET_FILE:zlib>"
#        COMMAND ${CMAKE_COMMAND} -E echo $<TARGET_FILE:zlib>
#        COMMAND ${CMAKE_COMMAND} -E echo $<TARGET_PROPERTY:zlib,INCLUDE_DIRECTORIES>
#        )