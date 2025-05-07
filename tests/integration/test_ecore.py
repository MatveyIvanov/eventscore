import os
from typing import Literal
from unittest import mock

import pytest

from eventscore.core.ecore import ECore
from eventscore.core.exceptions import NotADirectoryError, NotAPackageError, PathError
from tests.conftest import require_env

DiscoverableScope = Literal["all", "single"]

ScopeToConsumers = {
    "single": {
        "group": [
            (
                "consumer_ecore",
                "tests/integration/discoverable/single.py:consumer_ecore",
                "event",
                "group",
                1,
            ),
            (
                "consumer",
                "tests/integration/discoverable/single.py:consumer",
                "event",
                "group",
                1,
            ),
        ]
    },
    "multiple": {
        "multiple-group1": [
            (
                "consumer1",
                "tests/integration/discoverable/multiple/group1.py:consumer1",
                "event1",
                "multiple-group1",
                1,
            ),
            (
                "consumer2",
                "tests/integration/discoverable/multiple/group1.py:consumer2",
                "event2",
                "multiple-group1",
                1,
            ),
        ],
        "multiple-group2": [
            (
                "consumer1",
                "tests/integration/discoverable/multiple/group2.py:consumer1",
                "event1",
                "multiple-group2",
                1,
            ),
            (
                "consumer2",
                "tests/integration/discoverable/multiple/group2.py:consumer2",
                "event2",
                "multiple-group2",
                1,
            ),
        ],
    },
}


def consumers_by_scope(scope: DiscoverableScope):
    if scope != "all":
        return ScopeToConsumers[scope]
    result = {}
    for key, value in ScopeToConsumers.items():
        result.update(value)
    return result


@pytest.mark.integration
class TestECore:
    @pytest.mark.parametrize(
        "root,group_to_expected_items,expected_error",
        (
            ("", consumers_by_scope("all"), NotAPackageError),
            ("unknown", consumers_by_scope("all"), PathError),
            ("tests", consumers_by_scope("all"), None),
            ("tests/integration", consumers_by_scope("all"), None),
            ("tests/integration/discoverable", consumers_by_scope("all"), None),
            (
                "tests/integration/discoverable/single.py",
                consumers_by_scope("all"),
                NotADirectoryError,
            ),
            (
                "tests/integration/discoverable/multiple",
                consumers_by_scope("multiple"),
                None,
            ),
            (
                "tests/integration/discoverable/notapackage",
                consumers_by_scope("all"),
                NotAPackageError,
            ),
        ),
        ids=(
            "root-directory-not-a-package",
            "directory-does-not-exist",
            "package-with-all-consumers",
            "sub-package-with-all-consumers",
            "sub-sub-package-with-all-consumers",
            "not-a-directory",
            "multiple-scope",
            "not-a-package",
        ),
    )
    @require_env(name="ABSOLUTE_PATH_TO_PROJECT")
    def test_discover_consumers(self, root, group_to_expected_items, expected_error):
        ecore = ECore(stream_factory=lambda: None)

        with mock.patch(
            "eventscore.core.ecore.os.getcwd",
            # imitate process start from root, event if specific test is ran
            return_value=os.environ["ABSOLUTE_PATH_TO_PROJECT"],
        ):
            if expected_error:
                with pytest.raises(expected_error):
                    ecore.discover_consumers(root=root)
                for group, items in group_to_expected_items.items():
                    assert len(ecore._ECore__pipelines[group].items) == 0
            else:
                ecore.discover_consumers(root=root)

                for group, items in group_to_expected_items.items():
                    assert len(ecore._ECore__pipelines[group].items) == len(
                        group_to_expected_items[group]
                    )
                    for item, (func_name, func_path, event, group_, clones) in zip(
                        sorted(
                            ecore._ECore__pipelines[group].items,
                            key=lambda item: item.func_path,
                        ),
                        sorted(
                            group_to_expected_items[group],
                            key=lambda item: item[1],
                        ),
                    ):
                        assert item.func.__name__ == func_name
                        assert (
                            item.func_path
                            == os.environ["ABSOLUTE_PATH_TO_PROJECT"] + "/" + func_path
                        )
                        assert item.event == event
                        assert item.group == group
                        assert item.clones == clones
