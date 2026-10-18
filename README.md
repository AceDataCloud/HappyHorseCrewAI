# HappyHorse by Ace Data Cloud for CrewAI

Independent native **HappyHorse** video tools for CrewAI. Provided by **Ace Data Cloud**, not an official HappyHorse or CrewAI product. This is a standalone service package; no all-services bundle or generic provider setup is required.

[简体中文](readme/README_zh_Hans.md) · [Current models and prices](https://platform.acedata.cloud/models?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=happyhorsecrewai_readme_pricing)

## 1. Install the correct service package

Review-preview source and wheels are being prepared. **Not yet PyPI-published or listed in the official CrewAI / AMP catalog.** The source PR/release links below will name the exact reviewed version. Do not treat a repository as an official listing.

```bash
uv add 'crewai-happyhorse @ git+https://github.com/AceDataCloud/HappyHorseCrewAI.git@REVIEWED_COMMIT'
```

Replace REVIEWED_COMMIT with the full implementation commit SHA from this repository's reviewed PR. After verified PyPI publication the standard command will be `uv add crewai-happyhorse`; do not assume it works before publication. CrewAI supports Python 3.10–3.13. Intel macOS may lack its mandatory lancedb wheel; use supported Linux rather than bypassing dependencies for production.

## 2. Register / sign in and get your own API Token

1. Open [Ace Data Cloud → Applications](https://platform.acedata.cloud/console/applications?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=happyhorsecrewai_readme_api_key); register and sign in. If needed, choose **Initialize General Application**.
2. Open **General application**, check **HappyHorse** service access, current model price and balance. A service-specific application can only use its entitled service.
3. Copy the selected API Key using icon **1**, or **Manage Keys** **2** → **Create** for a separate `HappyHorse CrewAI` key.

![Copy Key or open Manage Keys; authentic screenshot with credentials redacted](assets/tutorial/get-api-key-en.png)

4. Configure expiration and usage limits only as needed. If **Allowed APIs** is enabled, include both `/happyhorse/videos` and `/happyhorse/tasks`.

![Create a separate credential; historical example name](assets/tutorial/create-api-key-en.png)

Historical authentic Ace screenshots reused unchanged from SunoDify commit `8d3d03570e73324220f111f7fe343da0792a8071`, retrieved 2026-10-18. The second image's old name `Dify tutorial` is an example only: use `HappyHorse CrewAI`. No visible real credential is included; [image sources](assets/tutorial/source.json).

Set the raw consumer Token in environment variable `ACEDATACLOUD_API_KEY` through secure terminal input or a secret manager. It is not a `platform-...` management Token and must not include `Bearer `, spaces or quotation marks. Never place it in prompts, screenshots, committed `.env` or workflow exports. `api_key=...` may be supplied from secure credential storage and is excluded from serialization.

## 3. Add the named native tools

```python
from crewai import Agent
from happyhorse_crewai import HappyHorseGenerateVideoTool, HappyHorseRetrieveTaskTool

agent = Agent(
    role="HappyHorse producer",
    goal="Create the approved media, then retrieve the original task result",
    backstory="Use HappyHorse through Ace Data Cloud within the user's approved budget.",
    llm=your_configured_llm,
    tools=[HappyHorseGenerateVideoTool(), HappyHorseRetrieveTaskTool()],
    allow_delegation=False,
    max_retry_limit=0,
)
```

The two discoverable tool names are **HappyHorse by Ace Data Cloud - Generate Video** and **HappyHorse by Ace Data Cloud - Retrieve Task**. The Token goes in the environment, not a custom MCP header or agent prompt. Adding tools does not execute them. The caller approves paid requests; generation defaults to one use per instance to reduce duplicate submissions, which is not a funds cap or a permission system.

## 4. Service-specific input and first use

Explicit actions `generate`, `image_to_video`, `reference_to_video`, `video_edit` use prompt plus the matching image_url/image_urls/video_url; reference fields are required for those actions. Resolution is uppercase `720P/1080P`; duration 3..15; ratio, watermark, audio_setting auto/origin and seed retain service spelling. The selected public model must support that action; no automatic replacement.

Check [the current model catalog and price](https://platform.acedata.cloud/models?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=happyhorsecrewai_readme_first_use) before calling; model IDs are passed unchanged and no substitute model is added. The following values are examples from the pinned current API contract, not permanent defaults. **Executing generation is billable**; this guide does not run it.

```python
import json
from happyhorse_crewai import HappyHorseGenerateVideoTool, HappyHorseRetrieveTaskTool

parameters = {
    "model": "happyhorse-1.1-t2v",
    "prompt": "A calm sunrise over a mountain lake",
    "resolution": "720P",
    "ratio": "16:9",
    "duration": 3
}
# BILLABLE when executed; approve the current model and budget first.
submitted = HappyHorseGenerateVideoTool().run(**parameters)
submitted = json.loads(submitted)  # A ToolFailure must be handled before this step.
task_id = submitted["task_id"]
result = HappyHorseRetrieveTaskTool().run(task_id=task_id, wait_seconds=240)
print(result)
```

The request submits once with `async=true`. accepted/pending is **not** a terminal result, even when an envelope has success=true. Preserve the original task ID; pending, timeouts or unknown submission outcomes do not authorize another generation. Bounded wait only queries that same ID, and can include an in-flight request timeout. Continue using Retrieve Task until terminal status. A true completed response requires the stored finished_at, service success and a valid target media URL. Nested failed states are treated as failure; a missing terminal media link is not fake success.

For a task you already own, run only this read-only example:

```bash
uv run python examples/query_existing.py YOUR_EXISTING_TASK_ID
```

The query is `POST /happyhorse/tasks` with `action=retrieve,id=...`. A completed result returns `status=succeeded`, `success=true`, `task_id`, filtered `media_urls` and original `cost` in Credits when present. No raw original prompt, request, account/application identity, internal diagnostics or unfiltered body is returned. `cost` is not a new bill or USD amount. URL presence does not verify ongoing media playback.

## 5. Inspect execution and output

![Official historical CrewAI execution trace; not this service or Ace runtime evidence](assets/tutorial/official-crewai-tracing.png)

Official [CrewAI tracing reference](https://docs.crewai.com/en/observability/tracing), historical date marker 10/1/2025, capture version unspecified; retrieved 2026-10-18. Left: task and tool timeline; right: expanded Response output, not input. **Not this package running, not an Ace task and not a promised new GUI.** Trace account/auth/consent is optional and not enabled by this package. For your actual run inspect the named tool and its returned terminal fields; never expose Token or private media URLs in screenshots.

## Troubleshooting, privacy and cost

| Result | Action |
|---|---|
| 401 / 403 | Check full raw consumer Token, expiration, service entitlement, Allowed APIs and balance. A 403 is not always moderation. |
| 400 / schema rejection | Follow this service's fields, casing and model capability; unknown cross-service fields are rejected before network. |
| pending / no media yet | Query the same original task ID; never regenerate to poll. |
| 429 | Reduce concurrency and wait. One HTTP attempt per operation; your configured LLM/agent may retry separately. |
| Timeout / 5xx | Submission outcome can be unknown. Inspect request history before creating another task. |
| ToolFailure | Failed task or invalid terminal media; structured non-retryable result. Preserve task/trace ID for support, never Key. |
| Result URL cannot open | Check terminal success and your network; link existence alone is not playback evidence. |

The code is free; media generation and the LLM you configure have their current prices. No payment handler, fallback or automatic paid HTTP retry is added. Original Credits cost follows the API's current package/account rate and discounts; this package does not hard-code USD conversion. No install/CI count is presented as users or revenue.

Provided prompts/references and the consumer Token are sent to `api.acedata.cloud` over HTTPS. The package adds no telemetry or tracing; CrewAI/your LLM may have separate settings. [Privacy](PRIVACY.md). [Source](https://github.com/AceDataCloud/HappyHorseCrewAI) · [Issues](https://github.com/AceDataCloud/HappyHorseCrewAI/issues) · dev@acedata.cloud

Development: `uv sync --group dev`, `uv run pytest`, `uv run ruff check .`, `uv build`. Paid HTTP is mocked in tests; native Agent/Task/Crew cycles use a deterministic local model fixture. See `tests/contract-source.json` for immutable service contract provenance and `tests/live-readonly-evidence.json` when an old-task check is available. No new paid request runs in CI.
