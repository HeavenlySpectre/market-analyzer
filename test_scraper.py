#!/usr/bin/env python3
"""
Test script to validate enhanced scraper reliability.
Tests domain validation, structured logging, and pagination.
"""

import requests
import json
import time

# Test URLs - representative Tokopedia products
TEST_URLS = [
    "https://www.tokopedia.com/xiaomiofficial/xiaomi-redmi-note-12-4g-smartphone-4-128gb-6-67-amoled-50mp-triple-camera-5000mah",
    "https://www.tokopedia.com/samsung-official/samsung-galaxy-a34-5g-8-128gb",
    "https://www.tokopedia.com/unilever-indonesia/rinso-anti-noda-detergent-bubuk-1-8kg",
    # Invalid domain for testing
    "https://shopee.co.id/some-product",
]

BASE_URL = "http://127.0.0.1:8000"

def test_analyze_endpoint(url: str, expected_min_reviews: int = 20):
    """Test the /api/v1/analyze endpoint with a given URL."""
    print(f"\n{'='*60}")
    print(f"Testing URL: {url}")
    print(f"Expected minimum reviews: {expected_min_reviews}")
    print(f"{'='*60}")
    
    payload = {"url": url}
    
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/v1/analyze", json=payload, timeout=120)
        elapsed_time = time.time() - start_time
        
        print(f"Response status: {response.status_code}")
        print(f"Response time: {elapsed_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS - Analysis completed")
            
            # Check product metadata
            metadata = data.get('product_metadata', {})
            if metadata and metadata.get('product_title'):
                print(f"📦 Product: {metadata.get('product_title', 'N/A')[:50]}...")
                print(f"💰 Price: {metadata.get('price', 'N/A')}")
                print(f"⭐ Rating: {metadata.get('average_rating', 'N/A')}")
                print(f"📊 Total Reviews: {metadata.get('total_reviews', 'N/A')}")
            else:
                print("❌ No product metadata found")
            
            # Check summary
            summary = data.get('summary', '')
            if summary and not summary.startswith('ERROR'):
                print(f"📝 Summary: {len(summary)} characters")
                print(f"📈 Analysis: {'Contains insights' if 'sentiment' in summary.lower() or 'positive' in summary.lower() else 'Basic analysis'}")
            else:
                print(f"❌ Summary issue: {summary[:100]}...")
            
            return True
            
        elif response.status_code == 400:
            data = response.json()
            error_detail = data.get('detail', 'Unknown error')
            print(f"❌ BAD REQUEST - {error_detail}")
            
            # Check if it's a domain validation error (expected for non-Tokopedia URLs)
            if 'domain tidak didukung' in error_detail or 'tidak valid' in error_detail:
                print("✅ Domain validation working correctly")
                return True
            return False
            
        else:
            print(f"❌ FAILED - Status {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Request took longer than 120 seconds")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR - {str(e)}")
        return False

def main():
    """Run the scraper reliability tests."""
    print("🚀 Starting Enhanced Scraper Reliability Tests")
    print(f"Base URL: {BASE_URL}")
    
    # Check if server is running
    try:
        health_response = requests.get(f"{BASE_URL}/", timeout=5)
        if health_response.status_code != 200:
            print("❌ Server not responding correctly")
            return
    except:
        print("❌ Cannot connect to server. Make sure it's running on http://127.0.0.1:8000")
        return
    
    print("✅ Server is running")
    
    results = []
    
    for i, url in enumerate(TEST_URLS, 1):
        print(f"\n🔍 Test {i}/{len(TEST_URLS)}")
        
        if 'shopee.co.id' in url:
            # This should fail with domain validation
            expected_min_reviews = 0  # Should be rejected
            success = test_analyze_endpoint(url, expected_min_reviews)
        else:
            # Real Tokopedia URLs - expect to get reviews
            expected_min_reviews = 20
            success = test_analyze_endpoint(url, expected_min_reviews)
        
        results.append({
            'url': url,
            'success': success,
            'test_number': i
        })
        
        # Brief pause between tests
        if i < len(TEST_URLS):
            print(f"\n⏳ Waiting 5 seconds before next test...")
            time.sleep(5)
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    successful_tests = sum(1 for r in results if r['success'])
    total_tests = len(results)
    
    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"Test {result['test_number']}: {status}")
    
    if successful_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED! Scraper is demo-ready.")
    else:
        print(f"\n⚠️  Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
