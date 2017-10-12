//
// Created by hborcher on 10/6/2017.
//
#include <catch.hpp>
#include <glue/glue.h>
#include <glue/Image.h>

TEST_CASE("Try Image", "[glue]"){
    const std::string filename = "tests/sample_images/dummy.jp2";
    Image i(filename);
    SECTION("File is correctly added"){
        REQUIRE(i.filename == filename);
    }
}