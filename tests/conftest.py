import os
import shutil
import tarfile

import pytest
import urllib.request
from tempfile import TemporaryDirectory


def download_images(url, destination):
    with TemporaryDirectory() as download_path:
        print("Downloading {}".format(url))
        urllib.request.urlretrieve(url,
                                   filename=os.path.join(download_path, "sample_images.tar.gz"))
        if not os.path.exists(os.path.join(download_path, "sample_images.tar.gz")):
            raise FileNotFoundError("sample images not download")
        print("Extracting images")
        with tarfile.open(os.path.join(download_path, "sample_images.tar.gz"), "r:gz") as archive_file:
            for item in archive_file.getmembers():
                print("Extracting {}".format(item.name))
                archive_file.extract(item, path=destination)
            pass


@pytest.fixture(scope="session")
def sample_images_readonly(request):

    test_path = os.path.dirname(__file__)
    sample_images_path = os.path.join(test_path, "sample_images")

    if os.path.exists(sample_images_path):
        print("{} already exits".format(sample_images_path))

    else:
        print("Downloading sample images")
        download_images(url="https://jenkins.library.illinois.edu/userContent/sample_images.tar.gz",
                        destination=test_path)

    return sample_images_path


@pytest.fixture
def sample_images_editable(tmpdir_factory, sample_images_readonly):
    new_set = tmpdir_factory.mktemp("sample_set")

    for file in os.scandir(sample_images_readonly):
        shutil.copyfile(file.path, os.path.join(new_set, file.name))

    return new_set
