#!/usr/bin/env python3
"""CarlaAir Quick Start - Interactive Weather Control"""
import carla

client = carla.Client('localhost', 2000)
world = client.get_world()

print("=== CARLA Interactive Weather Control ===")
print("Commands: 'make it rain', 'make it sunny', 'start wind', 'foggy', 'cloudy', 'exit'")

while True:
    try:
        prompt = input("\nEnter weather prompt: ").strip().lower()
        
        if prompt in ["exit", "quit"]:
            print("Exiting weather control.")
            break
            
        # Get current weather state to allow incremental changes
        weather = world.get_weather()
        
        if "rain" in prompt:
            weather.precipitation = 100.0
            weather.precipitation_deposits = 80.0
            weather.cloudiness = 90.0
            weather.wetness = 100.0
            print("-> Weather updated: Heavy Rain activated.")
            
        elif "sunny" in prompt or "clear" in prompt:
            weather = carla.WeatherParameters.ClearNoon
            print("-> Weather updated: Restored to Sunny.")
            
        elif "wind" in prompt:
            weather.wind_intensity = 80.0
            print("-> Weather updated: Wind intensity increased.")
            
        elif "cloud" in prompt:
            weather.cloudiness = 80.0
            weather.sun_altitude_angle = 50.0
            print("-> Weather updated: Cloudy skies.")
            
        elif "fog" in prompt:
            weather.fog_density = 90.0
            weather.fog_distance = 10.0
            weather.cloudiness = 40.0
            print("-> Weather updated: Dense Fog enabled.")
            
        else:
            print("-> Command not recognized. Try variations like 'make it rain', 'make it sunny', or 'start wind'.")
            continue
            
        world.set_weather(weather)

    except KeyboardInterrupt:
        print("\nExiting weather control.")
        break