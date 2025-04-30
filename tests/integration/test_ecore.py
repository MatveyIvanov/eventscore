import os
from unittest import mock

import pytest

from eventscore.core.ecore import ECore
from tests.conftest import require_env


@pytest.mark.integration
class TestECore:
    @pytest.mark.parametrize(
        "root,group_to_expected_items",
        (
            (
                "",
                {
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
            ),
            (
                "tests",
                {
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
            ),
            (
                "tests/integration",
                {
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
            ),
        ),
    )
    @require_env(name="ABSOLUTE_PATH_TO_PROJECT")
    def test_discover_consumers(self, root, group_to_expected_items):
        """Test only works if ran from package root"""
        ecore = ECore(stream_factory=lambda: None)

        with mock.patch(
            "eventscore.core.ecore.os.getcwd",
            # imitate process start from root, event if specific test is ran
            return_value=os.environ["ABSOLUTE_PATH_TO_PROJECT"],
        ):
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
                sorted(group_to_expected_items[group], key=lambda item: item[1]),
            ):
                assert item.func.__name__ == func_name
                assert (
                    item.func_path
                    == os.environ["ABSOLUTE_PATH_TO_PROJECT"] + "/" + func_path
                )
                assert item.event == event
                assert item.group == group
                assert item.clones == clones
