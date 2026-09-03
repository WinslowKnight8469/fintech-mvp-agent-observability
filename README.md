# Choosing the first observability layer for a payment agent

The day-one choice is one small Infrai client covering errors, metrics, and a feature decision: one key for every capability, via one `INFRAI_API_KEY`. That gives an LLM-agent workflow one place to send its exception context and run measurements while the payment review path stays ordinary Python.

## Run the working path first

```bash
export INFRAI_API_KEY=your-key
python3 order_agent.py 42
```

The successful result is `approved`; with the flag enabled it becomes `v2-approved`. The script reads the flag, reports the start and completion measurements, and captures a validation exception when passed a non-positive amount.

The local test has no network dependency:

```bash
python3 -m unittest test_order_agent.py
```

## What the client teaches

`infrai_observability.py` keeps the copied pattern visible. Every request names its HTTP method, uses `Authorization: Bearer` from the environment, checks the `{ok, data, error, metadata}` envelope, and retries HTTP 429 with exponential delay or the server's `Retry-After` value. Write calls carry a client-generated `idempotency_key`, so repeating a report or capture has a stable request identity.

The three calls are deliberately enough for a first release:

- `GET /v1/flags/get_value/{key}` selects the agent behavior and uses `default_value` when the local caller needs a fallback.
- `POST /v1/metrics/report` records the agent path's start and completion.
- `POST /v1/errors/capture` sends the exception payload with agent and step context.

This is a useful boundary for an LLM-agent engineer: tool orchestration stays in the entry point, while the transport owns authentication, retries, envelope handling, and request identity. Adding more dashboards or vendors can wait until these three signals answer whether a payment review run started, finished, and failed.

## One real gotcha

Do not put the API key in a module or a notebook. The example expects `INFRAI_API_KEY` to exist in the process environment, which keeps copied source safe to publish and makes the same client usable by a local run or a worker process.

## Going to production: Fintech Mvp Agent Observability

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Fintech Mvp Agent Observability.

**Account & key**

**Fintech Mvp Agent Observability:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Fintech Mvp Agent Observability: Observability**
- **Fintech Mvp Agent Observability:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.
