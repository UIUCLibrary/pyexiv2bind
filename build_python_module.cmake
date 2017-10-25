# BUILD the Python Module
file(GLOB python_files RELATIVE ${CMAKE_SOURCE_DIR}/
        "${CMAKE_SOURCE_DIR}/py3exiv2bind/*.py")
set(extra_python_files
        setup.py
        setup.cfg
        tox.ini
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

add_test(NAME tox
        COMMAND ${PYTHON_EXECUTABLE} -m tox --workdir ${CMAKE_BINARY_DIR}
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        )

add_custom_target(Wheel
        COMMAND ${PYTHON_EXECUTABLE} setup.py bdist_wheel -d ${CMAKE_BINARY_DIR}/dist -b ${CMAKE_BINARY_DIR}/python_build
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
