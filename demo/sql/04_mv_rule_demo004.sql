CREATE MATERIALIZED VIEW IF NOT EXISTS ag.mv_rule_demo004
INTO ag.agentguard_security_events AS
SELECT
  detected_at,
  'demo-004' AS rule_id,
  'Tool-call Burst' AS rule_name,
  'warning' AS severity,
  agent_id,
  dep AS deployment_id,
  sid AS session_id,
  sid AS run_id,
  'baseline' AS hook_name,
  '' AS tool_name,
  concat('Tool-call rate ', to_string(calls), '/min exceeds baseline (40/min) for agent ', agent_id) AS message,
  '' AS event_data
FROM (
  SELECT
    window_end AS detected_at,
    agent_id,
    any(deployment_id) AS dep,
    any(session_id) AS sid,
    count() AS calls
  FROM tumble(ag.agentguard_cim_metrics, event_time, 1m)
  WHERE metric_name = 'tool.call'
  GROUP BY window_end, agent_id
  HAVING count() > 40
)
