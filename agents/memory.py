from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings, MEMORY_AGENT_PROMPT
from memory import conversation_memory, context_manager
from utils import logger
from typing import Dict, Any


class MemoryAgent:
    """
    The Memory Agent manages conversation context.
    It retrieves relevant history and maintains session state.
    """
    
    def __init__(self):
        self.model = ChatGroq(
            model=settings.model_name,
            temperature=settings.model_temperature,
            api_key=settings.groq_api_key
        )
        self.system_prompt = MEMORY_AGENT_PROMPT
        self.memory = conversation_memory
        self.context_mgr = context_manager
    
    def get_relevant_context(self, session_id: str, current_query: str) -> Dict[str, Any]:
        """
        Retrieve relevant context for the current query
        
        Args:
            session_id: Session identifier
            current_query: Current user query
            
        Returns:
            Dictionary with context and metadata
        """
        try:
            logger.info(f"Memory Agent: Retrieving context for session {session_id}")
            
            # Get conversation history
            history = self.memory.get_history(session_id)
            
            if not history:
                logger.info("Memory Agent: No history found")
                return {
                    "context": "No previous conversation history.",
                    "has_history": False,
                    "agent": "memory",
                    "success": True
                }
            
            # Format context
            formatted_context = self.context_mgr.get_context_for_agent(
                session_id, 
                include_last_n=5
            )
            
            # Use LLM to determine relevance and summarize if needed
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"""Current Query: {current_query}

Conversation History:
{formatted_context}

Analyze this conversation history. Identify any relevant context that would help answer the current query. If nothing is relevant, say so.""")
            ]
            
            response = self.model.invoke(messages)
            analysis = response.content
            
            logger.info("Memory Agent: Context retrieved and analyzed")
            
            return {
                "context": formatted_context,
                "analysis": analysis,
                "has_history": True,
                "message_count": len(history),
                "agent": "memory",
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Memory Agent failed: {e}")
            return {
                "context": "Error retrieving context",
                "has_history": False,
                "agent": "memory",
                "success": False,
                "error": str(e)
            }
    
    def save_interaction(self, session_id: str, user_query: str, agent_response: str):
        """
        Save user-agent interaction to memory
        
        Args:
            session_id: Session identifier
            user_query: User's query
            agent_response: Agent's response
        """
        try:
            self.memory.add_message(session_id, "user", user_query)
            self.memory.add_message(session_id, "assistant", agent_response)
            logger.info(f"Memory Agent: Saved interaction for session {session_id}")
        except Exception as e:
            logger.error(f"Memory Agent: Failed to save interaction: {e}")
    
    def __call__(self, session_id: str, current_query: str) -> Dict[str, Any]:
        """Allow agent to be called directly"""
        return self.get_relevant_context(session_id, current_query)