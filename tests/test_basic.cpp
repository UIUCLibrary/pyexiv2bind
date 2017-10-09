//
// Created by hborcher on 10/6/2017.
//
#include <catch.hpp>
#include <glue.h>


TEST_CASE("get_exif_metadata", "[glue]") {
    const std::string filename = "tests/sample_images/dummy.jp2";
    auto metadata = get_exif_metadata(filename);
    REQUIRE(!metadata.empty());
}

TEST_CASE("get_exif_metadata2", "[glue]") {
    const std::string filename = "tests/sample_images/dummy.jp2";
    auto metadata = get_exif_metadata2(filename);

    REQUIRE(metadata.size() != 0);
}