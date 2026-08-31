#!/usr/bin/env python3
"""CarlaAir Quick Start - Step 4: Sensor Data Collection"""
import carla
import numpy as np
import cv2
import queue
import time

client = carla.Client('localhost', 2000)
world = client.get_world()
bp_lib = world.get_blueprint_library()

# Spawn vehicle with sensors
spawn_points = world.get_map().get_spawn_points()
vehicle = world.spawn_actor(
    bp_lib.find('vehicle.tesla.model3'),
    [sp for sp in spawn_points if sp.location.x > 55][0]
)
print(f"Spawned vehicle: {vehicle.type_id} at {vehicle.get_location()}")
# vehicle.set_autopilot(True)

# Attach RGB Camera
cam_bp = bp_lib.find('sensor.camera.rgb')
cam_bp.set_attribute('image_size_x', '1280')
cam_bp.set_attribute('image_size_y', '720')
cam_bp.set_attribute('fov', '100')
camera = world.spawn_actor(cam_bp,
    carla.Transform(carla.Location(x=1.5, z=2.0)), attach_to=vehicle)

img_queue = queue.Queue(10)
camera.listen(lambda img: img_queue.put(img) if not img_queue.full() else None)

print("Collecting 5 image frames...")
time.sleep(2)

for i in range(5):
    time.sleep(0.5)
    try:
        img = img_queue.get(timeout=2)
        arr = np.frombuffer(img.raw_data, dtype=np.uint8)
        frame = arr.reshape(img.height, img.width, 4)[:, :, :3]
        cv2.imwrite(f'/tmp/carla_frame_{i}.png', frame)
        print(f"Saved frame {i}: {img.width}x{img.height}")
    except queue.Empty:
        print(f"  Frame {i}: Timeout")

camera.stop(); camera.destroy(); vehicle.destroy()
print(f"Collection completed! Images: /tmp/carla_frame_*.png")
