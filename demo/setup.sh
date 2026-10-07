#!/usr/bin/env bash
# One-shot setup for the DSS 2026 AgentGuard demo laptop.
#
#   ./demo/setup.sh              install the hook plugin, wire it into ~/.claude/settings.json, check the stack
#   ./demo/setup.sh --verify     show the last hook events this laptop sent to the stack (run after a session)
#   ./demo/setup.sh --uninstall  remove the agentguard-hook entries and AGENTGUARD_* env from settings.json
#
# Credentials: pass AGENTGUARD_USERNAME / AGENTGUARD_PASSWORD in the environment, or answer the prompt.
# Idempotent: re-running updates env values and never duplicates hook entries. settings.json is backed up first.
set -euo pipefail

PLUGIN="@timeplus/agentguard-claudecode-plugin@0.4.1"
STACK="${AGENTGUARD_TIMEPLUS_URL:-https://release.demo.timeplus.com}"
SETTINGS="${CLAUDE_SETTINGS:-$HOME/.claude/settings.json}"
AGENT_ID="${AGENTGUARD_AGENT_ID:-$(hostname)}"
MODE="${1:-install}"

say()  { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31merror:\033[0m %s\n' "$*" >&2; exit 1; }

need_creds() {
  if [ -z "${AGENTGUARD_USERNAME:-}" ]; then read -r -p "Timeplus username for $STACK: " AGENTGUARD_USERNAME; fi
  if [ -z "${AGENTGUARD_PASSWORD:-}" ]; then read -r -s -p "Timeplus password: " AGENTGUARD_PASSWORD; echo; fi
  [ -n "$AGENTGUARD_USERNAME" ] && [ -n "$AGENTGUARD_PASSWORD" ] || fail "username and password are required"
  export AGENTGUARD_USERNAME AGENTGUARD_PASSWORD
}

# POST a historical SQL query to the stack, print the result rows as JSON.
query() {
  python3 - "$STACK" "$1" <<'PY'
import base64, json, os, sys, urllib.request
stack, sql = sys.argv[1], sys.argv[2]
auth = base64.b64encode(f"{os.environ['AGENTGUARD_USERNAME']}:{os.environ['AGENTGUARD_PASSWORD']}".encode()).decode()
req = urllib.request.Request(f"{stack}/default/api/v1beta2/exec",
    data=json.dumps({"sql": sql, "type": "historical"}).encode(),
    headers={"Content-Type": "application/json", "Authorization": "Basic " + auth})
try:
    body = urllib.request.urlopen(req, timeout=20).read().decode()
except urllib.error.HTTPError as e:
    sys.exit(f"stack returned HTTP {e.code}: {e.read().decode()[:200]}")
print(body)
PY
}

case "$MODE" in
  install)
    say "Checking prerequisites"
    command -v node >/dev/null || fail "Node.js >= 18 is required (brew install node)"
    command -v claude >/dev/null || fail "Claude Code CLI not found (https://code.claude.com)"
    command -v python3 >/dev/null || fail "python3 is required"

    if command -v agentguard-hook >/dev/null; then
      say "agentguard-hook already installed ($(npm ls -g @timeplus/agentguard-claudecode-plugin 2>/dev/null | grep -o 'plugin@[0-9.]*' || echo unknown))"
    else
      say "Installing $PLUGIN globally"
      npm install -g "$PLUGIN"
      command -v agentguard-hook >/dev/null || fail "agentguard-hook is not on PATH after install; add the npm global bin dir to PATH"
    fi

    need_creds
    say "Checking stack access at $STACK"
    query "SELECT count() AS mvs FROM system.tables WHERE database = 'ag' AND name IN ('mv_rule_demo001','mv_rule_demo003','mv_demo_chain','mv_rule_demo004')" \
      | python3 -c 'import json,sys; n=int(json.load(sys.stdin)["data"][0][0]); print(f"    demo rules on stack: {n}/4" + ("" if n==4 else "  <-- run demo/sql/0*.sql in the Console"))'

    say "Wiring hooks and env into $SETTINGS"
    mkdir -p "$(dirname "$SETTINGS")"
    [ -f "$SETTINGS" ] && cp "$SETTINGS" "$SETTINGS.bak.$(date +%Y%m%d%H%M%S)" && echo "    backup written next to it"
    STACK="$STACK" AGENT_ID="$AGENT_ID" python3 - "$SETTINGS" <<'PY'
import json, os, sys
path = sys.argv[1]
s = json.load(open(path)) if os.path.exists(path) else {}
EVENTS = ["SessionStart","SessionEnd","UserPromptSubmit","PreToolUse","PostToolUse",
          "PostToolUseFailure","SubagentStart","SubagentStop","Stop","PermissionDenied"]
hooks = s.setdefault("hooks", {})
for ev in EVENTS:
    entries = hooks.setdefault(ev, [])
    if any(h.get("command") == "agentguard-hook" for e in entries for h in e.get("hooks", [])):
        continue
    hook = {"type": "command", "command": "agentguard-hook"}
    if ev == "PreToolUse":
        hook["timeout"] = 600000          # synchronous: required by the hold path, harmless otherwise
    else:
        hook["async"] = True
    entries.append({"matcher": "*", "hooks": [hook]})
env = s.setdefault("env", {})
env.update({
    "AGENTGUARD_AGENT_ID": os.environ["AGENT_ID"],
    "AGENTGUARD_DEPLOYMENT_ID": "local",
    "AGENTGUARD_DEPLOYMENT_NAME": "Local Dev",
    "AGENTGUARD_INGEST_API": "rest",
    "AGENTGUARD_TIMEPLUS_URL": os.environ["STACK"],
    "AGENTGUARD_DATABASE": "ag",
    "AGENTGUARD_STREAM": "agentguard_hook_events",
    "AGENTGUARD_USERNAME": os.environ["AGENTGUARD_USERNAME"],
    "AGENTGUARD_PASSWORD": os.environ["AGENTGUARD_PASSWORD"],
    "AGENTGUARD_HOLDS_ENABLED": "false",
})
json.dump(s, open(path, "w"), indent=2); open(path, "a").write("\n")
print(f"    hooks: {len(EVENTS)} events wired; env: agent_id={env['AGENTGUARD_AGENT_ID']} deployment=local")
PY

    say "Done. Next:"
    echo "    1. ./demo/run-demo.sh            start a demo session (tagged deployment dss-demo)"
    echo "    2. ask it anything, then exit"
    echo "    3. ./demo/setup.sh --verify      confirm the events reached the stack"
    echo "    Dashboard: $STACK/default/console/dashboard/dda310c0-1c64-4fd9-8432-37e566e0d964"
    ;;

  --verify)
    need_creds
    say "Last hook events from this laptop in the past 15 minutes"
    query "SELECT to_string(_tp_time) AS t, deployment_id, hook_name, tool_name FROM table(ag.agentguard_hook_events) WHERE agent_type = 'claudecode' AND agent_id IN ('$AGENT_ID', 'dss-demo-claude') AND _tp_time > now() - 15m ORDER BY _tp_time DESC LIMIT 15" \
      | python3 -c '
