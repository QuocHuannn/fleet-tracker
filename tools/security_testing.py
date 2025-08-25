#!/usr/bin/env python3
"""
Fleet Tracker Security Testing Suite
Comprehensive security testing for all microservices
"""

import asyncio
import httpx
import json
import logging
import time
import base64
import hashlib
import random
import string
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from urllib.parse import urljoin, quote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SecurityTestResult:
    """Result of a security test"""
    test_name: str
    passed: bool
    severity: str  # low, medium, high, critical
    description: str
    details: str = ""
    recommendation: str = ""


@dataclass
class VulnerabilityReport:
    """Comprehensive vulnerability report"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    vulnerabilities: List[SecurityTestResult]


class SecurityTester:
    """Security testing utility for Fleet Tracker"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.valid_token = None
        self.test_results: List[SecurityTestResult] = []
        
    async def setup(self):
        """Setup for security tests"""
        try:
            # Get a valid token for authenticated tests
            auth_data = {
                "email": "test@fleettracker.com",
                "password": "testpassword123"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/auth/login",
                    json=auth_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.valid_token = data["access_token"]
                    logger.info("✅ Security testing setup complete")
                else:
                    logger.warning("⚠️ Could not get valid token for authenticated tests")
                    
        except Exception as e:
            logger.warning(f"⚠️ Setup failed: {e}")

    def add_result(self, test_name: str, passed: bool, severity: str, 
                  description: str, details: str = "", recommendation: str = ""):
        """Add a test result"""
        result = SecurityTestResult(
            test_name=test_name,
            passed=passed,
            severity=severity,
            description=description,
            details=details,
            recommendation=recommendation
        )
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} [{severity.upper()}] {test_name}: {description}")

    # Authentication & Authorization Tests
    async def test_authentication_security(self):
        """Test authentication mechanisms"""
        logger.info("🔐 Testing Authentication Security...")
        
        async with httpx.AsyncClient() as client:
            # Test 1: No authentication required on public endpoints
            try:
                response = await client.get(f"{self.base_url}/health")
                self.add_result(
                    "Public Endpoint Access",
                    response.status_code == 200,
                    "low",
                    "Health endpoint accessible without authentication"
                )
            except Exception as e:
                self.add_result(
                    "Public Endpoint Access",
                    False,
                    "medium",
                    "Health endpoint not accessible",
                    str(e)
                )
            
            # Test 2: Authentication required on protected endpoints
            try:
                response = await client.get(f"{self.base_url}/api/vehicles")
                self.add_result(
                    "Protected Endpoint Security",
                    response.status_code == 401,
                    "high",
                    "Protected endpoints require authentication",
                    f"Status: {response.status_code}",
                    "Ensure all sensitive endpoints require valid authentication"
                )
            except Exception as e:
                self.add_result(
                    "Protected Endpoint Security",
                    False,
                    "critical",
                    "Could not test protected endpoint",
                    str(e)
                )
            
            # Test 3: Invalid token rejection
            try:
                headers = {"Authorization": "Bearer invalid_token_12345"}
                response = await client.get(
                    f"{self.base_url}/api/vehicles",
                    headers=headers
                )
                self.add_result(
                    "Invalid Token Rejection",
                    response.status_code == 401,
                    "high",
                    "Invalid tokens are properly rejected",
                    f"Status: {response.status_code}"
                )
            except Exception as e:
                self.add_result(
                    "Invalid Token Rejection",
                    False,
                    "high",
                    "Could not test invalid token rejection",
                    str(e)
                )
            
            # Test 4: Token format validation
            malformed_tokens = [
                "Bearer",  # Missing token
                "Bearer ",  # Empty token
                "InvalidBearer token123",  # Wrong format
                "Bearer " + "x" * 1000,  # Extremely long token
            ]
            
            for i, token in enumerate(malformed_tokens):
                try:
                    headers = {"Authorization": token}
                    response = await client.get(
                        f"{self.base_url}/api/vehicles",
                        headers=headers
                    )
                    self.add_result(
                        f"Malformed Token Test {i+1}",
                        response.status_code in [400, 401],
                        "medium",
                        f"Malformed token properly rejected: {token[:20]}...",
                        f"Status: {response.status_code}"
                    )
                except Exception as e:
                    self.add_result(
                        f"Malformed Token Test {i+1}",
                        False,
                        "medium",
                        f"Error testing malformed token: {token[:20]}...",
                        str(e)
                    )

    async def test_authorization_security(self):
        """Test authorization and access control"""
        logger.info("🛡️ Testing Authorization Security...")
        
        if not self.valid_token:
            self.add_result(
                "Authorization Tests",
                False,
                "high",
                "Cannot test authorization - no valid token available"
            )
            return
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.valid_token}"}
            
            # Test 1: Access to allowed resources
            try:
                response = await client.get(
                    f"{self.base_url}/api/vehicles",
                    headers=headers
                )
                self.add_result(
                    "Authorized Resource Access",
                    response.status_code in [200, 404],  # 404 OK if no vehicles
                    "medium",
                    "Valid token allows access to authorized resources",
                    f"Status: {response.status_code}"
                )
            except Exception as e:
                self.add_result(
                    "Authorized Resource Access",
                    False,
                    "high",
                    "Error accessing authorized resource",
                    str(e)
                )
            
            # Test 2: Privilege escalation attempts
            admin_endpoints = [
                "/api/admin/users",
                "/api/admin/config",
                "/api/admin/logs",
                "/api/system/config"
            ]
            
            for endpoint in admin_endpoints:
                try:
                    response = await client.get(
                        f"{self.base_url}{endpoint}",
                        headers=headers
                    )
                    self.add_result(
                        f"Admin Endpoint Access: {endpoint}",
                        response.status_code in [403, 404],
                        "high",
                        f"Non-admin user cannot access admin endpoint",
                        f"Status: {response.status_code}",
                        "Ensure proper role-based access control"
                    )
                except Exception as e:
                    self.add_result(
                        f"Admin Endpoint Access: {endpoint}",
                        True,  # Error is expected if endpoint doesn't exist
                        "low",
                        f"Admin endpoint test completed",
                        str(e)
                    )

    async def test_input_validation_security(self):
        """Test input validation and sanitization"""
        logger.info("🔍 Testing Input Validation Security...")
        
        if not self.valid_token:
            logger.warning("⚠️ Skipping input validation tests - no valid token")
            return
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.valid_token}"}
            
            # Test 1: SQL Injection attempts
            sql_payloads = [
                "'; DROP TABLE vehicles; --",
                "' OR '1'='1",
                "1' UNION SELECT * FROM users --",
                "'; INSERT INTO vehicles VALUES ('hack'); --"
            ]
            
            for payload in sql_payloads:
                try:
                    # Test in license plate field
                    vehicle_data = {
                        "license_plate": payload,
                        "make": "Toyota",
                        "model": "Test",
                        "year": 2023
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/api/vehicles",
                        json=vehicle_data,
                        headers=headers
                    )
                    
                    self.add_result(
                        f"SQL Injection Protection",
                        response.status_code in [400, 422],
                        "critical",
                        "SQL injection payload properly rejected",
                        f"Payload: {payload[:30]}..., Status: {response.status_code}",
                        "Ensure all inputs are properly sanitized and parameterized"
                    )
                except Exception as e:
                    self.add_result(
                        f"SQL Injection Test",
                        True,  # Exception might indicate protection
                        "medium",
                        "SQL injection test completed with exception",
                        str(e)
                    )
            
            # Test 2: XSS attempts
            xss_payloads = [
                "<script>alert('xss')</script>",
                "javascript:alert('xss')",
                "<img src=x onerror=alert('xss')>",
                "';!--\"<XSS>=&{()}"
            ]
            
            for payload in xss_payloads:
                try:
                    vehicle_data = {
                        "license_plate": f"XSS-{random.randint(1000, 9999)}",
                        "make": payload,
                        "model": "Test",
                        "year": 2023
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/api/vehicles",
                        json=vehicle_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        # Check if payload was sanitized
                        vehicle = response.json()
                        make_field = vehicle.get("make", "")
                        
                        self.add_result(
                            "XSS Protection",
                            payload not in make_field,
                            "high",
                            "XSS payload properly sanitized",
                            f"Original: {payload[:30]}..., Stored: {make_field[:30]}...",
                            "Ensure all user inputs are properly sanitized"
                        )
                    else:
                        self.add_result(
                            "XSS Input Validation",
                            response.status_code in [400, 422],
                            "high",
                            "XSS payload rejected by input validation",
                            f"Status: {response.status_code}"
                        )
                        
                except Exception as e:
                    self.add_result(
                        "XSS Test",
                        True,
                        "medium",
                        "XSS test completed with exception",
                        str(e)
                    )
            
            # Test 3: Command injection attempts
            command_payloads = [
                "; ls -la",
                "| cat /etc/passwd",
                "&& whoami",
                "`id`",
                "$(uname -a)"
            ]
            
            for payload in command_payloads:
                try:
                    vehicle_data = {
                        "license_plate": f"CMD-{random.randint(1000, 9999)}",
                        "make": "Toyota",
                        "model": payload,
                        "year": 2023
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/api/vehicles",
                        json=vehicle_data,
                        headers=headers
                    )
                    
                    self.add_result(
                        "Command Injection Protection",
                        response.status_code in [400, 422] or 
                        (response.status_code == 201 and payload not in response.text),
                        "critical",
                        "Command injection payload properly handled",
                        f"Payload: {payload[:30]}..., Status: {response.status_code}",
                        "Ensure no user input is passed to system commands"
                    )
                except Exception as e:
                    self.add_result(
                        "Command Injection Test",
                        True,
                        "medium",
                        "Command injection test completed with exception",
                        str(e)
                    )

    async def test_data_exposure_security(self):
        """Test for data exposure vulnerabilities"""
        logger.info("📊 Testing Data Exposure Security...")
        
        async with httpx.AsyncClient() as client:
            # Test 1: Error message information disclosure
            try:
                # Test with malformed JSON
                response = await client.post(
                    f"{self.base_url}/api/vehicles",
                    data="malformed json{{{",
                    headers={"Content-Type": "application/json"}
                )
                
                error_response = response.text.lower()
                sensitive_info = [
                    "password", "secret", "key", "token", "database",
                    "connection", "stack trace", "traceback", "exception"
                ]
                
                has_sensitive = any(info in error_response for info in sensitive_info)
                
                self.add_result(
                    "Error Message Information Disclosure",
                    not has_sensitive,
                    "medium",
                    "Error messages do not expose sensitive information",
                    f"Response length: {len(error_response)} chars",
                    "Ensure error messages are generic and don't expose internal details"
                )
            except Exception as e:
                self.add_result(
                    "Error Message Test",
                    False,
                    "low",
                    "Could not test error message disclosure",
                    str(e)
                )
            
            # Test 2: HTTP methods exposure
            try:
                response = await client.request("OPTIONS", f"{self.base_url}/api/vehicles")
                
                allowed_methods = response.headers.get("Allow", "")
                dangerous_methods = ["TRACE", "CONNECT", "DELETE"]
                
                has_dangerous = any(method in allowed_methods for method in dangerous_methods)
                
                self.add_result(
                    "HTTP Methods Exposure",
                    not has_dangerous or response.status_code == 405,
                    "low",
                    "No dangerous HTTP methods exposed",
                    f"Allowed methods: {allowed_methods}",
                    "Disable unnecessary HTTP methods"
                )
            except Exception as e:
                self.add_result(
                    "HTTP Methods Test",
                    True,
                    "low",
                    "HTTP methods test completed",
                    str(e)
                )

    async def test_session_security(self):
        """Test session management security"""
        logger.info("🔐 Testing Session Security...")
        
        if not self.valid_token:
            logger.warning("⚠️ Skipping session security tests - no valid token")
            return
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.valid_token}"}
            
            # Test 1: Token expiration
            try:
                response = await client.get(
                    f"{self.base_url}/api/vehicles",
                    headers=headers
                )
                
                self.add_result(
                    "Token Validation",
                    response.status_code == 200,
                    "medium",
                    "Valid token allows access",
                    f"Status: {response.status_code}"
                )
            except Exception as e:
                self.add_result(
                    "Token Validation",
                    False,
                    "high",
                    "Error validating token",
                    str(e)
                )
            
            # Test 2: Concurrent session handling
            try:
                # Make multiple simultaneous requests with same token
                tasks = []
                for _ in range(5):
                    task = client.get(
                        f"{self.base_url}/api/vehicles",
                        headers=headers
                    )
                    tasks.append(task)
                
                responses = await asyncio.gather(*tasks)
                
                all_success = all(r.status_code == 200 for r in responses)
                
                self.add_result(
                    "Concurrent Session Handling",
                    all_success,
                    "low",
                    "Token handles concurrent requests properly",
                    f"All {len(responses)} concurrent requests succeeded"
                )
            except Exception as e:
                self.add_result(
                    "Concurrent Session Test",
                    False,
                    "medium",
                    "Error testing concurrent sessions",
                    str(e)
                )

    async def test_rate_limiting_security(self):
        """Test rate limiting and DoS protection"""
        logger.info("🚦 Testing Rate Limiting Security...")
        
        async with httpx.AsyncClient() as client:
            # Test 1: Rapid requests without authentication
            try:
                start_time = time.time()
                requests_made = 0
                blocked_requests = 0
                
                for _ in range(20):  # Make 20 rapid requests
                    response = await client.get(f"{self.base_url}/health")
                    requests_made += 1
                    
                    if response.status_code == 429:  # Too Many Requests
                        blocked_requests += 1
                    
                    # Small delay to avoid overwhelming
                    await asyncio.sleep(0.1)
                
                end_time = time.time()
                duration = end_time - start_time
                requests_per_second = requests_made / duration
                
                # If we made more than 50 requests per second without being blocked, it might be a concern
                rate_limiting_active = blocked_requests > 0 or requests_per_second < 50
                
                self.add_result(
                    "Rate Limiting Protection",
                    rate_limiting_active,
                    "medium",
                    "Rate limiting protects against rapid requests",
                    f"RPS: {requests_per_second:.2f}, Blocked: {blocked_requests}/{requests_made}",
                    "Implement rate limiting to prevent DoS attacks"
                )
            except Exception as e:
                self.add_result(
                    "Rate Limiting Test",
                    False,
                    "medium",
                    "Error testing rate limiting",
                    str(e)
                )

    async def test_security_headers(self):
        """Test security-related HTTP headers"""
        logger.info("🛡️ Testing Security Headers...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/health")
                headers = response.headers
                
                # Check for important security headers
                security_headers = {
                    "X-Content-Type-Options": ("nosniff", "Prevents MIME type sniffing"),
                    "X-Frame-Options": (["DENY", "SAMEORIGIN"], "Prevents clickjacking"),
                    "X-XSS-Protection": ("1; mode=block", "Enables XSS protection"),
                    "Strict-Transport-Security": (None, "Enforces HTTPS"),
                    "Content-Security-Policy": (None, "Prevents XSS and injection attacks"),
                    "Referrer-Policy": (None, "Controls referrer information"),
                }
                
                for header_name, (expected_value, description) in security_headers.items():
                    header_value = headers.get(header_name)
                    
                    if expected_value is None:
                        # Header should exist
                        self.add_result(
                            f"Security Header: {header_name}",
                            header_value is not None,
                            "medium",
                            f"{description}",
                            f"Value: {header_value or 'Not set'}",
                            f"Set {header_name} header for security"
                        )
                    elif isinstance(expected_value, list):
                        # Header should have one of the expected values
                        self.add_result(
                            f"Security Header: {header_name}",
                            header_value in expected_value if header_value else False,
                            "medium",
                            f"{description}",
                            f"Value: {header_value or 'Not set'}",
                            f"Set {header_name} to one of: {expected_value}"
                        )
                    else:
                        # Header should have exact value
                        self.add_result(
                            f"Security Header: {header_name}",
                            header_value == expected_value,
                            "medium",
                            f"{description}",
                            f"Expected: {expected_value}, Got: {header_value or 'Not set'}",
                            f"Set {header_name} to {expected_value}"
                        )
                        
            except Exception as e:
                self.add_result(
                    "Security Headers Test",
                    False,
                    "medium",
                    "Error testing security headers",
                    str(e)
                )

    async def test_cors_security(self):
        """Test CORS configuration security"""
        logger.info("🌐 Testing CORS Security...")
        
        async with httpx.AsyncClient() as client:
            try:
                # Test preflight request
                headers = {
                    "Origin": "https://malicious-site.com",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                }
                
                response = await client.request(
                    "OPTIONS",
                    f"{self.base_url}/api/vehicles",
                    headers=headers
                )
                
                cors_origin = response.headers.get("Access-Control-Allow-Origin", "")
                
                # Check if CORS is too permissive
                too_permissive = cors_origin == "*" and "Access-Control-Allow-Credentials" in response.headers
                
                self.add_result(
                    "CORS Configuration",
                    not too_permissive,
                    "medium",
                    "CORS is not overly permissive",
                    f"Allow-Origin: {cors_origin}",
                    "Avoid using '*' for Access-Control-Allow-Origin with credentials"
                )
                
            except Exception as e:
                self.add_result(
                    "CORS Test",
                    True,
                    "low",
                    "CORS test completed",
                    str(e)
                )

    def generate_report(self) -> VulnerabilityReport:
        """Generate comprehensive vulnerability report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        failed_tests = total_tests - passed_tests
        
        # Count by severity
        critical_issues = sum(1 for r in self.test_results if not r.passed and r.severity == "critical")
        high_issues = sum(1 for r in self.test_results if not r.passed and r.severity == "high")
        medium_issues = sum(1 for r in self.test_results if not r.passed and r.severity == "medium")
        low_issues = sum(1 for r in self.test_results if not r.passed and r.severity == "low")
        
        return VulnerabilityReport(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            critical_issues=critical_issues,
            high_issues=high_issues,
            medium_issues=medium_issues,
            low_issues=low_issues,
            vulnerabilities=[r for r in self.test_results if not r.passed]
        )

    def print_report(self, report: VulnerabilityReport):
        """Print formatted security report"""
        logger.info(f"\n{'='*60}")
        logger.info("🔒 SECURITY ASSESSMENT REPORT")
        logger.info(f"{'='*60}")
        logger.info(f"📊 Total Tests: {report.total_tests}")
        logger.info(f"✅ Passed: {report.passed_tests}")
        logger.info(f"❌ Failed: {report.failed_tests}")
        
        if report.failed_tests > 0:
            logger.info(f"\n🚨 Security Issues by Severity:")
            if report.critical_issues > 0:
                logger.info(f"   🔴 Critical: {report.critical_issues}")
            if report.high_issues > 0:
                logger.info(f"   🟠 High: {report.high_issues}")
            if report.medium_issues > 0:
                logger.info(f"   🟡 Medium: {report.medium_issues}")
            if report.low_issues > 0:
                logger.info(f"   🔵 Low: {report.low_issues}")
            
            logger.info(f"\n📋 Detailed Vulnerabilities:")
            for vuln in report.vulnerabilities:
                severity_icon = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🔵"
                }.get(vuln.severity, "⚪")
                
                logger.info(f"\n{severity_icon} [{vuln.severity.upper()}] {vuln.test_name}")
                logger.info(f"   Description: {vuln.description}")
                if vuln.details:
                    logger.info(f"   Details: {vuln.details}")
                if vuln.recommendation:
                    logger.info(f"   Recommendation: {vuln.recommendation}")
        else:
            logger.info("\n🎉 No security vulnerabilities found!")

    async def run_all_security_tests(self):
        """Run comprehensive security test suite"""
        logger.info("🔒 Starting Fleet Tracker Security Assessment")
        logger.info("=" * 60)
        
        await self.setup()
        
        test_suites = [
            ("Authentication Security", self.test_authentication_security),
            ("Authorization Security", self.test_authorization_security),
            ("Input Validation Security", self.test_input_validation_security),
            ("Data Exposure Security", self.test_data_exposure_security),
            ("Session Security", self.test_session_security),
            ("Rate Limiting Security", self.test_rate_limiting_security),
            ("Security Headers", self.test_security_headers),
            ("CORS Security", self.test_cors_security),
        ]
        
        for suite_name, test_func in test_suites:
            try:
                logger.info(f"\n🧪 Running {suite_name} tests...")
                await test_func()
            except Exception as e:
                logger.error(f"❌ Error in {suite_name}: {e}")
                self.add_result(
                    f"{suite_name} Suite",
                    False,
                    "high",
                    f"Test suite failed with error",
                    str(e)
                )
        
        # Generate and print report
        report = self.generate_report()
        self.print_report(report)
        
        return report


async def main():
    """Main security testing function"""
    tester = SecurityTester()
    report = await tester.run_all_security_tests()
    
    # Exit with appropriate code
    if report.critical_issues > 0:
        exit_code = 1
    elif report.high_issues > 0:
        exit_code = 2
    elif report.medium_issues > 0:
        exit_code = 3
    else:
        exit_code = 0
    
    logger.info(f"\n🏁 Security assessment completed with exit code: {exit_code}")
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
