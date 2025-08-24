#!/usr/bin/env python3
"""GPS Device Simulator for Fleet Tracker Testing"""

import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from typing import List, Tuple
import argparse
import logging

import aiomqtt
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPSPoint(BaseModel):
    """GPS coordinate point"""
    latitude: float
    longitude: float
    name: str = ""

class VehicleSimulator:
    """Simulates a single GPS tracking device"""
    
    def __init__(
        self, 
        vehicle_id: str, 
        device_id: str,
        route_points: List[GPSPoint],
        mqtt_client: aiomqtt.Client
    ):
        self.vehicle_id = vehicle_id
        self.device_id = device_id
        self.route_points = route_points
        self.mqtt_client = mqtt_client
        self.current_point_index = 0
        self.current_lat = route_points[0].latitude
        self.current_lng = route_points[0].longitude
        self.speed = 0.0
        self.heading = 0
        self.is_running = False
        self.odometer = random.uniform(10000, 50000)
        self.fuel_level = random.uniform(20, 100)
        
    async def start_simulation(self, update_interval: float = 5.0):
        """Start GPS simulation"""
        self.is_running = True
        logger.info(f"🚗 Starting simulation for vehicle {self.vehicle_id}")
        
        while self.is_running:
            try:
                # Move towards next point
                await self._move_to_next_point()
                
                # Send GPS data
                await self._send_gps_data()
                
                # Send heartbeat occasionally
                if random.random() < 0.2:  # 20% chance
                    await self._send_heartbeat()
                
                await asyncio.sleep(update_interval)
                
            except Exception as e:
                logger.error(f"Simulation error for {self.vehicle_id}: {str(e)}")
                await asyncio.sleep(1)
    
    async def stop_simulation(self):
        """Stop GPS simulation"""
        self.is_running = False
        logger.info(f"🛑 Stopped simulation for vehicle {self.vehicle_id}")
    
    async def _move_to_next_point(self):
        """Move vehicle towards next route point"""
        if not self.route_points:
            return
        
        target_point = self.route_points[self.current_point_index]
        
        # Calculate direction and distance to target
        lat_diff = target_point.latitude - self.current_lat
        lng_diff = target_point.longitude - self.current_lng
        distance = (lat_diff ** 2 + lng_diff ** 2) ** 0.5
        
        # If close to target, move to next point
        if distance < 0.001:  # ~100m
            self.current_point_index = (self.current_point_index + 1) % len(self.route_points)
            self.speed = random.uniform(30, 80)  # km/h
            return
        
        # Move towards target
        move_speed = 0.001  # Adjust for realistic movement speed
        if distance > 0:
            self.current_lat += (lat_diff / distance) * move_speed
            self.current_lng += (lng_diff / distance) * move_speed
        
        # Calculate heading
        import math
        self.heading = int(math.degrees(math.atan2(lng_diff, lat_diff))) % 360
        
        # Update vehicle stats
        self.odometer += 0.1  # km
        self.fuel_level = max(0, self.fuel_level - 0.01)
    
    async def _send_gps_data(self):
        """Send GPS data via MQTT"""
        gps_data = {
            "device_id": self.device_id,
            "vehicle_id": self.vehicle_id,
            "timestamp": datetime.utcnow().isoformat(),
            "latitude": self.current_lat,
            "longitude": self.current_lng,
            "altitude": random.uniform(50, 200),
            "speed": self.speed,
            "heading": self.heading,
            "satellites": random.randint(6, 12),
            "hdop": random.uniform(0.8, 2.0),
            "accuracy": random.uniform(3, 15),
            "battery_level": random.randint(70, 100),
            "ignition": True,
            "odometer": self.odometer,
            "fuel_level": self.fuel_level
        }
        
        topic = f"fleet/vehicles/{self.vehicle_id}/location"
        payload = json.dumps(gps_data)
        
        await self.mqtt_client.publish(topic, payload)
        logger.debug(f"📍 Sent GPS data for {self.vehicle_id}: {self.current_lat:.6f}, {self.current_lng:.6f}")
    
    async def _send_heartbeat(self):
        """Send device heartbeat"""
        heartbeat_data = {
            "device_id": self.device_id,
            "vehicle_id": self.vehicle_id,
            "timestamp": datetime.utcnow().isoformat(),
            "battery_level": random.randint(80, 100),
            "signal_strength": random.randint(60, 100),
            "temperature": random.uniform(20, 45),
            "status": "online"
        }
        
        topic = f"fleet/devices/{self.device_id}/heartbeat"
        payload = json.dumps(heartbeat_data)
        
        await self.mqtt_client.publish(topic, payload)
        logger.debug(f"💓 Sent heartbeat for device {self.device_id}")

