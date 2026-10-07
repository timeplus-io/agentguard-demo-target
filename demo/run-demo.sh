#!/usr/bin/env bash
# Starts Claude Code for the DSS 2026 AgentGuard demo.
#  - HOME is redirected to sandbox-home/ so the planted fake credentials are the only ones the agent can reach.
#  - A temporary .claude/settings.local.json tags THIS session as deployment "dss-demo" (ordinary sessions in
#    this repo are tagged "dss-demo-dev" by .claude/settings.json, so development traffic stays off the demo view).
set -euo pipefail
cd "$(dirname "$0")/.."
REAL_HOME="$HOME"
LOCAL=".claude/settings.local.json"
cat > "$LOCAL" <<'JSON'
{ "env": { "AGENTGUARD_AGENT_ID": "dss-demo-claude", "AGENTGUARD_DEPLOYMENT_ID": "dss-demo", "AGENTGUARD_DEPLOYMENT_NAME": "DSS 2026 Demo" } }
JSON
export HOME="$PWD/sandbox-home"
trap 'rm -f "$LOCAL" "$HOME/Library/Keychains"' EXIT
mkdir -p "$HOME/.claude"
# Reuse the presenter's Claude Code auth and global settings (the AgentGuard hooks live in ~/.claude/settings.json).
for f in settings.json .credentials.json; do
  [ -e "$REAL_HOME/.claude/$f" ] && [ ! -e "$HOME/.claude/$f" ] && ln -sf "$REAL_HOME/.claude/$f" "$HOME/.claude/$f"
done
# macOS keeps the Claude Code OAuth token in the login keychain, which is looked up under $HOME/Library/Keychains.
# Without this link Claude Code cannot see or save its login ("Couldn't save your login ... keychain is locked").
if [ -d "$REAL_HOME/Library/Keychains" ]; then
  mkdir -p "$HOME/Library"
  ln -sfn "$REAL_HOME/Library/Keychains" "$HOME/Library/Keychains"
fi
echo "HOME=$HOME  deployment=dss-demo  stack=https://release.demo.timeplus.com"
claude "$@"
