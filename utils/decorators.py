"""
Decorators for Smart Hostel Management System.
Provides activity logging and other cross-cutting concerns.
"""

import os
import functools
from datetime import datetime
from typing import Callable, Any

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "activity_log.txt")


def ensure_log_dir() -> None:
    """Ensure the logs directory exists."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log_activity(func: Callable) -> Callable:
    """
    Decorator that logs every function call to activity_log.txt.
    Format: [DATE TIME] FUNCTION_NAME EXECUTED
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        ensure_log_dir()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {func.__name__.upper()} EXECUTED\n"
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as log_file:
                log_file.write(log_entry)
        except OSError:
            pass  # Non-fatal: don't crash the app if logging fails
        return func(*args, **kwargs)
    return wrapper


def require_login(func: Callable) -> Callable:
    """
    Decorator that checks if the hostel system is logged in.
    The first positional argument must be a HostelManagementSystem instance.
    """
    @functools.wraps(func)
    def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        from utils.exceptions import UnauthorizedAccess
        if not getattr(self, "_logged_in", False):
            raise UnauthorizedAccess()
        return func(self, *args, **kwargs)
    return wrapper


def validate_input(func: Callable) -> Callable:
    """
    Decorator that catches common input-related exceptions and prints user-friendly messages.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            print(f"\n  [ERROR] Invalid input: {e}")
        except KeyError as e:
            print(f"\n  [ERROR] Missing data key: {e}")
        except IndexError as e:
            print(f"\n  [ERROR] Index out of range: {e}")
        except TypeError as e:
            print(f"\n  [ERROR] Type mismatch: {e}")
    return wrapper


def confirm_action(prompt: str = "Are you sure? (y/n): ") -> Callable:
    """
    Parameterized decorator that requires confirmation before executing a function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            choice = input(f"\n  {prompt}").strip().lower()
            if choice == "y":
                return func(*args, **kwargs)
            else:
                print("  Action cancelled.")
        return wrapper
    return decorator
