#!/usr/bin/env python3
"""
Fleet Tracker Load Testing Suite
Performance and stress testing for all microservices
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any, Callable
import httpx
import json
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import psutil
import aiofiles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LoadTestConfig:
    """Configuration for load tests"""
    concurrent_users: int = 10
    requests_per_user: int = 10
    ramp_up_time: float = 1.0  # seconds
    test_duration: int = 60  # seconds
    base_url: str = "http://localhost:8000"
    auth_token: str = ""


@dataclass
class TestResult:
    """Result of a single test request"""
    success: bool
    response_time: float
    status_code: int
    error_message: str = ""


@dataclass
class LoadTestResults:
    """Aggregated results of load test"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    errors: Dict[str, int]


class LoadTester:
    """Load testing utility for Fleet Tracker"""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results: List[TestResult] = []
        self.start_time = 0
        self.end_time = 0
        
    async def authenticate(self) -> str:
        """Get authentication token"""
        auth_data = {
            "email": "test@fleettracker.com",
            "password": "testpassword123"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.config.base_url}/api/auth/login",
                json=auth_data
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["access_token"]
            else:
                raise Exception(f"Authentication failed: {response.status_code}")
    
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {
            "Authorization": f"Bearer {self.config.auth_token}",
            "Content-Type": "application/json"
        }

    async def single_request(self, client: httpx.AsyncClient, endpoint: str, 
                           method: str = "GET", data: Dict = None) -> TestResult:
        """Perform a single HTTP request and measure performance"""
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = await client.get(
                    f"{self.config.base_url}{endpoint}",
                    headers=self.get_headers(),
                    timeout=30
                )
            elif method.upper() == "POST":
                response = await client.post(
                    f"{self.config.base_url}{endpoint}",
                    json=data,
                    headers=self.get_headers(),
                    timeout=30
                )
            elif method.upper() == "PUT":
                response = await client.put(
                    f"{self.config.base_url}{endpoint}",
                    json=data,
                    headers=self.get_headers(),
                    timeout=30
                )
            elif method.upper() == "DELETE":
                response = await client.delete(
                    f"{self.config.base_url}{endpoint}",
                    headers=self.get_headers(),
                    timeout=30
                )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return TestResult(
                success=response.status_code < 400,
                response_time=response_time,
                status_code=response.status_code
            )
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            return TestResult(
                success=False,
                response_time=response_time,
                status_code=0,
                error_message=str(e)
            )

    async def user_simulation(self, user_id: int, client: httpx.AsyncClient) -> List[TestResult]:
        """Simulate a single user's behavior"""
        user_results = []
        
        # Simulate realistic user workflow
        workflows = [
            # Get vehicle list
            ("/api/vehicles", "GET", None),
            # Get analytics
            ("/api/analytics", "GET", None),
            # Get alerts
            ("/api/alerts", "GET", None),
            # Create a vehicle
            ("/api/vehicles", "POST", {
                "license_plate": f"LOAD-{user_id}-{int(time.time())}",
                "make": "Toyota",
                "model": "LoadTest",
                "year": 2023,
                "device_id": f"GPS-LOAD-{user_id}-{int(time.time())}"
            }),
            # Get location data
            ("/api/locations/current", "GET", None),
        ]
        
        for _ in range(self.config.requests_per_user):
            for endpoint, method, data in workflows:
                result = await self.single_request(client, endpoint, method, data)
                user_results.append(result)
                
                # Small delay between requests to simulate real usage
                await asyncio.sleep(0.1)
        
        return user_results

    async def run_load_test(self, test_name: str = "General Load Test") -> LoadTestResults:
        """Run a complete load test"""
        logger.info(f"🚀 Starting {test_name}")
        logger.info(f"👥 Users: {self.config.concurrent_users}")
        logger.info(f"📊 Requests per user: {self.config.requests_per_user}")
        logger.info(f"⏱️ Ramp-up time: {self.config.ramp_up_time}s")
        
        # Get authentication token
        self.config.auth_token = await self.authenticate()
        
        self.start_time = time.time()
        
        # Create HTTP clients for each user
        clients = [httpx.AsyncClient() for _ in range(self.config.concurrent_users)]
        
        try:
            # Create user simulation tasks with ramp-up
            tasks = []
            for i, client in enumerate(clients):
                # Stagger user start times for ramp-up
                delay = (i / self.config.concurrent_users) * self.config.ramp_up_time
                task = asyncio.create_task(
                    self.delayed_user_simulation(i, client, delay)
                )
                tasks.append(task)
            
            # Wait for all users to complete
            all_results = await asyncio.gather(*tasks)
            
            # Flatten results
            for user_results in all_results:
                self.results.extend(user_results)
            
            self.end_time = time.time()
            
            return self.calculate_results()
            
        finally:
            # Close all clients
            for client in clients:
                await client.aclose()

    async def delayed_user_simulation(self, user_id: int, client: httpx.AsyncClient, 
                                    delay: float) -> List[TestResult]:
        """Run user simulation with initial delay for ramp-up"""
        await asyncio.sleep(delay)
        return await self.user_simulation(user_id, client)

    def calculate_results(self) -> LoadTestResults:
        """Calculate aggregated test results"""
        if not self.results:
            return LoadTestResults(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, {})
        
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        response_times = [r.response_time for r in self.results]
        
        # Calculate percentiles
        response_times.sort()
        p95_index = int(0.95 * len(response_times))
        p99_index = int(0.99 * len(response_times))
        
        # Count errors by type
        errors = {}
        for result in failed:
            error_key = f"{result.status_code}: {result.error_message}"
            errors[error_key] = errors.get(error_key, 0) + 1
        
        test_duration = self.end_time - self.start_time
        
        return LoadTestResults(
            total_requests=len(self.results),
            successful_requests=len(successful),
            failed_requests=len(failed),
            avg_response_time=statistics.mean(response_times),
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            median_response_time=statistics.median(response_times),
            p95_response_time=response_times[p95_index] if p95_index < len(response_times) else 0,
            p99_response_time=response_times[p99_index] if p99_index < len(response_times) else 0,
            requests_per_second=len(self.results) / test_duration if test_duration > 0 else 0,
            error_rate=(len(failed) / len(self.results)) * 100 if self.results else 0,
            errors=errors
        )

    def print_results(self, results: LoadTestResults, test_name: str):
        """Print formatted test results"""
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 LOAD TEST RESULTS: {test_name}")
        logger.info(f"{'='*60}")
        logger.info(f"📈 Total Requests: {results.total_requests}")
        logger.info(f"✅ Successful: {results.successful_requests}")
        logger.info(f"❌ Failed: {results.failed_requests}")
        logger.info(f"📊 Success Rate: {100 - results.error_rate:.2f}%")
        logger.info(f"⚡ Requests/sec: {results.requests_per_second:.2f}")
        logger.info(f"\n⏱️ Response Times (seconds):")
        logger.info(f"   Average: {results.avg_response_time:.3f}")
        logger.info(f"   Median: {results.median_response_time:.3f}")
        logger.info(f"   Min: {results.min_response_time:.3f}")
        logger.info(f"   Max: {results.max_response_time:.3f}")
        logger.info(f"   95th percentile: {results.p95_response_time:.3f}")
        logger.info(f"   99th percentile: {results.p99_response_time:.3f}")
        
        if results.errors:
            logger.info(f"\n🚨 Errors:")
            for error, count in results.errors.items():
                logger.info(f"   {error}: {count}")

    async def save_results(self, results: LoadTestResults, filename: str):
        """Save results to JSON file"""
        data = {
            "timestamp": time.time(),
            "config": {
                "concurrent_users": self.config.concurrent_users,
                "requests_per_user": self.config.requests_per_user,
                "ramp_up_time": self.config.ramp_up_time,
                "base_url": self.config.base_url
            },
            "results": {
                "total_requests": results.total_requests,
                "successful_requests": results.successful_requests,
                "failed_requests": results.failed_requests,
                "avg_response_time": results.avg_response_time,
                "min_response_time": results.min_response_time,
                "max_response_time": results.max_response_time,
                "median_response_time": results.median_response_time,
                "p95_response_time": results.p95_response_time,
                "p99_response_time": results.p99_response_time,
                "requests_per_second": results.requests_per_second,
                "error_rate": results.error_rate,
                "errors": results.errors
            }
        }
        
        async with aiofiles.open(filename, 'w') as f:
            await f.write(json.dumps(data, indent=2))
        
        logger.info(f"💾 Results saved to {filename}")


