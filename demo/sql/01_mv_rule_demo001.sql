CREATE MATERIALIZED VIEW IF NOT EXISTS ag.mv_rule_demo001
INTO ag.agentguard_security_events AS
SELECT
  event_time AS detected_at,
  'demo-001' AS rule_id,
  'Indirect Prompt Injection' AS rule_name,
  'critical' AS severity,
  agent_id, deployment_id, session_id, run_id,
  raw_hook_name AS hook_name,
  tool_name,
  concat('Injection pattern in tool result of ', tool_name, ' from agent ', agent_id) AS message,
  raw_event_data AS event_data
FROM ag.agentguard_cim_event
WHERE event_type = 'tool_complete'
  AND tool_name IN ('WebFetch', 'WebSearch', 'Read', 'Bash')
  AND (
       lower(tool_result) LIKE '%ignore previous instructions%'
    OR lower(tool_result) LIKE '%ignore all previous%'
    OR match(lower(tool_result), '\\b(disregard|forget) (all |your )?(previous |prior )?instructions\\b')
    OR match(lower(tool_result), '\\byou are now (a|an|the)\\b')
    OR match(lower(tool_result), '\\bnew instructions:\\s')
  )
