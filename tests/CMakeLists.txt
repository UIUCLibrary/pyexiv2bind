include(FetchContent)
if (BUILD_TESTING)

    FetchContent_Declare(test_images
            URL https://jenkins.library.illinois.edu/userContent/sample_images.tar.gz
            SOURCE_DIR ${CMAKE_CURRENT_BINARY_DIR}/sample_images
            )
    FetchContent_GetProperties(test_images)
    if (NOT test_images_POPULATED)
        FetchContent_Populate(test_images)
    endif()

    find_path(TEST_IMAGE_PATH dummy.jp2
            PATHS ${test_images_SOURCE_DIR})
    set(TEST_IMAGE_PATH ${TEST_IMAGE_PATH}/)
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
    find_path(PYTEST_PATH
            NAMES pytest
            PATHS ${Python3_SITELIB}
            )
    if(PYTEST_PATH)
        execute_process(
                COMMAND ${Python3_EXECUTABLE} -m pytest --collect-only
                WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
                OUTPUT_FILE ${PROJECT_BINARY_DIR}/pytest_collection.xml
#                OUTPUT_VARIABLE PYTEST_COLLECTION
                OUTPUT_STRIP_TRAILING_WHITESPACE
        )
        file(STRINGS "${PROJECT_BINARY_DIR}/pytest_collection.xml" PYTEST_COLLECTION)
        foreach(line ${PYTEST_COLLECTION})
            if (line MATCHES "^<Module ([a-z]+\\/test_[a-zA-Z]+.py)")
                add_test(NAME ${PROJECT_NAME}::${CMAKE_MATCH_1}
                    COMMAND ${Python3_EXECUTABLE} -m pytest ${PROJECT_SOURCE_DIR}/${CMAKE_MATCH_1}
                    WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
                    )

            endif ()
        endforeach()
        if(pyexiv2bind_generate_python_bindings)
            set_target_properties(core PROPERTIES EXCLUDE_FROM_ALL off)
        endif()
    endif()

    FetchContent_MakeAvailable(libcatch2)
    FetchContent_GetProperties(libcatch2)
    list(APPEND CMAKE_MODULE_PATH ${libcatch2_SOURCE_DIR}/contrib/)
    include(${libcatch2_SOURCE_DIR}/contrib/Catch.cmake)
    target_include_directories(Catch2 INTERFACE ${libcatch2_SOURCE_DIR}/single_include/catch2)
    add_executable(cpp_tests
            test_basic.cpp
            tests-main.cpp
            $<TARGET_OBJECTS:glue>
#            test_metadata_processor.cpp
#            test_editing.cpp
            )
    target_compile_definitions(cpp_tests PRIVATE TEST_IMAGE_PATH="${TEST_IMAGE_PATH}")
    set_target_properties(cpp_tests PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
            RUNTIME_OUTPUT_NAME test
            CXX_STANDARD 11
            )
    target_include_directories(cpp_tests PRIVATE ${PROJECT_SOURCE_DIR}/py3exiv2bind/core)
    target_link_libraries(cpp_tests PRIVATE Catch2::Catch2 exiv2lib)

    catch_discover_tests(cpp_tests TEST_PREFIX ${PROJECT_NAME}::test-pyexiv2::)
    add_executable(test_editing
            test_editing.cpp
#            test_simple_edit.cpp
            tests-main.cpp
            )

    set_target_properties(test_editing PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
            CXX_STANDARD 11
            )
    target_link_libraries(test_editing PRIVATE exiv2lib Catch2::Catch2)
    target_compile_definitions(test_editing PRIVATE TEST_IMAGE_PATH="${TEST_IMAGE_PATH}")

endif ()