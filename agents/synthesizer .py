from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings, SYNTHESIZER_PROMPT
from utils import logger
from typing import Dict, Any


class SynthesizerAgent:
    """
    The Synthesizer Agent creates final responses.
    It combines research findings and context into comprehensive answers.
    """
    
    def __init__(self):
        self.model = ChatGroq(
            model=settings.model_name,
            temperature=settings.model_temperature,
            api_key=settings.groq_api_key
        )
        self.system_prompt = SYNTHESIZER_PROMPT
    
    def synthesize_response(
        self, 
        query: str, 
        research_findings: str,
        context: str = "",
        plan: str = ""
    ) -> Dict[str, Any]:
        """
        Synthesize final response from research findings
        
        Args:
            query: Original user query
            research_findings: Findings from Researcher
            context: Conversation context from Memory
            plan: Research plan from Planner
            
        Returns:
            Dictionary with final response and metadata
        """
        try:
            logger.info("Synthesizer Agent: Creating final response")
            
            # Build synthesis prompt
            synthesis_prompt = f"""Original Query: {query}

"""
            
            if context and context != "No previous conversation history.":
                synthesis_prompt += f"""Conversation Context:
{context}

"""
            
            if plan:
                synthesis_prompt += f"""Research Plan:
{plan}

"""
            
            synthesis_prompt += f"""Research Findings:
{research_findings}

Based on all the above information, create a comprehensive, well-structured answer to the user's query. Include relevant citations and make sure the response directly addresses what the user asked."""
            
            # Get synthesis from model
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=synthesis_prompt)
            ]
            
            response = self.model.invoke(messages)
            final_answer = response.content
            
            logger.info("Synthesizer Agent: Response synthesized successfully")
            logger.debug(f"Response: {final_answer[:200]}...")
            
            return {
                "response": final_answer,
                "query": query,
                "agent": "synthesizer",
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Synthesizer Agent failed: {e}")
            return {
                "response": f"I encountered an error while synthesizing the response: {str(e)}",
                "query": query,
                "agent": "synthesizer",
                "success": False,
                "error": str(e)
            }
    
    def __call__(
        self, 
        query: str, 
        research_findings: str,
        context: str = "",
        plan: str = ""
    ) -> Dict[str, Any]:
        """Allow agent to be called directly"""
        return self.synthesize_response(query, research_findings, context, plan)