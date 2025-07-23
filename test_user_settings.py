#!/usr/bin/env python3
"""
Test script for user settings API endpoints.
This script tests the basic functionality of the user settings endpoints.
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_TOKEN = None  # Will be set after login

async def login_test_user() -> str:
    """Login a test user and return the JWT token."""
    async with httpx.AsyncClient() as client:
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/auth/signin",
                json=login_data
            )
            response.raise_for_status()
            return response.json()["access_token"]
        except Exception as e:
            print(f"Login failed: {e}")
            return None


async def test_user_settings_endpoints():
    """Test all user settings endpoints."""
    global TEST_USER_TOKEN
    
    print("🧪 Testing User Settings API Endpoints")
    print("=" * 50)
    
    # Login first
    TEST_USER_TOKEN = await login_test_user()
    if not TEST_USER_TOKEN:
        print("❌ Cannot proceed without valid token")
        return
    
    headers = {"Authorization": f"Bearer {TEST_USER_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        # Test 1: Create user settings
        print("\n1. Creating user settings...")
        create_data = {
            "main_language": "English",
            "learning_language": "Spanish",
            "language_level": "Intermediate (B1)",
            "preferred_categories": ["Technology", "Travel", "Culture"]
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/user-settings/",
                json=create_data,
                headers=headers
            )
            if response.status_code == 201:
                print("✅ Settings created successfully")
                settings = response.json()
                print(f"   Settings ID: {settings['id']}")
            elif response.status_code == 409:
                print("⚠️ Settings already exist, skipping creation")
            else:
                print(f"❌ Failed to create settings: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Error creating settings: {e}")
        
        # Test 2: Get user settings
        print("\n2. Retrieving user settings...")
        try:
            response = await client.get(
                f"{BASE_URL}/user-settings/me",
                headers=headers
            )
            if response.status_code == 200:
                settings = response.json()
                print("✅ Settings retrieved successfully")
                print(f"   Main Language: {settings['main_language']}")
                print(f"   Learning Language: {settings['learning_language']}")
                print(f"   Level: {settings['language_level']}")
                print(f"   Categories: {settings['preferred_categories']}")
            else:
                print(f"❌ Failed to get settings: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Error getting settings: {e}")
        
        # Test 3: Update user settings
        print("\n3. Updating user settings...")
        update_data = {
            "language_level": "Advanced (C1)",
            "preferred_categories": ["Technology", "Business", "Science"]
        }
        
        try:
            response = await client.put(
                f"{BASE_URL}/user-settings/me",
                json=update_data,
                headers=headers
            )
            if response.status_code == 200:
                updated_settings = response.json()
                print("✅ Settings updated successfully")
                print(f"   New Level: {updated_settings['language_level']}")
                print(f"   New Categories: {updated_settings['preferred_categories']}")
            else:
                print(f"❌ Failed to update settings: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Error updating settings: {e}")
        
        # Test 4: Delete user settings (optional - comment out if you want to keep them)
        print("\n4. Deleting user settings...")
        try:
            response = await client.delete(
                f"{BASE_URL}/user-settings/me",
                headers=headers
            )
            if response.status_code == 204:
                print("✅ Settings deleted successfully")
            else:
                print(f"❌ Failed to delete settings: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Error deleting settings: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 User Settings API testing completed!")


if __name__ == "__main__":
    asyncio.run(test_user_settings_endpoints())