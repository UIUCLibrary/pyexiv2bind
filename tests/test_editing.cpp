//
// Created by hborcher on 10/4/2018.
//

#include <catch2/catch.hpp>
#include <exiv2/exiv2.hpp>
#include <cassert>

void exifPrint(const Exiv2::ExifData& exifData);

#define METADATA_KEY "Exif.Image.XResolution"
//#define METADATA_KEY "Exif.Image.Make"
//#define METADATA_NEW_VALUE "MEa"

const std::string IMAGE_TEST_PATH(TEST_IMAGE_PATH);

TEST_CASE("Edit"){
    const std::string filename = IMAGE_TEST_PATH + "dummy.tif";
    {

        auto image = Exiv2::ImageFactory::open(filename);
        assert(image.get() != 0);
        assert(image->good());
        assert(image->checkMode(Exiv2::MetadataId::mdExif) !=Exiv2::AccessMode::amRead);

        image->readMetadata();

        Exiv2::ExifData exifData = image->exifData();
//        Exiv2::ExifData exifData = image->exifData();

//        exifPrint(exifData);
//
//        Exiv2::ExifKey metadata_key(METADATA_KEY);
//
//        Exiv2::ExifData::iterator pos = exifData.findKey(metadata_key);
//
//        if (pos == exifData.end()) {
//            throw Exiv2::Error(Exiv2::kerErrorMessage, "Metadatum with key = " + metadata_key.key() + " not found");
//        }
        std::cout << "The original value of "<< METADATA_KEY << " is " << exifData[METADATA_KEY] << std::endl;
//        Exiv2::ExifData data;
//        data.
//        Exiv2::FloatValue("sd")

//        exifData[METADATA_KEY].setValue("300",Exiv2::FloatValue) = "300";
//        std::cout << "The original value of "<< pos->key() << " is " <<pos->value() << std::endl;
//        exifData["Exif.Image.ResolutionUnit"] = uint16_t(1);
////        auto rc = exifData["Exif.Image.XResolution"].setValue("300");
////        Exiv2::signedLong d(300);
//        pos->setValue(METADATA_NEW_VALUE);
////        exifData["Exif.Image.YResolution"] = Exiv2::Rational(-2, 3);
//
////
//////        exifData["Exif.Image.XResolution"].set;
////        REQUIRE(exifData["Exif.Image.XResolution"].toString() ==  std::string("300"));
//////        Exiv2::Exifdatum& tag = exifData["Exif.Image.XResolution"];
//////        int rc = tag.setValue("400");
//////        std::cout <<"Rc ="<< rc << std::endl;
////
//////        .setValue("200");// = int32_t(-2);
//////        exifData["Exif.Image.XResolution"] = Exiv2::Rational(-2, 3);
//////        image->clearExifData();
        Exiv2::Exifdatum d = exifData["Exif.Image.XResolution"];
        std::cout << "family name " << d.familyName() << std::endl;
        std::cout << "groupName " << d.groupName() << std::endl;
        std::cout << "tagName " << d.tagName() << std::endl;


//        Exiv2::Value::AutoPtr v = Exiv2::Value::create(Exiv2::unsignedRational);
//        v->read("300 / 1");
//        std::cout << "converted to String " << v->toString() << "\n";
//        std::cout << "converted to Float " << v->toFloat() << "\n";
//        std::cout << "converted to toRational " << v->toRational().first << "/" << v->toRational().second << "\n";
//        Exiv2::ExifKey key(METADATA_KEY);
//        Exiv2::ExifData::iterator i = exifData.findKey(key);
////        i.
////        exifData.erase(i);
//        exifData.add(key, v.get());

        Exiv2::RationalValue value;
        value.read("300/1");
//        std::cout << "converted to String " << value.toString() << "\n";
        std::cout << "converted to Float " << value.toFloat() << "\n";
        std::cout << "converted to toRational " << value.toRational().first << "/" << value.toRational().second << "\n";
        exifData["Exif.Image.XResolution"] = value;
        image->setExifData(exifData);
        image->writeMetadata();

//        exifDataExifdatum


    }

    std::cout << "Written to " << filename <<std::endl;
    {
        auto image = Exiv2::ImageFactory::open(filename);
        assert(image.get() != 0);
        image->readMetadata();
        Exiv2::ExifData exifData_second = image->exifData();
        std::cout << "Now the value of " << exifData_second[METADATA_KEY].key() << " is " << exifData_second[METADATA_KEY].value().toFloat() << std::endl;
        exifPrint(exifData_second);
    }
//
//    {
//        Exiv2::Image::AutoPtr image_read = Exiv2::ImageFactory::open(filename);
//        assert(image_read.get() != 0);
//        image_read->readMetadata();
//
//
//        Exiv2::ExifData exifData_second = image_read->exifData();
//        std::cout <<"Exif.Image.XResolution = " << exifData_second["Exif.Image.XResolution"] << std::endl;
//        Exiv2::Exifdatum value = exifData_second["Exif.Image.XResolution"];
//        REQUIRE(value.toString() == "300");
//        std::cout <<"Exif.Image.ResolutionUnit = " << exifData_second["Exif.Image.ResolutionUnit"] << std::endl;
//
//        Exiv2::IptcData iptcData = image_read->iptcData();
//
//    }
}
TEST_CASE("Edit tiff") {
    const std::string filename = IMAGE_TEST_PATH + "dummy.tif";
    {

        auto image = Exiv2::ImageFactory::open(filename);

        assert(image.get() != 0);
        assert(image->good());
        assert(image->checkMode(Exiv2::MetadataId::mdExif) != Exiv2::AccessMode::amRead);


        Exiv2::ExifData exifData = image->exifData();
        image->readMetadata();
        exifPrint(exifData);
        exifData["Exif.Image.XResolution"] = int32_t(300);
        exifData["Exif.Image.YResolution"] = int32_t(300);
//        exifData["Exif.Image.Make"] = "Mine";

        std::string stringvalue = exifData[METADATA_KEY].toString();
        exifData["Exif.Image.ResolutionUnit"] = int32_t(2);
        Exiv2::Exifdatum d = exifData["Exif.Image.ResolutionUnit"];

        image->setExifData(exifData);
        image->writeMetadata();
        std::cout << "Written to " << filename << std::endl;



    }

    {
        auto image = Exiv2::ImageFactory::open(filename);
        assert(image.get() != 0);
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
    Exiv2::ExifData::const_iterator i = exifData.begin();
    for (; i != exifData.end(); ++i) {
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
