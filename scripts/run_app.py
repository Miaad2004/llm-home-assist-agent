"""
Entry point for launching the Smart Home Assistant system.
Initializes core components and starts the main loop (text-based demo).
"""
from app.agent.agent_impl import MyAgent
from app.agent.llm_client_impl import GenericLLMClient
from app.devices.hardware import ArduinoController
from app.ui.ui_impl import SmartHomeUIManagerImpl
from config.settings import Settings
from tests.test_tools import run_test_tools
from colorama import Fore, Back, Style, init
import os

from app.tools import tools

# Initialize colorama for Windows compatibility
init(autoreset=True)

def main():
    # Clear the console on start (cross-platform)
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    llm_client = GenericLLMClient()
    device_control = ArduinoController()
    agent = MyAgent(llm_client=llm_client, 
                    tools=tools.TOOLS,
                    device_control=device_control)
    # ui = SmartHomeUIManagerImpl(agent=agent)

    print(f"{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════╗")
    print(f"║        Smart Home Assistant          ║")
    print(f"║         (Text Demo Mode)             ║")
    print(f"╚══════════════════════════════════════╝{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}💡 Type 'exit' to quit.{Style.RESET_ALL}\n")
    
    while True:
        user_text = input(f"{Fore.GREEN}🏠 You: {Style.RESET_ALL}")
        if user_text.strip().lower() == "exit":
            print(f"{Fore.MAGENTA}👋 Goodbye!{Style.RESET_ALL}")
            break
        
        elif user_text.strip() == "SYS_CLEAR_HIST":
            agent.llm_client.clear_hist()
            print(f"{Fore.YELLOW}🔄 History cleared.{Style.RESET_ALL}")
            continue
        
        # Agent handles user input and returns system message
        response = agent.handle_user_input(user_text)
        print(f"{Fore.BLUE}🤖 Assistant: {Fore.WHITE}{response}{Style.RESET_ALL}\n")
        #ui.display_response(response)


if __name__ == "__main__":
    main()