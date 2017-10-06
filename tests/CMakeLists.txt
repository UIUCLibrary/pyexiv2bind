set(PYTHON_TEST_FILES python_tests/test_run.py)
find_package(PythonInterp 3 REQUIRED)
add_custom_target(add_python_tests
        COMMENT "Adding test the build directory"
        DEPENDS core project_libexiv2
        )
add_dependencies(add_python_tests core project_libexiv2)
add_custom_command(TARGET add_python_tests
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/python_tests/test_run.py ${CMAKE_CURRENT_BINARY_DIR}
        )

add_test(NAME python_tests
        COMMAND ${PYTHON_EXECUTABLE} -m tox
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        )
add_subdirectory(thirdparty/catch)

add_library(Catch INTERFACE)
target_include_directories(Catch INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/catch/include)
add_executable(tests test_basic.cpp)
set_target_properties(tests PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
target_link_libraries(tests Catch)
add_test(NAME cpp_tests
        COMMAND tests
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        )