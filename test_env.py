#!/usr/bin/env python3
"""Quick script to test environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()

print("Environment Variables Check:")
print("=" * 50)
print(f"OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
if os.getenv('OPENAI_API_KEY'):
    key = os.getenv('OPENAI_API_KEY')
    print(f"  Value: {key[:10]}...{key[-5:] if len(key) > 15 else ''}")
print(f"PORT: {os.getenv('PORT', 'NOT SET')}")
print(f"HOST: {os.getenv('HOST', 'NOT SET')}")
print("=" * 50)

