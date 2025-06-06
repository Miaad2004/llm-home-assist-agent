"""
Entry point for launching the Smart Home Assistant system.
Initializes core components and starts the main loop (text-based demo).
"""
from app.agent.agent_impl import MyAgent
from app.agent.llm_client_impl import GenericLLMClient
from app.devices.hardware import ArduinoHardwareSimulator
from app.ui.ui_impl import SmartHomeUIManagerImpl
from config.settings import Settings
from tests.test_tools import run_test_tools

from app.tools import tools

def main():
    llm_client = GenericLLMClient()
    agent = MyAgent(llm_client=llm_client, 
                    tools=tools.TOOLS)
    # ui = SmartHomeUIManagerImpl(agent=agent)

    print("Smart Home Assistant (text demo mode)")
    print("Type 'exit' to quit.")
    while True:
        user_text = input("You: ")
        if user_text.strip().lower() == "exit":
            print("Goodbye!")
            break
        # Agent handles user input and returns system message
        response = agent.handle_user_input(user_text)
        print(f"Assistant: {response}")
        #ui.display_response(response)


if __name__ == "__main__":
    main()
