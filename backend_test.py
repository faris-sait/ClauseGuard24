import requests
import sys
import json
from datetime import datetime
import time

class TermsAnalyzerAPITester:
    def __init__(self, base_url="https://missing-endpoint.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timed out after {timeout} seconds")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test(
            "Root API Endpoint",
            "GET",
            "api/",
            200
        )

    def test_analyze_github_terms(self):
        """Test analysis with GitHub Terms of Service"""
        return self.run_test(
            "Analyze GitHub Terms",
            "POST",
            "api/analyze",
            200,
            data={"url": "https://github.com/site/terms"},
            timeout=60  # Analysis might take longer
        )

    def test_analyze_invalid_url(self):
        """Test analysis with invalid URL"""
        return self.run_test(
            "Analyze Invalid URL",
            "POST", 
            "api/analyze",
            422,  # Validation error expected
            data={"url": "not-a-valid-url"}
        )

    def test_analyze_empty_request(self):
        """Test analysis with empty request"""
        return self.run_test(
            "Analyze Empty Request",
            "POST",
            "api/analyze", 
            422,  # Validation error expected
            data={}
        )

    def test_analyze_nonexistent_url(self):
        """Test analysis with non-existent URL"""
        return self.run_test(
            "Analyze Non-existent URL",
            "POST",
            "api/analyze",
            400,  # Bad request expected
            data={"url": "https://nonexistent-domain-12345.com/terms"},
            timeout=30
        )

    def validate_analysis_response(self, response_data):
        """Validate the structure of analysis response"""
        required_fields = ['url', 'title', 'summary', 'risks', 'risk_score', 'analysis_time']
        
        print(f"\n🔍 Validating Analysis Response Structure...")
        
        for field in required_fields:
            if field not in response_data:
                print(f"❌ Missing required field: {field}")
                return False
            else:
                print(f"✅ Found field: {field}")

        # Validate data types
        if not isinstance(response_data['summary'], list):
            print(f"❌ Summary should be a list, got {type(response_data['summary'])}")
            return False
        
        if not isinstance(response_data['risks'], list):
            print(f"❌ Risks should be a list, got {type(response_data['risks'])}")
            return False
            
        if not isinstance(response_data['risk_score'], int):
            print(f"❌ Risk score should be an integer, got {type(response_data['risk_score'])}")
            return False

        # Validate risk score range
        if not (0 <= response_data['risk_score'] <= 100):
            print(f"❌ Risk score should be 0-100, got {response_data['risk_score']}")
            return False

        print(f"✅ Response structure validation passed")
        print(f"   Risk Score: {response_data['risk_score']}/100")
        print(f"   Summary Points: {len(response_data['summary'])}")
        print(f"   Identified Risks: {len(response_data['risks'])}")
        print(f"   Analysis Time: {response_data['analysis_time']:.2f}s")
        
        return True

def main():
    print("🚀 Starting Terms & Conditions Risk Analyzer API Tests")
    print("=" * 60)
    
    # Setup
    tester = TermsAnalyzerAPITester()
    
    # Test 1: Root endpoint
    success, response = tester.test_root_endpoint()
    if not success:
        print("❌ Root endpoint failed, API may not be running")
        return 1

    # Test 2: Valid analysis with GitHub Terms
    print(f"\n📋 Testing with GitHub Terms of Service...")
    success, response = tester.test_analyze_github_terms()
    if success and isinstance(response, dict):
        if not tester.validate_analysis_response(response):
            print("❌ Analysis response validation failed")
            tester.tests_passed -= 1  # Adjust count since validation failed
    elif not success:
        print("❌ GitHub Terms analysis failed")

    # Test 3: Invalid URL validation
    tester.test_analyze_invalid_url()

    # Test 4: Empty request validation  
    tester.test_analyze_empty_request()

    # Test 5: Non-existent URL handling
    tester.test_analyze_nonexistent_url()

    # Print final results
    print(f"\n" + "=" * 60)
    print(f"📊 FINAL TEST RESULTS")
    print(f"   Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    print(f"   Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print(f"🎉 All tests passed! API is working correctly.")
        return 0
    else:
        print(f"⚠️  Some tests failed. Check the API implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())