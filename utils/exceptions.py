"""
Custom Exception Classes for Smart Hostel Management System.
All domain-specific errors are defined here for clean error handling.
"""


class InvalidStudentID(Exception):
    """Raised when a student ID is not found or invalid."""
    def __init__(self, student_id: str = ""):
        self.student_id = student_id
        message = f"Invalid Student ID: '{student_id}'" if student_id else "Invalid Student ID."
        super().__init__(message)


class RoomNotAvailable(Exception):
    """Raised when a room has no available beds or does not exist."""
    def __init__(self, room_number: str = ""):
        self.room_number = room_number
        message = f"Room '{room_number}' is not available." if room_number else "No rooms available."
        super().__init__(message)


class InvalidFeeAmount(Exception):
    """Raised when a fee amount is zero, negative, or non-numeric."""
    def __init__(self, amount=None):
        self.amount = amount
        message = f"Invalid fee amount: '{amount}'." if amount is not None else "Invalid fee amount."
        super().__init__(message)


class DuplicateStudentRegistration(Exception):
    """Raised when trying to register a student who already exists."""
    def __init__(self, student_id: str = ""):
        self.student_id = student_id
        message = f"Student '{student_id}' is already registered." if student_id else "Duplicate student registration."
        super().__init__(message)


class InvalidComplaintID(Exception):
    """Raised when a complaint ID is not found or invalid."""
    def __init__(self, complaint_id: str = ""):
        self.complaint_id = complaint_id
        message = f"Invalid Complaint ID: '{complaint_id}'" if complaint_id else "Invalid Complaint ID."
        super().__init__(message)


class InvalidRoomID(Exception):
    """Raised when a room ID is not found or invalid."""
    def __init__(self, room_id: str = ""):
        self.room_id = room_id
        message = f"Invalid Room ID: '{room_id}'" if room_id else "Invalid Room ID."
        super().__init__(message)


class UnauthorizedAccess(Exception):
    """Raised when a user tries to access a restricted area without login."""
    def __init__(self):
        super().__init__("Unauthorized access. Please login first.")


class InvalidDateFormat(Exception):
    """Raised when a date string is not in the expected format."""
    def __init__(self, date_str: str = ""):
        self.date_str = date_str
        message = f"Invalid date format: '{date_str}'. Expected YYYY-MM-DD." if date_str else "Invalid date format."
        super().__init__(message)
