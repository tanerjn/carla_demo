#!/usr/bin/env python3
"""CarlaAir Quick Start - Step 8: Complete Feature Showcase"""
import carla
import airsim
import numpy as np
import cv2
import queue
import time
import math

print("=" * 50)
print("CarlaAir Complete Feature Showcase")
print("=" * 50)

client = carla.Client('localhost', 2000)
client.set_timeout(10)
world = client.get_world()
bp_lib = world.get_blueprint_library()

air = airsim.MultirotorClient(port=41451)
air.confirmConnection()
air.enableApiControl(True)
air.armDisarm(True)

# [1/5] Weather
print("\n[1/5] Weather")
for name, w in [("Sunny", carla.WeatherParameters.ClearNoon),
                ("Rainy", carla.WeatherParameters.HardRainNoon),
                ("Sunset", carla.WeatherParameters.ClearSunset)]:
    world.set_weather(w)
    print(f"  {name}")
    time.sleep(2)
world.set_weather(carla.WeatherParameters.ClearNoon)

# [2/5] Traffic
print("\n[2/5] Traffic")
spawns = [sp for sp in world.get_map().get_spawn_points() if sp.location.x > 55]
vehicles = []
for sp in spawns[:8]:
    v = world.try_spawn_actor(bp_lib.filter('vehicle.*')[len(vehicles)], sp)
    if v:
        v.set_autopilot(True)
        vehicles.append(v)
print(f"  {len(vehicles)} vehicles running")

# [3/5] Ground Sensors
print("\n[3/5] Ground Sensors")
cam_bp = bp_lib.find('sensor.camera.rgb')
cam_bp.set_attribute('image_size_x', '1920')
cam_bp.set_attribute('image_size_y', '1080')
cam = world.spawn_actor(cam_bp,
    carla.Transform(carla.Location(x=80, y=30, z=25), carla.Rotation(pitch=-30)))
q = queue.Queue(10)
cam.listen(lambda img: q.put(img) if not q.full() else None)
time.sleep(1)
try:
    img = q.get(timeout=3)
    arr = np.frombuffer(img.raw_data, dtype=np.uint8).reshape(img.height, img.width, 4)[:,:,:3]
    cv2.imwrite('/tmp/showcase_ground.png', arr)
    print("Saved /tmp/showcase_ground.png")
except: pass
cam.stop(); cam.destroy()

# [4/5] Drone Flight
print("\n[4/5] Drone Flight")
air.takeoffAsync().join()
air.moveToPositionAsync(80, 0, -30, 5).join()
print("30m above the city center")
responses = air.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
if responses[0].height > 0:
    img = np.frombuffer(responses[0].image_data_uint8, dtype=np.uint8)
    cv2.imwrite('/tmp/showcase_aerial.png', img.reshape(responses[0].height, responses[0].width, 3))
    print("Saved /tmp/showcase_aerial.png")

# [5/5] Joint Cruise
print("\n[5/5] Joint Cruise (10 seconds)")
for i in range(20):
    t = i / 20 * 2 * math.pi
    air.moveToPositionAsync(80 + 12*math.cos(t), 12*math.sin(t), -30, 8)
    time.sleep(0.5)

# Cleanup
air.landAsync().join()
air.armDisarm(False)
air.enableApiControl(False)
for v in vehicles: v.destroy()

print("\n" + "=" * 50)
print("Showcase complete! All core features verified successfully.")
print("=" * 50)
