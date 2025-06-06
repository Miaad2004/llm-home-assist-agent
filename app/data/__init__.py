import datetime

tools = {"get_time": lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
         "get_weather": lambda: "Sunny, 25°C",}