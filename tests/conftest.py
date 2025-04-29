from unittest import mock

import pytest


@pytest.fixture
def mock_factory():
    def factory():
        return mock.Mock()

    return factory
