"""
Helper utilities — terminal UI, recursive search, sorting lambdas,
date helpers, and input validation.
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.student import Student
    from models.room import Room
    from models.complaint import Complaint

# ── Optional colour support ────────────────────────────────────────────────
try:
    from colorama import Fore, Back, Style, init as _cinit
    _cinit(autoreset=True)
    COLORS = True
except ImportError:
    COLORS = False


# ── Color helpers ─────────────────────────────────────────────────────────

def color(code: str, text: str) -> str:
    return f"{code}{text}{Style.RESET_ALL}" if COLORS else text

def green(text: str) -> str:
    return color(Fore.GREEN, text) if COLORS else text

def red(text: str) -> str:
    return color(Fore.RED, text) if COLORS else text

def yellow(text: str) -> str:
    return color(Fore.YELLOW, text) if COLORS else text

def cyan(text: str) -> str:
    return color(Fore.CYAN, text) if COLORS else text

def magenta(text: str) -> str:
    return color(Fore.MAGENTA, text) if COLORS else text

def bold(text: str) -> str:
    return f"\033[1m{text}\033[0m" if COLORS else text


# ── UI banners ────────────────────────────────────────────────────────────

def print_header(title: str, width: int = 52) -> None:
    border = "═" * width
    pad = (width - len(title) - 2) // 2
    print(f"\n  {cyan(border)}")
    print(f"  {cyan('║')}{' ' * pad}{bold(yellow(title))}{' ' * (width - pad - len(title))}{cyan('║')}")
    print(f"  {cyan(border)}\n")


def print_section(title: str, width: int = 46) -> None:
    print(f"\n  {cyan('─' * width)}")
    print(f"  {yellow('  ' + title)}")
    print(f"  {cyan('─' * width)}")


def success(msg: str) -> None:
    print(f"\n  {green('✔')}  {green(msg)}")


def error(msg: str) -> None:
    print(f"\n  {red('✘')}  {red(msg)}")


def info(msg: str) -> None:
    print(f"\n  {cyan('ℹ')}  {msg}")


def warning(msg: str) -> None:
    print(f"\n  {yellow('⚠')}  {yellow(msg)}")


def pause() -> None:
    input(f"\n  {cyan('Press Enter to continue...')}")


# ── Input helpers ─────────────────────────────────────────────────────────

def get_input(prompt: str, required: bool = True) -> str:
    """Read stripped input; loop if empty and required."""
    while True:
        value = input(f"  {prompt}: ").strip()
        if value or not required:
            return value
        print(f"  {red('This field is required.')}")


def get_int(prompt: str, min_val: int = 0, max_val: int = 9999) -> int:
    """Read and validate an integer within [min_val, max_val]."""
    while True:
        raw = input(f"  {prompt}: ").strip()
        try:
            val = int(raw)
            if min_val <= val <= max_val:
                return val
            print(f"  {red(f'Enter a number between {min_val} and {max_val}.')}")
        except ValueError:
            print(f"  {red('Invalid number. Try again.')}")


def get_float(prompt: str, min_val: float = 0.0) -> float:
    """Read and validate a float ≥ min_val."""
    while True:
        raw = input(f"  {prompt}: ").strip()
        try:
            val = float(raw)
            if val >= min_val:
                return val
            print(f"  {red(f'Value must be ≥ {min_val}.')}")
        except ValueError:
            print(f"  {red('Invalid number. Try again.')}")


def get_choice(prompt: str, choices: List[str]) -> str:
    """Present a numbered menu and return the chosen item."""
    for i, c in enumerate(choices, 1):
        print(f"    {cyan(str(i))}. {c}")
    while True:
        raw = input(f"  {prompt}: ").strip()
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            pass
        print(f"  {red('Invalid choice.')}")


def get_date(prompt: str = "Enter date (YYYY-MM-DD)") -> str:
    """Read and validate a date string."""
    while True:
        raw = input(f"  {prompt}: ").strip()
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print(f"  {red('Invalid date. Use YYYY-MM-DD format.')}")


def confirm(prompt: str = "Confirm? (y/n)") -> bool:
    """Return True if user answers 'y'."""
    return input(f"  {prompt}: ").strip().lower() == "y"


# ── Recursive student search ──────────────────────────────────────────────

def search_student_recursive(
    student_list: List["Student"],
    target_id: str,
    index: int = 0,
) -> Optional["Student"]:
    """
    Recursively search for a student by ID.

    Args:
        student_list: list of Student objects.
        target_id   : the student_id to find.
        index       : current recursion index (starts at 0).

    Returns:
        Matching Student, or None if not found.
    """
    if index >= len(student_list):
        return None
    if student_list[index].student_id == target_id:
        return student_list[index]
    return search_student_recursive(student_list, target_id, index + 1)


# ── Lambda sort functions ─────────────────────────────────────────────────

# Sort students: "Overdue" first, "Pending" second, "Paid" last
sort_students_by_fee = lambda students: sorted(
    students,
    key=lambda s: {"Overdue": 0, "Pending": 1, "Paid": 2}.get(s.fee_status, 9)
)

# Sort rooms: most occupied first
sort_rooms_by_occupancy = lambda rooms: sorted(
    rooms,
    key=lambda r: r.occupied_beds,
    reverse=True
)

# Sort complaints: "High" first, then "Medium", then "Low"
sort_complaints_by_priority = lambda complaints: sorted(
    complaints,
    key=lambda c: {"High": 0, "Medium": 1, "Low": 2}.get(c.priority, 9)
)


# ── Miscellaneous helpers ─────────────────────────────────────────────────

def today_str() -> str:
    return date.today().isoformat()


def now_time_str() -> str:
    return datetime.now().strftime("%H:%M")


def fee_due_date(months_ahead: int = 1) -> str:
    """Return ISO date string for the end of the current month + offset."""
    today = date.today()
    month = today.month + months_ahead
    year = today.year + (month - 1) // 12
    month = ((month - 1) % 12) + 1
    # Last day of that month
    import calendar
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, last_day).isoformat()


def truncate(text: str, max_len: int = 30) -> str:
    """Truncate text for display in narrow table cells."""
    return text if len(text) <= max_len else text[: max_len - 1] + "…"
