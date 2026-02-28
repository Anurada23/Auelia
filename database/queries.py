"""SQL queries for Snowflake operations"""

# Research Sessions
INSERT_RESEARCH_SESSION = """
INSERT INTO research_sessions (
    session_id, user_query, agent_response, research_plan, 
    sources_used, tokens_used, cost
) VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

GET_RESEARCH_SESSION = """
SELECT * FROM research_sessions 
WHERE session_id = %s
"""

GET_RECENT_SESSIONS = """
SELECT * FROM research_sessions 
ORDER BY created_at DESC 
LIMIT %s
"""

# Conversation History
INSERT_CONVERSATION_MESSAGE = """
INSERT INTO conversation_history (
    id, session_id, role, content, metadata
) VALUES (%s, %s, %s, %s, %s)
"""

GET_CONVERSATION_HISTORY = """
SELECT * FROM conversation_history 
WHERE session_id = %s 
ORDER BY created_at ASC
"""

DELETE_OLD_CONVERSATIONS = """
DELETE FROM conversation_history 
WHERE created_at < DATEADD(day, -%s, CURRENT_TIMESTAMP())
"""

# Agent Traces
INSERT_AGENT_TRACE = """
INSERT INTO agent_traces (
    id, session_id, agent_name, action, result, duration_ms
) VALUES (%s, %s, %s, %s, %s, %s)
"""

GET_AGENT_TRACES = """
SELECT * FROM agent_traces 
WHERE session_id = %s 
ORDER BY created_at ASC
"""

# Analytics Queries
GET_QUERY_STATS = """
SELECT 
    COUNT(*) as total_queries,
    AVG(tokens_used) as avg_tokens,
    AVG(cost) as avg_cost,
    MIN(created_at) as first_query,
    MAX(created_at) as last_query
FROM research_sessions
WHERE created_at >= DATEADD(day, -%s, CURRENT_TIMESTAMP())
"""

GET_TOP_QUERIES = """
SELECT 
    user_query,
    COUNT(*) as frequency
FROM research_sessions
WHERE created_at >= DATEADD(day, -%s, CURRENT_TIMESTAMP())
GROUP BY user_query
ORDER BY frequency DESC
LIMIT %s
"""

GET_AGENT_PERFORMANCE = """
SELECT 
    agent_name,
    COUNT(*) as total_actions,
    AVG(duration_ms) as avg_duration_ms
FROM agent_traces
WHERE created_at >= DATEADD(day, -%s, CURRENT_TIMESTAMP())
GROUP BY agent_name
ORDER BY total_actions DESC
"""