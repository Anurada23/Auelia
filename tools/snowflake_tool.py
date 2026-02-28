from langchain_core.tools import tool
from database import snowflake_client, queries
from utils import logger, get_timestamp, generate_message_id
import json


@tool
def save_to_snowflake(
    session_id: str, 
    user_query: str, 
    agent_response: str,
    research_plan: str = "",
    sources_used: str = "",
    tokens_used: int = 0,
    cost: float = 0.0
) -> str:
    """
    Save research session data to Snowflake.
    
    Args:
        session_id: Session identifier
        user_query: The user's original query
        agent_response: The agent's response
        research_plan: The research plan created
        sources_used: Sources that were consulted
        tokens_used: Number of tokens consumed
        cost: Cost of the operation
        
    Returns:
        Success or error message
    """
    try:
        logger.info(f"Saving session {session_id} to Snowflake")
        
        snowflake_client.execute_write(
            queries.INSERT_RESEARCH_SESSION,
            (session_id, user_query, agent_response, research_plan, 
             sources_used, tokens_used, cost)
        )
        
        return f"Successfully saved session {session_id} to Snowflake"
        
    except Exception as e:
        error_msg = f"Failed to save to Snowflake: {str(e)}"
        logger.error(error_msg)
        return error_msg


@tool
def save_conversation_to_snowflake(session_id: str, messages: list) -> str:
    """
    Save conversation history to Snowflake.
    
    Args:
        session_id: Session identifier
        messages: List of message dictionaries
        
    Returns:
        Success or error message
    """
    try:
        logger.info(f"Saving conversation history for {session_id} to Snowflake")
        
        saved_count = 0
        for msg in messages:
            message_id = msg.get('id', generate_message_id())
            role = msg.get('role')
            content = msg.get('content')
            metadata = json.dumps(msg.get('metadata', {}))
            
            snowflake_client.execute_write(
                queries.INSERT_CONVERSATION_MESSAGE,
                (message_id, session_id, role, content, metadata)
            )
            saved_count += 1
        
        return f"Successfully saved {saved_count} messages to Snowflake"
        
    except Exception as e:
        error_msg = f"Failed to save conversation: {str(e)}"
        logger.error(error_msg)
        return error_msg


@tool
def query_past_sessions(limit: int = 10) -> str:
    """
    Query recent research sessions from Snowflake.
    
    Args:
        limit: Maximum number of sessions to retrieve
        
    Returns:
        Formatted list of past sessions
    """
    try:
        logger.info(f"Querying last {limit} sessions from Snowflake")
        
        results = snowflake_client.execute_query(
            queries.GET_RECENT_SESSIONS,
            (limit,)
        )
        
        if not results:
            return "No past sessions found."
        
        output = f"Found {len(results)} recent session(s):\n\n"
        for session in results:
            output += f"Session: {session['SESSION_ID']}\n"
            output += f"Query: {session['USER_QUERY'][:100]}...\n"
            output += f"Date: {session['CREATED_AT']}\n\n"
        
        return output.strip()
        
    except Exception as e:
        error_msg = f"Failed to query sessions: {str(e)}"
        logger.error(error_msg)
        return error_msg