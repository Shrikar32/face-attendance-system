import tkinter as tk
from tkinter import messagebox
import sqlite3
import pandas as pd
import os
import sys  # <-- Added sys

def run_register():
    # Forces the use of the .venv Python and keeps the console open (/k)
    os.system(f'start cmd /k "{sys.executable}" app/register.py')

def run_attendance():
    # Forces the use of the .venv Python and keeps the console open (/k)
    os.system(f'start cmd /k "{sys.executable}" app/recognize.py')

def view_attendance():
# ... (Keep the rest of your file exactly the same below this)
    conn = sqlite3.connect("data/attendance.db")
    df = pd.read_sql_query("""
        SELECT a.date, a.time, s.roll_number, s.name, a.status 
        FROM attendance a 
        JOIN students s ON a.student_id = s.id
    """, conn)
    conn.close()
    
    top = tk.Toplevel()
    top.title("Attendance Records")
    text = tk.Text(top, width=70, height=15, font=("Courier", 10))
    text.pack(padx=10, pady=10)
    
    if df.empty:
        text.insert(tk.END, "No attendance records found.")
    else:
        text.insert(tk.END, df.to_string(index=False))
    text.config(state=tk.DISABLED)

def export_csv():
    conn = sqlite3.connect("data/attendance.db")
    df = pd.read_sql_query("""
        SELECT a.date, a.time, s.roll_number, s.name, a.status 
        FROM attendance a 
        JOIN students s ON a.student_id = s.id
    """, conn)
    conn.close()
    
    if df.empty:
        messagebox.showinfo("Export", "No attendance records found.")
        return
        
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/attendance_export.csv", index=False)
    messagebox.showinfo("Export", "Successfully exported to data/attendance_export.csv!")

def create_gui():
    root = tk.Tk()
    root.title("Facial Attendance System")
    root.geometry("450x450")
    
    tk.Label(root, text="=================================", font=("Courier", 12)).pack(pady=10)
    tk.Label(root, text="FACIAL ATTENDANCE SYSTEM", font=("Courier", 16, "bold")).pack()
    tk.Label(root, text="=================================", font=("Courier", 12)).pack(pady=10)
    
    tk.Button(root, text="[ REGISTER STUDENT ]", width=30, height=2, command=run_register).pack(pady=8)
    tk.Button(root, text="[ START ATTENDANCE ]", width=30, height=2, command=run_attendance).pack(pady=8)
    tk.Button(root, text="[ VIEW ATTENDANCE ]", width=30, height=2, command=view_attendance).pack(pady=8)
    tk.Button(root, text="[ EXPORT CSV ]", width=30, height=2, command=export_csv).pack(pady=8)
    tk.Button(root, text="[ EXIT ]", width=30, height=2, command=root.quit).pack(pady=8)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()