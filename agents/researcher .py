from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from config import settings, RESEARCHER_PROMPT
from tools import search_web, visit_website
from utils import logger
from typing import Dict, Any, List


class ResearcherAgent:
    """
    The Researcher Agent executes research tasks.
    It uses search and web scraping tools to gather information.
    """
    
    def __init__(self):
        self.model = ChatGroq(
            model=settings.model_name,
            temperature=settings.model_temperature,
            api_key=settings.groq_api_key
        )
        self.system_prompt = RESEARCHER_PROMPT
        self.tools = [search_web, visit_website]
        
        # Create ReAct agent with tools
        self.agent = create_react_agent(self.model, self.tools)
    
    def conduct_research(self, plan: str, query: str) -> Dict[str, Any]:
        """
        Conduct research based on the plan
        
        Args:
            plan: Research plan from Planner
            query: Original user query
            
        Returns:
            Dictionary with findings and metadata
        """
        try:
            logger.info("Researcher Agent: Starting research")
            
            # Create research prompt
            research_prompt = f"""Research Plan:
{plan}

Original Query: {query}

Execute this research plan. Use the search_web tool to find information and visit_website tool to get detailed content from relevant pages. Gather comprehensive, accurate information."""
            
            # Execute research using the agent
            response = self.agent.invoke({
                "messages": [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=research_prompt)
                ]
            })
            
            # Extract findings from the last message
            findings = response["messages"][-1].content
            
            # Extract tool calls for tracking
            tool_calls = []
            for msg in response["messages"]:
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    tool_calls.extend(msg.tool_calls)
            
            logger.info(f"Researcher Agent: Research complete ({len(tool_calls)} tool calls)")
            logger.debug(f"Findings: {findings[:200]}...")
            
            return {
                "findings": findings,
                "tool_calls": tool_calls,
                "agent": "researcher",
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Researcher Agent failed: {e}")
            return {
                "findings": f"Error during research: {str(e)}",
                "tool_calls": [],
                "agent": "researcher",
                "success": False,
                "error": str(e)
            }
    
    def __call__(self, plan: str, query: str) -> Dict[str, Any]:
        """Allow agent to be called directly"""
        return self.conduct_research(plan, query)