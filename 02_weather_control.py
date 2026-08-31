#!/usr/bin/env python3
"""CarlaAir Quick Start - Step 2: Weather Control"""
import carla
import time

client = carla.Client('localhost', 2000)
world = client.get_world()

presets = {
    "Sunny": {"sun_altitude_angle": 70, "cloudiness": 10},
    "Cloudy": {"sun_altitude_angle": 50, "cloudiness": 80},
    "Heavy": {"precipitation": 100, "cloudiness": 90, "wetness": 100,
             "precipitation_deposits": 80, "wind_intensity": 50},
    "Rain": {"fog_density": 80, "fog_distance": 10, "cloudiness": 60},
    "Heavy Fog": {"sun_altitude_angle": 5, "cloudiness": 30},
}

for name, params in presets.items():
    weather = carla.WeatherParameters()
    for k, v in params.items():
        setattr(weather, k, v)
    world.set_weather(weather)
    print(f"Weather Switched: {name}")
    time.sleep(10)

world.set_weather(carla.WeatherParameters.ClearNoon)
print("Weather restored to Sunny")
