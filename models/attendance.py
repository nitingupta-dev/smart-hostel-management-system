"""
Attendance model — daily in/out tracking with percentage calculation.
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Dict, Any, List


STATUS_CHOICES = {"Present", "Absent", "Leave", "Late"}


class Attendance:
    """
    Represents one attendance record for a student on a specific date.

    Attributes:
        _attendance_id (str) : Auto-generated e.g. ATT001.
        _student_id    (str) : Associated student.
        _date          (str) : ISO date string YYYY-MM-DD.
        _status        (str) : Present | Absent | Leave | Late.
        _in_time       (str) : Entry time HH:MM or "—".
        _out_time      (str) : Exit time HH:MM or "—".
        _remarks       (str) : Optional notes.
    """

    _id_counter: int = 1

    def __init__(
        self,
        attendance_id: str,
        student_id: str,
        date_str: str,
        status: str = "Present",
        in_time: str = "—",
        out_time: str = "—",
        remarks: str = "",
    ) -> None:
        self._attendance_id: str = attendance_id
        self._student_id: str = student_id
        self._date: str = date_str
        self._status: str = status if status in STATUS_CHOICES else "Present"
        self._in_time: str = in_time
        self._out_time: str = out_time
        self._remarks: str = remarks

    # ── Class method ─────────────────────────────────────────────────────
    @classmethod
    def generate_id(cls) -> str:
        aid = f"ATT{cls._id_counter:03d}"
        cls._id_counter += 1
        return aid

    @classmethod
    def set_counter(cls, value: int) -> None:
        if value >= cls._id_counter:
            cls._id_counter = value + 1

    # ── Getters ───────────────────────────────────────────────────────────
    @property
    def attendance_id(self) -> str:
        return self._attendance_id

    @property
    def student_id(self) -> str:
        return self._student_id

    @property
    def date(self) -> str:
        return self._date

    @property
    def status(self) -> str:
        return self._status

    @property
    def in_time(self) -> str:
        return self._in_time

    @property
    def out_time(self) -> str:
        return self._out_time

    @property
    def remarks(self) -> str:
        return self._remarks

    # ── Core methods ─────────────────────────────────────────────────────
    def mark_attendance(
        self,
        status: str,
        in_time: str = "",
        out_time: str = "",
        remarks: str = "",
    ) -> str:
        """Update the attendance record."""
        if status not in STATUS_CHOICES:
            raise ValueError(f"Status must be one of {STATUS_CHOICES}.")
        self._status = status
        if in_time:
            self._in_time = in_time
        if out_time:
            self._out_time = out_time
        if remarks:
            self._remarks = remarks
        return f"Attendance marked for {self._student_id} on {self._date}: {status}"

    def record_out_time(self, out_time: str) -> str:
        """Set exit time for the day."""
        self._out_time = out_time
        return f"Out-time recorded for {self._student_id}: {out_time}"

    @staticmethod
    def calculate_percentage(records: List["Attendance"]) -> float:
        """
        Calculate attendance percentage from a list of records.
        Present + Late counts as attended.
        """
        if not records:
            return 0.0
        attended = sum(1 for r in records if r.status in {"Present", "Late"})
        return round((attended / len(records)) * 100, 2)

    def view_attendance(self) -> str:
        """Return a single-line attendance summary."""
        return (f"[{self._attendance_id}] {self._date} | {self._student_id} | "
                f"{self._status} | In:{self._in_time} Out:{self._out_time}")

    # ── Serialisation ─────────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        return {
            "attendance_id": self._attendance_id,
            "student_id":    self._student_id,
            "date":          self._date,
            "status":        self._status,
            "in_time":       self._in_time,
            "out_time":      self._out_time,
            "remarks":       self._remarks,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Attendance":
        return cls(
            attendance_id = data["attendance_id"],
            student_id    = data["student_id"],
            date_str      = data["date"],
            status        = data.get("status", "Present"),
            in_time       = data.get("in_time", "—"),
            out_time      = data.get("out_time", "—"),
            remarks       = data.get("remarks", ""),
        )

    def __str__(self) -> str:
        return self.view_attendance()

    def __repr__(self) -> str:
        return f"Attendance(id={self._attendance_id!r}, student={self._student_id!r}, date={self._date!r})"
