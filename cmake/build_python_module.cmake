# BUILD the Python Module
file(GLOB python_files RELATIVE ${CMAKE_SOURCE_DIR}/
        "${CMAKE_SOURCE_DIR}/py3exiv2bind/*.py")
set(extra_python_files
        ${PROJECT_SOURCE_DIR}/setup.py
        ${PROJECT_SOURCE_DIR}/setup.cfg
        ${PROJECT_SOURCE_DIR}/tox.ini
        )
foreach (_file ${extra_python_files})
    list(APPEND PYTHON_PACKAGE_SOURCE ${_file})
endforeach ()

foreach (_file ${python_files})
    list(APPEND PYTHON_PACKAGE_SOURCE ${_file})
endforeach ()

add_custom_target(py3exiv2bind
        DEPENDS ${PYTHON_PACKAGE_SOURCE} core
        )
foreach (python_file ${PYTHON_PACKAGE_SOURCE})
    add_custom_command(OUTPUT ${python_file}
            COMMENT "Updating ${python_file}"
            COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_SOURCE_DIR}/${python_file} ${CMAKE_BINARY_DIR}/${python_file}
            )
endforeach ()
function(add_tox_tests)
    message(STATUS "Getting tox tests")
    execute_process(
            COMMAND ${PYTHON_EXECUTABLE} -m tox -l
            OUTPUT_VARIABLE TOX_TESTS
    )
    string(REPLACE "\n" ";" TOX_TESTS ${TOX_TESTS})
    foreach(_test ${TOX_TESTS})

        add_test(NAME Tox_Test_${_test}
                COMMAND ${PYTHON_EXECUTABLE} -m tox -e ${_test} --workdir ${CMAKE_BINARY_DIR}
                WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
                )
        message(STATUS "Added Tox_Test_${_test} to CTest")
    endforeach()
endfunction()
add_tox_tests()
add_custom_target(Wheel
        COMMAND ${PYTHON_EXECUTABLE} setup.py bdist_wheel -d ${CMAKE_BINARY_DIR}/dist -b ${CMAKE_BINARY_DIR}/python_build
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
