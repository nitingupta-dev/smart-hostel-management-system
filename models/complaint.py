"""
Complaint model — student grievance and maintenance request tracking.
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Dict, Any


PRIORITY_LEVELS = {"Low", "Medium", "High"}
COMPLAINT_TYPES = {
    "Maintenance", "Electrical", "Plumbing", "Housekeeping",
    "Food", "Noise", "Security", "Other"
}
COMPLAINT_STATUSES = {"Open", "In-Progress", "Resolved", "Closed", "Rejected"}


class Complaint:
    """
    Represents a student complaint or maintenance request.

    Attributes:
        _complaint_id     (str) : Auto-generated e.g. CMP001.
        _student_id       (str) : Submitting student.
        _complaint_type   (str) : Category.
        _description      (str) : Detail of the complaint.
        _complaint_status (str) : Open | In-Progress | Resolved | Closed | Rejected.
        _priority         (str) : Low | Medium | High.
        _date_submitted   (str) : ISO date.
        _date_resolved    (str) : ISO date or "—".
        _remarks          (str) : Warden remarks on resolution.
    """

    _id_counter: int = 1

    def __init__(
        self,
        complaint_id: str,
        student_id: str,
        complaint_type: str,
        description: str,
        complaint_status: str = "Open",
        priority: str = "Medium",
        date_submitted: str = "",
        date_resolved: str = "—",
        remarks: str = "",
    ) -> None:
        self._complaint_id: str = complaint_id
        self._student_id: str = student_id
        self._complaint_type: str = complaint_type
        self._description: str = description
        self._complaint_status: str = complaint_status if complaint_status in COMPLAINT_STATUSES else "Open"
        self._priority: str = priority if priority in PRIORITY_LEVELS else "Medium"
        self._date_submitted: str = date_submitted or date.today().isoformat()
        self._date_resolved: str = date_resolved
        self._remarks: str = remarks

    # ── Class method ─────────────────────────────────────────────────────
    @classmethod
    def generate_id(cls) -> str:
        cid = f"CMP{cls._id_counter:03d}"
        cls._id_counter += 1
        return cid

    @classmethod
    def set_counter(cls, value: int) -> None:
        if value >= cls._id_counter:
            cls._id_counter = value + 1

    # ── Getters ───────────────────────────────────────────────────────────
    @property
    def complaint_id(self) -> str:
        return self._complaint_id

    @property
    def student_id(self) -> str:
        return self._student_id

    @property
    def complaint_type(self) -> str:
        return self._complaint_type

    @property
    def description(self) -> str:
        return self._description

    @property
    def complaint_status(self) -> str:
        return self._complaint_status

    @property
    def priority(self) -> str:
        return self._priority

    @property
    def date_submitted(self) -> str:
        return self._date_submitted

    @property
    def date_resolved(self) -> str:
        return self._date_resolved

    @property
    def remarks(self) -> str:
        return self._remarks

    # ── Core methods ─────────────────────────────────────────────────────
    def register_complaint(self) -> str:
        """Acknowledge complaint registration."""
        return (f"Complaint {self._complaint_id} registered by Student {self._student_id}. "
                f"Priority: {self._priority}.")

    def update_status(self, new_status: str, remarks: str = "") -> str:
        """Update the complaint status and optionally add warden remarks."""
        from utils.exceptions import InvalidComplaintID
        if new_status not in COMPLAINT_STATUSES:
            raise ValueError(f"Status must be one of {COMPLAINT_STATUSES}.")
        self._complaint_status = new_status
        if remarks:
            self._remarks = remarks
        if new_status in {"Resolved", "Closed"}:
            self._date_resolved = date.today().isoformat()
        return f"Complaint {self._complaint_id} updated to '{new_status}'."

    def escalate(self) -> str:
        """Escalate priority to the next level."""
        levels = ["Low", "Medium", "High"]
        current_idx = levels.index(self._priority)
        if current_idx < len(levels) - 1:
            self._priority = levels[current_idx + 1]
            return f"Complaint {self._complaint_id} escalated to '{self._priority}'."
        return f"Complaint {self._complaint_id} is already at highest priority."

    # ── Serialisation ─────────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        return {
            "complaint_id":     self._complaint_id,
            "student_id":       self._student_id,
            "complaint_type":   self._complaint_type,
            "description":      self._description,
            "complaint_status": self._complaint_status,
            "priority":         self._priority,
            "date_submitted":   self._date_submitted,
            "date_resolved":    self._date_resolved,
            "remarks":          self._remarks,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Complaint":
        return cls(
            complaint_id     = data["complaint_id"],
            student_id       = data["student_id"],
            complaint_type   = data["complaint_type"],
            description      = data["description"],
            complaint_status = data.get("complaint_status", "Open"),
            priority         = data.get("priority", "Medium"),
            date_submitted   = data.get("date_submitted", ""),
            date_resolved    = data.get("date_resolved", "—"),
            remarks          = data.get("remarks", ""),
        )

    def __str__(self) -> str:
        return (f"Complaint({self._complaint_id} | {self._complaint_type} | "
                f"{self._priority} | {self._complaint_status})")

    def __repr__(self) -> str:
        return (f"Complaint(id={self._complaint_id!r}, student={self._student_id!r}, "
                f"type={self._complaint_type!r}, status={self._complaint_status!r})")
