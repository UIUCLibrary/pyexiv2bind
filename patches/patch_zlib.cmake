set(TEMP_CMAKE dummy.cmake)
set(ZLIB_CMAKE_LISTS "CMakeLists.txt")

message(STATUS "Modifying CMakeLists.txt from ZLib source tree")

# Remove the Example binary targets from zlib's cmake build
file(STRINGS CMakeLists.txt cmake_lines)
foreach (cmake_line ${cmake_lines})
    if (${cmake_line} STREQUAL "# Example binaries")
        break()
    else ()
        file(APPEND ${TEMP_CMAKE} "${cmake_line}\n")
    endif ()
endforeach ()
file(RENAME ${TEMP_CMAKE} CMakeLists.txt)