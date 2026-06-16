"""
HostelManagementSystem — the central controller class.
Composes all sub-modules and drives the menu-based interface.
"""

from __future__ import annotations
import os
from datetime import date, datetime
from typing import Dict, List, Optional, Any, Tuple

# ── Models ────────────────────────────────────────────────────────────────
from models.student import Student
from models.warden import Warden
from models.room import Room, ROOM_TYPES
from models.fee import Fee
from models.attendance import Attendance
from models.visitor import Visitor
from models.complaint import Complaint
from models.mess import Mess
from models.report import Report, report_generator

# ── Utils ─────────────────────────────────────────────────────────────────
from utils.decorators import log_activity
from utils.exceptions import (
    InvalidStudentID, RoomNotAvailable, InvalidFeeAmount,
    DuplicateStudentRegistration, InvalidComplaintID,
)
from utils.file_handler import save_json, load_json, ensure_data_files
from utils.helper import (
    print_header, print_section, success, error, info, warning, pause,
    get_input, get_int, get_float, get_choice, get_date, confirm,
    search_student_recursive,
    sort_students_by_fee, sort_rooms_by_occupancy, sort_complaints_by_priority,
    today_str, now_time_str, fee_due_date, truncate,
    green, red, yellow, cyan, bold,
)

# ── Optional display libs ─────────────────────────────────────────────────
try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


# ══════════════════════════════════════════════════════════════════════════════
#  HOSTEL RULES tuple (immutable)
# ══════════════════════════════════════════════════════════════════════════════
HOSTEL_RULES: Tuple[str, ...] = (
    "No Ragging",
    "No Smoking",
    "No Alcohol",
    "Maintain Discipline",
    "Lights Off by 11 PM",
    "Guests allowed only in visitor area",
    "Keep common areas clean",
)


def _tab(rows: List[List[Any]], headers: List[str] = (), fmt: str = "rounded_outline") -> str:
    """Thin wrapper around tabulate (falls back to basic string if not installed)."""
    if HAS_TABULATE:
        return tabulate(rows, headers=headers or (), tablefmt=fmt)
    lines = []
    if headers:
        lines.append("  " + "  |  ".join(str(h) for h in headers))
        lines.append("  " + "-" * 60)
    for row in rows:
        lines.append("  " + "  |  ".join(str(c) for c in row))
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN SYSTEM CLASS
# ══════════════════════════════════════════════════════════════════════════════

