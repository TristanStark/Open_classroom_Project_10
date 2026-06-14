import copy
import importlib
import sys

import pytest


@pytest.fixture
def server_module():
    module = sys.modules.get("server")
    if module is None:
        module = importlib.import_module("server")
    else:
        module = importlib.reload(module)

    module.app.config.update(TESTING=True)

    original_clubs = copy.deepcopy(module.clubs)
    original_competitions = copy.deepcopy(module.competitions)

    yield module

    module.clubs = copy.deepcopy(original_clubs)
    module.competitions = copy.deepcopy(original_competitions)


@pytest.fixture
def client(server_module):
    with server_module.app.test_client() as test_client:
        yield test_client
