# BUILD the Python Module
file(GLOB python_files "${CMAKE_CURRENT_SOURCE_DIR}/py3exiv2bind/*.py")
add_custom_target(py3exiv2bind
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/setup.py $<TARGET_FILE_DIR:core>/..
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/setup.cfg $<TARGET_FILE_DIR:core>/..
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_CURRENT_SOURCE_DIR}/tox.ini $<TARGET_FILE_DIR:core>/..
        BYPRODUCTS
            setup.py
            setup.cfg
            tox.ini
        )
foreach (_file ${python_files})
    add_custom_command(TARGET py3exiv2bind
            COMMAND ${CMAKE_COMMAND} -E copy_if_different ${_file} $<TARGET_FILE_DIR:core>
            )
endforeach ()
add_subdirectory(py3exiv2bind/core)
