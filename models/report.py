"""
Report model — generates and exports hostel reports to CSV files.
Uses a generator to stream records lazily.
"""

from __future__ import annotations
import csv
import os
from datetime import date, datetime
from typing import Dict, Any, List, Generator, TYPE_CHECKING

if TYPE_CHECKING:
    from models.student import Student
    from models.room import Room
    from models.fee import Fee
    from models.attendance import Attendance
    from models.complaint import Complaint
    from models.mess import Mess

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")


# ── Generator helper ──────────────────────────────────────────────────────────
def report_generator(records: List[Any]) -> Generator[Any, None, None]:
    """
    Lazily yield one record at a time from a list.
    Use this whenever iterating over large record sets.
    """
    for record in records:
        yield record


class Report:
    """
    Generates and exports various hostel management reports.

    Attributes:
        _report_id      (str): Auto-generated e.g. RPT001.
        _report_type    (str): Category of the report.
        _generated_date (str): ISO date string.
    """

    _id_counter: int = 1

    def __init__(self, report_type: str) -> None:
        self._report_id: str = f"RPT{self.__class__._id_counter:03d}"
        self.__class__._id_counter += 1
        self._report_type: str = report_type
        self._generated_date: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ── Getters ───────────────────────────────────────────────────────────
    @property
    def report_id(self) -> str:
        return self._report_id

    @property
    def report_type(self) -> str:
        return self._report_type

    @property
    def generated_date(self) -> str:
        return self._generated_date

    # ── Core method ───────────────────────────────────────────────────────
    def generate_report(self, records: List[Any]) -> str:
        """Return a header string confirming report generation."""
        count = sum(1 for _ in report_generator(records))  # consume generator
        return (f"Report '{self._report_type}' ({self._report_id}) "
                f"generated at {self._generated_date} with {count} records.")

    def export_report(self, filepath: str, headers: List[str], rows: List[List[Any]]) -> str:
        """Write a CSV file. Returns a success/error message."""
        os.makedirs(REPORTS_DIR, exist_ok=True)
        full_path = os.path.join(REPORTS_DIR, filepath)
        try:
            with open(full_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for row in report_generator(rows):
                    writer.writerow(row)
            return f"Report exported to: {full_path}"
        except OSError as e:
            return f"Export failed: {e}"

    # ── Specific report methods ───────────────────────────────────────────
    def export_student_report(self, students: List["Student"]) -> str:
        headers = ["Student ID", "Name", "Course", "Year", "Room", "Fee Status", "Mobile", "Gender"]
        rows = [
            [s.student_id, s.name, s.course, s.year, s.room_number, s.fee_status, s.mobile_number, s.gender]
            for s in report_generator(students)
        ]
        return self.export_report("student_report.csv", headers, rows)

    def export_room_report(self, rooms: List["Room"]) -> str:
        headers = ["Room ID", "Room Number", "Type", "Floor", "Capacity", "Occupied", "Vacant", "Monthly Charge"]
        rows = [
            [r.room_id, r.room_number, r.room_type, r.floor,
             r.capacity, r.occupied_beds, r.available_beds, f"₹{r.monthly_charge:,.0f}"]
            for r in report_generator(rooms)
        ]
        return self.export_report("room_report.csv", headers, rows)

    def export_fee_report(self, fees: List["Fee"]) -> str:
        headers = ["Fee ID", "Student ID", "Month", "Amount", "Fine", "Total Due", "Due Date", "Status", "Paid On"]
        rows = [
            [f.fee_id, f.student_id, f.month, f"₹{f.amount:.2f}",
             f"₹{f.fine:.2f}", f"₹{f.total_due:.2f}", f.due_date, f.payment_status, f.payment_date]
            for f in report_generator(fees)
        ]
        return self.export_report("fee_report.csv", headers, rows)

    def export_attendance_report(self, records: List["Attendance"]) -> str:
        headers = ["Attendance ID", "Student ID", "Date", "Status", "In Time", "Out Time", "Remarks"]
        rows = [
            [a.attendance_id, a.student_id, a.date, a.status, a.in_time, a.out_time, a.remarks]
            for a in report_generator(records)
        ]
        return self.export_report("attendance_report.csv", headers, rows)

    def export_complaint_report(self, complaints: List["Complaint"]) -> str:
        headers = ["Complaint ID", "Student ID", "Type", "Priority", "Status", "Submitted", "Resolved", "Remarks"]
        rows = [
            [c.complaint_id, c.student_id, c.complaint_type, c.priority,
             c.complaint_status, c.date_submitted, c.date_resolved, c.remarks]
            for c in report_generator(complaints)
        ]
        return self.export_report("complaint_report.csv", headers, rows)

    def export_mess_report(self, mess_records: List["Mess"]) -> str:
        headers = ["Mess ID", "Student ID", "Month", "Base Charge", "Extra Meals", "Total Bill", "Status"]
        rows = [
            [m.mess_id, m.student_id, m.month,
             f"₹{m.monthly_charge:.2f}", m.extra_meals,
             f"₹{m.calculate_mess_bill():.2f}", m.payment_status]
            for m in report_generator(mess_records)
        ]
        return self.export_report("mess_report.csv", headers, rows)

    def __str__(self) -> str:
        return f"Report({self._report_id} | {self._report_type} | {self._generated_date})"

    def __repr__(self) -> str:
        return f"Report(id={self._report_id!r}, type={self._report_type!r})"
