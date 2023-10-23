add_library(glue OBJECT EXCLUDE_FROM_ALL
        glue.cpp
        glue.h
        Image.cpp
        Image.h
        MetadataStrategies.h
        MetadataProcessor.cpp
        MetadataProcessor.h
        IPTC_Strategy.cpp
        IPTC_Strategy.h
        ExifStrategy.cpp
        ExifStrategy.h
        AbsMetadataStrategy.h
        XmpStrategy.cpp
        XmpStrategy.h
        make_dictionary.h
        glue_execeptions.h)
#exiv2lib
target_include_directories(glue PUBLIC ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR}
        PRIVATE
        $<TARGET_PROPERTY:exiv2lib,INCLUDE_DIRECTORIES>
        )
set_target_properties(glue PROPERTIES
        CXX_STANDARD 17
        )
target_link_libraries(glue PRIVATE exiv2lib)