import json,sys
rows=json.load(sys.stdin).get("data",[])
if not rows: sys.exit("    no events yet. Start a session with ./demo/run-demo.sh, run one prompt, then retry.")
for r in rows: print("   ", " | ".join(str(c) for c in r))
print(f"    {len(rows)} event(s) found. The hook is working.")'
    ;;

  --uninstall)
    say "Removing agentguard-hook entries and AGENTGUARD_* env from $SETTINGS"
    [ -f "$SETTINGS" ] || fail "$SETTINGS not found"
    cp "$SETTINGS" "$SETTINGS.bak.$(date +%Y%m%d%H%M%S)"
    python3 - "$SETTINGS" <<'PY'
import json, sys
path = sys.argv[1]; s = json.load(open(path))
for ev, entries in list(s.get("hooks", {}).items()):
    kept = [e for e in entries if not any(h.get("command") == "agentguard-hook" for h in e.get("hooks", []))]
    if kept: s["hooks"][ev] = kept
    else: del s["hooks"][ev]
if not s.get("hooks"): s.pop("hooks", None)
for k in [k for k in s.get("env", {}) if k.startswith("AGENTGUARD_")]: del s["env"][k]
if not s.get("env"): s.pop("env", None)
json.dump(s, open(path, "w"), indent=2); open(path, "a").write("\n")
print("    removed")
PY
    ;;

  *) fail "usage: $0 [--verify|--uninstall]" ;;
esac
