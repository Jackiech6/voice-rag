#!/usr/bin/env python3
"""Test script to verify OpenAI API key is working."""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import config after loading .env
import config

def test_api_key():
    """Test if OpenAI API key is configured and working."""
    print("Testing OpenAI API Key Configuration...")
    print("=" * 50)
    
    # Check if API key is loaded
    if not config.OPENAI_API_KEY:
        print("❌ ERROR: OPENAI_API_KEY is not set!")
        print("\nPlease set it in one of these ways:")
        print("1. Create a .env file with: OPENAI_API_KEY=your_key_here")
        print("2. Set environment variable: export OPENAI_API_KEY=your_key_here")
        print("3. For Railway: Set in Railway Variables (Settings → Variables)")
        return False
    
    print(f"✅ API Key loaded: {config.OPENAI_API_KEY[:20]}...{config.OPENAI_API_KEY[-10:]}")
    print(f"   Length: {len(config.OPENAI_API_KEY)} characters")
    
    # Test API connection
    try:
        from openai import OpenAI
        
        print("\nTesting API connection...")
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        # Try a simple API call
        response = client.models.list()
        print("✅ API connection successful!")
        print(f"   Available models: {len(response.data)} models")
        
        # Test embedding generation
        print("\nTesting embedding generation...")
        embedding_response = client.embeddings.create(
            model="text-embedding-3-small",
            input="test"
        )
        print(f"✅ Embedding generation successful!")
        print(f"   Embedding dimension: {len(embedding_response.data[0].embedding)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ API test failed: {str(e)}")
        error_msg = str(e).lower()
        
        if "api key" in error_msg or "authentication" in error_msg or "401" in error_msg or "403" in error_msg:
            print("\n🔑 Authentication Error:")
            print("   - Your API key may be invalid or expired")
            print("   - Check your API key at: https://platform.openai.com/api-keys")
            print("   - Make sure there are no extra spaces or characters")
        elif "connection" in error_msg or "timeout" in error_msg:
            print("\n🌐 Connection Error:")
            print("   - Check your internet connection")
            print("   - OpenAI API might be temporarily unavailable")
            print("   - Check status: https://status.openai.com/")
        else:
            print(f"\n⚠️  Unexpected error: {type(e).__name__}")
        
        return False

if __name__ == "__main__":
    success = test_api_key()
    sys.exit(0 if success else 1)

