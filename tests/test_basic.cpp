//
// Created by hborcher on 10/6/2017.
//
#include <catch2/catch_test_macros.hpp>
#include <glue/glue.h>
#include <glue/Image.h>
#include <iostream>

const std::string IMAGE_TEST_PATH(TEST_IMAGE_PATH);

TEST_CASE("Try jp2 Image", "[glue][jp2]"){
    const std::string filename = IMAGE_TEST_PATH + "dummy.jp2";
    Image i(filename);
    SECTION("File is correctly added"){
        REQUIRE(i.getFilename() == filename);
    }
    SECTION("File is good"){
        REQUIRE(i.is_good());
    }
    SECTION("get_icc_profile"){
        try {
            auto icc = i.get_icc_profile();
        } catch (std::exception &e){
            std::cerr << e.what() << std::endl;
        }


		//REQUIRE(icc);
    }

    SECTION("get xmp"){
        auto xmp = i.get_xmp_metadata();
        REQUIRE(xmp["Xmp.dc.creator"] == "University of Illinois Library");

    }

    SECTION("Get IPTC"){
        auto iptc = i.get_iptc_metadata();
        //REQUIRE(iptc["Iptc.Application2.TransmissionReference"] == "Preservation master");
    }

    SECTION("Get Exif metadata") {
        auto exif = i.get_exif_metadata();
        //REQUIRE(exif["Exif.Image.Artist"] == "University of Illinois Library");
    }

}
TEST_CASE("Try tiff Image", "[glue][tiff]"){
    const std::string filename = IMAGE_TEST_PATH + "dummy.tif";
    Image i(filename);

    SECTION("File is correctly added"){
        REQUIRE(i.getFilename() == filename);
    }

    SECTION("File is good"){
        REQUIRE(i.is_good());
    }

    SECTION("get_icc_profile"){
        std::string icc_profile = i.get_icc_profile();
        REQUIRE(icc_profile.length() > 1);
    }

    SECTION("get xmp"){
        auto xmp = i.get_xmp_metadata();
        REQUIRE(xmp["Xmp.dc.creator"] == "University of Illinois Library");

    }

    SECTION("Get IPTC"){
        auto iptc = i.get_iptc_metadata();
        REQUIRE(iptc["Iptc.Application2.TransmissionReference"] == "Access");
    }

    SECTION("Get Exif metadata"){
        auto exif = i.get_exif_metadata();
        std::vector<std::string> keys;
        REQUIRE(exif["Exif.Image.ImageWidth"] == "2703");
    }
}
