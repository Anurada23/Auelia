import uuid
from datetime import datetime
from typing import Dict, Any


def generate_session_id() -> str:
    """Generate a unique session ID"""
    return str(uuid.uuid4())


def generate_message_id() -> str:
    """Generate a unique message ID"""
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat()


def format_message(role: str, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Format a message with standard structure
    
    Args:
        role: Message role (user/assistant/system)
        content: Message content
        metadata: Additional metadata
        
    Returns:
        Formatted message dictionary
    """
    message = {
        "id": generate_message_id(),
        "role": role,
        "content": content,
        "timestamp": get_timestamp()
    }
    
    if metadata:
        message["metadata"] = metadata
        
    return message


def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def extract_urls(text: str) -> list[str]:
    """Extract URLs from text (simple implementation)"""
    import re
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)