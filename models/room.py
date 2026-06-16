"""
Room model — represents a hostel room with allocation/vacancy logic.
"""

from __future__ import annotations
from typing import List, Dict, Any, Set

# Valid room type constants
ROOM_TYPES: Set[str] = {"Single", "Double", "Triple", "AC", "Non-AC"}

# Base monthly charges per room type
ROOM_CHARGES: Dict[str, float] = {
    "Single":  3000.0,
    "Double":  2000.0,
    "Triple":  1500.0,
    "AC":      4000.0,
    "Non-AC":  1800.0,
}


class Room:
    """
    Represents a hostel room.

    Attributes:
        _room_id      (str) : Auto-generated e.g. RM101.
        _room_number  (str) : Human-readable room number.
        _room_type    (str) : One of ROOM_TYPES.
        _capacity     (int) : Maximum occupants.
        _occupied_beds(int) : Current occupants.
        _occupants    (list): Student IDs currently in this room.
        _floor        (int) : Floor number.
    """

    _id_counter: int = 101

    def __init__(
        self,
        room_id: str,
        room_number: str,
        room_type: str,
        capacity: int,
        floor: int = 1,
        occupied_beds: int = 0,
        occupants: List[str] | None = None,
    ) -> None:
        if room_type not in ROOM_TYPES:
            raise ValueError(f"room_type must be one of {ROOM_TYPES}.")
        self._room_id: str = room_id
        self._room_number: str = room_number
        self._room_type: str = room_type
        self._capacity: int = capacity
        self._floor: int = floor
        self._occupied_beds: int = occupied_beds
        self._occupants: List[str] = occupants if occupants else []

    # ── Class methods ─────────────────────────────────────────────────────
    @classmethod
    def generate_id(cls) -> str:
        rid = f"RM{cls._id_counter}"
        cls._id_counter += 1
        return rid

    @classmethod
    def set_counter(cls, value: int) -> None:
        if value >= cls._id_counter:
            cls._id_counter = value + 1

    @staticmethod
    def calculate_room_charge(room_type: str, months: int = 1) -> float:
        """Static method: compute total room charge for given months."""
        base = ROOM_CHARGES.get(room_type, 2000.0)
        return base * months

    @classmethod
    def hostel_occupancy_stats(cls, rooms: List["Room"]) -> Dict[str, int]:
        """Class method: return aggregate occupancy stats across all rooms."""
        total_capacity = sum(r.capacity for r in rooms)
        total_occupied = sum(r.occupied_beds for r in rooms)
        return {
            "total_rooms":    len(rooms),
            "total_capacity": total_capacity,
            "total_occupied": total_occupied,
            "total_vacant":   total_capacity - total_occupied,
        }

    # ── Getters ───────────────────────────────────────────────────────────
    @property
    def room_id(self) -> str:
        return self._room_id

    @property
    def room_number(self) -> str:
        return self._room_number

    @property
    def room_type(self) -> str:
        return self._room_type

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def occupied_beds(self) -> int:
        return self._occupied_beds

    @property
    def floor(self) -> int:
        return self._floor

    @property
    def occupants(self) -> List[str]:
        return list(self._occupants)

    @property
    def available_beds(self) -> int:
        return self._capacity - self._occupied_beds

    @property
    def monthly_charge(self) -> float:
        return ROOM_CHARGES.get(self._room_type, 2000.0)

    # ── Core methods ─────────────────────────────────────────────────────
    def check_availability(self) -> bool:
        """Return True if there is at least one free bed."""
        return self._occupied_beds < self._capacity

    def allocate_room(self, student_id: str) -> str:
        """Assign a student to this room, incrementing occupied count."""
        from utils.exceptions import RoomNotAvailable
        if not self.check_availability():
            raise RoomNotAvailable(self._room_number)
        if student_id in self._occupants:
            return f"Student {student_id} is already in Room {self._room_number}."
        self._occupants.append(student_id)
        self._occupied_beds += 1
        return f"Student {student_id} allocated to Room {self._room_number} successfully."

    def vacate_room(self, student_id: str) -> str:
        """Remove a student from this room."""
        if student_id not in self._occupants:
            return f"Student {student_id} is not in Room {self._room_number}."
        self._occupants.remove(student_id)
        self._occupied_beds = max(0, self._occupied_beds - 1)
        return f"Student {student_id} vacated Room {self._room_number}."

    # ── Display ───────────────────────────────────────────────────────────
    def display_details(self) -> None:
        try:
            from tabulate import tabulate
            rows = [
                ["Room ID",      self._room_id],
                ["Room Number",  self._room_number],
                ["Type",         self._room_type],
                ["Floor",        self._floor],
                ["Capacity",     self._capacity],
                ["Occupied",     self._occupied_beds],
                ["Vacant Beds",  self.available_beds],
                ["Monthly ₹",    f"₹{self.monthly_charge:,.0f}"],
                ["Occupants",    ", ".join(self._occupants) or "—"],
            ]
            print()
            from tabulate import tabulate
            print(tabulate(rows, tablefmt="rounded_outline"))
        except ImportError:
            print(f"\n  Room {self._room_number} | Type: {self._room_type} | "
                  f"Occupied: {self._occupied_beds}/{self._capacity}")

    # ── Serialisation ─────────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        return {
            "room_id":       self._room_id,
            "room_number":   self._room_number,
            "room_type":     self._room_type,
            "capacity":      self._capacity,
            "floor":         self._floor,
            "occupied_beds": self._occupied_beds,
            "occupants":     self._occupants,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Room":
        return cls(
            room_id      = data["room_id"],
            room_number  = data["room_number"],
            room_type    = data["room_type"],
            capacity     = int(data["capacity"]),
            floor        = int(data.get("floor", 1)),
            occupied_beds= int(data.get("occupied_beds", 0)),
            occupants    = data.get("occupants", []),
        )

    # ── Magic methods ─────────────────────────────────────────────────────
    def __str__(self) -> str:
        status = "FULL" if not self.check_availability() else f"{self.available_beds} beds free"
        return f"Room({self._room_number} | {self._room_type} | {status})"

    def __repr__(self) -> str:
        return (f"Room(id={self._room_id!r}, number={self._room_number!r}, "
                f"type={self._room_type!r}, occupied={self._occupied_beds}/{self._capacity})")

    def __len__(self) -> int:
        """len(room) returns the number of current occupants."""
        return self._occupied_beds
