"""HTTP health checks with retries and exponential backoff."""
from __future__ import annotations

import time
from dataclasses import dataclass

import requests

from .config import Service


@dataclass
class CheckResult:
    service: str
    healthy: bool
    status: int | None
    latency_ms: float | None
    error: str | None = None


def check_service(service: Service, session: requests.Session | None = None,
                  sleep=time.sleep) -> CheckResult:
    http = session or requests.Session()
    last_error, status = None, None
    for attempt in range(service.retries):
        started = time.perf_counter()
        try:
            resp = http.get(service.url, timeout=service.timeout)
            latency = (time.perf_counter() - started) * 1000
            status = resp.status_code
            if status == service.expected_status:
                return CheckResult(service.name, True, status, round(latency, 1))
            last_error = f"unexpected status {status}"
        except requests.RequestException as exc:
            last_error, status = str(exc), None
        if attempt < service.retries - 1:
            sleep(2 ** attempt * 0.5)
    return CheckResult(service.name, False, status, None, last_error)


def check_all(services: list[Service], **kwargs) -> list[CheckResult]:
    return [check_service(s, **kwargs) for s in services]
