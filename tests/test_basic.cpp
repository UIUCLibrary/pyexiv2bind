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
//    SECTION("get_icc_profile"){
//        i.get_icc_profile();
//    }

    SECTION("get xmp"){
        auto xmp = i.get_xmp_metadata();
        REQUIRE(xmp["Xmp.dc.creator"] == "University of Illinois Library");

    }

    SECTION("Get IPTC"){
        auto iptc = i.get_iptc_metadata();
        REQUIRE(iptc["Iptc.Application2.TransmissionReference"] == "Preservation master");
    }

    SECTION("Get Exif metadata") {
        auto exif = i.get_exif_metadata();
        REQUIRE(exif["Exif.Image.Artist"] == "University of Illinois Library");
    }

}
TEST_CASE("Try tiff Image", "[glue][tiff]"){
    const std::string filename = "tests/sample_images/dummy.tif";
    Image i(filename);

    SECTION("File is correctly added"){
        REQUIRE(i.getFilename() == filename);
    }

    SECTION("File is good"){
        REQUIRE(i.is_good());
    }

    SECTION("get_icc_profile"){
        std::string icc_profile = i.get_icc_profile();
        REQUIRE(icc_profile.length() != 0);
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
        REQUIRE(exif["Exif.Image.Artist"] == "University of Illinois Library");
    }
}