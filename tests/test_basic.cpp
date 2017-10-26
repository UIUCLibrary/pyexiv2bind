//
// Created by hborcher on 10/6/2017.
//
#include <catch.hpp>
#include <glue/glue.h>
#include <glue/Image.h>

TEST_CASE("Try jp2 Image", "[glue][jp2]"){
    const std::string filename = "tests/sample_images/dummy.jp2";
    Image i(filename);
    SECTION("File is correctly added"){
        REQUIRE(i.getFilename() == filename);
    }
    SECTION("File is good"){
        REQUIRE(i.is_good());
    }
    SECTION("foo"){
        i.foo();
    }

}
TEST_CASE("Try tiff Image", "[glue][tiff]"){
    const std::string filename = "tests/sample_images/000001_001.tif";
    Image i(filename);
    SECTION("File is correctly added"){
        REQUIRE(i.getFilename() == filename);
    }
    SECTION("File is good"){
        REQUIRE(i.is_good());
    }
    SECTION("foo"){
        i.foo();
    }

}