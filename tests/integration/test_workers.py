import os
import subprocess
import textwrap

import pytest

from tests.integration.conftest import override_mp_start_method


def is_process_alive(pid: int):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:  # No such process
        return False
    except PermissionError:  # Not permitted to signal the process
        return True
    else:
        return True


@pytest.mark.integration
class TestSpawnMPWorker:
    @pytest.mark.parametrize("mp_start_method", ("fork", "spawn"))
    @pytest.mark.parametrize(
        "clones",
        (1, 2, 3, 4),
        ids=("one-clone", "two-clones", "three-clones", "four-clones"),
    )
    def test_daemon_processes(self, mp_start_method, clones):
        file = "test_daemon_processes.txt"
        code = textwrap.dedent(
            f"""
            from eventscore.core.abstract import IRunner
            from eventscore.core.types import Worker
            from eventscore.core.workers import SpawnMPWorker
            
            
            class InfiniteRunner(IRunner):
                def __init__(self):
                    pass
            
                def run(self) -> None:
                    while True:
                        pass
            
            pids = SpawnMPWorker()(Worker(name="name", runner=InfiniteRunner(), clones={clones}))
            with open("{file}", "w") as f:
                f.writelines(str(pid) + "," for pid in pids)
            """
        )
        with override_mp_start_method(mp_start_method):
            # NOTE: we cannot test that spawned processes terminate
            # after parent terminates, because in "obvious" scenario
            # pytest process is the parent one, which shouldn't be killed.
            # So, we have to spawn child process that will act like parent one
            # for spawned runners, and after its termination
            # check if runners still "running".
            p = subprocess.Popen(
                ["python", "-c", code],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            _, stderr = p.communicate()
            assert not stderr

        with open(file, "r") as f:
            pids = list(int(item) for item in f.readline().split(",")[:-1])

        assert len(pids) == clones
        assert len(pids) == len(set(pids))
        for pid in pids:
            assert not is_process_alive(pid)

        os.remove(file)
