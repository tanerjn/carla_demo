#!/usr/bin/env python3
"""CarlaAir Quick Start - Interactive Drone Control"""
import airsim
import time

client = airsim.MultirotorClient(port=41451)
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)
print("Drone armed and ready for interactive commands.")

print("=== AirSim Interactive Drone Control ===")
print("Commands: 'takeoff', 'land', 'move x y z' (e.g., move 80 0 -30), 'square', 'exit'")

try:
    while True:
        prompt = input("\nEnter drone command: ").strip().lower()
        parts = prompt.split()
        
        if not parts:
            continue
            
        cmd = parts[0]
        
        if cmd in ["exit", "quit"]:
            print("Landing and exiting...")
            client.landAsync().join()
            client.armDisarm(False)
            client.enableApiControl(False)
            break
            
        elif "takeoff" in cmd:
            print("Taking off...")
            client.takeoffAsync().join()
            print("Take-off complete!")
            
        elif "land" in cmd:
            print("Landing...")
            client.landAsync().join()
            print("Landing complete!")
            
        elif "move" in cmd and len(parts) >= 4:
            try:
                x = float(parts[1])
                y = float(parts[2])
                z = float(parts[3])
                print(f"Moving to NED position: ({x}, {y}, {z})...")
                client.moveToPositionAsync(x, y, z, 5).join()
                
                state = client.getMultirotorState()
                pos = state.kinematics_estimated.position
                print(f"Current position NED: ({pos.x_val:.1f}, {pos.y_val:.1f}, {pos.z_val:.1f})")
            except ValueError:
                print("Invalid coordinates. Usage: move x y z (e.g., move 80 0 -30)")
                
        elif "square" in cmd:
            print("Executing square route...")
            for i, (x, y, z) in enumerate([(90, 0, -30), (90, 10, -30), (80, 10, -30), (80, 0, -30)]):
                print(f"  Waypoint {i+1}/4: ({x}, {y}, {z})")
                client.moveToPositionAsync(x, y, z, 5).join()
            print("Square route complete!")
            
        else:
            print("Command not recognized. Try 'takeoff', 'land', 'move x y z', 'square', or 'exit'.")

except KeyboardInterrupt:
    print("\nEmergency landing and exiting...")
    try:
        client.landAsync().join()
        client.armDisarm(False)
        client.enableApiControl(False)
    except Exception:
        pass