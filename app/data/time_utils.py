from datetime import datetime

# Assigned to: Person C (Data pipeline)
class TimeUtils:
    """
    Provides current time and date utilities.
    """
    @staticmethod
    def get_current_datetime() -> str:
        """
        Input: None
        Output: str — Current date and time (e.g., "2025-06-05 12:45 PM")
        Calls: datetime.now()
        """
        return datetime.now().strftime("%Y-%m-%d %I:%M %p")