#!/usr/bin/env python3
"""Demo script to test the Voice to RAG system with multiple queries."""
import requests
import time
import json
from typing import Dict, List


API_URL = "http://localhost:8000"


def test_query(query: str, expected_keywords: List[str] = None) -> Dict:
    """
    Test a single query.
    
    Args:
        query: Query text
        expected_keywords: Keywords that should appear in the answer
        
    Returns:
        Result dictionary with status and metrics
    """
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/query",
            json={"text": query},
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Status: Success")
            print(f"⏱️  Latency: {data.get('latency_ms', elapsed * 1000):.0f}ms")
            print(f"📝 Answer: {data.get('answer', '')[:200]}...")
            print(f"📚 Citations: {len(data.get('citations', []))}")
            print(f"🔍 Retrieved chunks: {len(data.get('retrieved_chunks', []))}")
            
            # Check for expected keywords
            if expected_keywords:
                answer_lower = data.get('answer', '').lower()
                found_keywords = [kw for kw in expected_keywords if kw.lower() in answer_lower]
                if found_keywords:
                    print(f"✅ Found expected keywords: {', '.join(found_keywords)}")
                else:
                    print(f"⚠️  Expected keywords not found: {', '.join(expected_keywords)}")
            
            return {
                "status": "success",
                "latency_ms": data.get('latency_ms', elapsed * 1000),
                "has_citations": len(data.get('citations', [])) > 0,
                "has_chunks": len(data.get('retrieved_chunks', [])) > 0
            }
        else:
            print(f"❌ Status: Error {response.status_code}")
            print(f"Error: {response.text}")
            return {
                "status": "error",
                "status_code": response.status_code,
                "error": response.text
            }
    
    except requests.exceptions.Timeout:
        print(f"❌ Status: Timeout (>30s)")
        return {"status": "timeout"}
    except Exception as e:
        print(f"❌ Status: Exception - {str(e)}")
        return {"status": "exception", "error": str(e)}


def check_health() -> bool:
    """Check if API is running."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """Run demo script with multiple test queries."""
    print("="*60)
    print("Voice to RAG System - Demo Script")
    print("="*60)
    
    # Check API health
    print("\n🔍 Checking API health...")
    if not check_health():
        print("❌ API is not running. Please start the server:")
        print("   python api.py")
        return
    print("✅ API is running")
    
    # Test queries
    test_queries = [
        {
            "query": "What is machine learning?",
            "expected_keywords": ["machine learning", "artificial intelligence", "learn"]
        },
        {
            "query": "What are the types of machine learning?",
            "expected_keywords": ["supervised", "unsupervised", "reinforcement"]
        },
        {
            "query": "Explain deep learning",
            "expected_keywords": ["deep learning", "neural", "layers"]
        },
        {
            "query": "What are applications of machine learning?",
            "expected_keywords": ["application", "recommendation", "recognition"]
        },
        {
            "query": "How does machine learning work?",
            "expected_keywords": ["data", "learn", "experience"]
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}/{len(test_queries)}")
        result = test_query(
            test["query"],
            test.get("expected_keywords")
        )
        result["query"] = test["query"]
        results.append(result)
        time.sleep(1)  # Brief pause between queries
    
    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    
    successful = [r for r in results if r.get("status") == "success"]
    failed = [r for r in results if r.get("status") != "success"]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        avg_latency = sum(r.get("latency_ms", 0) for r in successful) / len(successful)
        print(f"⏱️  Average latency: {avg_latency:.0f}ms")
        
        with_citations = sum(1 for r in successful if r.get("has_citations"))
        print(f"📚 Queries with citations: {with_citations}/{len(successful)}")
    
    if failed:
        print(f"\n❌ Failed queries:")
        for r in failed:
            print(f"   - {r.get('query', 'Unknown')}: {r.get('status', 'Unknown error')}")
    
    print(f"\n{'='*60}")
    print("Demo complete!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

