-- Removes everything the DSS 2026 demo added to release.demo.timeplus.com (database ag).
DROP VIEW IF EXISTS ag.mv_rule_demo001;
DROP VIEW IF EXISTS ag.mv_rule_demo003;
DROP VIEW IF EXISTS ag.mv_demo_chain;
DROP VIEW IF EXISTS ag.mv_rule_demo004;
-- Demo threat rows (mutable stream, hard delete):
DELETE FROM ag.agentguard_threats WHERE deployment_id = 'dss-demo' OR rule_id IN ('demo-001','demo-003','demo-chain','demo-004');
-- Append-only streams keep history; demo rows are identifiable by deployment_id = 'dss-demo'.
-- The dashboard "AgentGuard Overview" (dda310c0-1c64-4fd9-8432-37e566e0d964) was edited in place;
-- demo/dashboard.backup.json holds the pre-demo version for restore via PUT.
