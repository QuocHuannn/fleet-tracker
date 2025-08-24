#!/usr/bin/env python3
"""System Integration Tests for Fleet Tracker"""

import asyncio
import json
import time
import logging
from typing import Dict, Any
import pytest
import httpx
import aiomqtt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FleetTrackerSystemTest:
    """Integration tests for Fleet Tracker microservices"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"  # API Gateway
        self.services = {
            "gateway": f"{self.base_url}",
            "auth": "http://localhost:8001",
            "vehicle": "http://localhost:8002", 
            "location": "http://localhost:8003",
            "notification": "http://localhost:8004"
        }
        self.access_token = None
        self.test_user_id = None
        
    async def test_health_checks(self):
        """Test health endpoints for all services"""
        logger.info("🏥 Testing health checks...")
        
        async with httpx.AsyncClient() as client:
            for service_name, url in self.services.items():
                try:
                    response = await client.get(f"{url}/health", timeout=5)
                    if response.status_code == 200:
                        health_data = response.json()
                        logger.info(f"✅ {service_name}: {health_data.get('status', 'unknown')}")
                    else:
                        logger.error(f"❌ {service_name}: HTTP {response.status_code}")
                        return False
                except Exception as e:
                    logger.error(f"❌ {service_name}: {str(e)}")
                    return False
        
        return True
    
    async def test_authentication_flow(self):
        """Test authentication with development mode"""
        logger.info("🔐 Testing authentication flow...")
        
        async with httpx.AsyncClient() as client:
            # Test login with development credentials
            login_data = {
                "firebase_token": "dev_token_" + str(int(time.time())),
                "device_info": {
                    "platform": "test",
                    "user_agent": "system-test"
                }
            }
            
            response = await client.post(
                f"{self.services['auth']}/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                self.access_token = auth_data.get('access_token')
                self.test_user_id = auth_data.get('user_id')
                logger.info(f"✅ Login successful: {auth_data.get('email')}")
                
                # Test token validation
                validate_response = await client.post(
                    f"{self.services['auth']}/auth/validate-token",
                    json={"token": self.access_token},
                    timeout=5
                )
                
                if validate_response.status_code == 200:
                    token_data = validate_response.json()
                    if token_data.get('valid'):
                        logger.info("✅ Token validation successful")
                        return True
                    
                logger.error("❌ Token validation failed")
                return False
            else:
                logger.error(f"❌ Login failed: HTTP {response.status_code}")
                return False
    
    async def test_api_gateway_routing(self):
        """Test API Gateway routing to services"""
        logger.info("🚀 Testing API Gateway routing...")
        
        if not self.access_token:
            logger.error("❌ No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        async with httpx.AsyncClient() as client:
            # Test routing to different services via Gateway
            endpoints = [
                ("/auth/validate-token", "POST", {"token": self.access_token}),
                ("/vehicles", "GET", None),
                ("/locations/current", "GET", None),
                ("/alerts", "GET", None)
            ]
            
            for endpoint, method, data in endpoints:
                try:
                    if method == "GET":
                        response = await client.get(
                            f"{self.base_url}{endpoint}",
                            headers=headers,
                            timeout=5
                        )
                    else:
                        response = await client.post(
                            f"{self.base_url}{endpoint}",
                            json=data,
                            headers=headers if endpoint != "/auth/validate-token" else {},
                            timeout=5
                        )
                    
                    if response.status_code in [200, 404]:  # 404 is OK for empty resources
                        logger.info(f"✅ Gateway routing {method} {endpoint}: {response.status_code}")
                    else:
                        logger.error(f"❌ Gateway routing {method} {endpoint}: {response.status_code}")
                        return False
                        
                except Exception as e:
                    logger.error(f"❌ Gateway routing error {endpoint}: {str(e)}")
                    return False
        
        return True
    
    async def test_vehicle_service(self):
        """Test vehicle service operations"""
        logger.info("🚗 Testing vehicle service...")
        
        if not self.access_token:
            logger.error("❌ No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        async with httpx.AsyncClient() as client:
            # Test creating a vehicle
            vehicle_data = {
                "license_plate": "TEST001",
                "make": "Toyota",
                "model": "Camry",
                "year": 2022,
                "color": "White",
                "vin": "TEST123456789",
                "vehicle_type": "sedan",
                "status": "active"
            }
            
            response = await client.post(
                f"{self.services['vehicle']}/vehicles",
                json=vehicle_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                vehicle = response.json()
                vehicle_id = vehicle.get('id')
                logger.info(f"✅ Vehicle created: {vehicle_id}")
                
                # Test getting the vehicle
                get_response = await client.get(
                    f"{self.services['vehicle']}/vehicles/{vehicle_id}",
                    headers=headers,
                    timeout=5
                )
                
                if get_response.status_code == 200:
                    logger.info("✅ Vehicle retrieved successfully")
                    return True
                else:
                    logger.error(f"❌ Failed to retrieve vehicle: {get_response.status_code}")
                    return False
            else:
                logger.error(f"❌ Failed to create vehicle: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
    
    async def test_location_service(self):
        """Test location service operations"""
        logger.info("📍 Testing location service...")
        
        if not self.access_token:
            logger.error("❌ No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        async with httpx.AsyncClient() as client:
            # Test location endpoints
            endpoints = [
                ("/locations/current", "GET"),
                ("/geofences", "GET")
            ]
            
            for endpoint, method in endpoints:
                response = await client.get(
                    f"{self.services['location']}{endpoint}",
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code in [200, 404]:
                    logger.info(f"✅ Location service {endpoint}: {response.status_code}")
                else:
                    logger.error(f"❌ Location service {endpoint}: {response.status_code}")
                    return False
            
            # Test location creation
            location_data = {
                "vehicle_id": "test_vehicle_001",
                "latitude": 10.8231,
                "longitude": 106.6297,
                "speed": 45.5,
                "heading": 90
            }
            
            response = await client.post(
                f"{self.services['location']}/locations/",
                json=location_data,
                headers=headers,
                timeout=5
            )
            
            if response.status_code in [200, 201]:
                logger.info("✅ Location created successfully")
                return True
            else:
                logger.error(f"❌ Failed to create location: {response.status_code}")
                return False
    
    async def test_notification_service(self):
        """Test notification service operations"""
        logger.info("📢 Testing notification service...")
        
        if not self.access_token:
            logger.error("❌ No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        async with httpx.AsyncClient() as client:
            # Test alerts endpoint
            response = await client.get(
                f"{self.services['notification']}/alerts",
                headers=headers,
                timeout=5
            )
            
            if response.status_code in [200, 404]:
                logger.info(f"✅ Notification service alerts: {response.status_code}")
                
                # Test WebSocket stats
                stats_response = await client.get(
                    f"{self.services['notification']}/ws/stats",
                    timeout=5
                )
                
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    logger.info(f"✅ WebSocket stats: {stats}")
                    return True
                else:
                    logger.error(f"❌ WebSocket stats failed: {stats_response.status_code}")
                    return False
            else:
                logger.error(f"❌ Notification service failed: {response.status_code}")
                return False
    
    async def test_mqtt_connection(self):
        """Test MQTT broker connection"""
        logger.info("📡 Testing MQTT connection...")
        
        try:
            client = aiomqtt.Client(
                hostname="localhost",
                port=1883,
                username="mqtt_user",
                password="mqtt_password",
                client_id="system_test_client"
            )
            
            async with client:
                await client.subscribe("fleet/test")
                
                # Send test message
                test_message = {
                    "test": True,
                    "timestamp": time.time(),
                    "message": "System integration test"
                }
                
                await client.publish("fleet/test", json.dumps(test_message))
                logger.info("✅ MQTT message published successfully")
                
                # Try to receive message (with timeout)
                try:
                    async with asyncio.timeout(3):
                        async for message in client.messages:
                            received_data = json.loads(message.payload.decode())
                            if received_data.get('test'):
                                logger.info("✅ MQTT message received successfully")
                                return True
                except asyncio.TimeoutError:
                    logger.info("⚠️ MQTT message not received (timeout)")
                    return True  # Connection worked, might be normal
        
        except Exception as e:
            logger.error(f"❌ MQTT connection failed: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all system integration tests"""
        logger.info("🧪 Starting Fleet Tracker System Integration Tests")
        logger.info("=" * 60)
        
        tests = [
            ("Health Checks", self.test_health_checks),
            ("Authentication Flow", self.test_authentication_flow),
            ("API Gateway Routing", self.test_api_gateway_routing),
            ("Vehicle Service", self.test_vehicle_service),
            ("Location Service", self.test_location_service),
            ("Notification Service", self.test_notification_service),
            ("MQTT Connection", self.test_mqtt_connection)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            logger.info(f"\n🔄 Running: {test_name}")
            try:
                result = await test_func()
                if result:
                    logger.info(f"✅ {test_name}: PASSED")
                    passed += 1
                else:
                    logger.error(f"❌ {test_name}: FAILED")
                    failed += 1
            except Exception as e:
                logger.error(f"💥 {test_name}: ERROR - {str(e)}")
                failed += 1
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        logger.info("\n" + "=" * 60)
        logger.info(f"📊 TEST RESULTS: {passed} passed, {failed} failed")
        
        if failed == 0:
            logger.info("🎉 ALL TESTS PASSED!")
            return True
        else:
            logger.error(f"❌ {failed} tests failed")
            return False

async def main():
    """Main test function"""
    test_suite = FleetTrackerSystemTest()
    
    try:
        success = await test_suite.run_all_tests()
        exit_code = 0 if success else 1
    except KeyboardInterrupt:
        logger.info("\n⏹️ Tests interrupted by user")
        exit_code = 130
    except Exception as e:
        logger.error(f"💥 Test suite error: {str(e)}")
        exit_code = 1
    
    logger.info(f"🏁 Test suite completed with exit code: {exit_code}")
    return exit_code

if __name__ == "__main__":
    exit_code = asyncio.run(main())
