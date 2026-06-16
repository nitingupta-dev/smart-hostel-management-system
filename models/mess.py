"""
Mess model — monthly meal tracking and billing.
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Dict, Any, List


MEAL_TYPES = {"Breakfast", "Lunch", "Dinner", "Snacks"}
MONTHLY_MESS_RATE = 2500.0  # ₹ per month base charge
PER_MEAL_RATE = 40.0        # ₹ per extra meal


class Mess:
    """
    Represents a monthly mess record for a student.

    Attributes:
        _mess_id          (str)  : Auto-generated e.g. MES001.
        _student_id       (str)  : Associated student.
        _month            (str)  : "June 2025".
        _monthly_charge   (float): Base monthly charge.
        _meal_count       (int)  : Number of meals consumed.
        _extra_meals      (int)  : Additional meals beyond standard.
        _special_requests (list) : Special dietary requests.
        _payment_status   (str)  : Paid | Pending.
        _payment_date     (str)  : ISO date or "—".
    """

    _id_counter: int = 1

    def __init__(
        self,
        mess_id: str,
        student_id: str,
        month: str = "",
        monthly_charge: float = MONTHLY_MESS_RATE,
        meal_count: int = 0,
        extra_meals: int = 0,
        special_requests: List[str] | None = None,
        payment_status: str = "Pending",
        payment_date: str = "—",
    ) -> None:
        self._mess_id: str = mess_id
        self._student_id: str = student_id
        self._month: str = month or datetime.now().strftime("%B %Y")
        self._monthly_charge: float = float(monthly_charge)
        self._meal_count: int = int(meal_count)
        self._extra_meals: int = int(extra_meals)
        self._special_requests: List[str] = special_requests or []
        self._payment_status: str = payment_status
        self._payment_date: str = payment_date

    # ── Class method ─────────────────────────────────────────────────────
    @classmethod
    def generate_id(cls) -> str:
        mid = f"MES{cls._id_counter:03d}"
        cls._id_counter += 1
        return mid

    @classmethod
    def set_counter(cls, value: int) -> None:
        if value >= cls._id_counter:
            cls._id_counter = value + 1

    # ── Getters ───────────────────────────────────────────────────────────
    @property
    def mess_id(self) -> str:
        return self._mess_id

    @property
    def student_id(self) -> str:
        return self._student_id

    @property
    def month(self) -> str:
        return self._month

    @property
    def monthly_charge(self) -> float:
        return self._monthly_charge

    @property
    def meal_count(self) -> int:
        return self._meal_count

    @property
    def extra_meals(self) -> int:
        return self._extra_meals

    @property
    def special_requests(self) -> List[str]:
        return list(self._special_requests)

    @property
    def payment_status(self) -> str:
        return self._payment_status

    # ── Core methods ─────────────────────────────────────────────────────
    def add_meal(self, is_extra: bool = False) -> None:
        """Record one meal. Extra meals incur additional charge."""
        self._meal_count += 1
        if is_extra:
            self._extra_meals += 1

    def add_special_request(self, request: str) -> str:
        """Add a special dietary / food request."""
        if request.strip():
            self._special_requests.append(request.strip())
            return f"Special request added: {request.strip()}"
        return "Empty request ignored."

    def calculate_mess_bill(self) -> float:
        """
        Total bill = monthly base charge + extra meals × per-meal rate.
        """
        extra_charge = self._extra_meals * PER_MEAL_RATE
        return round(self._monthly_charge + extra_charge, 2)

    def process_payment(self) -> str:
        """Mark mess fee as paid."""
        if self._payment_status == "Paid":
            return f"Mess bill for {self._mess_id} is already paid."
        self._payment_status = "Paid"
        self._payment_date = date.today().isoformat()
        total = self.calculate_mess_bill()
        return f"Mess bill ₹{total:.2f} paid for Student {self._student_id} ({self._month})."

    def generate_mess_report(self) -> str:
        """Return a formatted string summary of this mess record."""
        sep = "─" * 36
        return (
            f"\n  {sep}\n"
            f"     MESS BILL — {self._month}\n"
            f"  {sep}\n"
            f"  Mess ID      : {self._mess_id}\n"
            f"  Student      : {self._student_id}\n"
            f"  Total Meals  : {self._meal_count}\n"
            f"  Extra Meals  : {self._extra_meals}\n"
            f"  Base Charge  : ₹{self._monthly_charge:>8.2f}\n"
            f"  Extra Charge : ₹{self._extra_meals * PER_MEAL_RATE:>8.2f}\n"
            f"  Total Bill   : ₹{self.calculate_mess_bill():>8.2f}\n"
            f"  Status       : {self._payment_status}\n"
            f"  Special Req  : {', '.join(self._special_requests) or '—'}\n"
            f"  {sep}\n"
        )

    # ── Serialisation ─────────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mess_id":          self._mess_id,
            "student_id":       self._student_id,
            "month":            self._month,
            "monthly_charge":   self._monthly_charge,
            "meal_count":       self._meal_count,
            "extra_meals":      self._extra_meals,
            "special_requests": self._special_requests,
            "payment_status":   self._payment_status,
            "payment_date":     self._payment_date,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Mess":
        return cls(
            mess_id          = data["mess_id"],
            student_id       = data["student_id"],
            month            = data.get("month", ""),
            monthly_charge   = float(data.get("monthly_charge", MONTHLY_MESS_RATE)),
            meal_count       = int(data.get("meal_count", 0)),
            extra_meals      = int(data.get("extra_meals", 0)),
            special_requests = data.get("special_requests", []),
            payment_status   = data.get("payment_status", "Pending"),
            payment_date     = data.get("payment_date", "—"),
        )

    def __str__(self) -> str:
        return (f"Mess({self._mess_id} | Student:{self._student_id} | "
                f"{self._month} | ₹{self.calculate_mess_bill():.0f} | {self._payment_status})")

    def __repr__(self) -> str:
        return f"Mess(id={self._mess_id!r}, student={self._student_id!r}, month={self._month!r})"
