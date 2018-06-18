include(FetchContent)
if (BUILD_TESTING)
    set(PYTHON_TEST_FILES test_core.py)
    find_package(PythonInterp 3 REQUIRED)
    add_custom_target(add_python_tests
            COMMENT "Adding Python test"
            DEPENDS core exiv2
            )
    add_dependencies(add_python_tests core)
    add_custom_command(TARGET add_python_tests
            COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/conftest.py ${CMAKE_CURRENT_BINARY_DIR}
            COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/test_core.py ${CMAKE_CURRENT_BINARY_DIR}
#            COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/test_common.py ${CMAKE_CURRENT_BINARY_DIR}
            COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/test_image.py ${CMAKE_CURRENT_BINARY_DIR}
            )


    add_library(Catch INTERFACE)
    target_include_directories(Catch INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/catch/include)
    add_executable(cpp_tests
            test_basic.cpp
            tests-main.cpp
            $<TARGET_OBJECTS:glue>
#            test_metadata_processor.cpp
            )

    set_target_properties(cpp_tests PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
            RUNTIME_OUTPUT_NAME test
            CXX_STANDARD 11
            )
        target_include_directories(cpp_tests PRIVATE ${PROJECT_SOURCE_DIR}/py3exiv2bind/core)
    target_link_libraries(cpp_tests PRIVATE Catch exiv2lib)
#    target_link_libraries(cpp_tests PRIVATE Catch glue)

    add_test(NAME cpp_tests
            COMMAND $<TARGET_FILE:cpp_tests>
            WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
            )
    FetchContent_Declare(test_images
            URL https://jenkins.library.illinois.edu/userContent/sample_images.tar.gz
            SOURCE_DIR ${CMAKE_CURRENT_BINARY_DIR}/sample_images
            )
    FetchContent_GetProperties(test_images)
    if (NOT test_images_POPULATED)
        FetchContent_Populate(test_images)
    endif()
endif ()