class HostelManagementSystem:
    """
    Centralises all hostel management operations.

    Attributes:
        students            : list of Student objects
        rooms               : list of Room objects
        fees                : list of Fee objects
        attendance_records  : list of Attendance objects
        visitors            : list of Visitor objects
        complaints          : list of Complaint objects
        mess_records        : list of Mess objects
        _warden             : the default Warden account
        _logged_in          : authentication flag
    """

    # ── Room type set ──────────────────────────────────────────────────────
    ROOM_TYPES_SET = set(ROOM_TYPES)   # Using SET data structure

    def __init__(self) -> None:
        # LIST data structures
        self.students:           List[Student]    = []
        self.rooms:              List[Room]       = []
        self.visitors:           List[Visitor]    = []
        self.complaints:         List[Complaint]  = []
        # These could also be lists — kept as lists for uniform iteration
        self.fees:               List[Fee]        = []
        self.attendance_records: List[Attendance] = []
        self.mess_records:       List[Mess]       = []

        # DICTIONARY data structures for fast lookups
        self._fee_index:        Dict[str, Fee]        = {}   # fee_id → Fee
        self._attendance_index: Dict[str, Attendance] = {}   # att_id → Attendance

        # Default warden
        self._warden: Warden = Warden(
            warden_id    = "WRD001",
            name         = "Admin Warden",
            mobile_number= "9999999999",
            address      = "Hostel Office",
            hostel_name  = "Smart Hostel",
            username     = "admin",
            password     = "admin123",
        )
        self._logged_in: bool = False

    # ══════════════════════════════════════════════════════════════════════
    #  Magic methods
    # ══════════════════════════════════════════════════════════════════════
    def __len__(self) -> int:
        """len(hostel_system) returns the total number of registered students."""
        return len(self.students)

    def __str__(self) -> str:
        return (f"HostelManagementSystem("
                f"students={len(self.students)}, rooms={len(self.rooms)})")

    def __repr__(self) -> str:
        return self.__str__()

    # ══════════════════════════════════════════════════════════════════════
    #  Authentication
    # ══════════════════════════════════════════════════════════════════════
    def login(self) -> bool:
        print_header("WARDEN LOGIN")
        username = get_input("Username")
        password = get_input("Password")
        if (username == self._warden.username and
                self._warden.verify_password(password)):
            self._logged_in = True
            success(f"Welcome, {self._warden.name}!")
            pause()
            return True
        error("Invalid credentials. Access denied.")
        pause()
        return False

    def logout(self) -> None:
        self._logged_in = False
        success("Logged out successfully.")

    # ══════════════════════════════════════════════════════════════════════
    #  Data persistence
    # ══════════════════════════════════════════════════════════════════════
    def save_data(self) -> None:
        """Serialise all in-memory records to JSON files."""
        save_json("students.json",   [s.to_dict() for s in self.students])
        save_json("rooms.json",      [r.to_dict() for r in self.rooms])
        save_json("fees.json",       [f.to_dict() for f in self.fees])
        save_json("attendance.json", [a.to_dict() for a in self.attendance_records])
        save_json("visitors.json",   [v.to_dict() for v in self.visitors])
        save_json("complaints.json", [c.to_dict() for c in self.complaints])
        save_json("mess.json",       [m.to_dict() for m in self.mess_records])
        success("All data saved successfully.")

    def load_data(self) -> None:
        """Deserialise records from JSON files into memory."""
        ensure_data_files()

        raw_students = load_json("students.json", default=[])
        self.students = [Student.from_dict(d) for d in raw_students]
        if self.students:
            max_id = max(int(s.student_id.replace("STD", "")) for s in self.students)
            Student.set_counter(max_id)

        raw_rooms = load_json("rooms.json", default=[])
        self.rooms = [Room.from_dict(d) for d in raw_rooms]
        if self.rooms:
            max_id = max(int(r.room_id.replace("RM", "")) for r in self.rooms)
            Room.set_counter(max_id)

        raw_fees = load_json("fees.json", default=[])
        self.fees = [Fee.from_dict(d) for d in raw_fees]
        for f in self.fees:
            f.refresh_overdue()
            self._fee_index[f.fee_id] = f
        if self.fees:
            max_id = max(int(f.fee_id.replace("FEE", "")) for f in self.fees)
            Fee.set_counter(max_id)

        raw_att = load_json("attendance.json", default=[])
        self.attendance_records = [Attendance.from_dict(d) for d in raw_att]
        for a in self.attendance_records:
            self._attendance_index[a.attendance_id] = a
        if self.attendance_records:
            max_id = max(int(a.attendance_id.replace("ATT", "")) for a in self.attendance_records)
            Attendance.set_counter(max_id)

        raw_vis = load_json("visitors.json", default=[])
        self.visitors = [Visitor.from_dict(d) for d in raw_vis]
        if self.visitors:
            max_id = max(int(v.visitor_id.replace("VIS", "")) for v in self.visitors)
            Visitor.set_counter(max_id)

        raw_cmp = load_json("complaints.json", default=[])
        self.complaints = [Complaint.from_dict(d) for d in raw_cmp]
        if self.complaints:
            max_id = max(int(c.complaint_id.replace("CMP", "")) for c in self.complaints)
            Complaint.set_counter(max_id)

        raw_mess = load_json("mess.json", default=[])
        self.mess_records = [Mess.from_dict(d) for d in raw_mess]
        if self.mess_records:
            max_id = max(int(m.mess_id.replace("MES", "")) for m in self.mess_records)
            Mess.set_counter(max_id)

        success("Data loaded successfully.")

    # ══════════════════════════════════════════════════════════════════════
    #  STUDENT MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════
    @log_activity
    def register_student(self) -> None:
        print_section("REGISTER NEW STUDENT")
        try:
            student_id = Student.generate_id()
            name          = get_input("Full Name")
            mobile        = get_input("Mobile Number (10 digits)")
            address       = get_input("Address")
            email         = get_input("Email", required=False)
            gender        = get_choice("Gender", ["Male", "Female", "Other"])
            course        = get_input("Course / Programme")
            year          = get_int("Academic Year (1-5)", 1, 5)

            # Duplicate check
            existing = search_student_recursive(self.students, student_id)
            if existing:
                raise DuplicateStudentRegistration(student_id)

            student = Student(
                student_id    = student_id,
                name          = name,
                mobile_number = mobile,
                address       = address,
                course        = course,
                year          = year,
                email         = email,
                gender        = gender,
            )
            self.students.append(student)
            success(f"Student registered successfully! ID: {cyan(student_id)}")
        except DuplicateStudentRegistration as e:
            error(str(e))
        except ValueError as e:
            error(str(e))

    def search_student(self) -> Optional[Student]:
        """Search student by ID (uses recursive function) or by name."""
        print_section("SEARCH STUDENT")
        query = get_input("Enter Student ID or Name")
        # Try ID first (recursive)
        found = search_student_recursive(self.students, query)
        if found:
            return found
        # Fallback: name search (case-insensitive)
        matches = [s for s in self.students if query.lower() in s.name.lower()]
        if not matches:
            error(f"No student found for '{query}'.")
            return None
        if len(matches) == 1:
            return matches[0]
        # Multiple matches
        print_section("Multiple Matches")
        rows = [[s.student_id, s.name, s.course, s.room_number] for s in matches]
        print(_tab(rows, ["ID", "Name", "Course", "Room"]))
        sid = get_input("Enter exact Student ID")
        return next((s for s in matches if s.student_id == sid), None)

    def view_all_students(self) -> None:
        print_section("ALL STUDENTS")
        if not self.students:
            info("No students registered yet.")
            return
        sorted_students = sort_students_by_fee(self.students)
        rows = [
            [s.student_id, truncate(s.name, 22), s.course, s.year,
             s.room_number, s.fee_status, s.mobile_number]
            for s in report_generator(sorted_students)
        ]
        print(_tab(rows, ["ID", "Name", "Course", "Year", "Room", "Fee", "Mobile"]))
        print(f"\n  Total Students: {bold(str(len(self.students)))}")

    def update_student(self) -> None:
        print_section("UPDATE STUDENT")
        student = self.search_student()
        if not student:
            return
        print(f"\n  Editing: {student}")
        print("  (Press Enter to keep current value)")
        name    = get_input(f"Name [{student.name}]", required=False) or None
        mobile  = get_input(f"Mobile [{student.mobile_number}]", required=False) or None
        address = get_input(f"Address [{truncate(student.address)}]", required=False) or None
        course  = get_input(f"Course [{student.course}]", required=False) or None
        year_s  = get_input(f"Year [{student.year}] (1-5)", required=False)
        year    = int(year_s) if year_s else None

        student.update_details(name=name, mobile_number=mobile, address=address)
        if course:
            student.course = course
        if year is not None:
            student.year = year
        success("Student updated successfully.")

    def delete_student(self) -> None:
        print_section("DELETE STUDENT")
        student = self.search_student()
        if not student:
            return
        student.display_details()
        if not confirm(f"Delete student {student.student_id}? (y/n)"):
            info("Deletion cancelled.")
            return
        # Vacate room if allocated
        if student.room_number != "N/A":
            room = self._find_room_by_number(student.room_number)
            if room:
                room.vacate_room(student.student_id)
        self.students.remove(student)
        success(f"Student {student.student_id} deleted.")

    def manage_students(self) -> None:
        while True:
            print_header("STUDENT MANAGEMENT")
            print("  1. Register New Student")
            print("  2. View All Students")
            print("  3. Search Student")
            print("  4. Update Student")
            print("  5. Delete Student")
            print("  6. View Student Profile")
            print("  0. Back\n")
            choice = get_input("Enter choice")
            if choice == "1":
                self.register_student()
            elif choice == "2":
                self.view_all_students()
            elif choice == "3":
                s = self.search_student()
                if s:
                    s.display_details()
            elif choice == "4":
                self.update_student()
            elif choice == "5":
                self.delete_student()
            elif choice == "6":
                s = self.search_student()
                if s:
                    s.display_details()
            elif choice == "0":
                break
            else:
                warning("Invalid choice.")
            pause()

    # ══════════════════════════════════════════════════════════════════════
    #  ROOM MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════
    def _find_room_by_number(self, number: str) -> Optional[Room]:
        return next((r for r in self.rooms if r.room_number == number), None)

    def add_room(self) -> None:
        print_section("ADD NEW ROOM")
        room_id     = Room.generate_id()
        room_number = get_input("Room Number (e.g. 101)")
        if self._find_room_by_number(room_number):
            error(f"Room {room_number} already exists.")
            return
        room_type   = get_choice("Room Type", list(ROOM_TYPES))
        capacity    = get_int("Capacity", 1, 10)
        floor       = get_int("Floor", 1, 20)
        room = Room(room_id, room_number, room_type, capacity, floor)
        self.rooms.append(room)
        success(f"Room {room_number} added (ID: {room_id}).")

    @log_activity
    def allocate_room(self) -> None:
        print_section("ALLOCATE ROOM TO STUDENT")
        student = self.search_student()
        if not student:
            return
        if student.room_number != "N/A":
            warning(f"Student already in Room {student.room_number}.")
            if not confirm("Transfer to a different room? (y/n)"):
                return
            old_room = self._find_room_by_number(student.room_number)
            if old_room:
                old_room.vacate_room(student.student_id)

        # Show available rooms
        available = [r for r in self.rooms if r.check_availability()]
        if not available:
            error("No rooms available at this time.")
            return
        sorted_rooms = sort_rooms_by_occupancy(available)
        rows = [[r.room_id, r.room_number, r.room_type, r.floor,
                 r.available_beds, f"₹{r.monthly_charge:,.0f}"]
                for r in report_generator(sorted_rooms)]
        print(_tab(rows, ["ID", "Number", "Type", "Floor", "Free Beds", "Charge/mo"]))
        room_num = get_input("Enter Room Number to allocate")
        room = self._find_room_by_number(room_num)
        if not room:
            error(f"Room {room_num} not found.")
            return
        try:
            msg = room.allocate_room(student.student_id)
            student.room_number = room_num
            success(msg)
        except RoomNotAvailable as e:
            error(str(e))

    def view_room_status(self) -> None:
        print_section("ROOM STATUS")
        if not self.rooms:
            info("No rooms configured.")
            return
        rows = [
            [r.room_number, r.room_type, r.floor, r.capacity,
             r.occupied_beds, r.available_beds,
             green("Available") if r.check_availability() else red("Full"),
             f"₹{r.monthly_charge:,.0f}"]
            for r in report_generator(sort_rooms_by_occupancy(self.rooms))
        ]
        print(_tab(rows, ["Number", "Type", "Floor", "Cap", "Occ", "Free", "Status", "₹/mo"]))
        stats = Room.hostel_occupancy_stats(self.rooms)
        print(f"\n  Total Rooms: {stats['total_rooms']}  |  "
              f"Occupied: {stats['total_occupied']}  |  "
              f"Vacant: {stats['total_vacant']}")

    def transfer_room(self) -> None:
        """Transfer a student from their current room to another."""
        print_section("ROOM TRANSFER")
        student = self.search_student()
        if not student or student.room_number == "N/A":
            warning("Student is not assigned to any room.")
            return
        old_room = self._find_room_by_number(student.room_number)
        new_num  = get_input("New Room Number")
        new_room = self._find_room_by_number(new_num)
        if not new_room:
            error("Target room not found.")
            return
        if not new_room.check_availability():
            error(f"Room {new_num} is full.")
            return
        if old_room:
            old_room.vacate_room(student.student_id)
        new_room.allocate_room(student.student_id)
        student.room_number = new_num
        success(f"Student {student.student_id} transferred to Room {new_num}.")

    def manage_rooms(self) -> None:
        while True:
            print_header("ROOM MANAGEMENT")
            print("  1. Add New Room")
            print("  2. Allocate Room")
            print("  3. View Room Status")
            print("  4. Transfer Room")
            print("  5. View Room Details")
            print("  0. Back\n")
            choice = get_input("Enter choice")
            if choice == "1":
                self.add_room()
            elif choice == "2":
                self.allocate_room()
            elif choice == "3":
                self.view_room_status()
            elif choice == "4":
                self.transfer_room()
            elif choice == "5":
                num = get_input("Room Number")
                r = self._find_room_by_number(num)
                if r:
                    r.display_details()
                else:
                    error("Room not found.")
            elif choice == "0":
                break
            else:
                warning("Invalid choice.")
            pause()

    # ══════════════════════════════════════════════════════════════════════
    #  FEE MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════
    @log_activity
    def manage_fees(self) -> None:
        while True:
            print_header("FEE MANAGEMENT")
            print("  1. Generate Fee for Student")
            print("  2. Process Payment")
            print("  3. View Fee Records")
            print("  4. View Due / Overdue Fees")
            print("  5. Calculate Fine (manual)")
            print("  6. Print Receipt")
            print("  0. Back\n")
            choice = get_input("Enter choice")
            if choice == "1":
                self._generate_fee()
            elif choice == "2":
                self._process_payment()
            elif choice == "3":
                self._view_fees()
            elif choice == "4":
                self._view_due_fees()
            elif choice == "5":
                days = get_int("Days overdue", 0, 365)
                fine = Fee.calculate_fine(days)
                info(f"Fine for {days} day(s) overdue: {cyan('₹' + str(fine))}")
            elif choice == "6":
                self._print_receipt()
            elif choice == "0":
                break
            else:
                warning("Invalid choice.")
            pause()

    def _generate_fee(self) -> None:
        print_section("GENERATE FEE")
        student = self.search_student()
        if not student:
            return
        amount   = get_float("Fee Amount (₹)", min_val=1.0)
        due_date = get_date("Due Date (YYYY-MM-DD)")
        month    = get_input("Month (e.g. June 2025)", required=False) or datetime.now().strftime("%B %Y")
        fee_id   = Fee.generate_id()
        fee      = Fee(fee_id, student.student_id, amount, due_date, month=month)
        self.fees.append(fee)
        self._fee_index[fee_id] = fee
        success(f"Fee {fee_id} generated for {student.student_id}.")

    def _process_payment(self) -> None:
        print_section("PROCESS PAYMENT")
        student = self.search_student()
        if not student:
            return
        student_fees = [f for f in self.fees
                        if f.student_id == student.student_id and f.payment_status != "Paid"]
        if not student_fees:
            info("No pending fees for this student.")
            return
        rows = [[f.fee_id, f.month, f"₹{f.amount:.2f}",
                 f"₹{f.fine:.2f}", f"₹{f.total_due:.2f}", f.payment_status]
                for f in student_fees]
        print(_tab(rows, ["Fee ID", "Month", "Amount", "Fine", "Total", "Status"]))
        fee_id = get_input("Enter Fee ID to pay")
        fee = self._fee_index.get(fee_id)
        if not fee:
            error(f"Fee {fee_id} not found.")
            return
        msg = fee.process_payment()
        student.fee_status = "Paid"
        success(msg)

    def _view_fees(self) -> None:
        print_section("ALL FEE RECORDS")
        if not self.fees:
            info("No fee records.")
            return
        for f in self.fees:
            f.refresh_overdue()
        rows = [[f.fee_id, f.student_id, f.month, f"₹{f.amount:.2f}",
                 f"₹{f.fine:.2f}", f.payment_status, f.due_date]
                for f in report_generator(self.fees)]
        print(_tab(rows, ["Fee ID", "Student", "Month", "Amount", "Fine", "Status", "Due"]))

    def _view_due_fees(self) -> None:
        print_section("DUE / OVERDUE FEES")
        due = [f for f in self.fees if f.payment_status in {"Pending", "Overdue"}]
        if not due:
            success("No outstanding fees.")
            return
        rows = [[f.fee_id, f.student_id, f.month, f"₹{f.total_due:.2f}",
                 red(f.payment_status), f.due_date]
                for f in due]
        print(_tab(rows, ["Fee ID", "Student", "Month", "Total Due", "Status", "Due Date"]))

    def _print_receipt(self) -> None:
        fee_id = get_input("Enter Fee ID")
        fee = self._fee_index.get(fee_id)
        if fee:
            print(fee.generate_receipt())
        else:
            error(f"Fee {fee_id} not found.")

    # ══════════════════════════════════════════════════════════════════════
    #  ATTENDANCE MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════
    def manage_attendance(self) -> None:
        while True:
            print_header("ATTENDANCE MANAGEMENT")
            print("  1. Mark Attendance")
            print("  2. View Today's Attendance")
            print("  3. View Student Attendance")
            print("  4. Record Out-Time")
            print("  5. Attendance Percentage")
            print("  0. Back\n")
            choice = get_input("Enter choice")
            if choice == "1":
                self._mark_attendance()
            elif choice == "2":
                self._view_today_attendance()
            elif choice == "3":
                self._view_student_attendance()
            elif choice == "4":
                self._record_out_time()
            elif choice == "5":
                self._attendance_percentage()
            elif choice == "0":
                break
            else:
                warning("Invalid choice.")
            pause()

    def _mark_attendance(self) -> None:
        print_section("MARK ATTENDANCE")
        student = self.search_student()
        if not student:
            return
        today = today_str()
        # Check if already marked today
        existing = next(
            (a for a in self.attendance_records
             if a.student_id == student.student_id and a.date == today),
            None,
        )
        if existing:
            warning(f"Attendance already marked for {student.student_id} today ({existing.status}).")
            if not confirm("Override? (y/n)"):
                return
            status = get_choice("Status", ["Present", "Absent", "Leave", "Late"])
            existing.mark_attendance(status)
            success("Attendance updated.")
            return

        status   = get_choice("Status", ["Present", "Absent", "Leave", "Late"])
        in_time  = now_time_str() if status in {"Present", "Late"} else "—"
        remarks  = get_input("Remarks", required=False)
        att_id   = Attendance.generate_id()
        att = Attendance(att_id, student.student_id, today, status, in_time, remarks=remarks)
        self.attendance_records.append(att)
        self._attendance_index[att_id] = att
        success(f"Attendance marked: {student.student_id} — {status}")

    def _view_today_attendance(self) -> None:
        print_section(f"TODAY'S ATTENDANCE — {today_str()}")
        today_recs = [a for a in self.attendance_records if a.date == today_str()]
        if not today_recs:
            info("No attendance records for today.")
            return
        rows = [[a.attendance_id, a.student_id, a.status, a.in_time, a.out_time]
                for a in report_generator(today_recs)]
        print(_tab(rows, ["ID", "Student", "Status", "In", "Out"]))

    def _view_student_attendance(self) -> None:
        student = self.search_student()
        if not student:
            return
        recs = [a for a in self.attendance_records if a.student_id == student.student_id]
        if not recs:
            info("No records found.")
            return
        rows = [[a.date, a.status, a.in_time, a.out_time, a.remarks]
                for a in report_generator(sorted(recs, key=lambda a: a.date, reverse=True))]
        print(_tab(rows, ["Date", "Status", "In", "Out", "Remarks"]))

    def _record_out_time(self) -> None:
        student = self.search_student()
        if not student:
            return
        today = today_str()
        rec = next(
            (a for a in self.attendance_records
             if a.student_id == student.student_id and a.date == today),
            None,
        )
        if not rec:
            error("No attendance record found for today.")
            return
        out_time = now_time_str()
        msg = rec.record_out_time(out_time)
        success(msg)

    def _attendance_percentage(self) -> None:
        student = self.search_student()
        if not student:
            return
        recs = [a for a in self.attendance_records if a.student_id == student.student_id]
        pct  = Attendance.calculate_percentage(recs)
        print(f"\n  {student.name} | Total Records: {len(recs)} | "
              f"Attendance: {cyan(str(pct) + '%')}")

    # ══════════════════════════════════════════════════════════════════════
    #  VISITOR MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════
    def manage_visitors(self) -> None:
        while True:
            print_header("VISITOR MANAGEMENT")
            print("  1. Register Visitor")
            print("  2. Approve Visitor")
            print("  3. Reject Visitor")
            print("  4. Visitor Checkout")
            print("  5. View Visitor Log")
            print("  0. Back\n")
            choice = get_input("Enter choice")
            if choice == "1":
                self._register_visitor()
            elif choice == "2":
                self._approve_visitor()
            elif choice == "3":
                self._reject_visitor()
            elif choice == "4":
                self._checkout_visitor()
            elif choice == "5":
                self._view_visitors()
            elif choice == "0":
                break
            else:
                warning("Invalid choice.")
            pause()

    def _register_visitor(self) -> None:
        print_section("REGISTER VISITOR")
        student = self.search_student()
        if not student:
            return
        visitor_id   = Visitor.generate_id()
        visitor_name = get_input("Visitor Name")
        relation     = get_choice("Relation", ["Parent", "Guardian", "Sibling", "Friend", "Relative", "Other"])
        mobile       = get_input("Visitor Mobile", required=False)
        purpose      = get_input("Purpose of Visit", required=False)
        v = Visitor(visitor_id, visitor_name, relation, student.student_id,
                    today_str(), purpose, mobile=mobile)
        self.visitors.append(v)
        success(v.register_visitor())

    def _approve_visitor(self) -> None:
        pending = [v for v in self.visitors if v.status == "Pending"]
        if not pending:
            info("No pending visitors.")
            return
        rows = [[v.visitor_id, v.visitor_name, v.relation, v.student_id, v.visit_date]
                for v in pending]
        print(_tab(rows, ["ID", "Name", "Relation", "Student", "Date"]))
        vid = get_input("Enter Visitor ID to approve")
        v = next((x for x in self.visitors if x.visitor_id == vid), None)
        if v:
            success(v.approve_visit())
        else:
            error("Visitor not found.")

    def _reject_visitor(self) -> None:
        vid = get_input("Enter Visitor ID to reject")
        v = next((x for x in self.visitors if x.visitor_id == vid), None)
        if v:
            success(v.reject_visit())
        else:
            error("Visitor not found.")

    def _checkout_visitor(self) -> None:
        active = [v for v in self.visitors if v.status == "Approved"]
        if not active:
            info("No visitors currently inside.")
            return
        rows = [[v.visitor_id, v.visitor_name, v.student_id, v.in_time] for v in active]
        print(_tab(rows, ["ID", "Name", "Student", "In Time"]))
        vid = get_input("Enter Visitor ID for checkout")
        v = next((x for x in self.visitors if x.visitor_id == vid), None)
        if v:
            success(v.checkout_visitor())
        else:
            error("Visitor not found.")

    def _view_visitors(self) -> None:
        print_section("VISITOR LOG")
        if not self.visitors:
            info("No visitor records.")
            return
        rows = [[v.visitor_id, truncate(v.visitor_name), v.relation,
                 v.student_id, v.visit_date, v.status]
                for v in report_generator(self.visitors)]
        print(_tab(rows, ["ID", "Name", "Relation", "Student", "Date", "Status"]))

    # ══════════════════════════════════════════════════════════════════════
    #  COMPLAINT MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════
    @log_activity
    def manage_complaints(self) -> None:
        while True:
            print_header("COMPLAINT MANAGEMENT")
            print("  1. Register Complaint")
            print("  2. View All Complaints")
            print("  3. Update Complaint Status")
            print("  4. View Open / High-Priority")
            print("  5. Escalate Priority")
            print("  0. Back\n")
            choice = get_input("Enter choice")
            if choice == "1":
                self._register_complaint()
            elif choice == "2":
                self._view_complaints()
            elif choice == "3":
                self._update_complaint_status()
            elif choice == "4":
                self._view_open_complaints()
            elif choice == "5":
                self._escalate_complaint()
            elif choice == "0":
                break
            else:
                warning("Invalid choice.")
            pause()

    def _register_complaint(self) -> None:
        print_section("REGISTER COMPLAINT")
        student = self.search_student()
        if not student:
            return
        ctype       = get_choice("Complaint Type",
                                 ["Maintenance", "Electrical", "Plumbing",
                                  "Housekeeping", "Food", "Noise", "Security", "Other"])
        priority    = get_choice("Priority", ["Low", "Medium", "High"])
        description = get_input("Description")
        cid = Complaint.generate_id()
        c   = Complaint(cid, student.student_id, ctype, description, priority=priority)
        self.complaints.append(c)
        success(c.register_complaint())

    def _view_complaints(self) -> None:
        print_section("ALL COMPLAINTS")
        if not self.complaints:
            info("No complaints registered.")
            return
        sorted_c = sort_complaints_by_priority(self.complaints)
        rows = [
            [c.complaint_id, c.student_id, c.complaint_type,
             c.priority, c.complaint_status, c.date_submitted]
            for c in report_generator(sorted_c)
        ]
        print(_tab(rows, ["ID", "Student", "Type", "Priority", "Status", "Date"]))

    def _update_complaint_status(self) -> None:
        cid = get_input("Enter Complaint ID")
        c = next((x for x in self.complaints if x.complaint_id == cid), None)
        if not c:
            error(f"Complaint {cid} not found.")
            return
        print(f"\n  Current status: {c.complaint_status}")
        new_status = get_choice("New Status",
                                ["Open", "In-Progress", "Resolved", "Closed", "Rejected"])
        remarks = get_input("Warden Remarks", required=False)
        success(c.update_status(new_status, remarks))

    def _view_open_complaints(self) -> None:
        open_c = [c for c in self.complaints
                  if c.complaint_status in {"Open", "In-Progress"} or c.priority == "High"]
        if not open_c:
            success("No open/high-priority complaints.")
            return
        rows = [[c.complaint_id, c.student_id, c.complaint_type,
                 c.priority, c.complaint_status]
                for c in sort_complaints_by_priority(open_c)]
        print(_tab(rows, ["ID", "Student", "Type", "Priority", "Status"]))

    def _escalate_complaint(self) -> None:
        cid = get_input("Complaint ID to escalate")
        c = next((x for x in self.complaints if x.complaint_id == cid), None)
        if c:
            success(c.escalate())
        else:
            error("Complaint not found.")

    # ══════════════════════════════════════════════════════════════════════
    #  MESS MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════
    def manage_mess(self) -> None:
        while True:
            print_header("MESS MANAGEMENT")
            print("  1. Create Mess Record")
            print("  2. Add Meal / Extra Meal")
            print("  3. Add Special Request")
            print("  4. Process Mess Payment")
            print("  5. View Mess Records")
            print("  6. View Mess Bill")
            print("  0. Back\n")
            choice = get_input("Enter choice")
            if choice == "1":
                self._create_mess_record()
            elif choice == "2":
                self._add_meal()
            elif choice == "3":
                self._add_special_request()
            elif choice == "4":
                self._process_mess_payment()
            elif choice == "5":
                self._view_mess_records()
            elif choice == "6":
                self._view_mess_bill()
            elif choice == "0":
                break
            else:
                warning("Invalid choice.")
            pause()

    def _create_mess_record(self) -> None:
        student = self.search_student()
        if not student:
            return
        month    = get_input("Month (e.g. June 2025)", required=False) or datetime.now().strftime("%B %Y")
        charge   = get_float(f"Monthly Charge [default ₹2500]", min_val=0)
        if charge == 0:
            charge = 2500.0
        mid = Mess.generate_id()
        m   = Mess(mid, student.student_id, month, monthly_charge=charge)
        self.mess_records.append(m)
        success(f"Mess record {mid} created for {student.student_id}.")

    def _add_meal(self) -> None:
        student = self.search_student()
        if not student:
            return
        recs = [m for m in self.mess_records if m.student_id == student.student_id]
        if not recs:
            error("No mess record found.")
            return
        m = recs[-1]
        is_extra = confirm("Is this an extra meal? (y/n)")
        m.add_meal(is_extra)
        success(f"Meal added. Total: {m.meal_count}. Extra: {m.extra_meals}.")

    def _add_special_request(self) -> None:
        student = self.search_student()
        if not student:
            return
        recs = [m for m in self.mess_records if m.student_id == student.student_id]
        if not recs:
            error("No mess record found.")
            return
        req = get_input("Special Food Request")
        success(recs[-1].add_special_request(req))

    def _process_mess_payment(self) -> None:
        student = self.search_student()
        if not student:
            return
        recs = [m for m in self.mess_records
                if m.student_id == student.student_id and m.payment_status == "Pending"]
        if not recs:
            info("No pending mess payments.")
            return
        m = recs[-1]
        print(m.generate_mess_report())
        if confirm("Confirm payment? (y/n)"):
            success(m.process_payment())

    def _view_mess_records(self) -> None:
        print_section("MESS RECORDS")
        if not self.mess_records:
            info("No mess records.")
            return
        rows = [[m.mess_id, m.student_id, m.month, m.meal_count,
                 m.extra_meals, f"₹{m.calculate_mess_bill():.2f}", m.payment_status]
                for m in report_generator(self.mess_records)]
        print(_tab(rows, ["ID", "Student", "Month", "Meals", "Extra", "Bill", "Status"]))

    def _view_mess_bill(self) -> None:
        student = self.search_student()
        if not student:
            return
        recs = [m for m in self.mess_records if m.student_id == student.student_id]
        if not recs:
            info("No records.")
            return
        print(recs[-1].generate_mess_report())

    # ══════════════════════════════════════════════════════════════════════
    #  REPORT GENERATION
    # ══════════════════════════════════════════════════════════════════════
    @log_activity
    def generate_reports(self) -> None:
        while True:
            print_header("REPORT GENERATION")
            print("  1. Student Report (CSV)")
            print("  2. Room Occupancy Report (CSV)")
            print("  3. Fee Report (CSV)")
            print("  4. Attendance Report (CSV)")
            print("  5. Complaint Report (CSV)")
            print("  6. Mess Report (CSV)")
            print("  7. Generate ALL Reports")
            print("  0. Back\n")
            choice = get_input("Enter choice")
            r = Report("Hostel Reports")
            if choice == "1":
                success(r.export_student_report(self.students))
            elif choice == "2":
                success(r.export_room_report(self.rooms))
            elif choice == "3":
                success(r.export_fee_report(self.fees))
            elif choice == "4":
                success(r.export_attendance_report(self.attendance_records))
            elif choice == "5":
                success(r.export_complaint_report(self.complaints))
            elif choice == "6":
                success(r.export_mess_report(self.mess_records))
            elif choice == "7":
                for fn in [r.export_student_report, r.export_room_report,
                           r.export_fee_report, r.export_attendance_report,
                           r.export_complaint_report, r.export_mess_report]:
                    data_map = {
                        r.export_student_report:    self.students,
                        r.export_room_report:       self.rooms,
                        r.export_fee_report:        self.fees,
                        r.export_attendance_report: self.attendance_records,
                        r.export_complaint_report:  self.complaints,
                        r.export_mess_report:       self.mess_records,
                    }
                    success(fn(data_map[fn]))
            elif choice == "0":
                break
            else:
                warning("Invalid choice.")
            pause()

    # ══════════════════════════════════════════════════════════════════════
    #  DASHBOARD
    # ══════════════════════════════════════════════════════════════════════
    def show_dashboard(self) -> None:
        print_header("SMART HOSTEL DASHBOARD")
        total_students = len(self.students)
        total_rooms    = len(self.rooms)
        occupied_rooms = sum(1 for r in self.rooms if r.occupied_beds > 0)
        vacant_rooms   = sum(1 for r in self.rooms if r.check_availability())
        pending_comp   = sum(1 for c in self.complaints if c.complaint_status == "Open")
        collected_fees = sum(f.amount for f in self.fees if f.payment_status == "Paid")
        due_fees       = sum(f.total_due for f in self.fees if f.payment_status != "Paid")
        today_att      = sum(1 for a in self.attendance_records
                             if a.date == today_str() and a.status == "Present")

        rows = [
            ["👥 Total Students",      cyan(str(total_students))],
            ["🏠 Total Rooms",          cyan(str(total_rooms))],
            ["🔒 Occupied Rooms",       yellow(str(occupied_rooms))],
            ["🔓 Rooms with Free Beds", green(str(vacant_rooms))],
            ["⚠  Pending Complaints",  red(str(pending_comp))],
            ["💰 Collected Fees",       green(f"₹{collected_fees:,.2f}")],
            ["📅 Due/Overdue Fees",     red(f"₹{due_fees:,.2f}")],
            ["📋 Today's Attendance",   cyan(str(today_att))],
        ]
        print(_tab(rows, ["Metric", "Value"]))
        print()

    # ══════════════════════════════════════════════════════════════════════
    #  HOSTEL RULES
    # ══════════════════════════════════════════════════════════════════════
    def show_rules(self) -> None:
        print_section("HOSTEL RULES")
        for i, rule in enumerate(HOSTEL_RULES, 1):
            print(f"  {cyan(str(i))}. {rule}")
