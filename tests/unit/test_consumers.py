import pytest


@pytest.mark.unit
class TestConsumer:
    def test_consume(self, consumer_func_mock, event, consumer):
        consumer.consume(event)

        consumer_func_mock.assert_called_once_with(event)
