from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings, PLANNER_PROMPT
from utils import logger
from typing import Dict, Any


class PlannerAgent:
    """
    The Planner Agent creates research strategies.
    It analyzes user queries and creates actionable research plans.
    """
    
    def __init__(self):
        self.model = ChatGroq(
            model=settings.model_name,
            temperature=settings.model_temperature,
            api_key=settings.groq_api_key
        )
        self.system_prompt = PLANNER_PROMPT
    
    def create_plan(self, query: str, context: str = "") -> Dict[str, Any]:
        """
        Create a research plan for the given query
        
        Args:
            query: User's question
            context: Optional conversation context
            
        Returns:
            Dictionary with plan and metadata
        """
        try:
            logger.info("Planner Agent: Creating research plan")
            
            # Build messages
            messages = [
                SystemMessage(content=self.system_prompt)
            ]
            
            if context:
                messages.append(HumanMessage(content=f"Context:\n{context}\n\n"))
            
            messages.append(
                HumanMessage(content=f"Create a research plan for: {query}")
            )
            
            # Get plan from model
            response = self.model.invoke(messages)
            plan = response.content
            
            logger.info("Planner Agent: Plan created successfully")
            logger.debug(f"Plan: {plan[:200]}...")
            
            return {
                "plan": plan,
                "query": query,
                "agent": "planner",
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Planner Agent failed: {e}")
            return {
                "plan": f"Error creating plan: {str(e)}",
                "query": query,
                "agent": "planner",
                "success": False,
                "error": str(e)
            }
    
    def __call__(self, query: str, context: str = "") -> Dict[str, Any]:
        """Allow agent to be called directly"""
        return self.create_plan(query, context)