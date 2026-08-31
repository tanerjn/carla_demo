#!/usr/bin/env python3
"""CarlaAir Quick Start - Step 3: Spawn Traffic"""
import carla
import random
import time

client = carla.Client('localhost', 2000)
world = client.get_world()
bp_lib = world.get_blueprint_library()

# Spawn vehicles near the city center (x > 55, away from the coast)
spawn_points = world.get_map().get_spawn_points()
city_spawns = [sp for sp in spawn_points if sp.location.x > 55][:10]

vehicles = []
for sp in city_spawns:
    bp = random.choice(bp_lib.filter('vehicle.*'))
    if bp.has_attribute('color'):
        bp.set_attribute('color', random.choice(bp.get_attribute('color').recommended_values))
    v = world.try_spawn_actor(bp, sp)
    if v:
        print(f"Spawned vehicle: {v.type_id} at {v.get_location()}")
        # v.set_autopilot(True)
        vehicles.append(v)
print(f"Spawned {len(vehicles)} autonomous vehicles")

# Spawn static pedesterians
walkers = []
for _ in range(15):
    loc = world.get_random_location_from_navigation()
    if loc:
        bp = random.choice(bp_lib.filter('walker.pedestrian.*'))
        if bp.has_attribute('is_invincible'):
            bp.set_attribute('is_invincible', 'true')
        w = world.try_spawn_actor(bp, carla.Transform(loc))
        if w:
            walkers.append(w)
print(f"Spawned {len(walkers)} pedesterians")

print("Observing traffic... (20 seconds)")
time.sleep(20)

for v in vehicles: v.destroy()
for w in walkers: w.destroy()
print("Cleanup completed")
