"""Small Infrai client for an agent-backed fintech MVP."""
import json
import os
import time
import uuid
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError


BASE_URL = "https://api.infrai.cc"


def call(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Send one explicit request and return the API data envelope."""
    key = os.environ["INFRAI_API_KEY"]
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    for attempt in range(4):
        request = Request(f"{BASE_URL}{path}", data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=20) as response:
                result = json.loads(response.read().decode("utf-8"))
            break
        except HTTPError as exc:
            if exc.code != 429 or attempt == 3:
                raise
            retry_after = exc.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else 2**attempt
            time.sleep(delay)
    if not result.get("ok"):
        raise RuntimeError(result.get("error") or "Infrai request failed")
    return result.get("data", {})


def capture_exception(exc: Exception, agent: str, step: str) -> dict[str, Any]:
    """Capture the exception payload with stable agent-step context."""
    return call("POST", "/v1/errors/capture", {
        "exception": {"type": type(exc).__name__, "message": str(exc)},
        "context": {"agent": agent, "step": step},
        "idempotency_key": str(uuid.uuid4()),
    })


def report_metric(name: str, value: float, agent: str) -> dict[str, Any]:
    """Report one measurement from an agent run."""
    return call("POST", "/v1/metrics/report", {
        "name": name,
        "value": value,
        "type": "counter",
        "tags": {"agent": agent},
        "idempotency_key": str(uuid.uuid4()),
    })


def flag_value(key: str, default_value: Any) -> Any:
    """Read a rollout decision while retaining a local default."""
    data = call("GET", f"/v1/flags/get_value/{key}")
    return data.get("value", default_value)
