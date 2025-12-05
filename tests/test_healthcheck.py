import requests

from automation.config import Service
from automation.healthcheck import check_service


class FakeSession:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    def get(self, url, timeout):
        self.calls += 1
        out = self.outcomes.pop(0)
        if isinstance(out, Exception):
            raise out

        class R:
            status_code = out
        return R()


def test_healthy_first_try():
    s = FakeSession([200])
    r = check_service(Service("a", "http://x"), session=s, sleep=lambda _: None)
    assert r.healthy and r.status == 200 and s.calls == 1


def test_retries_then_succeeds():
    s = FakeSession([requests.ConnectionError("boom"), 503, 200])
    r = check_service(Service("a", "http://x"), session=s, sleep=lambda _: None)
    assert r.healthy and s.calls == 3


def test_fails_after_retries():
    s = FakeSession([503, 503, 503])
    r = check_service(Service("a", "http://x"), session=s, sleep=lambda _: None)
    assert not r.healthy and r.status == 503 and "503" in r.error
