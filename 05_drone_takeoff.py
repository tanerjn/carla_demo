#!/usr/bin/env python3
"""CarlaAir Quick Start - Step 5: Drone Takeoff and Flight"""
import airsim
import time
import math

client = airsim.MultirotorClient(port=41451)
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)
print("Drone armed，preparing for take-off...")

# Take-off
client.takeoffAsync().join()
print("Take-off complete!")

# Fly to the city center(NED: x=80 inland, y=0, z=-30 meaning 30m altitude)
print("Flying to the city center...")
client.moveToPositionAsync(80, 0, -30, 5).join()

state = client.getMultirotorState()
pos = state.kinematics_estimated.position
print(f"Current position NED: ({pos.x_val:.1f}, {pos.y_val:.1f}, {pos.z_val:.1f})")
print(f"Altitude: {abs(pos.z_val):.1f}m")

# Square flight path
print("Executing square route...")
for i, (x, y, z) in enumerate([(90,0,-30), (90,10,-30), (80,10,-30), (80,0,-30)]):
    print(f"  Waypoint {i+1}/4: ({x}, {y}, {z})")
    client.moveToPositionAsync(x, y, z, 5).join()

# Land
print("Landing...")
client.landAsync().join()
client.armDisarm(False)
client.enableApiControl(False)
print("Landing complete!")
