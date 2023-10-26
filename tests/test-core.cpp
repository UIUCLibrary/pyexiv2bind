#include <filesystem>
#include <string>
#include <catch2/catch.hpp>
#include "glue/glue.h"
#include "glue/Image.h"
#include <regex>

const std::string IMAGE_TEST_PATH(TEST_IMAGE_PATH);

namespace fs = std::filesystem;
TEST_CASE("TIFF files can edit their dpi"){
    const std::string source = IMAGE_TEST_PATH + "dummy.tif";
    const std::string test_file = IMAGE_TEST_PATH + "current.tif";
    SECTION("Copy test file"){
        fs::copy(source, test_file);
        SECTION("Edit DPI"){
            auto new_dpi_x_value = GENERATE(100, 200, 400);
            auto new_dpi_y_value = GENERATE(100, 200, 400);
            DYNAMIC_SECTION("Set DPI to " << new_dpi_x_value << " dots per inch x and " << new_dpi_y_value << " dots per inch y"){
                set_dpi(test_file, new_dpi_x_value, new_dpi_y_value);
                const Image image(test_file);
                REQUIRE(image.get_exif_metadata()["Exif.Image.XResolution"] == std::to_string(new_dpi_x_value) + "/1");
                REQUIRE(image.get_exif_metadata()["Exif.Image.YResolution"] == std::to_string(new_dpi_y_value) + "/1");
            }
        }
    }
    fs::remove(test_file);
}

TEST_CASE("invalid file with set_dpi raises"){
    const std::string no_such_file = IMAGE_TEST_PATH + "invalid_file.tif";
    REQUIRE_THROWS_AS(set_dpi(no_such_file, 100, 100), Exiv2::Error);
}

TEST_CASE("exiv2_version uses a semantic versioning scheme"){
    REQUIRE(std::regex_match(exiv2_version(), std::regex("^([0-9]+)\\.([0-9]+)\\.([0-9]+)$")));
}