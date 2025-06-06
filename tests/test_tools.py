from app.tools.generic_tools import GenericTools
from app.tools.web_viewer import WebViewer
from app.tools.tools import TOOLS

def run_test_tools():
    for tool_name, tool_info in TOOLS.items():
        print(f"Tool Name: {tool_name}")
        print(f"Description: {tool_info['description']}")
        print(f"Function Docstring: {tool_info['function_docstring']}")
        print(f"Parameters: {tool_info['parameters']}")
        print(f"Function: {tool_info['function'].__name__}\n")
        
        # test weather
        print(f"Testing {tool_name}...")
        if tool_name == "get_url_content":
            # Example test for get_url_content
            url_content_output = tool_info['function']("https://example.com")
            print(f"URL Content Output: {url_content_output}\n")
    
        elif tool_name == "get_weather":
            # Example test for get_weather
            weather_output = tool_info['function']("New York")
            print(f"Weather Output: {weather_output}\n")
        
        elif tool_name == "get_date_time":
            # Example test for get_date_time
            date_time_output = tool_info['function']()
            print(f"Date and Time Output: {date_time_output}\n")
        
        elif tool_name == "get_news":
            # Example test for get_news
            news_output = tool_info['function']("latest technology")
            print(f"News Output: {news_output}\n")
        
        elif tool_name == "view_webpage":
            # Example test for view_webpage
            webpage_output = tool_info['function']("https://example.com")
            print(f"Webpage Output: {webpage_output}\n")
        
        elif tool_name == "search_web":
            # Example test for search_web
            search_output = tool_info['function']("latest AI news")
            print(f"Search Output: {search_output}\n")
        
        input("Press Enter to continue to the next tool...")
    