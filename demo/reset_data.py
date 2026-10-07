#!/usr/bin/env python3
"""Reset the DSS 2026 demo data for a clean rerun — WITHOUT dropping the demo rules.

  python3 demo/reset_data.py            # clear threats for dss-demo and dss-demo-dev (after a prompt)
  python3 demo/reset_data.py --yes      # same, no prompt
  python3 demo/reset_data.py --deployments dss-demo   # only the stage deployment

What it does, and why only this:
  * ag.agentguard_threats is a MutableStream, so demo threat rows are HARD-deleted. These are the rows
    that persist and keep the dashboard tiles / "recent threats" table showing stale state, so clearing
    them is what actually gives a clean slate for a rerun.
  * ag.agentguard_hook_events / _cim_event / _cim_metrics / _security_events are APPEND-ONLY streams on
    this stack: per-row delete is not allowed, and the only full wipe (TRUNCATE) would destroy EVERY
    deployment's history, including the presenter's `local` traffic and `prod`. So this script does NOT
    touch them. Their panels are time-windowed (last 15m), so old events disappear on their own — just
    let the previous run age out, or start the rerun and its fresh events will dominate the window.

Safety: only the deployments in ALLOWED may be targeted. `local`, `prod`, and anything else are refused,
because this is a shared, live stack. The demo rule MVs are left running (use demo/cleanup.sql to remove
them entirely after the conference).

Credentials: AGENTGUARD_USERNAME / AGENTGUARD_PASSWORD from the environment, else from ~/.claude/settings.json.
"""
import argparse, base64, json, os, sys, urllib.request, urllib.error

BASE = "https://release.demo.timeplus.com/default/api/v1beta2"
ALLOWED = {"dss-demo", "dss-demo-dev"}          # never local / prod / anything else
THREATS = "ag.agentguard_threats"


def creds():
    u, p = os.environ.get("AGENTGUARD_USERNAME"), os.environ.get("AGENTGUARD_PASSWORD")
    if not (u and p):
        try:
            env = json.load(open(os.path.expanduser("~/.claude/settings.json"))).get("env", {})
            u, p = u or env.get("AGENTGUARD_USERNAME"), p or env.get("AGENTGUARD_PASSWORD")
        except (OSError, ValueError):
            pass
    if not (u and p):
        sys.exit("set AGENTGUARD_USERNAME and AGENTGUARD_PASSWORD (or run demo/setup.sh first)")
    return u, p


AUTH = "Basic " + base64.b64encode(":".join(creds()).encode()).decode()


def call(sql, kind="historical"):
    req = urllib.request.Request(BASE + "/exec",
        data=json.dumps({"sql": sql, "type": kind}).encode(),
        headers={"Authorization": AUTH, "Content-Type": "application/json"})
    try:
        body = urllib.request.urlopen(req, timeout=30).read().decode()
        return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"stack returned HTTP {e.code}: {e.read().decode()[:300]}")


def threat_counts():
    d = call(f"SELECT deployment_id, count() FROM table({THREATS}) GROUP BY deployment_id ORDER BY 2 DESC")
    return {r[0]: r[1] for r in d.get("data", [])}


def main():
    ap = argparse.ArgumentParser(description="Reset demo threats for a clean rerun.")
    ap.add_argument("--deployments", default="dss-demo,dss-demo-dev",
                    help="comma-separated; only dss-demo / dss-demo-dev are permitted")
    ap.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    args = ap.parse_args()

    targets = [d.strip() for d in args.deployments.split(",") if d.strip()]
    bad = [d for d in targets if d not in ALLOWED]
    if bad:
        sys.exit(f"refusing to touch {bad}: only {sorted(ALLOWED)} may be reset on this shared stack")

    before = threat_counts()
    print("Threat rows by deployment (before):")
    for dep, n in before.items():
        mark = "  <- will clear" if dep in targets else "  (kept)"
        print(f"  {dep:16} {n}{mark}")
    to_clear = sum(before.get(d, 0) for d in targets)
    if to_clear == 0:
        print(f"\nNothing to clear for {targets}. Threats are already clean.")
        print("Event streams are append-only and age out of the 15m window on their own.")
        return

    if not args.yes:
        resp = input(f"\nHard-delete {to_clear} threat row(s) for {targets}? [y/N] ").strip().lower()
        if resp != "y":
            sys.exit("aborted")

    qlist = ", ".join("'" + d.replace("'", "") + "'" for d in targets)
    call(f"DELETE FROM {THREATS} WHERE deployment_id IN ({qlist})", kind="ddl")

    after = threat_counts()
    print("\nThreat rows by deployment (after):")
    for dep in sorted(set(before) | set(after)):
        print(f"  {dep:16} {after.get(dep, 0)}")
    print("\nDone. The demo rule MVs are still running (use demo/cleanup.sql to remove them).")
    print("Event history (hook/cim/security streams) is append-only; it is not deleted but ages out")
    print("of the 15-minute dashboard window. Start your rerun and the fresh events take over the view.")


if __name__ == "__main__":
    main()
