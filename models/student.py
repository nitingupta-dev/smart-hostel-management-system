"""
Student model — inherits from Person.
Handles student-specific data and actions.
"""

from __future__ import annotations
from typing import Optional, Dict, Any
from models.person import Person

try:
    from colorama import Fore, Style
    COLORS = True
except ImportError:
    COLORS = False

def _c(color_code: str, text: str) -> str:
    return f"{color_code}{text}{Style.RESET_ALL}" if COLORS else text


class Student(Person):
    """
    Represents a hostel student.

    Attributes:
        _student_id   (str) : Auto-generated e.g. STD1001.
        _course       (str) : Enrolled course / programme.
        _year         (int) : Academic year (1–5).
        _room_number  (str) : Allocated room number ("N/A" if none).
        _fee_status   (str) : "Paid" | "Pending" | "Overdue".
        _email        (str) : Contact email.
        _gender       (str) : Gender.
    """

    _id_counter: int = 1001  # Class-level auto-increment seed

    def __init__(
        self,
        student_id: str,
        name: str,
        mobile_number: str,
        address: str,
        course: str,
        year: int,
        email: str = "",
        gender: str = "",
        room_number: str = "N/A",
        fee_status: str = "Pending",
    ) -> None:
        super().__init__(student_id, name, mobile_number, address)
        self._student_id: str = student_id
        self._course: str = course
        self._year: int = year
        self._email: str = email
        self._gender: str = gender
        self._room_number: str = room_number
        self._fee_status: str = fee_status

    # ── Class method: ID generation ────────────────────────────────────────
    @classmethod
    def generate_id(cls) -> str:
        """Generate the next sequential student ID."""
        sid = f"STD{cls._id_counter}"
        cls._id_counter += 1
        return sid

    @classmethod
    def set_counter(cls, value: int) -> None:
        """Sync counter from persisted data on load."""
        if value >= cls._id_counter:
            cls._id_counter = value + 1

    # ── Getters / setters ─────────────────────────────────────────────────
    @property
    def student_id(self) -> str:
        return self._student_id

    @property
    def course(self) -> str:
        return self._course

    @course.setter
    def course(self, value: str) -> None:
        if not value.strip():
            raise ValueError("Course cannot be empty.")
        self._course = value.strip()

    @property
    def year(self) -> int:
        return self._year

    @year.setter
    def year(self, value: int) -> None:
        if not (1 <= int(value) <= 5):
            raise ValueError("Year must be between 1 and 5.")
        self._year = int(value)

    @property
    def room_number(self) -> str:
        return self._room_number

    @room_number.setter
    def room_number(self, value: str) -> None:
        self._room_number = value

    @property
    def fee_status(self) -> str:
        return self._fee_status

    @fee_status.setter
    def fee_status(self, value: str) -> None:
        allowed = {"Paid", "Pending", "Overdue"}
        if value not in allowed:
            raise ValueError(f"Fee status must be one of {allowed}.")
        self._fee_status = value

    @property
    def email(self) -> str:
        return self._email

    @property
    def gender(self) -> str:
        return self._gender

    # ── Actions ───────────────────────────────────────────────────────────
    def apply_for_room(self) -> str:
        """Return a room-application status message."""
        if self._room_number != "N/A":
            return f"Student {self._student_id} is already assigned to Room {self._room_number}."
        return f"Room application submitted for student {self._student_id}."

    def pay_fee(self, amount: float) -> str:
        """Mark fee as paid (simple status flip)."""
        if amount <= 0:
            from utils.exceptions import InvalidFeeAmount
            raise InvalidFeeAmount(amount)
        self._fee_status = "Paid"
        return f"Fee of ₹{amount:.2f} received for {self._student_id}."

    def submit_complaint(self, complaint_text: str) -> str:
        """Return a complaint submission acknowledgement."""
        if not complaint_text.strip():
            raise ValueError("Complaint text cannot be empty.")
        return f"Complaint submitted by {self._student_id}: {complaint_text}"

    # ── Display ───────────────────────────────────────────────────────────
    def display_details(self) -> None:
        """Print a formatted student profile card."""
        try:
            from tabulate import tabulate
            rows = [
                ["Student ID",    self._student_id],
                ["Name",          self._name],
                ["Email",         self._email or "—"],
                ["Gender",        self._gender or "—"],
                ["Mobile",        self._mobile_number],
                ["Address",       self._address],
                ["Course",        self._course],
                ["Year",          self._year],
                ["Room",          self._room_number],
                ["Fee Status",    self._fee_status],
            ]
            header = _c(Fore.CYAN if COLORS else "", "── Student Profile ──")
            print(f"\n  {header}")
            print(tabulate(rows, tablefmt="rounded_outline"))
        except ImportError:
            print(f"\n  Student ID   : {self._student_id}")
            print(f"  Name         : {self._name}")
            print(f"  Course       : {self._course} (Year {self._year})")
            print(f"  Room         : {self._room_number}")
            print(f"  Fee Status   : {self._fee_status}")

    # ── Serialisation ─────────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id":    self._student_id,
            "name":          self._name,
            "email":         self._email,
            "gender":        self._gender,
            "mobile_number": self._mobile_number,
            "address":       self._address,
            "course":        self._course,
            "year":          self._year,
            "room_number":   self._room_number,
            "fee_status":    self._fee_status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Student":
        """Reconstruct a Student from a saved dictionary."""
        return cls(
            student_id    = data["student_id"],
            name          = data["name"],
            mobile_number = data["mobile_number"],
            address       = data["address"],
            course        = data["course"],
            year          = int(data["year"]),
            email         = data.get("email", ""),
            gender        = data.get("gender", ""),
            room_number   = data.get("room_number", "N/A"),
            fee_status    = data.get("fee_status", "Pending"),
        )

    # ── Magic methods ─────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f"Student({self._student_id} | {self._name} | {self._course})"

    def __repr__(self) -> str:
        return f"Student(id={self._student_id!r}, name={self._name!r}, room={self._room_number!r})"
