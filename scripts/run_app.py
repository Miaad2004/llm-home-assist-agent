"""
Entry point for launching the Smart Home Assistant system.
Initializes core components and starts the main loop (text-based demo).
"""
from app.agent.agent_impl import DeviceCommandAgentImpl
from app.agent.llm_client_impl import GroqLLMClient
from app.devices.simulator import DeviceSimulator
from app.ui.ui_impl import SmartHomeUIManagerImpl


def main():
    # Initialize components
    llm_client = GroqLLMClient()
    device_controller = DeviceSimulator()
    agent = DeviceCommandAgentImpl(llm_client, device_controller)
    ui = SmartHomeUIManagerImpl(agent=agent)

    print("Smart Home Assistant (text demo mode)")
    print("Type 'exit' to quit.")
    while True:
        user_text = input("You: ")
        if user_text.strip().lower() == "exit":
            print("Goodbye!")
            break
        # Agent handles user input and returns system message
        response = agent.handle_user_input(user_text)
        ui.display_response(response)

if __name__ == "__main__":
    main()