class GPSFleetSimulator:
    """Simulates multiple GPS tracking devices"""
    
    def __init__(self, mqtt_host="localhost", mqtt_port=1883, mqtt_username=None, mqtt_password=None):
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        self.vehicles = []
        self.mqtt_client = None
        
    async def setup_mqtt(self):
        """Setup MQTT connection"""
        self.mqtt_client = aiomqtt.Client(
            hostname=self.mqtt_host,
            port=self.mqtt_port,
            username=self.mqtt_username,
            password=self.mqtt_password,
            client_id=f"gps-simulator-{int(time.time())}"
        )
        
        await self.mqtt_client.__aenter__()
        logger.info(f"✅ Connected to MQTT broker at {self.mqtt_host}:{self.mqtt_port}")
    
    async def cleanup_mqtt(self):
        """Cleanup MQTT connection"""
        if self.mqtt_client:
            await self.mqtt_client.__aexit__(None, None, None)
            logger.info("✅ Disconnected from MQTT broker")
    
    def add_vehicle(self, vehicle_id: str, device_id: str, route_points: List[GPSPoint]):
        """Add vehicle to simulation"""
        vehicle = VehicleSimulator(vehicle_id, device_id, route_points, self.mqtt_client)
        self.vehicles.append(vehicle)
        logger.info(f"➕ Added vehicle {vehicle_id} with {len(route_points)} route points")
    
    async def start_simulation(self, update_interval: float = 5.0):
        """Start simulation for all vehicles"""
        logger.info(f"🚀 Starting GPS simulation for {len(self.vehicles)} vehicles")
        
        # Start simulation for each vehicle
        tasks = []
        for vehicle in self.vehicles:
            task = asyncio.create_task(vehicle.start_simulation(update_interval))
            tasks.append(task)
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("⏹️ Stopping simulation...")
            for vehicle in self.vehicles:
                await vehicle.stop_simulation()

def get_ho_chi_minh_routes() -> List[List[GPSPoint]]:
    """Get sample routes in Ho Chi Minh City"""
    return [
        # Route 1: District 1 to District 7
        [
            GPSPoint(latitude=10.8231, longitude=106.6297, name="Ben Thanh Market"),
            GPSPoint(latitude=10.8127, longitude=106.6256, name="Nguyen Hue"),
            GPSPoint(latitude=10.7769, longitude=106.7009, name="Phu My Hung"),
            GPSPoint(latitude=10.7411, longitude=106.7203, name="Crescent Mall"),
        ],
        # Route 2: Airport to City Center  
        [
            GPSPoint(latitude=10.8189, longitude=106.6520, name="Tan Son Nhat Airport"),
            GPSPoint(latitude=10.8145, longitude=106.6443, name="Airport Road"),
            GPSPoint(latitude=10.7879, longitude=106.6465, name="District 3"),
            GPSPoint(latitude=10.7769, longitude=106.6297, name="City Center"),
        ],
        # Route 3: Thu Duc to District 1
        [
            GPSPoint(latitude=10.8505, longitude=106.7717, name="Thu Duc"),
            GPSPoint(latitude=10.8275, longitude=106.7344, name="Binh Thanh"),
            GPSPoint(latitude=10.8048, longitude=106.6944, name="District 2"),
            GPSPoint(latitude=10.7867, longitude=106.6297, name="District 1"),
        ]
    ]

async def main():
    parser = argparse.ArgumentParser(description="GPS Fleet Simulator for Fleet Tracker")
    parser.add_argument("--mqtt-host", default="localhost", help="MQTT broker host")
    parser.add_argument("--mqtt-port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--mqtt-username", default="mqtt_user", help="MQTT username")
    parser.add_argument("--mqtt-password", default="mqtt_password", help="MQTT password")
    parser.add_argument("--vehicles", type=int, default=3, help="Number of vehicles to simulate")
    parser.add_argument("--interval", type=float, default=5.0, help="Update interval in seconds")
    
    args = parser.parse_args()
    
    # Create simulator
    simulator = GPSFleetSimulator(
        mqtt_host=args.mqtt_host,
        mqtt_port=args.mqtt_port,
        mqtt_username=args.mqtt_username,
        mqtt_password=args.mqtt_password
    )
    
    try:
        # Setup MQTT
        await simulator.setup_mqtt()
        
        # Add vehicles with different routes
        routes = get_ho_chi_minh_routes()
        
        for i in range(args.vehicles):
            vehicle_id = f"VEHICLE_{i+1:03d}"
            device_id = f"GPS_DEVICE_{i+1:03d}"
            route = routes[i % len(routes)]
            
            simulator.add_vehicle(vehicle_id, device_id, route)
        
        # Start simulation
        await simulator.start_simulation(args.interval)
        
    except KeyboardInterrupt:
        logger.info("👋 Simulation stopped by user")
    except Exception as e:
        logger.error(f"❌ Simulation error: {str(e)}")
    finally:
        await simulator.cleanup_mqtt()

if __name__ == "__main__":
    asyncio.run(main())
