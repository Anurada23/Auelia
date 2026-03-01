#!/usr/bin/env python3
"""
Check if .env file is configured correctly
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def check_env_file():
    """Check if .env file exists and is configured"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env file not found!")
        print("\n📝 Create a .env file with this content:")
        print("""
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional - only if using Snowflake
SNOWFLAKE_ACCOUNT=yqhfkpb-pu09002
SNOWFLAKE_USER=ANRADHA23
SNOWFLAKE_PASSWORD=your_password_here
SNOWFLAKE_DATABASE=FINDER_AI
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_WAREHOUSE=COMPUTE_WH

# Application Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Memory Settings
MAX_CONVERSATION_HISTORY=10
SESSION_TIMEOUT_MINUTES=30
        """)
        return False
    
    print("✅ .env file found")
    return True

def check_settings():
    """Try to load settings"""
    try:
        from config import settings
        
        print("\n📋 Checking configuration...")
        
        # Check required settings
        #if not settings.groq_api_key or settings.groq_api_key == "your_groq_api_key_here":
         #   print("❌ GROQ_API_KEY not set or using default value")
        #    print("   Get your key from: https://console.groq.com")
         #   return False
        
        print(f"✅ GROQ_API_KEY: {settings.groq_api_key[:10]}...{settings.groq_api_key[-4:]}")
        print(f"✅ API Host: {settings.api_host}")
        print(f"✅ API Port: {settings.api_port}")
        print(f"✅ Model: {settings.model_name}")
        
        # Check optional Snowflake settings
        if settings.snowflake_account:
            print(f"✅ Snowflake Account: {settings.snowflake_account}")
            print(f"✅ Snowflake User: {settings.snowflake_user}")
            print("✅ Snowflake enabled")
        else:
            print("ℹ️  Snowflake not configured (optional - app will work without it)")
        
        print("\n🎉 Configuration looks good!")
        return True
        
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        print("\n💡 Make sure your .env file has:")
        print("   GROQ_API_KEY=your_actual_key")
        return False

def test_imports():
    """Test if all modules can be imported"""
    print("\n📦 Testing imports...")
    
    modules = [
        ("langchain", "LangChain"),
        ("langchain_groq", "LangChain Groq"),
        ("langgraph", "LangGraph"),
        ("fastapi", "FastAPI"),
        ("config", "Config"),
        ("agents", "Agents"),
        ("tools", "Tools"),
        ("workflows", "Workflows"),
    ]
    
    all_ok = True
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
        except ImportError as e:
            print(f"❌ {display_name}: {e}")
            all_ok = False
    
    return all_ok

def main():
    print("=" * 60)
    print("🔧 Finder AI Configuration Check")
    print("=" * 60)
    
    # Check .env file
    if not check_env_file():
        return False
    
    # Check settings
    if not check_settings():
        return False
    
    # Test imports
    if not test_imports():
        print("\n❌ Some dependencies are missing")
        print("Run: pip install -r requirements-minimal.txt")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Everything is ready!")
    print("=" * 60)
    print("\n🚀 Start the app with: python run.py")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)