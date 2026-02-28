from langchain_core.tools import tool
from memory import conversation_memory, context_manager
from utils import logger


@tool
def retrieve_memory(session_id: str, query: str = "") -> str:
    """
    Retrieve conversation history and context for the current session.
    
    Args:
        session_id: The session identifier
        query: Optional specific query about past conversation
        
    Returns:
        Formatted conversation history or specific information
    """
    try:
        logger.info(f"Retrieving memory for session: {session_id}")
        
        # Check if session exists
        if not conversation_memory.session_exists(session_id):
            return "No conversation history found for this session."
        
        # If specific query is provided, try to find relevant context
        if query:
            history = conversation_memory.get_history(session_id)
            
            # Simple keyword matching (can be enhanced)
            relevant_messages = []
            query_lower = query.lower()
            
            for msg in history:
                if query_lower in msg["content"].lower():
                    relevant_messages.append(msg)
            
            if relevant_messages:
                result = f"Found {len(relevant_messages)} relevant message(s):\n\n"
                for msg in relevant_messages:
                    result += f"{msg['role'].upper()}: {msg['content']}\n\n"
                return result.strip()
            else:
                return f"No messages found matching '{query}'"
        
        # Otherwise return recent context
        context = context_manager.get_context_for_agent(session_id, include_last_n=5)
        return context
        
    except Exception as e:
        error_msg = f"Failed to retrieve memory: {str(e)}"
        logger.error(error_msg)
        return error_msg


@tool
def summarize_conversation(session_id: str) -> str:
    """
    Get a summary of the current conversation session.
    
    Args:
        session_id: The session identifier
        
    Returns:
        Summary of the conversation
    """
    try:
        logger.info(f"Summarizing conversation for session: {session_id}")
        summary = context_manager.summarize_context(session_id)
        return summary
    except Exception as e:
        error_msg = f"Failed to summarize conversation: {str(e)}"
        logger.error(error_msg)
        return error_msg