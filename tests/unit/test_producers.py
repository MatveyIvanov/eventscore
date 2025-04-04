import pytest


class TestProducer:
    @pytest.mark.parametrize("block", (False, True))
    @pytest.mark.parametrize("timeout", (0, 1))
    def test_produce(self, block, timeout, ecore_mock, event, producer):
        producer.produce(event, block=block, timeout=timeout)

        ecore_mock.stream.put.assert_called_once_with(
            event=event,
            block=block,
            timeout=timeout,
        )
