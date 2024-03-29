#include <filesystem>
#include <iostream>
#include <fstream>
#include <string>
#include <catch2/catch_test_macros.hpp>
#include <catch2/generators/catch_generators.hpp>
#include <catch2/matchers/catch_matchers_all.hpp>
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
TEST_CASE("jp2 files can edit their dpi"){
    const std::string source = IMAGE_TEST_PATH + "dummy.jp2";
    const std::string test_file = IMAGE_TEST_PATH + "current.jp2";
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


TEST_CASE("missing file with set_dpi raises"){
    const std::string no_such_file = IMAGE_TEST_PATH + "missing.tif";
    REQUIRE_THROWS_AS(set_dpi(no_such_file, 100, 100), Exiv2::Error);
}

TEST_CASE("empty file with set_dpi raises"){
    const std::string bad_file = IMAGE_TEST_PATH + "empty.tif";
    std::ofstream invalidFile;
    invalidFile.open(bad_file);
    invalidFile.close();
    REQUIRE_THROWS_AS(set_dpi(bad_file, 100, 100), Exiv2::Error);
}

TEST_CASE("bad tiff file with set_dpi raises"){
    struct OtherDataFormat {
        int first_number;
        int second_number;
        int third_number;
        float myFloat;
    };
    const std::string bad_file = IMAGE_TEST_PATH + "bad.tif";
    std::ofstream corruptedFile;
    corruptedFile.open(bad_file, std::ios::binary);
    OtherDataFormat packet{3, 3, 3, 1.2};
    int number = 444;
    const char header = 'I';
    corruptedFile.write(&header, sizeof(char ));
    corruptedFile.write(&header, sizeof(char ));
    corruptedFile.write((char*) &number, sizeof(int ));
    corruptedFile.write((char *) &packet, sizeof(OtherDataFormat));
    corruptedFile.close();
    REQUIRE_THROWS_AS(set_dpi(bad_file, 100, 100), Exiv2::Error);
}

TEST_CASE("exiv2_version uses a semantic versioning scheme"){
    REQUIRE(std::regex_match(exiv2_version(), std::regex("^([0-9]+)\\.([0-9]+)\\.([0-9]+)$")));
}


TEST_CASE("setting dpi for jp2 does not remove existing xmp metadata"){
    const std::string source = IMAGE_TEST_PATH + "dummy.jp2";
    const std::string test_file = IMAGE_TEST_PATH + "current.jp2";
    SECTION("Copy test file"){
        fs::copy(source, test_file);
        SECTION("Edit DPI"){
            {
                const Image originalImage(test_file);
                REQUIRE(originalImage.get_xmp_metadata()["Xmp.iptc.CreatorContactInfo/Iptc4xmpCore:CiAdrCity"] == "Urbana");
            }
            set_dpi(test_file, 200, 200);
            const Image image(test_file);
            REQUIRE(image.get_xmp_metadata()["Xmp.iptc.CreatorContactInfo/Iptc4xmpCore:CiAdrCity"] == "Urbana");
        }
    }
    fs::remove(test_file);
}
