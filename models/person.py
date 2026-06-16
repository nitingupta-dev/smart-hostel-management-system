"""
Abstract Person class — base for Student and Warden.
Enforces common identity attributes and the display_details contract.
"""

from abc import ABC, abstractmethod
from typing import Optional


class Person(ABC):
    """
    Abstract base class representing any person in the hostel system.

    Attributes:
        _person_id    (str): Unique identifier.
        _name         (str): Full name.
        _mobile_number(str): 10-digit mobile number.
        _address      (str): Residential address.
    """

    def __init__(
        self,
        person_id: str,
        name: str,
        mobile_number: str,
        address: str,
    ) -> None:
        self._person_id: str = person_id
        self._name: str = name
        self._mobile_number: str = mobile_number
        self._address: str = address

    # ── Getters ────────────────────────────────────────────────────────────
    @property
    def person_id(self) -> str:
        return self._person_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def mobile_number(self) -> str:
        return self._mobile_number

    @property
    def address(self) -> str:
        return self._address

    # ── Setters ────────────────────────────────────────────────────────────
    @name.setter
    def name(self, value: str) -> None:
        if not value.strip():
            raise ValueError("Name cannot be empty.")
        self._name = value.strip()

    @mobile_number.setter
    def mobile_number(self, value: str) -> None:
        value = value.strip()
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Mobile number must be exactly 10 digits.")
        self._mobile_number = value

    @address.setter
    def address(self, value: str) -> None:
        if not value.strip():
            raise ValueError("Address cannot be empty.")
        self._address = value.strip()

    # ── Abstract methods ───────────────────────────────────────────────────
    @abstractmethod
    def display_details(self) -> None:
        """Print a formatted summary of this person's details."""

    # ── Concrete shared methods ────────────────────────────────────────────
    def update_details(
        self,
        name: Optional[str] = None,
        mobile_number: Optional[str] = None,
        address: Optional[str] = None,
    ) -> None:
        """
        Update one or more fields. Skips fields that are None.

        Args:
            name           : New full name.
            mobile_number  : New 10-digit mobile number.
            address        : New address.
        """
        if name is not None:
            self.name = name
        if mobile_number is not None:
            self.mobile_number = mobile_number
        if address is not None:
            self.address = address

    # ── Magic methods ──────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self._person_id}, name={self._name})"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"person_id={self._person_id!r}, "
            f"name={self._name!r}, "
            f"mobile={self._mobile_number!r})"
        )
