import json
import re
import airsim
import ollama

# Match vehicle names defined in AirSim's settings.json
DRONES = ["Drone1", "Drone2"]


def parse_llm_response(raw_response: str) -> list[dict]:
    """Extract and parse structured JSON targets from LLM output."""
    cleaned = re.sub(r"```(?:json)?\s*(.*?)\s*```", r"\1", raw_response, flags=re.DOTALL).strip()
    data = json.loads(cleaned)
    if isinstance(data, dict):
        return [data]
    return data


def continuous_drone_control():
    """
    Runs a closed-loop control system managing two drones simultaneously.
    Accepts direct commands (e.g., 'Drone1: 10, 5, -5') or multi-drone instructions.
    """
    client = airsim.MultirotorClient()
    client.confirmConnection()

    print("Connecting and enabling control for all drones...")
    for drone in DRONES:
        client.enableApiControl(True)
        client.armDisarm(True)

    print("Initiating simultaneous takeoff for Drone1 and Drone2...")
    # Fire takeoff calls asynchronously for concurrent operation
    takeoff_tasks = [client.takeoffAsync(vehicle_name=d) for d in DRONES]
    for task in takeoff_tasks:
        task.join()

    print("\n--- Dual-Drone Control Active ---")
    print("Provide direct inputs (e.g., 'Drone1: 10, 5, -5') or natural language commands.")
    print("Example: 'Send Drone1 to 10, 0, -10 and fly Drone2 to -5, 10, -8'")
    print("Type 'land' or 'exit' to terminate.\n")

    try:
        while True:
            user_input = input("Target / Command > ").strip()

            if user_input.lower() in ["land", "exit", "quit"]:
                break

            try:
                targets = []

                # Direct string check: "Drone1: x, y, z"
                if ":" in user_input and any(user_input.startswith(d) for d in DRONES):
                    drone_part, coords_part = user_input.split(":", 1)
                    target_drone = drone_part.strip()
                    coords = [float(c.strip()) for c in coords_part.split(",")]
                    targets.append({
                        "drone": target_drone,
                        "x": coords[0],
                        "y": coords[1],
                        "z": coords[2]
                    })
                else:
                    # Instruct LLM to generate target vectors for active vehicles
                    system_prompt = (
                        "You are a dual-UAV flight controller managing 'Drone1' and 'Drone2'. "
                        "Parse instructions into target coordinates (x, y, z in meters, AirSim NED system). "
                        "Respond strictly with a JSON array of objects, containing keys: "
                        "\"drone\" (string: 'Drone1' or 'Drone2'), \"x\" (float), \"y\" (float), \"z\" (float). "
                        "Example output: [{\"drone\": \"Drone1\", \"x\": 10.0, \"y\": 5.0, \"z\": -5.0}]"
                    )

                    response = ollama.chat(
                        model="llama3.1:latest",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_input},
                        ],
                    )

                    raw_output = response["message"]["content"].strip()
                    print(f"LLM parsed targets: {raw_output}")
                    targets = parse_llm_response(raw_output)

                # Dispatch movement commands concurrently
                move_tasks = []
                for target in targets:
                    d_name = target.get("drone")
                    if d_name in DRONES:
                        tx, ty, tz = float(target["x"]), float(target["y"]), float(target["z"])
                        print(f"[{d_name}] Moving -> X: {tx}, Y: {ty}, Z: {tz}")
                        task = client.moveToPositionAsync(
                            tx, ty, tz, velocity=5, vehicle_name=d_name
                        )
                        move_tasks.append((d_name, task))
                    else:
                        print(f"Warning: Ignored unrecognized vehicle '{d_name}'.")

                # Block until all active flight tasks finish
                for d_name, task in move_tasks:
                    task.join()
                    print(f"[{d_name}] Reached target position.")

                print("All targets reached. Ready for next command.\n")

            except Exception as e:
                print(f"Error executing command: {e}\n")

    finally:
        print("Landing all drones...")
        land_tasks = [client.landAsync(vehicle_name=d) for d in DRONES]
        for task in land_tasks:
            task.join()

        for drone in DRONES:
            client.armDisarm(False, vehicle_name=drone)
            client.enableApiControl(False, vehicle_name=drone)

        print("Session closed safely.")


if __name__ == "__main__":
    continuous_drone_control()
