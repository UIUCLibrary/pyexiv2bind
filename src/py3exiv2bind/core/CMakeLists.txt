include(GenerateExportHeader)

add_subdirectory(glue)


if (pyexiv2bind_generate_python_bindings)
    Python3_add_library(core core.cpp $<TARGET_OBJECTS:glue> )
    set_target_properties(core PROPERTIES EXCLUDE_FROM_ALL on)
    add_custom_command(TARGET core
            POST_BUILD
            COMMAND ${Python3_EXECUTABLE} setup.py build_py --build-lib ${PROJECT_BINARY_DIR}
            WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
            )
    if (SKBUILD)
        python_extension_module(core)
    endif()
    set_target_properties(core PROPERTIES
            CXX_STANDARD 17
            LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/py3exiv2bind
            RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/py3exiv2bind
            PREFIX "${PYTHON_MODULE_PREFIX}"
            SUFFIX "${PYTHON_MODULE_EXTENSION}"
            )
    target_link_libraries(core PRIVATE pybind11::module exiv2lib)

    install(TARGETS core LIBRARY DESTINATION py3exiv2bind)
    set(CMAKE_INSTALL_SYSTEM_RUNTIME_DESTINATION ${CMAKE_INSTALL_PREFIX}/py3exiv2bind)
    include(InstallRequiredSystemLibraries)
endif (pyexiv2bind_generate_python_bindings)
