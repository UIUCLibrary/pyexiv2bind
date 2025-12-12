//
// Created by hborcher on 10/4/2018.
//


#include <catch2/catch_test_macros.hpp>
#include <catch2/generators/catch_generators.hpp>

#include <exiv2/exif.hpp>
#include <exiv2/image.hpp>
#include <exiv2/properties.hpp>
#include <exiv2/types.hpp>
#include <exiv2/value.hpp>

#include <cassert>
#include <filesystem>
#include <iostream>
#include <iomanip>

namespace fs = std::filesystem;

static void exifPrint(const Exiv2::ExifData& exifData);

constexpr auto METADATA_KEY = "Exif.Image.XResolution";

TEST_CASE("Edit"){
    constexpr auto filename = TEST_IMAGE_PATH "dummy.tif";
    {

        const auto image = Exiv2::ImageFactory::open(filename);
        assert(image.get() != nullptr);
        assert(image->good());
        assert(image->checkMode(Exiv2::MetadataId::mdExif) !=Exiv2::AccessMode::amRead);

        image->readMetadata();

        Exiv2::ExifData exifData = image->exifData();
        std::cout << "The original value of " << METADATA_KEY << " is " << exifData[METADATA_KEY] << std::endl;
        const Exiv2::Exifdatum data = exifData["Exif.Image.XResolution"];
        std::cout << "family name " << data.familyName() << std::endl;
        std::cout << "groupName " << data.groupName() << std::endl;
        std::cout << "tagName " << data.tagName() << std::endl;

        Exiv2::RationalValue value;
        value.read("300/1");
        std::cout << "converted to Float " << value.toFloat() << "\n";
        std::cout << "converted to toRational " << value.toRational().first << "/" << value.toRational().second << "\n";
        exifData["Exif.Image.XResolution"] = value;
        image->setExifData(exifData);
        image->writeMetadata();
    }

    std::cout << "Written to " << filename <<std::endl;
    {
        const auto image = Exiv2::ImageFactory::open(filename);
        assert(image.get() != nullptr);
        image->readMetadata();
        Exiv2::ExifData exifData_second = image->exifData();
        std::cout << "Now the value of " << exifData_second[METADATA_KEY].key() << " is " << exifData_second[METADATA_KEY].value().toFloat() << std::endl;
        exifPrint(exifData_second);
    }
}
TEST_CASE("Edit tiff") {
    constexpr auto filename = TEST_IMAGE_PATH "dummy.tif";
    {

        const auto image = Exiv2::ImageFactory::open(filename);

        assert(image.get() != nullptr);
        assert(image->good());
        assert(image->checkMode(Exiv2::MetadataId::mdExif) != Exiv2::AccessMode::amRead);


        Exiv2::ExifData exifData = image->exifData();
        image->readMetadata();
        exifPrint(exifData);
        exifData["Exif.Image.XResolution"] = 300;
        exifData["Exif.Image.YResolution"] = 300;
        exifData["Exif.Image.ResolutionUnit"] = 2;
        image->setExifData(exifData);
        image->writeMetadata();
        std::cout << "Written to " << filename << std::endl;



    }

    {
        const auto image = Exiv2::ImageFactory::open(filename);
        assert(image.get() != nullptr);
        image->readMetadata();
        Exiv2::ExifData exifData_second = image->exifData();
        std::cout << "Now the value of " << exifData_second["Exif.Image.XResolution"].key() << " is "
                  << exifData_second["Exif.Image.XResolution"].value().toString() << std::endl;
        exifPrint(exifData_second);
        REQUIRE(exifData_second["Exif.Image.XResolution"].value().toString() == "300");
    }
}


void exifPrint(const Exiv2::ExifData& exifData)
{
    for (auto i = exifData.begin(); i != exifData.end(); ++i) {
        std::cout << std::setw(44) << std::setfill(' ') << std::left
                  << i->key() << " "
                  << "0x" << std::setw(4) << std::setfill('0') << std::right
                  << std::hex << i->tag() << " "
                  << std::setw(9) << std::setfill(' ') << std::left
                  << i->typeName() << " "
                  << std::dec << std::setw(3)
                  << std::setfill(' ') << std::right
                  << i->count() << "  "
                  << std::dec << i->value()
                  << "\n";
    }
}

TEST_CASE("edit jp2 metadata", "[integration,upstream]"){
    auto [key, startingValue, value] = GENERATE(table<std::string, std::string, std::string>({
            {"Xmp.iptc.CreatorContactInfo/Iptc4xmpCore:CiAdrCity", "Urbana", "Champaign"},
            {"Xmp.iptc.CreatorContactInfo/Iptc4xmpCore:CiEmailWork", "digidcc@library.illinois.edu", "digitizationservices@library.illinois.edu"},
            {"Xmp.dc.creator", "University of Illinois Library", "University of Illinois"},
            {"Xmp.photoshop.Credit", "Alyssa Bralower", "University of Illinois Library"},
            {"Xmp.photoshop.DateCreated", "2016-05-19T18:41:17", "2024-01-10T18:41:17"},
    }
    ) );
    DYNAMIC_SECTION("Change " << key <<" to " << value){
        constexpr auto source = TEST_IMAGE_PATH "dummy.jp2";
        constexpr auto out = TEST_IMAGE_PATH "changeme.jp2";
        fs::copy(source, out, fs::copy_options::overwrite_existing);
        {
            auto image = Exiv2::ImageFactory::open(out);
            assert(image.get() != nullptr);
            image->readMetadata();
            auto xmpData = image->xmpData();
            REQUIRE(xmpData[key].value().toString() == startingValue);
            if (auto erase_key = xmpData.findKey(Exiv2::XmpKey(key)); erase_key != xmpData.end()){
                xmpData.erase(erase_key);
            }
            xmpData[key].setValue(value);
            image->setXmpData(xmpData);
            image->writeMetadata();
        }
        {
            auto second_image = Exiv2::ImageFactory::open(out);
            assert(second_image.get() != nullptr);
            second_image->readMetadata();
            auto secondXmpData = second_image->xmpData();
            REQUIRE(secondXmpData[key].value().toString() == value);
        }
        fs::remove(out);
    }
}
