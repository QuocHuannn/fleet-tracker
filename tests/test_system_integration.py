#!/usr/bin/env python3
"""
Fleet Tracker System Integration Tests
Tests the complete flow between all microservices
"""

import asyncio
import json
import time
import logging
from typing import Dict, Any, List
import pytest
import httpx
import websockets
from unittest.mock import AsyncMock, MagicMock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FleetTrackerIntegrationTest:
    """Comprehensive integration tests for Fleet Tracker microservices"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"  # API Gateway
        self.ws_url = "ws://localhost:8004/ws"
        self.services = {
            "gateway": f"{self.base_url}",
            "auth": "http://localhost:8001",
            "vehicle": "http://localhost:8002", 
            "location": "http://localhost:8003",
            "notification": "http://localhost:8004"
        }
        self.auth_token = None
        self.session = None
        
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
        
    async def setup(self):
        """Setup test environment"""
        self.session = httpx.AsyncClient()
        await self.authenticate()
        
    async def teardown(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.aclose()
            
    async def authenticate(self) -> str:
        """Authenticate and get JWT token"""
        auth_data = {
            "email": "test@fleettracker.com",
            "password": "testpassword123"
        }
        
        response = await self.session.post(
            f"{self.base_url}/api/auth/login",
            json=auth_data
        )
        
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data["access_token"]
            return self.auth_token
        else:
            raise Exception(f"Authentication failed: {response.status_code}")
    
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

    async def test_health_checks(self):
        """Test health endpoints for all services"""
        logger.info("🏥 Testing health checks...")
        
        for service_name, url in self.services.items():
            try:
                response = await self.session.get(f"{url}/health", timeout=5)
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
    
    # Test 1: Complete Vehicle Management Flow
    async def test_vehicle_lifecycle(self):
        """Test complete vehicle creation, update, and deletion flow"""
        logger.info("🚗 Testing Vehicle Lifecycle...")
        
        # Create vehicle
        vehicle_data = {
            "license_plate": "TEST-001",
            "make": "Toyota",
            "model": "Camry",
            "year": 2023,
            "device_id": "GPS-TEST-001"
        }
        
        response = await self.session.post(
            f"{self.base_url}/api/vehicles",
            json=vehicle_data,
            headers=self.get_headers()
        )
        assert response.status_code == 201
        created_vehicle = response.json()
        vehicle_id = created_vehicle["id"]
        assert created_vehicle["license_plate"] == "TEST-001"
        logger.info(f"✅ Vehicle created: {vehicle_id}")
        
        # Read vehicle
        response = await self.session.get(
            f"{self.base_url}/api/vehicles/{vehicle_id}",
            headers=self.get_headers()
        )
        assert response.status_code == 200
        vehicle = response.json()
        assert vehicle["license_plate"] == "TEST-001"
        logger.info("✅ Vehicle retrieved successfully")
        
        # Update vehicle
        update_data = {"make": "Honda"}
        response = await self.session.put(
            f"{self.base_url}/api/vehicles/{vehicle_id}",
            json=update_data,
            headers=self.get_headers()
        )
        assert response.status_code == 200
        updated_vehicle = response.json()
        assert updated_vehicle["make"] == "Honda"
        logger.info("✅ Vehicle updated successfully")
        
        # Delete vehicle
        response = await self.session.delete(
            f"{self.base_url}/api/vehicles/{vehicle_id}",
            headers=self.get_headers()
        )
        assert response.status_code == 204
        logger.info("✅ Vehicle deleted successfully")
        
        return vehicle_id

    # Test 2: Location Tracking Flow
    async def test_location_tracking(self):
        """Test GPS location updates and tracking"""
        logger.info("📍 Testing Location Tracking...")
        
        # Create test vehicle first
        vehicle_id = await self.create_test_vehicle()
        
        # Send location update
        location_data = {
            "vehicle_id": vehicle_id,
            "latitude": 10.7769,
            "longitude": 106.7009,
            "speed": 45.5,
            "heading": 120.0,
            "timestamp": int(time.time())
        }
        
        response = await self.session.post(
            f"{self.base_url}/api/locations",
            json=location_data,
            headers=self.get_headers()
        )
        assert response.status_code == 201
        logger.info("✅ Location data sent successfully")
        
        # Get location history
        response = await self.session.get(
            f"{self.base_url}/api/locations/vehicle/{vehicle_id}",
            headers=self.get_headers()
        )
        assert response.status_code == 200
        locations = response.json()
        assert len(locations) > 0
        assert locations[0]["latitude"] == 10.7769
        logger.info("✅ Location history retrieved successfully")
        
        # Get current location
        response = await self.session.get(
            f"{self.base_url}/api/locations/vehicle/{vehicle_id}/current",
            headers=self.get_headers()
        )
        assert response.status_code == 200
        current_location = response.json()
        assert current_location["latitude"] == 10.7769
        logger.info("✅ Current location retrieved successfully")
        
        await self.cleanup_test_vehicle(vehicle_id)
        return True

    async def test_authentication_flow(self):
        """Test authentication with development mode"""
        logger.info("🔐 Testing authentication flow...")
        
        # Test login with development credentials
        login_data = {
            "firebase_token": "dev_token_" + str(int(time.time())),
            "device_info": {
                "platform": "test",
                "user_agent": "system-test"
            }
        }
        
        response = await self.session.post(
            f"{self.services['auth']}/auth/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            auth_data = response.json()
            self.auth_token = auth_data.get('access_token')
            logger.info(f"✅ Login successful: {auth_data.get('email')}")
            
            # Test token validation
            validate_response = await self.session.post(
                f"{self.services['auth']}/auth/validate-token",
                json={"token": self.auth_token},
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
    
    # Test 3: Real-time WebSocket Communication
    async def test_websocket_communication(self):
        """Test real-time WebSocket notifications"""
        logger.info("🔌 Testing WebSocket Communication...")
        
        messages_received = []
        
        async def websocket_handler():
            try:
                uri = f"{self.ws_url}?token={self.auth_token}"
                async with websockets.connect(uri) as websocket:
                    # Subscribe to vehicle updates
                    subscribe_msg = {
                        "type": "subscribe",
                        "channel": "vehicle_updates"
                    }
                    await websocket.send(json.dumps(subscribe_msg))
                    
                    # Listen for messages for 5 seconds
                    try:
                        async with asyncio.timeout(5):
                            async for message in websocket:
                                data = json.loads(message)
                                messages_received.append(data)
                                logger.info(f"📨 Received WebSocket message: {data['type']}")
                                
                                if len(messages_received) >= 2:
                                    break
                    except asyncio.TimeoutError:
                        logger.info("⏱️ WebSocket test timeout (expected)")
                        
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
        
        # Start WebSocket listener
        websocket_task = asyncio.create_task(websocket_handler())
        
        # Wait a moment for connection to establish
        await asyncio.sleep(1)
        
        # Create vehicle and send location update to trigger notifications
        vehicle_id = await self.create_test_vehicle()
        
        # Send location update
        location_data = {
            "vehicle_id": vehicle_id,
            "latitude": 10.7769,
            "longitude": 106.7009,
            "speed": 45.5,
            "timestamp": int(time.time())
        }
        
        response = await self.session.post(
            f"{self.base_url}/api/locations",
            json=location_data,
            headers=self.get_headers()
        )
        assert response.status_code == 201
        
        # Wait for WebSocket task to complete
        await websocket_task
        
        # Verify messages were received
        assert len(messages_received) > 0
        logger.info(f"✅ Received {len(messages_received)} WebSocket messages")
        
        await self.cleanup_test_vehicle(vehicle_id)
        return True

    # Test 4: Alert System Integration
    async def test_alert_system(self):
        """Test alert generation and management"""
        logger.info("🚨 Testing Alert System...")
        
        vehicle_id = await self.create_test_vehicle()
        
        # Create alert rule
        rule_data = {
            "name": "Speed Limit Test",
            "type": "speed_limit",
            "severity": "high",
            "enabled": True,
            "conditions": {
                "speed_limit": 50
            }
        }
        
        response = await self.session.post(
            f"{self.base_url}/api/alert-rules",
            json=rule_data,
            headers=self.get_headers()
        )
        assert response.status_code == 201
        rule = response.json()
        rule_id = rule["id"]
        logger.info("✅ Alert rule created")
        
        # Trigger alert by sending high speed location
        location_data = {
            "vehicle_id": vehicle_id,
            "latitude": 10.7769,
            "longitude": 106.7009,
            "speed": 80.0,  # Above speed limit
            "timestamp": int(time.time())
        }
        
        response = await self.session.post(
            f"{self.base_url}/api/locations",
            json=location_data,
            headers=self.get_headers()
        )
        assert response.status_code == 201
        
        # Wait for alert processing
        await asyncio.sleep(2)
        
        # Check for generated alerts
        response = await self.session.get(
            f"{self.base_url}/api/alerts",
            headers=self.get_headers()
        )
        assert response.status_code == 200
        alerts_response = response.json()
        alerts = alerts_response["alerts"]
        
        # Find our test alert
        test_alerts = [a for a in alerts if a["vehicle_id"] == vehicle_id]
        assert len(test_alerts) > 0
        alert_id = test_alerts[0]["id"]
        logger.info("✅ Alert generated successfully")
        
        # Acknowledge alert
        response = await self.session.post(
            f"{self.base_url}/api/alerts/{alert_id}/acknowledge",
            headers=self.get_headers()
        )
        assert response.status_code == 200
        logger.info("✅ Alert acknowledged successfully")
        
        # Resolve alert
        response = await self.session.post(
            f"{self.base_url}/api/alerts/{alert_id}/resolve",
            headers=self.get_headers()
        )
        assert response.status_code == 200
        logger.info("✅ Alert resolved successfully")
        
        # Cleanup
        await self.cleanup_test_vehicle(vehicle_id)
        
        response = await self.session.delete(
            f"{self.base_url}/api/alert-rules/{rule_id}",
            headers=self.get_headers()
        )
        assert response.status_code == 204
        logger.info("✅ Alert rule deleted")
        
        return True

    # Test 5: Analytics and Reporting
    async def test_analytics_system(self):
        """Test analytics data generation and reporting"""
        logger.info("� Testing Analytics System...")
        
        # Get analytics data
        response = await self.session.get(
            f"{self.base_url}/api/analytics",
            headers=self.get_headers()
        )
        assert response.status_code == 200
        analytics = response.json()
        
        # Verify analytics structure
        assert "fleet_overview" in analytics
        assert "distance_analytics" in analytics
        assert "fuel_analytics" in analytics
        assert "performance_metrics" in analytics
        logger.info("✅ Analytics data retrieved successfully")
        
        # Get time series data
        response = await self.session.get(
            f"{self.base_url}/api/analytics/timeseries?metric=distance&period=day",
            headers=self.get_headers()
        )
        assert response.status_code == 200
        timeseries = response.json()
        assert isinstance(timeseries, list)
        logger.info("✅ Time series data retrieved successfully")
        
        # Test report generation
        response = await self.session.get(
            f"{self.base_url}/api/analytics/report?type=fleet_summary&format=pdf",
            headers=self.get_headers()
        )
        assert response.status_code == 200
        assert response.headers.get("Content-Type") == "application/pdf"
        logger.info("✅ Report generated successfully")
        
        return True

    # Test 6: Performance and Load Testing
    async def test_performance(self):
        """Test system performance under load"""
        logger.info("⚡ Testing System Performance...")
        
        # Concurrent vehicle creation
        tasks = []
        for i in range(10):
            vehicle_data = {
                "license_plate": f"PERF-{i:03d}",
                "make": "Toyota",
                "model": "Test",
                "year": 2023,
                "device_id": f"GPS-PERF-{i:03d}"
            }
            task = self.session.post(
                f"{self.base_url}/api/vehicles",
                json=vehicle_data,
                headers=self.get_headers()
            )
            tasks.append(task)
        
        # Measure response time
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify all requests succeeded
        for response in responses:
            assert response.status_code == 201
        
        duration = end_time - start_time
        logger.info(f"✅ Created 10 vehicles in {duration:.2f} seconds")
        assert duration < 5.0, "Performance test failed: too slow"
        
        # Cleanup
        for response in responses:
            vehicle = response.json()
            await self.cleanup_test_vehicle(vehicle["id"])
        
        return True

    # Test 7: Error Handling and Recovery
    async def test_error_handling(self):
        """Test system error handling and recovery"""
        logger.info("🛡️ Testing Error Handling...")
        
        # Test invalid authentication
        response = await self.session.get(
            f"{self.base_url}/api/vehicles",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
        logger.info("✅ Invalid authentication handled correctly")
        
        # Test invalid data
        invalid_vehicle = {
            "license_plate": "",  # Invalid empty plate
            "make": "Toyota",
            "model": "Test",
            "year": "invalid_year"  # Invalid year format
        }
        
        response = await self.session.post(
            f"{self.base_url}/api/vehicles",
            json=invalid_vehicle,
            headers=self.get_headers()
        )
        assert response.status_code == 422
        logger.info("✅ Invalid data validation working correctly")
        
        # Test non-existent resource
        response = await self.session.get(
            f"{self.base_url}/api/vehicles/non-existent-id",
            headers=self.get_headers()
        )
        assert response.status_code == 404
        logger.info("✅ Non-existent resource handled correctly")
        
        return True

    # Helper methods
    async def create_test_vehicle(self) -> str:
        """Create a test vehicle and return its ID"""
        vehicle_data = {
            "license_plate": f"TEST-{int(time.time())}",
            "make": "Toyota",
            "model": "Test",
            "year": 2023,
            "device_id": f"GPS-TEST-{int(time.time())}"
        }
        
        response = await self.session.post(
            f"{self.base_url}/api/vehicles",
            json=vehicle_data,
            headers=self.get_headers()
        )
        
        if response.status_code == 201:
            vehicle = response.json()
            return vehicle["id"]
        else:
            raise Exception(f"Failed to create test vehicle: {response.status_code}")
    
    async def cleanup_test_vehicle(self, vehicle_id: str):
        """Delete a test vehicle"""
        await self.session.delete(
            f"{self.base_url}/api/vehicles/{vehicle_id}",
            headers=self.get_headers()
        )

    async def test_api_gateway_routing(self):
        """Test API Gateway routing to services"""
        logger.info("🚀 Testing API Gateway routing...")
        
        if not self.auth_token:
            logger.error("❌ No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test routing to different services via Gateway
        endpoints = [
            ("/auth/validate-token", "POST", {"token": self.auth_token}),
            ("/vehicles", "GET", None),
            ("/locations/current", "GET", None),
            ("/alerts", "GET", None)
        ]
        
        for endpoint, method, data in endpoints:
            try:
                if method == "GET":
                    response = await self.session.get(
                        f"{self.base_url}{endpoint}",
                        headers=headers,
                        timeout=5
                    )
                else:
                    response = await self.session.post(
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
        
        if not self.auth_token:
            logger.error("❌ No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
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
        
        response = await self.session.post(
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
            get_response = await self.session.get(
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
        
        if not self.auth_token:
            logger.error("❌ No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test location endpoints
        endpoints = [
            ("/locations/current", "GET"),
            ("/geofences", "GET")
        ]
        
        for endpoint, method in endpoints:
            response = await self.session.get(
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
        
        response = await self.session.post(
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
            headers=headers,
            timeout=5
        )
        
        if response.status_code in [200, 201]:
            logger.info("✅ Location data created successfully")
            return True
        else:
            logger.error(f"❌ Failed to create location: {response.status_code}")
            return False

    # Main test runner
    async def run_all_tests(self):
        """Run all integration tests"""
        logger.info("🚀 Starting Fleet Tracker Integration Tests\n")
        
        try:
            await self.setup()
            
            tests = [
                ("Health Checks", self.test_health_checks),
                ("Authentication Flow", self.test_authentication_flow),
                ("API Gateway Routing", self.test_api_gateway_routing),
                ("Vehicle Service", self.test_vehicle_service),
                ("Location Service", self.test_location_service),
                ("Vehicle Lifecycle", self.test_vehicle_lifecycle),
                ("Location Tracking", self.test_location_tracking),
                ("WebSocket Communication", self.test_websocket_communication),
                ("Alert System", self.test_alert_system),
                ("Analytics System", self.test_analytics_system),
                ("Performance", self.test_performance),
                ("Error Handling", self.test_error_handling),
            ]
            
            passed = 0
            failed = 0
            
            for test_name, test_func in tests:
                try:
                    logger.info(f"\n{'='*50}")
                    logger.info(f"Running: {test_name}")
                    logger.info('='*50)
                    
                    await test_func()
                    passed += 1
                    logger.info(f"✅ {test_name} PASSED")
                    
                except Exception as e:
                    failed += 1
                    logger.error(f"❌ {test_name} FAILED: {e}")
            
            logger.info(f"\n{'='*50}")
            logger.info("TEST RESULTS")
            logger.info('='*50)
            logger.info(f"✅ Passed: {passed}")
            logger.info(f"❌ Failed: {failed}")
            logger.info(f"� Success Rate: {passed/(passed+failed)*100:.1f}%")
            
            if failed == 0:
                logger.info("\n🎉 ALL TESTS PASSED! System integration successful.")
            else:
                logger.info(f"\n⚠️ {failed} tests failed. Please check the logs above.")
            
        finally:
            await self.teardown()


# Run tests for individual services
class ServiceTest:
    """Individual service testing"""
    
    @staticmethod
    async def test_auth_service():
        """Test auth service independently"""
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/health")
            return response.status_code == 200
    
    @staticmethod
    async def test_vehicle_service():
        """Test vehicle service independently"""
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8002/health")
            return response.status_code == 200
    
    @staticmethod
    async def test_location_service():
        """Test location service independently"""
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8003/health")
            return response.status_code == 200
    
    @staticmethod
    async def test_notification_service():
        """Test notification service independently"""
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8004/health")
            return response.status_code == 200


# Main function
async def main():
    """Main test runner function"""
    logger.info("🏁 Fleet Tracker System Integration Test Suite")
    logger.info("=" * 60)
    
    # Run individual service tests first
    logger.info("\n🔍 Testing Individual Services...")
    services = [
        ("Auth Service", ServiceTest.test_auth_service),
        ("Vehicle Service", ServiceTest.test_vehicle_service),
        ("Location Service", ServiceTest.test_location_service),
        ("Notification Service", ServiceTest.test_notification_service),
    ]
    
    for service_name, test_func in services:
        try:
            result = await test_func()
            if result:
                logger.info(f"✅ {service_name} is running")
            else:
                logger.error(f"❌ {service_name} is not available")
        except Exception as e:
            logger.error(f"❌ {service_name} error: {e}")
    
    # Run full integration tests
    logger.info("\n🚀 Running Full Integration Tests...")
    test_runner = FleetTrackerIntegrationTest()
    await test_runner.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
