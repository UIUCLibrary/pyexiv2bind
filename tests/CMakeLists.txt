set(PYTHON_TEST_FILES python_tests/test_core.py)
find_package(PythonInterp 3 REQUIRED)
add_custom_target(add_python_tests
        COMMENT "Adding Python test"
        DEPENDS core project_libexiv2
        )
add_dependencies(add_python_tests core add_test_images)
add_custom_command(TARGET add_python_tests
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/python_tests/test_core.py ${CMAKE_CURRENT_BINARY_DIR}
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/python_tests/test_common.py ${CMAKE_CURRENT_BINARY_DIR}
        )

add_test(NAME python_tests
        COMMAND ${PYTHON_EXECUTABLE} -m tox
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        )

add_library(Catch INTERFACE)
target_include_directories(Catch INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/catch/include)
add_executable(cpp_tests test_basic.cpp tests-main.cpp)
add_dependencies(cpp_tests add_test_images)
set_target_properties(cpp_tests PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
        RUNTIME_OUTPUT_NAME test
        )
target_link_libraries(cpp_tests Catch glue)

add_test(NAME cpp_tests
        COMMAND test
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        )
add_custom_target(add_tests
        COMMENT "Adding tests to ${CMAKE_BINARY_DIR}"
        DEPENDS add_python_tests cpp_tests
        )
include(ExternalProject)
ExternalProject_Add(add_test_images
        #        URL https://github.com/henryborchers/exiv2/archive/v0.26_deps.tar.gz
        URL https://jenkins.library.illinois.edu/jenkins/userContent/sample_images.tar.gz
        CONFIGURE_COMMAND ""
        BUILD_COMMAND ""
        INSTALL_COMMAND ""
        SOURCE_DIR ${CMAKE_CURRENT_BINARY_DIR}/sample_images
#        INSTALL_COMMAND ${CMAKE_COMMAND} -E copy_directory <SOURCE_DIR> ${CMAKE_CURRENT_BINARY_DIR}/sample_images
        )