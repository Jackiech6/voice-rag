#!/usr/bin/env python3
"""Verify that the setup is correct."""
import sys
import os

def check_imports():
    """Check if all required modules can be imported."""
    print("Checking imports...")
    try:
        import fastapi
        print("  ✓ fastapi")
    except ImportError as e:
        print(f"  ✗ fastapi: {e}")
        return False
    
    try:
        import chromadb
        print("  ✓ chromadb")
    except ImportError as e:
        print(f"  ✗ chromadb: {e}")
        return False
    
    try:
        import openai
        print("  ✓ openai")
    except ImportError as e:
        print(f"  ✗ openai: {e}")
        return False
    
    try:
        import fitz  # PyMuPDF
        print("  ✓ pymupdf (fitz)")
    except ImportError as e:
        print(f"  ✗ pymupdf: {e}")
        return False
    
    try:
        import tiktoken
        print("  ✓ tiktoken")
    except ImportError as e:
        print(f"  ✗ tiktoken: {e}")
        return False
    
    try:
        import sqlalchemy
        print("  ✓ sqlalchemy")
    except ImportError as e:
        print(f"  ✗ sqlalchemy: {e}")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists."""
    print("\nChecking environment configuration...")
    if os.path.exists(".env"):
        print("  ✓ .env file exists")
        
        # Try to load config
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and api_key != "your_openai_api_key_here":
                print("  ✓ OPENAI_API_KEY is set")
                return True
            else:
                print("  ⚠ OPENAI_API_KEY not set or using placeholder")
                print("     Please set your OpenAI API key in .env file")
                return False
        except Exception as e:
            print(f"  ✗ Error loading .env: {e}")
            return False
    else:
        print("  ⚠ .env file not found")
        print("     Create .env file from .env.example and add your OpenAI API key")
        return False

def check_project_structure():
    """Check if all required files exist."""
    print("\nChecking project structure...")
    required_files = [
        "api.py",
        "config.py",
        "database.py",
        "document_processor.py",
        "embeddings.py",
        "llm_service.py",
        "vector_store.py",
        "ingest.py",
        "requirements.txt"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    """Run all checks."""
    print("=" * 50)
    print("Phase 1 Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Project Structure", check_project_structure),
        ("Python Imports", check_imports),
        ("Environment Config", check_env_file),
    ]
    
    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 50)
    print("Summary:")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n✅ All checks passed! You're ready to go.")
        print("\nNext steps:")
        print("  1. Ingest a document: python ingest.py sample_document.txt")
        print("  2. Start the server: python api.py")
        print("  3. Open browser: http://localhost:8000/static/index.html")
    else:
        print("\n⚠ Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

