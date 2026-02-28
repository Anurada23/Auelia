from langchain_core.tools import tool
import re
import requests
from markdownify import markdownify
from utils import logger


@tool
def visit_website(url: str) -> str:
    """
    Visit a URL and extract the main content in markdown format.
    
    Args:
        url: The URL of the webpage to visit
        
    Returns:
        Main content of the webpage in markdown format
    """
    try:
        logger.info(f"Visiting website: {url}")
        
        # Send request with timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=20, headers=headers)
        
        # Check if request was successful
        response.raise_for_status()
        
        # Convert HTML to markdown
        markdown_content = markdownify(response.text).strip()
        
        # Clean up excessive newlines
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)
        
        # Limit content length to avoid token overflow
        max_length = 8000
        if len(markdown_content) > max_length:
            markdown_content = markdown_content[:max_length] + "\n\n[Content truncated...]"
        
        logger.debug(f"Successfully extracted content from {url}")
        return markdown_content
        
    except requests.exceptions.Timeout:
        error_msg = f"Timeout while accessing {url}"
        logger.error(error_msg)
        return error_msg
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to access {url}: {str(e)}"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error processing {url}: {str(e)}"
        logger.error(error_msg)
        return error_msg