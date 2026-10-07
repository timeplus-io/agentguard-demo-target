import json, urllib.request, base64, sys, copy, os
BASE="https://release.demo.timeplus.com/default/api/v1beta2"
DID="dda310c0-1c64-4fd9-8432-37e566e0d964"
REPO=os.path.dirname(os.path.abspath(__file__))

def _creds():
    """AGENTGUARD_USERNAME / AGENTGUARD_PASSWORD from the environment, else from ~/.claude/settings.json env."""
    u, p = os.environ.get("AGENTGUARD_USERNAME"), os.environ.get("AGENTGUARD_PASSWORD")
    if not (u and p):
        try:
            env = json.load(open(os.path.expanduser("~/.claude/settings.json"))).get("env", {})
            u, p = u or env.get("AGENTGUARD_USERNAME"), p or env.get("AGENTGUARD_PASSWORD")
        except (OSError, ValueError): pass
    if not (u and p): sys.exit("set AGENTGUARD_USERNAME and AGENTGUARD_PASSWORD (or run demo/setup.sh first)")
    return u, p
AUTH="Basic "+base64.b64encode(":".join(_creds()).encode()).decode()
def call(method, path, body=None, timeout=60):
    req=urllib.request.Request(BASE+path, method=method, data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization":AUTH,"content-type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r: return r.status, json.loads(r.read() or b'null')
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read() or b'{}')

st, cur = call("GET", f"/dashboards/{DID}")
assert st==200, cur
pass  # backup = shipped app dashboard (demo/dashboard.backup.json); never overwrite
print("backup saved; current panels:", [p["title"] for p in cur["panels"]])

COLORS=["#D53F8C","#8934D9","#D12D50","#F0BE3E","#ED64A6","#FF4A71","#F7775A","#9A1563"]
def ts_cfg(chart, x, ys, color="", stacked=False, legend=True, points=False):
    return {"chartType": chart, "config": {"color": color, "colors": COLORS, "dataLabel": False, "fractionDigits": 0,
        "gridlines": True, "legend": legend, "lineStyle": "curve", "points": points, "showAll": False,
        "unit": {"position": "left", "value": ""}, "xAxis": x, "xFormat": "", "xRange": "Infinity", "xTitle": "",
        "yAxis": ys, "yRange": {"max": None, "min": None}, "yTickLabel": {"maxChar": 25}, "yTitle": "",
        **({"stacked": True} if stacked else {})}}
def sv_cfg(value, color, unit=""):
    return {"chartType":"singleValue","config":{"value":value,"sparkline":False,"delta":False,
        "unit":{"value":unit,"position":"right"},"color":color,"sparklineColor":color,"increaseColor":"#D12D50",
        "decreaseColor":"#38A169","fontSize":44,"fractionDigits":0}}
def tbl_cfg(): return {"chartType":"table","config":{"columns":[],"pageSize":20}}
def pos(x,y,w,h): return {"x":x,"y":y,"w":w,"h":h,"nextX":x+w,"nextY":y+h}
DEP="'{{filter_deployment}}'"; TR="{{filter_time_range}}"
P=[]
def add(id,title,desc,p,viz_type,content,cfg): P.append({"id":id,"title":title,"description":desc,"position":p,"viz_type":viz_type,"viz_content":content,"viz_config":cfg})

# Row 0 — controls
add("ag-ctl-time","Time Range","",pos(0,0,6,1),"control","",{"chartType":"selector","target":"filter_time_range","defaultValue":"15m","inlineValues":"5m,15m,1h,6h,24h","label":"Time Range","labelWidth":35})
add("ag-ctl-deployment","Deployment","",pos(6,0,6,1),"control","",{"chartType":"selector","target":"filter_deployment","defaultValue":"dss-demo","inlineValues":"dss-demo,dss-demo-dev,local","label":"Deployment","labelWidth":35})
# Row 1 — KPIs
add("ag-kpi-sessions","Active sessions (5 min)","Distinct sessions with any event in the last 5 minutes.",pos(0,1,3,2),"chart",
    f"SELECT count(DISTINCT session_id) AS sessions FROM table(ag.agentguard_cim_event) WHERE event_time > now() - 5m AND deployment_id = {DEP}", sv_cfg("sessions","#8934D9"))
add("ag-kpi-toolcalls","Tool calls (window)","tool_invoke events in the selected time range.",pos(3,1,3,2),"chart",
    f"SELECT count() AS tool_calls FROM table(ag.agentguard_cim_event) WHERE event_type = 'tool_invoke' AND event_time > now() - {TR} AND deployment_id = {DEP}", sv_cfg("tool_calls","#D53F8C"))
