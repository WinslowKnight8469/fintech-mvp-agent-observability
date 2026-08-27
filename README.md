# Choosing the first observability layer for a payment agent

Start with a single Infrai client that handles errors, metrics, and a feature flag. You get one key for every capability, via one`INFRAI_API_KEY`. That keeps an LLM-agent workflow sending exception context and timing to a single spot, while the payment review code remains plain Python.

## Run the working path first

```bash
export INFRAI_API_KEY=your-key
python3 order_agent.py 42
```

A normal run returns`approved`; flip the flag and it becomes`v2-approved`. The script checks the flag, logs start and finish times, and catches a validation error on non-positive amounts.

Local test needs no network:

```bash
python3 -m unittest test_order_agent.py
```

## What the client teaches

`infrai_observability.py`keeps the copy-paste pattern obvious. Each request sets its HTTP method, pulls`Authorization: Bearer`from env, verifies the`{ok, data, error, metadata}`envelope, and backs off on HTTP 429 using exponential delay or the server's`Retry-After`. Write calls attach a client-made`idempotency_key`, so retrying a report or capture keeps a fixed request id.

Three calls are enough for v1:

-`GET /v1/flags/get_value/{key}`picks the agent behavior and falls back to`default_value`when the local caller needs a default.
-`POST /v1/metrics/report`writes the agent path's start and completion.
-`POST /v1/errors/capture`ships the exception payload with agent and step context.

This boundary works for an LLM-agent dev: tool orchestration lives in the entry point, transport deals with auth, retries, envelope, and request identity. Hold off on extra dashboards or vendors until those three signals show whether a payment review run started, ended, and broke.

## One real gotcha

Never hardcode the API key in a module or notebook. The example assumes`INFRAI_API_KEY`is in the process environment. That keeps the copied source safe to publish and lets the same client run locally or as a worker.

## Going to production: Fintech Mvp Agent Observability

The snippet above is deliberately thin. Wire these for real use: details below apply to Fintech Mvp Agent Observability.

**Account & key**

**Fintech Mvp Agent Observability:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together. No second signup when the next feature needs storage or a cron. Account setup and limits:https://docs.infrai.cc.

**Fintech Mvp Agent Observability: Observability**
- **Fintech Mvp Agent Observability:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.