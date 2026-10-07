CREATE MATERIALIZED VIEW IF NOT EXISTS ag.mv_rule_demo003
INTO ag.agentguard_security_events AS
SELECT
  event_time AS detected_at,
  'demo-003' AS rule_id,
  'Outbound Data Transfer' AS rule_name,
  'critical' AS severity,
  agent_id, deployment_id, session_id, run_id,
  raw_hook_name AS hook_name,
  tool_name,
  concat('Outbound upload via ', tool_name, ' by agent ', agent_id) AS message,
  raw_event_data AS event_data
FROM ag.agentguard_cim_event
WHERE event_type = 'tool_invoke'
  AND match(lower(tool_input), '\\b(curl|wget|nc|ncat|scp|rsync|aws s3 cp)\\b')
  AND match(lower(tool_input), '(--data|--data-binary|-d @|-T |--upload-file|\\| *(nc|ncat)\\b|s3://)')