add("ag-kpi-critical","Open critical threats","Threat rows with severity critical not acknowledged or cleared.",pos(6,1,3,2),"chart",
    f"SELECT count() AS critical FROM table(ag.agentguard_threats) WHERE severity = 'critical' AND (status = '' OR status = 'open') AND deployment_id = {DEP}", sv_cfg("critical","#D12D50"))
add("ag-kpi-warning","Open warnings","Threat rows with severity warning not acknowledged or cleared.",pos(9,1,3,2),"chart",
    f"SELECT count() AS warnings FROM table(ag.agentguard_threats) WHERE severity = 'warning' AND (status = '' OR status = 'open') AND deployment_id = {DEP}", sv_cfg("warnings","#F0BE3E"))
# Row 2 — live tool calls (streaming) + threats over time
add("ag-live-toolcalls","Live tool calls","Streaming: every tool the agent invokes, as it happens.",pos(0,3,6,5),"chart",
    f"SELECT event_time, tool_name, substring(tool_input, 1, 120) AS input FROM ag.agentguard_cim_event WHERE event_type = 'tool_invoke' AND deployment_id = {DEP} SETTINGS seek_to = '-15m'", tbl_cfg())
add("ag-threats-over-time","Threats over time by rule","Security events per minute, stacked by rule.",pos(6,3,6,5),"chart",
    f"SELECT window_start AS time, rule_name, count() AS events FROM tumble(table(ag.agentguard_security_events), detected_at, 1m) WHERE detected_at > now() - {TR} AND deployment_id = {DEP} GROUP BY window_start, rule_name ORDER BY time", ts_cfg("column","time",["events"],color="rule_name",stacked=True))
# Row 3 — chain status + baseline
CHAIN=("WITH staged AS (SELECT event_time, session_id, agent_id, multi_if("
 "event_type = 'tool_complete' AND tool_name IN ('WebFetch','WebSearch'), 'probe', "
 "event_type = 'tool_complete' AND (lower(tool_result) LIKE '%ignore previous instructions%' OR lower(tool_result) LIKE '%ignore all previous%'), 'injection', "
 "event_type = 'tool_invoke' AND match(lower(tool_input), '(credentials|id_rsa|id_ed25519|\\\\.env\\\\b|private key)'), 'credential_access', "
 "event_type = 'tool_invoke' AND match(lower(tool_input), '\\\\bcurl\\\\b.*(--data|-d @|--upload-file)'), 'exfiltration', '') AS stage "
 f"FROM table(ag.agentguard_cim_event) WHERE event_time > now() - {TR} AND deployment_id = {DEP}) "
 "SELECT session_id, max(stage = 'probe') AS probe, max(stage = 'injection') AS injection, max(stage = 'credential_access') AS credential_access, "
 "max(stage = 'exfiltration') AS exfiltration, min(event_time) AS first_seen, max(event_time) AS last_seen FROM staged WHERE stage != '' GROUP BY session_id ORDER BY last_seen DESC LIMIT 20")
add("ag-chain-status","Attack chain by session","probe → injection → credential access → exfiltration, per session (1 = stage observed).",pos(0,8,6,4),"chart",CHAIN,tbl_cfg())
BASE_SQL=("WITH per_min AS (SELECT to_start_of_minute(event_time) AS m, count() AS calls FROM table(ag.agentguard_cim_event) WHERE event_type = 'tool_invoke' AND event_time > now() - {TR} AND deployment_id = {DEP} GROUP BY m ORDER BY m), "
 "raw AS (SELECT m AS time, calls, avg(calls) OVER (ORDER BY m ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING) AS base, stddev_pop(calls) OVER (ORDER BY m ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING) AS sd FROM per_min), "
 "banded AS (SELECT time, to_float64(calls) AS calls_v, if_not_finite(base, to_float64(calls)) AS baseline, if_not_finite(sd, 0.0) AS sd FROM raw) "
 "SELECT time, 'calls' AS series, calls_v AS value FROM banded UNION ALL SELECT time, 'baseline' AS series, round(baseline, 1) AS value FROM banded UNION ALL SELECT time, 'upper (mean + 3σ)' AS series, round(baseline + 3 * sd, 1) AS value FROM banded ORDER BY time, series")
BASE_SQL=BASE_SQL.replace("{TR}", TR).replace("{DEP}", DEP)
add("ag-rate-baseline","Tool-call rate vs trailing baseline","Calls per minute against the trailing mean and mean + 3σ of the previous hour.",pos(6,8,6,4),"chart",BASE_SQL,ts_cfg("line","time",["value"],color="series",legend=True))
# Row 4 — events per minute + top tools
add("ag-events-per-minute","Events per minute by agent type","Normalized CIM events per minute.",pos(0,12,7,4),"chart",
    f"SELECT window_start AS time, agent_type, count() AS events FROM tumble(table(ag.agentguard_cim_event), event_time, 1m) WHERE event_time > now() - {TR} AND deployment_id = {DEP} GROUP BY window_start, agent_type ORDER BY time", ts_cfg("line","time",["events"],color="agent_type"))
