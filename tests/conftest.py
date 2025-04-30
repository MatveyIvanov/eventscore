import functools
import os
from unittest import mock

import pytest


def require_env(func=None, *, name: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if name not in os.environ:
                pytest.fail(f"Missing required environment variable: {name}")
            return func(*args, **kwargs)

        return wrapper

    if func is None:
        return decorator
    return decorator(func)


@pytest.fixture
def mock_factory():
    def factory():
        return mock.Mock()

    return factory
