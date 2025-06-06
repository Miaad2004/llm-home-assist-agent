"""
Entry point for launching the Smart Home Assistant system.
Initializes core components and starts the main loop (text-based demo).
"""
from app.agent.agent_impl import DeviceCommandAgentImpl
from app.agent.llm_client_impl import GenericOpenAILLMClient
from app.devices.simulator import DeviceSimulator
from app.ui.ui_impl import SmartHomeUIManagerImpl
from config.settings import Settings


def main():
    # Initialize components
    api_key = Settings.GROQ_API_KEY or Settings.OPENAI_API_KEY or ""
    if Settings.GROQ_API_KEY:
        api_base = getattr(Settings, "GROQ_API_ENDPOINT", "")
        model = "gemma2-9b-it"
    else:
        api_base = ""  # Use default OpenAI endpoint
        model = "gpt-3.5-turbo"
        
    llm_client = GenericOpenAILLMClient(api_key=api_key, model=model, api_base=api_base)
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
        print(f"Assistant: {response}")


if __name__ == "__main__":
    main()
