include(ExternalProject)
ExternalProject_Add(project_libexpat
        URL https://github.com/libexpat/libexpat/archive/R_2_2_4.tar.gz
        SOURCE_SUBDIR expat
        CMAKE_ARGS
        -DBUILD_examples=off
        -DBUILD_shared=off
        -DBUILD_tests=ON
        -DBUILD_tools=off
        -DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>
        TEST_BEFORE_INSTALL 1
#        TEST_COMMAND=runtests${CMAKE_EXECUTABLE_SUFFIX}
        #        -DCMAKE_INSTALL_PREFIX=${CMAKE_BINARY_DIR}/thirdparty/expat
        )


ExternalProject_Get_Property(project_libexpat install_dir)
add_library(libexpat STATIC IMPORTED )

set_target_properties(libexpat PROPERTIES
        INCLUDE_DIRECTORIES ${install_dir}/include
        IMPORTED_LOCATION_DEBUG ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}expatd${CMAKE_STATIC_LIBRARY_SUFFIX}
        IMPORTED_LOCATION_RELEASE ${install_dir}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}expat${CMAKE_STATIC_LIBRARY_SUFFIX})
#get_target_property(ff libexpat LOCATION)
add_dependencies(libexpat project_libexpat)
#add_custom_target(dummy
#        COMMENT ""
#        )
#add_custom_target(dummy_expat)
#add_custom_command(TARGET dummy_expat
#        COMMAND ${CMAKE_COMMAND} -E echo $<TARGET_FILE:libexpat>
#        COMMAND ${CMAKE_COMMAND} -E echo $<TARGET_PROPERTY:libexpat,INCLUDE_DIRECTORIES>
#        )