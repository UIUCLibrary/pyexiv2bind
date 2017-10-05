set(PYTHON_TEST_FILES ${CMAKE_CURRENT_SOURCE_DIR}/test_run.py)
find_package(PythonInterp 3 REQUIRED)
add_custom_target(add_tests
        COMMENT "Adding test the build directory"
        DEPENDS py3exiv2bind
        )
add_custom_command(TARGET add_tests
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/test_run.py $<TARGET_FILE_DIR:py3exiv2bind>/../tests/
        )

add_test(NAME python_tests
        COMMAND ${PYTHON_EXECUTABLE} setup.py test
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        )