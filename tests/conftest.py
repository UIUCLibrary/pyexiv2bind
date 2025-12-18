import os
import shutil
import tarfile
import hashlib

import pytest
import urllib.request

SAMPLE_IMAGES_SHA256 = "0461f57db3806ca47d9063151eec4bc0720c66a83153dda04e230f838b64f063"
SAMPLE_IMAGES_URL = "https://nexus.library.illinois.edu/repository/sample-data/images/sample_images.tar.gz"

# To save time from redownloading the sample_images.tar.gz file every time,
# download it locally and set the environment variable SAMPLE_IMAGES_ARCHIVE
# to the path of the downloaded file

def download_images(url, download_path):

        print(f"Downloading {url}")
        output = os.path.join(download_path, "sample_images.tar.gz")
        urllib.request.urlretrieve(url, filename=output)
        if not os.path.exists(output):
            raise FileNotFoundError("sample images not download")
        return output
def extract_images(path, destination):
    print("Extracting images")
    with tarfile.open(path, "r:gz") as archive_file:
        for item in archive_file.getmembers():
            print("Extracting {}".format(item.name))
            archive_file.extract(item, path=destination)

def verify_hash(path, sha256_hash):
    with open(path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    assert file_hash == sha256_hash


@pytest.fixture(scope="session")
def sample_images_readonly(tmpdir_factory):

    test_path = tmpdir_factory.mktemp("data", numbered=False)
    sample_images_path = os.path.join(test_path, "sample_images")
    download_path = tmpdir_factory.mktemp("downloaded_archives", numbered=False)
    if os.path.exists(sample_images_path):
        print(f"{sample_images_path} already exits")

    else:
        archive = os.getenv('SAMPLE_IMAGES_ARCHIVE')
        if not archive:
            print("Downloading sample images")
            archive = download_images(
                url=SAMPLE_IMAGES_URL,
                download_path=download_path
            )
        if not os.path.exists(archive):
            raise FileNotFoundError(f"sample image archive not found. {archive} does not exist.")
        verify_hash(archive, sha256_hash=SAMPLE_IMAGES_SHA256)
        extract_images(path=archive, destination=test_path)
    yield sample_images_path
    if os.path.exists(test_path):
        shutil.rmtree(test_path)


@pytest.fixture
def sample_images(tmpdir_factory, sample_images_readonly):
    new_set = tmpdir_factory.mktemp("sample_set", numbered=False)
    sample_image_files = []
    for file in os.scandir(sample_images_readonly):
        sample_image_new = os.path.join(new_set, file.name)
        shutil.copyfile(file.path, sample_image_new)
        sample_image_files.append(sample_image_new)

    yield new_set
    shutil.rmtree(new_set)
