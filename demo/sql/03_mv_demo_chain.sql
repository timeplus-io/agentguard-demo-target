CREATE MATERIALIZED VIEW IF NOT EXISTS ag.mv_demo_chain
INTO ag.agentguard_security_events AS
WITH staged AS (
  SELECT event_time, agent_id, deployment_id, session_id, run_id,
    multi_if(
      event_type = 'tool_complete' AND tool_name IN ('WebFetch', 'WebSearch'), 'probe',
      event_type = 'tool_complete' AND (lower(tool_result) LIKE '%ignore previous instructions%'
                                     OR lower(tool_result) LIKE '%ignore all previous%'), 'injection',
      event_type = 'tool_invoke' AND match(lower(tool_input), '(credentials|id_rsa|id_ed25519|\\.env\\b|private key)'), 'credential_access',
      event_type = 'tool_invoke' AND match(lower(tool_input), '\\bcurl\\b.*(--data|-d @|--upload-file)'), 'exfiltration',
      '') AS stage
  FROM ag.agentguard_cim_event
)
SELECT
  window_end AS detected_at,
  'demo-chain' AS rule_id,
  'Attack Chain: probe → injection → exfiltration' AS rule_name,
  'critical' AS severity,
  any(agent_id) AS agent_id,
  any(deployment_id) AS deployment_id,
  session_id,
  any(run_id) AS run_id,
  'chain' AS hook_name,
  '' AS tool_name,
  concat('Attack chain in session ', session_id, ': probe → injection → exfiltration') AS message,
  '' AS event_data
FROM hop(staged, event_time, 1m, 10m)
WHERE stage != ''
GROUP BY window_end, session_id
HAVING count_if(stage = 'probe') > 0
   AND count_if(stage = 'injection') > 0
   AND count_if(stage = 'exfiltration') > 0
   AND min_if(event_time, stage = 'probe') < min_if(event_time, stage = 'exfiltration')
