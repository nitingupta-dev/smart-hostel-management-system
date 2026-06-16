"""
Fee model — handles hostel fee generation, payment, and fine calculation.
"""

from __future__ import annotations
from datetime import datetime, date, timedelta
from typing import Dict, Any


FINE_PER_DAY = 50.0  # ₹ per day late


class Fee:
    """
    Represents a hostel fee record for one student.

    Attributes:
        _fee_id         (str)  : Auto-generated e.g. FEE001.
        _student_id     (str)  : Associated student.
        _amount         (float): Base fee amount.
        _due_date       (str)  : ISO date string YYYY-MM-DD.
        _payment_status (str)  : "Paid" | "Pending" | "Overdue".
        _payment_date   (str)  : ISO date string or "—".
        _fine           (float): Accumulated fine.
        _month          (str)  : e.g. "June 2025".
    """

    _id_counter: int = 1

    def __init__(
        self,
        fee_id: str,
        student_id: str,
        amount: float,
        due_date: str,
        payment_status: str = "Pending",
        payment_date: str = "—",
        fine: float = 0.0,
        month: str = "",
    ) -> None:
        self._fee_id: str = fee_id
        self._student_id: str = student_id
        self._amount: float = float(amount)
        self._due_date: str = due_date
        self._payment_status: str = payment_status
        self._payment_date: str = payment_date
        self._fine: float = float(fine)
        self._month: str = month or datetime.now().strftime("%B %Y")

    # ── Class / static methods ────────────────────────────────────────────
    @classmethod
    def generate_id(cls) -> str:
        fid = f"FEE{cls._id_counter:03d}"
        cls._id_counter += 1
        return fid

    @classmethod
    def set_counter(cls, value: int) -> None:
        if value >= cls._id_counter:
            cls._id_counter = value + 1

    @staticmethod
    def calculate_fine(days_late: int) -> float:
        """
        Static method: return total fine for the given number of overdue days.
        Fine = days_late × FINE_PER_DAY (₹50/day).
        """
        if days_late <= 0:
            return 0.0
        return round(days_late * FINE_PER_DAY, 2)

    # ── Getters ───────────────────────────────────────────────────────────
    @property
    def fee_id(self) -> str:
        return self._fee_id

    @property
    def student_id(self) -> str:
        return self._student_id

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def due_date(self) -> str:
        return self._due_date

    @property
    def payment_status(self) -> str:
        return self._payment_status

    @property
    def payment_date(self) -> str:
        return self._payment_date

    @property
    def fine(self) -> float:
        return self._fine

    @property
    def month(self) -> str:
        return self._month

    @property
    def total_due(self) -> float:
        """Base amount + accumulated fine."""
        return round(self._amount + self._fine, 2)

    # ── Core methods ─────────────────────────────────────────────────────
    def generate_fee(self, amount: float, due_date: str, month: str = "") -> None:
        """Update fee details (re-generate for a new period)."""
        from utils.exceptions import InvalidFeeAmount
        if amount <= 0:
            raise InvalidFeeAmount(amount)
        self._amount = float(amount)
        self._due_date = due_date
        self._payment_status = "Pending"
        self._payment_date = "—"
        self._fine = 0.0
        if month:
            self._month = month

    def process_payment(self) -> str:
        """Mark this fee as paid and record today's date."""
        if self._payment_status == "Paid":
            return f"Fee {self._fee_id} is already marked as Paid."
        self._payment_status = "Paid"
        self._payment_date = date.today().isoformat()
        return (
            f"Payment processed for Fee {self._fee_id} | "
            f"Amount: ₹{self._amount:.2f} | Fine: ₹{self._fine:.2f} | "
            f"Total: ₹{self.total_due:.2f}"
        )

    def refresh_overdue(self) -> None:
        """
        Check whether the due date has passed and update status + fine.
        Called when loading records or viewing fee lists.
        """
        if self._payment_status == "Paid":
            return
        try:
            due = date.fromisoformat(self._due_date)
        except ValueError:
            return
        today = date.today()
        if today > due:
            days_late = (today - due).days
            self._fine = Fee.calculate_fine(days_late)
            self._payment_status = "Overdue"

    def generate_receipt(self) -> str:
        """Return a plain-text payment receipt."""
        sep = "─" * 38
        return (
            f"\n  {sep}\n"
            f"        HOSTEL FEE RECEIPT\n"
            f"  {sep}\n"
            f"  Receipt ID  : {self._fee_id}\n"
            f"  Student ID  : {self._student_id}\n"
            f"  Month       : {self._month}\n"
            f"  Base Amount : ₹{self._amount:>10.2f}\n"
            f"  Fine        : ₹{self._fine:>10.2f}\n"
            f"  Total Paid  : ₹{self.total_due:>10.2f}\n"
            f"  Due Date    : {self._due_date}\n"
            f"  Paid On     : {self._payment_date}\n"
            f"  Status      : {self._payment_status}\n"
            f"  {sep}\n"
        )

    # ── Serialisation ─────────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        return {
            "fee_id":         self._fee_id,
            "student_id":     self._student_id,
            "amount":         self._amount,
            "due_date":       self._due_date,
            "payment_status": self._payment_status,
            "payment_date":   self._payment_date,
            "fine":           self._fine,
            "month":          self._month,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Fee":
        return cls(
            fee_id         = data["fee_id"],
            student_id     = data["student_id"],
            amount         = float(data["amount"]),
            due_date       = data["due_date"],
            payment_status = data.get("payment_status", "Pending"),
            payment_date   = data.get("payment_date", "—"),
            fine           = float(data.get("fine", 0.0)),
            month          = data.get("month", ""),
        )

    # ── Magic ─────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return (f"Fee({self._fee_id} | Student:{self._student_id} | "
                f"₹{self._amount:.0f} | {self._payment_status})")

    def __repr__(self) -> str:
        return (f"Fee(id={self._fee_id!r}, student={self._student_id!r}, "
                f"amount={self._amount}, status={self._payment_status!r})")
