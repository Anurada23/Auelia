from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
from utils import logger


# Initialize DuckDuckGo search
search_engine = DuckDuckGoSearchResults(num_results=5)


@tool
def search_web(query: str) -> str:
    """
    Search the web using DuckDuckGo.
    
    Args:
        query: Search query string
        
    Returns:
        Search results as formatted string
    """
    try:
        logger.info(f"Searching web for: {query}")
        results = search_engine.invoke(query)
        logger.debug(f"Search returned {len(results)} results")
        return results
    except Exception as e:
        error_msg = f"Search failed: {str(e)}"
        logger.error(error_msg)
        return error_msg