class SystemMonitor:
    """Monitor system resources during load tests"""
    
    def __init__(self):
        self.monitoring = False
        self.cpu_usage = []
        self.memory_usage = []
        self.disk_usage = []
        
    async def start_monitoring(self):
        """Start monitoring system resources"""
        self.monitoring = True
        self.cpu_usage = []
        self.memory_usage = []
        self.disk_usage = []
        
        while self.monitoring:
            self.cpu_usage.append(psutil.cpu_percent())
            self.memory_usage.append(psutil.virtual_memory().percent)
            self.disk_usage.append(psutil.disk_usage('/').percent)
            await asyncio.sleep(1)
    
    def stop_monitoring(self):
        """Stop monitoring and return results"""
        self.monitoring = False
        
        return {
            "cpu": {
                "avg": statistics.mean(self.cpu_usage) if self.cpu_usage else 0,
                "max": max(self.cpu_usage) if self.cpu_usage else 0,
                "min": min(self.cpu_usage) if self.cpu_usage else 0
            },
            "memory": {
                "avg": statistics.mean(self.memory_usage) if self.memory_usage else 0,
                "max": max(self.memory_usage) if self.memory_usage else 0,
                "min": min(self.memory_usage) if self.memory_usage else 0
            },
            "disk": {
                "avg": statistics.mean(self.disk_usage) if self.disk_usage else 0,
                "max": max(self.disk_usage) if self.disk_usage else 0,
                "min": min(self.disk_usage) if self.disk_usage else 0
            }
        }


