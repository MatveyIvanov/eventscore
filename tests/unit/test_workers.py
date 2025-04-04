from unittest import mock

import pytest


class TestSpawnMPWorker:
    @pytest.mark.parametrize("clones", (0, 1, 2))
    def test_spawn(
        self,
        clones,
        mp_mock,
        mp_process_mock,
        worker_factory,
        spawn_mp_worker,
    ):
        worker = worker_factory(clones=clones)

        with mock.patch("eventscore.core.workers.mp", mp_mock):
            spawn_mp_worker(worker)

        mp_mock.Process.assert_has_calls(
            [mock.call(target=worker.runner.run, daemon=True)] * clones
        )
        mp_process_mock.start.assert_has_calls([mock.call()] * clones)
