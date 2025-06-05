from datetime import datetime

# Assigned to: Person A (Data pipeline)
class TimeUtils:
    """
    Provides current time and date utilities.
    """
    def get_current_time(self) -> str:
        """
        Input: None
        Output: str — Current time (e.g., "12:45 PM")
        Calls: datetime.now()
        """
        # TODO: Implement time formatting as needed
        return datetime.now().strftime("%I:%M %p")

    def get_current_date(self) -> str:
        """
        Input: None
        Output: str — Current date (e.g., "2025-06-05")
        Calls: datetime.now()
        """
        # TODO: Implement date formatting as needed
        return datetime.now().strftime("%Y-%m-%d")
