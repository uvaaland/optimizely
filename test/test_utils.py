import pytest
import os
from context import utils


## Pytest Fixtures


@pytest.fixture
def prefix():
    "Returns the path prefix"
    cwd = os.path.basename(os.getcwd())
    return "files/" if cwd == "test" else "test/files/"


## Unittests


def test_ReadFileToken(prefix):
    token = utils.ReadFileToken(token = prefix + "token/token.txt")
    assert token == "123456789:aBcDeFgH"

def test_ReadFileURL_single(prefix):
    url = utils.ReadFileURL(urlfile = prefix + "urls/single.url")
    assert len(url) == 1
    assert url[0] == "http://example.org/"

def test_ReadFileURL_multiple(prefix):
    urls = utils.ReadFileURL(urlfile = prefix + "urls/multiple.url")
    assert len(urls) == 3
    for u in urls:
        assert u == "http://example.org/"
