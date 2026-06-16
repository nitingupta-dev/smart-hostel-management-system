"""
Warden model — inherits from Person.
Manages hostel administrative actions.
"""

from __future__ import annotations
from typing import Dict, Any, Optional
from models.person import Person

try:
    from colorama import Fore, Style
    COLORS = True
except ImportError:
    COLORS = False

def _c(color_code: str, text: str) -> str:
    return f"{color_code}{text}{Style.RESET_ALL}" if COLORS else text


class Warden(Person):
    """
    Represents a hostel warden / administrator.

    Attributes:
        _warden_id   (str): Auto-generated e.g. WRD001.
        _hostel_name (str): Name of the hostel managed.
        _username    (str): Login username.
        _password    (str): Login password (plain-text for simplicity).
    """

    _id_counter: int = 1

    def __init__(
        self,
        warden_id: str,
        name: str,
        mobile_number: str,
        address: str,
        hostel_name: str,
        username: str = "admin",
        password: str = "admin123",
    ) -> None:
        super().__init__(warden_id, name, mobile_number, address)
        self._warden_id: str = warden_id
        self._hostel_name: str = hostel_name
        self._username: str = username
        self._password: str = password

    # ── Class method ──────────────────────────────────────────────────────
    @classmethod
    def generate_id(cls) -> str:
        wid = f"WRD{cls._id_counter:03d}"
        cls._id_counter += 1
        return wid

    # ── Getters ───────────────────────────────────────────────────────────
    @property
    def warden_id(self) -> str:
        return self._warden_id

    @property
    def hostel_name(self) -> str:
        return self._hostel_name

    @property
    def username(self) -> str:
        return self._username

    # ── Authentication ────────────────────────────────────────────────────
    def verify_password(self, password: str) -> bool:
        return self._password == password

    def change_password(self, old_password: str, new_password: str) -> str:
        if not self.verify_password(old_password):
            return "Incorrect current password."
        if len(new_password) < 6:
            return "New password must be at least 6 characters."
        self._password = new_password
        return "Password changed successfully."

    # ── Actions ───────────────────────────────────────────────────────────
    def allocate_room(self, student_id: str, room_number: str) -> str:
        return f"Warden {self._warden_id} allocated Room {room_number} to Student {student_id}."

    def approve_leave(self, student_id: str) -> str:
        return f"Leave approved by Warden {self._warden_id} for Student {student_id}."

    def resolve_complaint(self, complaint_id: str) -> str:
        return f"Complaint {complaint_id} resolved by Warden {self._warden_id}."

    # ── Display ───────────────────────────────────────────────────────────
    def display_details(self) -> None:
        try:
            from tabulate import tabulate
            rows = [
                ["Warden ID",   self._warden_id],
                ["Name",        self._name],
                ["Mobile",      self._mobile_number],
                ["Address",     self._address],
                ["Hostel",      self._hostel_name],
                ["Username",    self._username],
            ]
            header = _c(Fore.CYAN if COLORS else "", "── Warden Profile ──")
            print(f"\n  {header}")
            print(tabulate(rows, tablefmt="rounded_outline"))
        except ImportError:
            print(f"\n  Warden ID : {self._warden_id}")
            print(f"  Name      : {self._name}")
            print(f"  Hostel    : {self._hostel_name}")

    # ── Serialisation ─────────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        return {
            "warden_id":     self._warden_id,
            "name":          self._name,
            "mobile_number": self._mobile_number,
            "address":       self._address,
            "hostel_name":   self._hostel_name,
            "username":      self._username,
            "password":      self._password,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Warden":
        return cls(
            warden_id    = data["warden_id"],
            name         = data["name"],
            mobile_number= data["mobile_number"],
            address      = data["address"],
            hostel_name  = data["hostel_name"],
            username     = data.get("username", "admin"),
            password     = data.get("password", "admin123"),
        )

    def __str__(self) -> str:
        return f"Warden({self._warden_id} | {self._name} | {self._hostel_name})"

    def __repr__(self) -> str:
        return f"Warden(id={self._warden_id!r}, hostel={self._hostel_name!r})"
