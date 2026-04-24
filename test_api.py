#!/usr/bin/env python
"""
Test script for URL Shortener API
Run this to verify everything is working
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_health():
    print_section("1. Health Check")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        if resp.status_code == 200:
            print("✅ Health check passed")
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"❌ Health check failed: {resp.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_api_info():
    print_section("2. API Info")
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=5)
        if resp.status_code == 200:
            print("✅ API info retrieved")
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"❌ Failed: {resp.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_shorten_url():
    print_section("3. Shorten URL (auto-generated)")
    try:
        payload = {
            "url": "https://www.example.com/very/long/url/that/needs/shortening"
        }
        resp = requests.post(
            f"{BASE_URL}/shorten",
            json=payload,
            timeout=10
        )
        if resp.status_code == 200:
            print("✅ URL shortened successfully")
            data = resp.json()
            print(json.dumps(data, indent=2))
            return data.get("shortcode")
        else:
            print(f"❌ Failed: {resp.status_code}")
            print(resp.text)
    except Exception as e:
        print(f"❌ Error: {e}")
    return None

def test_custom_alias():
    print_section("4. Shorten URL (custom alias)")
    try:
        payload = {
            "url": "https://www.github.com/azizjonradjabov840-cmd",
            "custom_alias": "github_profile"
        }
        resp = requests.post(
            f"{BASE_URL}/shorten",
            json=payload,
            timeout=10
        )
        if resp.status_code == 200:
            print("✅ Custom alias created successfully")
            data = resp.json()
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Failed: {resp.status_code}")
            print(resp.text)
    except Exception as e:
        print(f"❌ Error: {e}")

def test_info(shortcode):
    print_section(f"5. Get Info ({shortcode})")
    try:
        resp = requests.get(f"{BASE_URL}/info/{shortcode}", timeout=5)
        if resp.status_code == 200:
            print("✅ Info retrieved")
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"❌ Failed: {resp.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_stats(shortcode):
    print_section(f"6. Get Analytics ({shortcode})")
    try:
        resp = requests.get(f"{BASE_URL}/stats/{shortcode}", timeout=5)
        if resp.status_code == 200:
            print("✅ Analytics retrieved")
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"❌ Failed: {resp.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_qr_code(shortcode):
    print_section(f"7. Get QR Code ({shortcode})")
    try:
        resp = requests.get(f"{BASE_URL}/qr/{shortcode}", timeout=5)
        if resp.status_code == 200:
            print("✅ QR code retrieved")
            print(f"   Content-Type: {resp.headers.get('content-type')}")
            print(f"   Size: {len(resp.content)} bytes")
        else:
            print(f"❌ Failed: {resp.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("\n🧪 URL Shortener API Test Suite")
    print(f"Base URL: {BASE_URL}")
    
    # Run tests
    test_health()
    test_api_info()
    shortcode = test_shorten_url()
    test_custom_alias()
    
    if shortcode:
        test_info(shortcode)
        test_stats(shortcode)
        test_qr_code(shortcode)
    
    print_section("✅ Test Suite Complete")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