async def run_comprehensive_load_tests():
    """Run a comprehensive suite of load tests"""
    logger.info("🧪 Fleet Tracker Comprehensive Load Testing Suite")
    logger.info("=" * 60)
    
    # Test configurations
    test_configs = [
        (LoadTestConfig(concurrent_users=1, requests_per_user=10), "Single User Test"),
        (LoadTestConfig(concurrent_users=5, requests_per_user=10), "Light Load Test"),
        (LoadTestConfig(concurrent_users=10, requests_per_user=10), "Medium Load Test"),
        (LoadTestConfig(concurrent_users=20, requests_per_user=5), "High Load Test"),
        (LoadTestConfig(concurrent_users=50, requests_per_user=2), "Stress Test"),
    ]
    
    all_results = []
    
    for config, test_name in test_configs:
        logger.info(f"\n🎯 Preparing {test_name}...")
        
        # Start system monitoring
        monitor = SystemMonitor()
        monitor_task = asyncio.create_task(monitor.start_monitoring())
        
        try:
            # Run load test
            tester = LoadTester(config)
            results = await tester.run_load_test(test_name)
            
            # Stop monitoring
            monitor.stop_monitoring()
            monitor_task.cancel()
            
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
            
            # Get system stats
            system_stats = monitor.stop_monitoring()
            
            # Print results
            tester.print_results(results, test_name)
            
            # Print system stats
            logger.info(f"\n🖥️ System Resources:")
            logger.info(f"   CPU: {system_stats['cpu']['avg']:.1f}% avg, {system_stats['cpu']['max']:.1f}% max")
            logger.info(f"   Memory: {system_stats['memory']['avg']:.1f}% avg, {system_stats['memory']['max']:.1f}% max")
            logger.info(f"   Disk: {system_stats['disk']['avg']:.1f}% avg, {system_stats['disk']['max']:.1f}% max")
            
            # Save results
            filename = f"load_test_results_{test_name.lower().replace(' ', '_')}_{int(time.time())}.json"
            await tester.save_results(results, filename)
            
            all_results.append((test_name, results, system_stats))
            
            # Cool down between tests
            if config != test_configs[-1][0]:  # Not the last test
                logger.info("😴 Cooling down for 10 seconds...")
                await asyncio.sleep(10)
                
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            monitor.stop_monitoring()
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
    
    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info("📋 LOAD TEST SUMMARY")
    logger.info(f"{'='*60}")
    
    for test_name, results, system_stats in all_results:
        logger.info(f"\n{test_name}:")
        logger.info(f"  ✅ Success Rate: {100 - results.error_rate:.1f}%")
        logger.info(f"  ⚡ RPS: {results.requests_per_second:.2f}")
        logger.info(f"  ⏱️ Avg Response: {results.avg_response_time:.3f}s")
        logger.info(f"  🖥️ CPU: {system_stats['cpu']['avg']:.1f}%")


if __name__ == "__main__":
    asyncio.run(run_comprehensive_load_tests())
