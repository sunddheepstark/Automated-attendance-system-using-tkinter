import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv, glob
from collections import defaultdict

students = {}
with open("D:\\students.csv", "r") as file:
    for line in file:
        sid, name = line.strip().split(",")
        students[sid] = name

attendance = {sid: None for sid in students}

def save_attendance_to_file():
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"D:\\attendance_{date_str}.csv"
    with open(filename, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ID", "Name", "Status", "Timestamp"])
        if f.tell() == 0:
            writer.writeheader()
        for sid, status in attendance.items():
            writer.writerow({
                "ID": sid,
                "Name": students[sid],
                "Status": status,
                "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

def show_summary_popup():
    popup = tk.Toplevel(root)
    popup.title("Attendance Summary")
    popup.geometry("400x400")
    popup.configure(bg="#f0f2f5")

    summary_label = ttk.Label(popup, text="📋 Attendance Summary", font=("Segoe UI", 14, "bold"))
    summary_label.pack(pady=10)

    summary_box = tk.Text(popup, height=20, width=45, font=("Courier", 10))
    summary_box.pack(pady=5)

    present_count = sum(1 for s in attendance.values() if s == "Present")
    total_count = len(attendance)
    absent_count = total_count - present_count

    present_percentage = (present_count / total_count) * 100
    absent_percentage = (absent_count / total_count) * 100

    for sid, name in students.items():
        status = attendance[sid] if attendance[sid] else "Absent"
        summary_box.insert(tk.END, f"{sid} - {name}: {status}\n")

    summary_box.insert(tk.END, f"\n✅ Present: {present_count}/{total_count} ({present_percentage:.2f}%)\n")
    summary_box.insert(tk.END, f"❌ Absent: {absent_count}/{total_count} ({absent_percentage:.2f}%)\n")

    summary_box.config(state=tk.DISABLED)

def show_absentees_popup():
    popup = tk.Toplevel(root)
    popup.title("Absentees Summary")
    popup.geometry("400x400")
    popup.configure(bg="#f0f2f5")

    absent_count = sum(1 for s in attendance.values() if s == "Absent")
    total_count = len(attendance)
    absent_percentage = (absent_count / total_count) * 100

    label = ttk.Label(popup, text=f"❌ Absentees ({absent_percentage:.2f}%)", font=("Segoe UI", 14, "bold"))
    label.pack(pady=10)

    box = tk.Text(popup, height=20, width=45, font=("Courier", 10))
    box.pack(pady=5)

    absentees = [f"{sid} - {students[sid]}" for sid, status in attendance.items() if status == "Absent"]
    if absentees:
        for entry in absentees:
            box.insert(tk.END, entry + "\n")
    else:
        box.insert(tk.END, "🎉 No absentees!")

    box.config(state=tk.DISABLED)

def show_overall_percentage():
    records = defaultdict(lambda: {"present": 0, "total": 0})
    
    for file in glob.glob("D:\\attendance_*.csv"):
        with open(file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sid = row["ID"]
                status = row["Status"]
                if sid in students:
                    records[sid]["total"] += 1
                    if status == "Present":
                        records[sid]["present"] += 1

    popup = tk.Toplevel(root)
    popup.title("📈 Overall Attendance Percentage")
    popup.geometry("420x450")
    popup.configure(bg="#f0f2f5")

    label = ttk.Label(popup, text="📊 Overall Attendance Summary", font=("Segoe UI", 14, "bold"))
    label.pack(pady=10)

    box = tk.Text(popup, height=20, width=50, font=("Courier", 10))
    box.pack(pady=5)

    if not records:
        box.insert(tk.END, "No attendance records found.\n")
    else:
        for sid, data in records.items():
            percentage = (data["present"] / data["total"]) * 100 if data["total"] > 0 else 0
            box.insert(tk.END, f"{sid} - {students[sid]}: {percentage:.2f}% ({data['present']}/{data['total']})\n")

    box.config(state=tk.DISABLED)

def mark_attendance():
    sid = entry.get().strip()

    if sid.lower() == "done":
        absentees = []
        for sid in attendance:
            if attendance[sid] is None:
                attendance[sid] = "Absent"
                absentees.append(f"{sid} - {students[sid]}")
        status_label.config(text="✅ Attendance finalized.", foreground="green")
        log_box.insert(tk.END, "\n--- Absentees ---\n")
        for entry_text in absentees:
            log_box.insert(tk.END, entry_text + "\n")
        log_box.see(tk.END)
        save_attendance_to_file()
        show_summary_popup()
        entry.delete(0, tk.END)
        return

    if sid.lower() == "exit":
        root.destroy()
        return

    if sid in students:
        if attendance[sid] == "Present":
            status_label.config(text=f"⚠️ {students[sid]} is already marked present.", foreground="orange")
        else:
            attendance[sid] = "Present"
            timestamp = datetime.now().strftime('%H:%M:%S')
            date = datetime.now().strftime('%Y-%m-%d')
            status_label.config(text=f"✅ Marked {students[sid]} at {timestamp}", foreground="green")
            log_box.insert(tk.END, f"{date} | {sid} - {students[sid]}: Present at {timestamp}\n")
            log_box.see(tk.END)
    else:
        status_label.config(text="❌ Invalid ID.", foreground="red")

    entry.delete(0, tk.END)

def mark_absent():
    sid = entry.get().strip()
    if sid in students:
        attendance[sid] = "Absent"
        timestamp = datetime.now().strftime('%H:%M:%S')
        date = datetime.now().strftime('%Y-%m-%d')
        status_label.config(text=f"❌ Marked {students[sid]} as Absent at {timestamp}", foreground="red")
        log_box.insert(tk.END, f"{date} | {sid} - {students[sid]}: Absent at {timestamp}\n")
        log_box.see(tk.END)
    else:
        status_label.config(text="❌ Invalid ID.", foreground="red")
    entry.delete(0, tk.END)

def mark_all_present():
    for sid in students:
        attendance[sid] = "Present"
    timestamp = datetime.now().strftime('%H:%M:%S')
    date = datetime.now().strftime('%Y-%m-%d')
    log_box.insert(tk.END, f"{date} | All students marked Present at {timestamp}\n")
    log_box.see(tk.END)
    status_label.config(text="✅ All students marked Present", foreground="green")

def reset_attendance():
    for sid in attendance:
        attendance[sid] = None
    log_box.delete(1.0, tk.END)
    status_label.config(text="🔄 Attendance reset.", foreground="blue")

root = tk.Tk()
root.title("🎓 Attendance App")
root.geometry("650x700")
root.configure(bg="#f0f2f5")
root.eval('tk::PlaceWindow . center')

style = ttk.Style()
style.configure("TButton", font=("Segoe UI", 11), padding=6)
style.configure("TLabel", font=("Segoe UI", 11))
style.configure("TEntry", font=("Segoe UI", 12))

main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

header = ttk.Label(main_frame, text="🎓 Attendance Tracker", font=("Segoe UI", 16, "bold"))
header.pack(pady=10)

entry = ttk.Entry(main_frame, font=("Segoe UI", 12))
entry.pack(pady=10)
entry.insert(0, "Enter Student ID")
entry.bind("<Return>", lambda event: mark_attendance())

mark_button = ttk.Button(main_frame, text="Mark Present", command=mark_attendance)
mark_button.pack(pady=5)

absent_button = ttk.Button(main_frame, text="Mark Absent", command=mark_absent)
absent_button.pack(pady=5)

all_present_button = ttk.Button(main_frame, text="Mark All Present", command=mark_all_present)
all_present_button.pack(pady=5)

reset_button = ttk.Button(main_frame, text="Reset Attendance", command=reset_attendance)
reset_button.pack(pady=5)

absentees_button = ttk.Button(main_frame, text="Show Absentees", command=show_absentees_popup)
absentees_button.pack(pady=5)

overall_button = ttk.Button(main_frame, text="Show Overall %", command=show_overall_percentage)
overall_button.pack(pady=5)

status_label = ttk.Label(main_frame, text="", font=("Segoe UI", 11))
status_label.pack(pady=10)

log_frame = ttk.Frame(main_frame)
log_frame.pack(pady=10, fill=tk.BOTH, expand=True)

log_box = tk.Text(log_frame, height=20, width=70, font=("Courier", 11))
log_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(log_frame, command=log_box.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_box.config(yscrollcommand=scrollbar.set)

root.mainloop()
