"""
Visitor model — tracks hostel visitor entries and exits.
"""

from __future__ import annotations
from datetime import datetime, date
from typing import Dict, Any


APPROVAL_STATUSES = {"Pending", "Approved", "Rejected", "Checked-Out"}
RELATION_TYPES = {"Parent", "Guardian", "Sibling", "Friend", "Relative", "Other"}


class Visitor:
    """
    Represents a visitor entry.

    Attributes:
        _visitor_id   (str): Auto-generated e.g. VIS001.
        _visitor_name (str): Full name of visitor.
        _relation     (str): Relation to the student.
        _student_id   (str): The student being visited.
        _visit_date   (str): YYYY-MM-DD.
        _purpose      (str): Reason for visit.
        _in_time      (str): Arrival time.
        _out_time     (str): Departure time or "—".
        _status       (str): Pending | Approved | Rejected | Checked-Out.
        _mobile       (str): Visitor's mobile number.
    """

    _id_counter: int = 1

    def __init__(
        self,
        visitor_id: str,
        visitor_name: str,
        relation: str,
        student_id: str,
        visit_date: str,
        purpose: str = "",
        in_time: str = "",
        out_time: str = "—",
        status: str = "Pending",
        mobile: str = "",
    ) -> None:
        self._visitor_id: str = visitor_id
        self._visitor_name: str = visitor_name
        self._relation: str = relation
        self._student_id: str = student_id
        self._visit_date: str = visit_date
        self._purpose: str = purpose
        self._in_time: str = in_time or datetime.now().strftime("%H:%M")
        self._out_time: str = out_time
        self._status: str = status if status in APPROVAL_STATUSES else "Pending"
        self._mobile: str = mobile

    # ── Class method ─────────────────────────────────────────────────────
    @classmethod
    def generate_id(cls) -> str:
        vid = f"VIS{cls._id_counter:03d}"
        cls._id_counter += 1
        return vid

    @classmethod
    def set_counter(cls, value: int) -> None:
        if value >= cls._id_counter:
            cls._id_counter = value + 1

    # ── Getters ───────────────────────────────────────────────────────────
    @property
    def visitor_id(self) -> str:
        return self._visitor_id

    @property
    def visitor_name(self) -> str:
        return self._visitor_name

    @property
    def relation(self) -> str:
        return self._relation

    @property
    def student_id(self) -> str:
        return self._student_id

    @property
    def visit_date(self) -> str:
        return self._visit_date

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
    def mobile(self) -> str:
        return self._mobile

    # ── Core methods ─────────────────────────────────────────────────────
    def register_visitor(self) -> str:
        """Acknowledge visitor registration."""
        return (f"Visitor {self._visitor_id} ({self._visitor_name}) "
                f"registered for Student {self._student_id} on {self._visit_date}.")

    def approve_visit(self) -> str:
        """Approve a pending visitor."""
        if self._status != "Pending":
            return f"Visitor {self._visitor_id} status is already '{self._status}'."
        self._status = "Approved"
        return f"Visit by {self._visitor_name} approved."

    def reject_visit(self) -> str:
        """Reject a pending visitor."""
        if self._status not in {"Pending", "Approved"}:
            return f"Cannot reject visitor with status '{self._status}'."
        self._status = "Rejected"
        return f"Visit by {self._visitor_name} rejected."

    def checkout_visitor(self) -> str:
        """Record visitor checkout."""
        if self._status != "Approved":
            return f"Visitor {self._visitor_id} is not currently inside."
        self._out_time = datetime.now().strftime("%H:%M")
        self._status = "Checked-Out"
        return f"Visitor {self._visitor_name} checked out at {self._out_time}."

    # ── Serialisation ─────────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        return {
            "visitor_id":   self._visitor_id,
            "visitor_name": self._visitor_name,
            "relation":     self._relation,
            "student_id":   self._student_id,
            "visit_date":   self._visit_date,
            "purpose":      self._purpose,
            "in_time":      self._in_time,
            "out_time":     self._out_time,
            "status":       self._status,
            "mobile":       self._mobile,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Visitor":
        return cls(
            visitor_id   = data["visitor_id"],
            visitor_name = data["visitor_name"],
            relation     = data["relation"],
            student_id   = data["student_id"],
            visit_date   = data["visit_date"],
            purpose      = data.get("purpose", ""),
            in_time      = data.get("in_time", ""),
            out_time     = data.get("out_time", "—"),
            status       = data.get("status", "Pending"),
            mobile       = data.get("mobile", ""),
        )

    def __str__(self) -> str:
        return (f"Visitor({self._visitor_id} | {self._visitor_name} | "
                f"For:{self._student_id} | {self._status})")

    def __repr__(self) -> str:
        return (f"Visitor(id={self._visitor_id!r}, name={self._visitor_name!r}, "
                f"student={self._student_id!r}, status={self._status!r})")
