import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json, os
from datetime import datetime

FILE = "students.json"

# ---------------- FILE SETUP ---------------- #
if not os.path.exists(FILE):
    with open(FILE, "w") as f:
        json.dump([], f)

def load_data():
    with open(FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------------- FUNCTIONS ---------------- #
def add_student():
    if not name_var.get() or not age_var.get() or not course_var.get():
        messagebox.showerror("Error", "All fields required!")
        return

    if not age_var.get().isdigit():
        messagebox.showerror("Error", "Age must be number!")
        return

    data = load_data()
    new_id = 1 if not data else data[-1]["id"] + 1

    data.append({
        "id": new_id,
        "name": name_var.get(),
        "age": age_var.get(),
        "course": course_var.get(),
        "attendance": {}
    })

    save_data(data)
    clear_fields()
    display_students()
    update_dashboard()

def display_students():
    for row in tree.get_children():
        tree.delete(row)

    for s in load_data():
        attendance = s.get("attendance", {})
        total = len(attendance)
        present = sum(1 for v in attendance.values() if v == "Present")
        percent = round((present / total * 100), 1) if total else 0

        tree.insert("", tk.END, values=(
            s["id"], s["name"], s["age"], s["course"], f"{percent}%"
        ))

def update_student():
    selected = tree.focus()
    values = tree.item(selected, "values")
    if not values:
        return

    data = load_data()
    for s in data:
        if s["id"] == int(values[0]):
            s["name"] = name_var.get()
            s["age"] = age_var.get()
            s["course"] = course_var.get()

    save_data(data)
    display_students()
    update_dashboard()
    clear_fields()

def delete_student():
    selected = tree.focus()
    values = tree.item(selected, "values")
    if not values:
        return

    data = [s for s in load_data() if s["id"] != int(values[0])]
    save_data(data)

    display_students()
    update_dashboard()
    clear_fields()

def mark_attendance(status):
    selected = tree.focus()
    values = tree.item(selected, "values")

    if not values:
        messagebox.showerror("Error", "Select student first!")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    data = load_data()

    for s in data:
        if s["id"] == int(values[0]):
            s.setdefault("attendance", {})
            s["attendance"][today] = status

    save_data(data)
    display_students()

def monthly_report():
    selected = tree.focus()
    values = tree.item(selected, "values")

    if not values:
        messagebox.showerror("Error", "Select student first!")
        return

    month = simpledialog.askstring("Monthly Report", "Enter month (YYYY-MM):")
    if not month:
        return

    win = tk.Toplevel(root)
    win.title("Monthly Report")
    win.geometry("400x400")

    text = tk.Text(win)
    text.pack(fill=tk.BOTH, expand=True)

    for s in load_data():
        if s["id"] == int(values[0]):
            attendance = s.get("attendance", {})
            present = absent = 0

            text.insert(tk.END, f"Name: {s['name']}\nMonth: {month}\n\n")

            for date, status in attendance.items():
                if date.startswith(month):
                    text.insert(tk.END, f"{date} → {status}\n")
                    if status == "Present":
                        present += 1
                    else:
                        absent += 1

            total = present + absent
            percent = round((present / total * 100), 1) if total else 0

            text.insert(tk.END, "\n-----------------\n")
            text.insert(tk.END, f"Present: {present}\nAbsent: {absent}\n")
            text.insert(tk.END, f"Attendance %: {percent}%\n")

def update_dashboard():
    data = load_data()

    total_students = len(data)

    courses = set(s.get("course", "").strip().lower() for s in data if s.get("course"))
    total_courses = len(courses)

    student_count.config(text=str(total_students))
    course_count.config(text=str(total_courses))

def select_student(event):
    values = tree.item(tree.focus(), "values")
    if values:
        name_var.set(values[1])
        age_var.set(values[2])
        course_var.set(values[3])

def clear_fields():
    name_var.set("")
    age_var.set("")
    course_var.set("")

# ---------------- UI ---------------- #
root = tk.Tk()
root.title("Student Management System - Card UI")
root.geometry("1000x550")
root.configure(bg="#f5f7fa")

# ---------- DASHBOARD CARDS ---------- #
top = tk.Frame(root, bg="#f5f7fa")
top.pack(fill=tk.X, pady=10)

# STUDENT CARD
card1 = tk.Frame(top, bg="#4CAF50", bd=0, relief="flat")
card1.pack(side=tk.LEFT, padx=20, ipadx=20, ipady=10)

tk.Label(card1, text="Students", bg="#4CAF50", fg="white",
         font=("Arial", 12)).pack()

student_count = tk.Label(card1, text="0", bg="#4CAF50", fg="white",
                         font=("Arial", 20, "bold"))
student_count.pack()

# COURSE CARD
card2 = tk.Frame(top, bg="#2196F3", bd=0, relief="flat")
card2.pack(side=tk.LEFT, padx=20, ipadx=20, ipady=10)

tk.Label(card2, text="Courses", bg="#2196F3", fg="white",
         font=("Arial", 12)).pack()

course_count = tk.Label(card2, text="0", bg="#2196F3", fg="white",
                        font=("Arial", 20, "bold"))
course_count.pack()

# ---------- MAIN ---------- #
main = ttk.Frame(root)
main.pack(fill=tk.BOTH, expand=True)

# FORM
form = ttk.Frame(main)
form.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

name_var = tk.StringVar()
age_var = tk.StringVar()
course_var = tk.StringVar()

ttk.Label(form, text="Name").grid(row=0, column=0)
ttk.Entry(form, textvariable=name_var).grid(row=0, column=1)

ttk.Label(form, text="Age").grid(row=1, column=0)
ttk.Entry(form, textvariable=age_var).grid(row=1, column=1)

ttk.Label(form, text="Course").grid(row=2, column=0)
ttk.Entry(form, textvariable=course_var).grid(row=2, column=1)

ttk.Button(form, text="Add", command=add_student).grid(row=3, column=0)
ttk.Button(form, text="Update", command=update_student).grid(row=3, column=1)

ttk.Button(form, text="Delete", command=delete_student).grid(row=4, column=0)
ttk.Button(form, text="Clear", command=clear_fields).grid(row=4, column=1)

ttk.Button(form, text="Mark Present", command=lambda: mark_attendance("Present")).grid(row=5, column=0)
ttk.Button(form, text="Mark Absent", command=lambda: mark_attendance("Absent")).grid(row=5, column=1)

ttk.Button(form, text="Monthly Report", command=monthly_report).grid(row=6, column=0, columnspan=2)

# TABLE
table_frame = ttk.Frame(main)
table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

columns = ("ID", "Name", "Age", "Course", "Attendance %")
tree = ttk.Treeview(table_frame, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center")

tree.pack(fill=tk.BOTH, expand=True)
tree.bind("<<TreeviewSelect>>", select_student)

scroll = ttk.Scrollbar(table_frame, command=tree.yview)
tree.configure(yscroll=scroll.set)
scroll.pack(side=tk.RIGHT, fill=tk.Y)

# INIT
display_students()
update_dashboard()

root.mainloop()