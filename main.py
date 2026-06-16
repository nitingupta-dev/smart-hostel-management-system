"""
main.py — Entry point for the Smart Hostel Management System.
Handles the login flow and top-level menu navigation.
"""

import sys
import os

# Ensure the project root is on the Python path when run from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.file_handler import ensure_data_files
from utils.helper import (
    print_header, print_section, success, error, info, warning, pause,
    get_input, green, red, yellow, cyan, bold,
)
from hostel_management import HostelManagementSystem


# ── Startup banner ────────────────────────────────────────────────────────
BANNER = r"""
   ╔═══════════════════════════════════════════════════╗
   ║        SMART HOSTEL MANAGEMENT SYSTEM             ║
   ║          Built with Python & OOP                  ║
   ╚═══════════════════════════════════════════════════╝
"""


def show_main_menu() -> None:
    """Print the primary navigation menu."""
    print_header("MAIN MENU", width=52)
    options = [
        ("1", "Student Management"),
        ("2", "Room Management"),
        ("3", "Fee Management"),
        ("4", "Attendance Management"),
        ("5", "Visitor Management"),
        ("6", "Complaint Management"),
        ("7", "Mess Management"),
        ("8", "Report Generation"),
        ("9", "Dashboard"),
        ("10", "Hostel Rules"),
        ("11", "Save Data"),
        ("12", "Load Data"),
        ("13", "Change Password"),
        ("0", "Logout & Exit"),
    ]
    for code, label in options:
        print(f"  {cyan(code.rjust(2))}. {label}")
    print()


def run() -> None:
    """Main application loop."""
    # Ensure data directory and files exist
    ensure_data_files()

    # Create system instance and load persisted data
    system = HostelManagementSystem()
    system.load_data()

    # Show startup banner
    try:
        from colorama import Fore, Style, init
        init(autoreset=True)
        print(Fore.CYAN + BANNER + Style.RESET_ALL)
    except ImportError:
        print(BANNER)

    # ── Login loop ─────────────────────────────────────────────────────
    max_attempts = 3
    attempts     = 0
    while not system._logged_in:
        if attempts >= max_attempts:
            error("Too many failed attempts. Exiting.")
            sys.exit(1)
        logged_in = system.login()
        if not logged_in:
            attempts += 1
            remaining = max_attempts - attempts
            if remaining > 0:
                warning(f"  {remaining} attempt(s) remaining.")
        else:
            # Successful login — show dashboard
            system.show_dashboard()
            pause()

    # ── Main menu loop ─────────────────────────────────────────────────
    while True:
        try:
            show_main_menu()
            choice = get_input("Enter choice").strip()

            if choice == "1":
                system.manage_students()

            elif choice == "2":
                system.manage_rooms()

            elif choice == "3":
                system.manage_fees()

            elif choice == "4":
                system.manage_attendance()

            elif choice == "5":
                system.manage_visitors()

            elif choice == "6":
                system.manage_complaints()

            elif choice == "7":
                system.manage_mess()

            elif choice == "8":
                system.generate_reports()

            elif choice == "9":
                system.show_dashboard()
                pause()

            elif choice == "10":
                system.show_rules()
                pause()

            elif choice == "11":
                system.save_data()
                pause()

            elif choice == "12":
                system.load_data()
                pause()

            elif choice == "13":
                _change_password(system)

            elif choice == "0":
                if _confirm_exit(system):
                    break

            else:
                warning("Invalid option. Please enter a number from the menu.")
                pause()

        except KeyboardInterrupt:
            print("\n")
            if _confirm_exit(system):
                break

        except Exception as exc:
            error(f"Unexpected error: {exc}")
            pause()

    # ── Graceful exit ──────────────────────────────────────────────────
    system.logout()
    print_header("GOODBYE", width=40)
    info("Thank you for using Smart Hostel Management System.")
    print()


def _confirm_exit(system: HostelManagementSystem) -> bool:
    """Ask whether to save before exiting."""
    print_section("EXIT")
    from utils.helper import confirm
    if confirm("Save data before exiting? (y/n)"):
        system.save_data()
    return confirm("Are you sure you want to exit? (y/n)")


def _change_password(system: HostelManagementSystem) -> None:
    """Allow the warden to change their password."""
    print_section("CHANGE PASSWORD")
    old  = get_input("Current Password")
    new  = get_input("New Password (min 6 chars)")
    conf = get_input("Confirm New Password")
    if new != conf:
        error("Passwords do not match.")
    else:
        msg = system._warden.change_password(old, new)
        if "successfully" in msg:
            success(msg)
        else:
            error(msg)
    pause()


# ── Module guard ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    run()
