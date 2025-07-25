#!/usr/bin/env python3
"""
Simple test script for the article generation feature.
This script demonstrates how to use the new endpoints.
"""

import requests
import json
import time

def test_simple_generation():
    """Test the simple article generation endpoints."""
    
    # Configuration
    base_url = "http://localhost:8000/api/v1"
    token = "your_jwt_token_here"  # Replace with actual token
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test data
    categories = ["technology", "travel", "food"]
    
    print("Testing simple article generation...")
    print(f"Categories: {categories}")
    
    # 1. Start generation
    print("\n1. Starting generation...")
    response = requests.post(
        f"{base_url}/articles/generate-simple",
        headers=headers,
        json={"categories": categories}
    )
    
    if response.status_code == 200:
        data = response.json()
        request_id = data["request_id"]
        print(f"✅ Generation started! Request ID: {request_id}")
        print(f"Estimated articles: {data['estimated_articles']}")
    else:
        print(f"❌ Failed to start generation: {response.status_code}")
        print(response.text)
        return
    
    # 2. Check status
    print("\n2. Checking status...")
    max_attempts = 10
    for attempt in range(max_attempts):
        response = requests.get(
            f"{base_url}/articles/generate-simple/{request_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            status_data = response.json()
            print(f"Attempt {attempt + 1}: Status = {status_data['status']}")
            
            if status_data["status"] == "completed":
                print("✅ Generation completed!")
                break
            elif status_data["status"] == "failed":
                print("❌ Generation failed!")
                break
        else:
            print(f"❌ Error checking status: {response.status_code}")
            break
        
        if attempt < max_attempts - 1:
            time.sleep(5)  # Wait 5 seconds before next check
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_simple_generation()