from .conftest import safe_producer_queue


def test_safe_producer_queue():
    def producer(q):
        q.put("foo")
        return

    with safe_producer_queue(producer) as q:
        assert q.get(timeout=0.1) == "foo"
