"""
Entry point for launching the Smart Home Assistant system.
Initializes core components and starts the main loop (text-based demo).
"""
from app.agent.agent_impl import MyAgent
from app.agent.llm_client_impl import GenericOpenAILLMClient
from app.devices.hardware import ArduinoHardwareSimulator
from app.ui.ui_impl import SmartHomeUIManagerImpl
from config.settings import Settings

from app.data import tools

def main():
    # Initialize components
    api_key = Settings.GROQ_API_KEY or ""
    api_base = getattr(Settings, "GROQ_API_ENDPOINT", "")
    system_prompt_path = Settings.SYSTEM_PROMPT_PATH or ""
    llm_client = GenericOpenAILLMClient(api_key=api_key, model="gemma2-9b-it", api_base=api_base, system_prompt_path=system_prompt_path)
    # device_controller = DeviceSimulator()
    agent = MyAgent(llm_client=llm_client, tools=tools)
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
