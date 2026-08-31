#!/usr/bin/env python3
"""CarlaAir Quick Start - Step 1: Connection Verification"""
import carla
import airsim

# Connect to CARLA（Ground Simulation）
client = carla.Client('localhost', 2000)
client.set_timeout(10)
world = client.get_world()
print(f"CARLA world: {world.get_map().name}")
print(f"Length: {len(world.get_map().get_spawn_points())} 个")

# Connect to AirSim（空中仿真）
air = airsim.MultirotorClient(port=41451)
air.confirmConnection()
print("AirSim connection confirmation")

weather = world.get_weather()
print(f"={weather.sun_altitude_angle:.1f}°, Sun Cloudiness={weather.cloudiness:.1f}%")
print("\nCarlaAir Ready! Both ground and aerial APIs are available")
