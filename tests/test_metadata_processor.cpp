//
// Created by hborcher on 10/11/2017.
//

#include <catch.hpp>
#include <glue/MetadataProcessor.h>
#include <cassert>
#include <utility>

TEST_CASE("process"){
    MetadataProcessor processor;
    Exiv2::Image::AutoPtr image = Exiv2::ImageFactory::open("tests/sample_images/dummy.jp2");
    assert(image.get() != 0);
    processor.set_output_format(MetadataStrategies::IPTC);
    processor.build(image);
    auto foo = processor.getMetadata();
    REQUIRE(foo.empty());
}

TEST_CASE("process XMP"){
    MetadataProcessor processor;
    Exiv2::Image::AutoPtr image = Exiv2::ImageFactory::open("tests/sample_images/dummy.jp2");
    assert(image.get() != 0);
    processor.set_output_format(MetadataStrategies::XMP);
    processor.build(image);

    auto foo = processor.getMetadata();
    REQUIRE(foo.empty());
}