add("ag-top-tools","Top tools","Most invoked tools in the selected time range.",pos(7,12,5,4),"chart",
    f"SELECT tool_name, count() AS calls FROM table(ag.agentguard_cim_event) WHERE event_type = 'tool_invoke' AND event_time > now() - {TR} AND deployment_id = {DEP} GROUP BY tool_name ORDER BY calls DESC LIMIT 10", ts_cfg("bar","tool_name",["calls"],legend=False) | {"config": {**ts_cfg("bar","tool_name",["calls"],legend=False)["config"], "yTickLabel": {"maxChar": 48}}})
# Row 5 — open threats by severity + recent threats
add("ag-threats-by-severity","Open threats by severity","",pos(0,16,4,4),"chart",
    f"SELECT severity, count() AS threats FROM table(ag.agentguard_threats) WHERE (status = '' OR status = 'open') AND deployment_id = {DEP} GROUP BY severity ORDER BY severity", ts_cfg("column","severity",["threats"],legend=False))
add("ag-recent-threats","Recent threats","One row per (agent, session, rule); folded by mv_threats.",pos(4,16,8,4),"chart",
    f"SELECT last_seen, severity, rule_id, rule_name, agent_id, session_id, if(status = '', 'open', status) AS status FROM table(ag.agentguard_threats) WHERE last_seen > now() - {TR} AND deployment_id = {DEP} ORDER BY last_seen DESC LIMIT 25", tbl_cfg())
# Row 6 — sessions + how it works
add("ag-sessions","Sessions","Per session: first/last event, tool calls, threats.",pos(0,20,8,4),"chart",
    f"SELECT e.session_id AS session_id, any(e.agent_id) AS agent_id, min(e.event_time) AS first_seen, max(e.event_time) AS last_seen, count_if(e.event_type = 'tool_invoke') AS tool_calls, any(t.threats) AS threats FROM table(ag.agentguard_cim_event) AS e LEFT JOIN (SELECT session_id, count() AS threats FROM table(ag.agentguard_threats) GROUP BY session_id) AS t ON e.session_id = t.session_id WHERE e.event_time > now() - {TR} AND e.deployment_id = {DEP} GROUP BY e.session_id ORDER BY last_seen DESC LIMIT 20", tbl_cfg())
add("ag-how","How this works","",pos(8,20,4,4),"markdown","",{"mdString": "**Claude Code hooks → `ag.agentguard_hook_events` → CIM normalizer MVs → `ag.agentguard_cim_event` → rule MVs (`mv_rule_*`) → `ag.agentguard_security_events` → `mv_threats` → `ag.agentguard_threats`**\n\nEvery rule is a `CREATE MATERIALIZED VIEW … AS SELECT … WHERE …`. Pause one with `SYSTEM PAUSE MATERIALIZED VIEW ag.mv_rule_rp002`.\n\nDemo rules: `demo-001` indirect prompt injection in tool results · `demo-003` outbound data transfer · `demo-chain` probe → injection → exfiltration in a 10-minute session window · `demo-004` tool-call burst.\n\nApp: github.com/timeplus-io/apps/tree/main/apps/agentguard"})

# Validate SQL
bad=0
for p in P:
    sql=p["viz_content"]
    if p["viz_type"]!="chart": continue
    s=sql.replace("{{filter_time_range}}","15m").replace("{{filter_deployment}}","local")
    if "table(" in s:
        st,r=call("POST","/exec",{"sql":s,"type":"historical","timeout":55000},timeout=90)
        ok = st==200 and (r is None or "data" in r)
        print(("OK  " if ok else "FAIL"), p["id"], "" if ok else r.get("message",r))
    else:
        st,r=call("POST","/sqlanalyze",{"sql":s})
        ok = st==200 and r.get("is_streaming") is True
        print(("OK  " if ok else "FAIL"), p["id"], "(streaming)", "" if ok else r)
    bad += (not ok)
if bad or "--dry" in sys.argv:
    print("not publishing; failures:", bad); sys.exit(1)
body={"name":"AgentGuard Overview","description":"Live view of AI coding agents: tool calls, detections, attack chains and baselines. Filter by deployment (dss-demo for the DSS 2026 demo).","panels":P}
st,r=call("PUT",f"/dashboards/{DID}",body)
print("PUT", st, r if st!=200 else "ok")
json.dump(body, open(f"{REPO}/dashboard.json","w"), indent=1)
