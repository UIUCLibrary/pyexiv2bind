function(create_venv)
    set(venv_args DESTINATION)
    set(venv_multiargs REQUIREMENTS)

    cmake_parse_arguments(VENV_ARGS
            ""
            "${venv_args}"
            "${venv_multiargs}"
            ${ARGN}
            )

    message(STATUS "Creating a Python virtual environment")
    execute_process(COMMAND ${PYTHON_EXECUTABLE} -m venv ${VENV_ARGS_DESTINATION}
            WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
            RESULT_VARIABLE VENV_CREATED
            )
    if(NOT "${VENV_CREATED}" STREQUAL "0")
        message(SEND_ERROR "Unable to make a Python virtual environment")
    endif()

    foreach(requirement_text ${VENV_ARGS_REQUIREMENTS})
        list(APPEND requirements_args -r)
        list(APPEND requirements_args ${requirement_text})
    endforeach()

    message(STATUS "Setting up the dependencies for the Python virtual environment")

    if(WIN32)
        set(PIP_PATH ${PROJECT_BINARY_DIR}/venv/scripts/pip.exe)
    else()
        set(PIP_PATH ${PROJECT_BINARY_DIR}/venv/bin/pip)
    endif()

    execute_process(COMMAND ${PIP_PATH} install ${requirements_args}
            RESULT_VARIABLE VENV_DEPS_INSTALLED)

    if(NOT "${VENV_DEPS_INSTALLED}" STREQUAL "0")
        message(SEND_ERROR "Error installing Python virtual environment dependencies")
    endif()

endfunction()


function(update_python_binary_dir root)

    file(GLOB python_files RELATIVE ${CMAKE_SOURCE_DIR}/
            "${root}/*.py"
            )

    foreach (_file ${python_files})
        list(APPEND PYTHON_PACKAGE_SOURCE ${_file})
    endforeach ()

    foreach (python_file ${PYTHON_PACKAGE_SOURCE})
        add_custom_command(OUTPUT ${python_file}
                COMMENT "Updating ${python_file}"
                COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_SOURCE_DIR}/${python_file} ${CMAKE_BINARY_DIR}/${python_file}
                )
    endforeach ()
endfunction(update_python_binary_dir)


function(add_tox_tests)
    message(STATUS "Getting tox tests")
    set(tox_single_value_args TOXPATH)

    cmake_parse_arguments(TOX_TEST_ARGS
            ""
            "${tox_single_value_args}"
            ""
            ${ARGN}
            )
    execute_process(
            COMMAND ${TOX_TEST_ARGS_TOXPATH} -l
			WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
            OUTPUT_VARIABLE TOX_TESTS
        )
    message(STATUS "Found Tox tests: ${TOX_TESTS}")

    string(REPLACE "\n" ";" TOX_TESTS ${TOX_TESTS})
    foreach(_test ${TOX_TESTS})

        add_test(NAME Tox_Test_${_test}
                COMMAND ${TOX_TEST_ARGS_TOXPATH} -e ${_test}
                WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
                )
        message(STATUS "Added Tox_Test_${_test} to CTest")
    endforeach()
endfunction()


function(add_python_wheel)
    add_custom_target(Wheel
            COMMAND ${PYTHON_EXECUTABLE} setup.py bdist_wheel -d ${PROJECT_BINARY_DIR}/dist -b ${PROJECT_BINARY_DIR}/python_build
            WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endfunction()
