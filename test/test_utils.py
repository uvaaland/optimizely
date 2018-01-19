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
