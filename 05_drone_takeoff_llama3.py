import airsim
import ollama

def continuous_drone_control():
    """
    Runs a closed-loop system where the drone stays airborne and 
    continuously accepts new target coordinates or commands.
    """
    client = airsim.MultirotorClient()
    client.confirmConnection()
    client.enableApiControl(True)
    client.armDisarm(True)

    print("Taking off and establishing hover...")
    client.takeoffAsync().join()

    print("\n--- Closed-Loop Drone Control Active ---")
    print("Provide direct coordinates (e.g., '10, 5, -5') or natural language commands.")
    print("Type 'land' or 'exit' to end the session.\n")

    try:
        while True:
            user_input = input("Target / Command > ").strip()
            
            if user_input.lower() in ["land", "exit", "quit"]:
                break

            try:
                # Check if input is already formatted as direct coordinates
                if "," in user_input and all(part.strip().replace('-', '').replace('.', '', 1).isdigit() for part in user_input.split(',')):
                    target_x, target_y, target_z = map(float, user_input.split(","))
                else:
                    # Use local Mistral to interpret natural language into absolute target coordinates
                    system_prompt = (
                        "You are a drone flight controller. Parse the user instruction into absolute "
                        "target coordinates x, y, and z in meters using the NED coordinate system. "
                        "Output ONLY the comma-separated numbers format: x, y, z"
                    )
                    response = ollama.chat(
                        model="llama3.1:latest",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_input},
                        ],
                    )
                    raw_output = response["message"]["content"].strip()
                    print(f"Mistral interpreted target: {raw_output}")
                    target_x, target_y, target_z = map(float, raw_output.split(","))

                print(f"Moving to -> X: {target_x}, Y: {target_y}, Z: {target_z}")
                client.moveToPositionAsync(target_x, target_y, target_z, 5).join()
                print("Target reached. Ready for next command.\n")

            except Exception as e:
                print(f"Error processing movement: {e}\n")

    finally:
        print("Landing drone...")
        client.landAsync().join()
        client.armDisarm(False)
        client.enableApiControl(False)
        print("Mission terminated safely.")

if __name__ == "__main__":
    continuous_drone_control()
