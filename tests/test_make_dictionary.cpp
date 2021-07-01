//
// Created by Borchers, Henry Samuel on 7/1/21.
//
#include <catch2/catch.hpp>
#include <exif.hpp>
#include <map>
#include <glue/make_dictionary.h>

TEST_CASE("Make dictionary"){
    SECTION("empty data"){
        Exiv2::ExifData empty_data;
        auto result = make_dictionary(empty_data);
        REQUIRE(result.empty());
    }
}