set(PYTHON_TEST_FILES ${CMAKE_CURRENT_SOURCE_DIR}/test_run.py)
find_package(PythonInterp 3 REQUIRED)
add_custom_target(add_tests
        COMMAND ${CMAKE_COMMAND} -E copy ${PYTHON_TEST_FILES} ${CMAKE_BINARY_DIR}/
        COMMENT "Adding test the build directory"
        )

add_dependencies(add_tests glue)
add_test(NAME import_test
        COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_BINARY_DIR}/test_run.py
        )