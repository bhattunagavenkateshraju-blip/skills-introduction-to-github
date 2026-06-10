import os
import tkinter as tk
import logging
from tkinter import messagebox, ttk

import mysql.connector
from mysql.connector import Error, IntegrityError, InterfaceError, OperationalError

logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger(__name__)


class StudentManagementSystem:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("1050x620")
        self.root.resizable(False, False)

        self.db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", "student_management"),
            "port": int(os.getenv("DB_PORT", "3306")),
        }

        self.student_vars = {
            "student_id": tk.StringVar(),
            "name": tk.StringVar(),
            "age": tk.StringVar(),
            "gender": tk.StringVar(),
            "course": tk.StringVar(),
            "email": tk.StringVar(),
            "phone": tk.StringVar(),
            "address": tk.StringVar(),
        }
        self.field_order = [
            "student_id",
            "name",
            "age",
            "gender",
            "course",
            "email",
            "phone",
            "address",
        ]
        self.search_var = tk.StringVar()

        self._build_ui()
        self.ensure_table_exists()
        self.load_students()

    def get_connection(self):
        return mysql.connector.connect(**self.db_config)

    def ensure_table_exists(self):
        query = """
        CREATE TABLE IF NOT EXISTS students (
            student_id VARCHAR(20) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            age INT NOT NULL,
            gender VARCHAR(20) NOT NULL,
            course VARCHAR(120) NOT NULL,
            email VARCHAR(100),
            phone VARCHAR(20),
            address VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.execute_query(query)

    def execute_query(self, query: str, params=None, fetch: bool = False):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            conn.commit()
            return True
        except (InterfaceError, OperationalError):
            messagebox.showerror(
                "Database Error",
                "Unable to connect to the database server. Please verify credentials and server status.",
            )
            return None if fetch else False
        except IntegrityError as exc:
            if "Duplicate entry" in str(exc):
                messagebox.showerror("Database Error", "Student ID already exists.")
            else:
                messagebox.showerror("Database Error", "Duplicate or invalid record data was provided.")
            return None if fetch else False
        except Error as exc:
            LOGGER.exception("Database operation failed: %s", exc)
            messagebox.showerror("Database Error", "Database operation failed. Please try again.")
            return None if fetch else False
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def _build_ui(self):
        title = tk.Label(
            self.root,
            text="Student Management System",
            font=("Arial", 20, "bold"),
            bg="#0f4c81",
            fg="white",
            pady=10,
        )
        title.pack(fill="x")

        form_frame = tk.LabelFrame(self.root, text="Student Details", padx=10, pady=10)
        form_frame.place(x=15, y=70, width=350, height=535)

        fields = [
            ("Student ID", "student_id"),
            ("Name", "name"),
            ("Age", "age"),
            ("Gender", "gender"),
            ("Course", "course"),
            ("Email", "email"),
            ("Phone", "phone"),
            ("Address", "address"),
        ]

        for idx, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label, anchor="w", width=12).grid(
                row=idx, column=0, sticky="w", pady=6
            )
            if key == "gender":
                field = ttk.Combobox(
                    form_frame,
                    textvariable=self.student_vars[key],
                    values=["Male", "Female", "Other"],
                    state="readonly",
                    width=23,
                )
            else:
                field = tk.Entry(form_frame, textvariable=self.student_vars[key], width=26)
            field.grid(row=idx, column=1, pady=6)

        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=15)

        buttons = [
            ("Add", self.add_student),
            ("Update", self.update_student),
            ("Delete", self.delete_student),
            ("Clear", self.clear_fields),
        ]

        for idx, (label, action) in enumerate(buttons):
            tk.Button(
                button_frame,
                text=label,
                command=action,
                width=12,
                bg="#0f4c81",
                fg="white",
            ).grid(row=idx // 2, column=idx % 2, padx=5, pady=5)

        right_frame = tk.LabelFrame(self.root, text="Student Records", padx=10, pady=10)
        right_frame.place(x=380, y=70, width=655, height=535)

        tk.Label(right_frame, text="Search by ID or Name:").grid(row=0, column=0, sticky="w")
        tk.Entry(right_frame, textvariable=self.search_var, width=35).grid(
            row=0, column=1, padx=6, sticky="w"
        )
        tk.Button(
            right_frame,
            text="Search",
            command=self.search_students,
            bg="#0f4c81",
            fg="white",
            width=12,
        ).grid(row=0, column=2, padx=6)
        tk.Button(
            right_frame,
            text="Reset",
            command=self.load_students,
            bg="#6c757d",
            fg="white",
            width=12,
        ).grid(row=0, column=3, padx=6)

        columns = ("student_id", "name", "age", "gender", "course", "email", "phone", "address")
        self.student_table = ttk.Treeview(right_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.student_table.heading(col, text=col.replace("_", " ").title())

        self.student_table.column("student_id", width=90, anchor="center")
        self.student_table.column("name", width=120)
        self.student_table.column("age", width=50, anchor="center")
        self.student_table.column("gender", width=80, anchor="center")
        self.student_table.column("course", width=120)
        self.student_table.column("email", width=140)
        self.student_table.column("phone", width=100)
        self.student_table.column("address", width=150)

        y_scroll = ttk.Scrollbar(right_frame, orient="vertical", command=self.student_table.yview)
        self.student_table.configure(yscrollcommand=y_scroll.set)

        self.student_table.grid(row=1, column=0, columnspan=4, pady=10, sticky="nsew")
        y_scroll.grid(row=1, column=4, sticky="ns", pady=10)

        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(1, weight=1)

        self.student_table.bind("<<TreeviewSelect>>", self.on_row_select)

    def validate_fields(self):
        required = ["student_id", "name", "age", "gender", "course"]
        for key in required:
            if not self.student_vars[key].get().strip():
                messagebox.showwarning("Validation Error", f"{key.replace('_', ' ').title()} is required.")
                return False

        age_value = self.student_vars["age"].get().strip()
        if not age_value.isdigit():
            messagebox.showwarning("Validation Error", "Age must be a positive number.")
            return False

        age_number = int(age_value)
        if age_number <= 0 or age_number > 150:
            messagebox.showwarning("Validation Error", "Age must be between 1 and 150.")
            return False

        return True

    def add_student(self):
        if not self.validate_fields():
            return

        query = """
            INSERT INTO students (student_id, name, age, gender, course, email, phone, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = tuple(self.student_vars[key].get().strip() for key in self.field_order)
        success = self.execute_query(query, params)
        if not success:
            return
        self.load_students()
        self.clear_fields()
        messagebox.showinfo("Success", "Student added successfully.")

    def update_student(self):
        if not self.validate_fields():
            return

        query = """
            UPDATE students
            SET name=%s, age=%s, gender=%s, course=%s, email=%s, phone=%s, address=%s
            WHERE student_id=%s
        """
        params = (
            self.student_vars["name"].get().strip(),
            self.student_vars["age"].get().strip(),
            self.student_vars["gender"].get().strip(),
            self.student_vars["course"].get().strip(),
            self.student_vars["email"].get().strip(),
            self.student_vars["phone"].get().strip(),
            self.student_vars["address"].get().strip(),
            self.student_vars["student_id"].get().strip(),
        )
        success = self.execute_query(query, params)
        if not success:
            return
        self.load_students()
        messagebox.showinfo("Success", "Student updated successfully.")

    def delete_student(self):
        student_id = self.student_vars["student_id"].get().strip()
        if not student_id:
            messagebox.showwarning("Validation Error", "Select or enter a Student ID to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
        if not confirm:
            return

        success = self.execute_query("DELETE FROM students WHERE student_id=%s", (student_id,))
        if not success:
            return
        self.load_students()
        self.clear_fields()
        messagebox.showinfo("Success", "Student deleted successfully.")

    def load_students(self):
        rows = self.execute_query(
            "SELECT student_id, name, age, gender, course, email, phone, address FROM students ORDER BY created_at DESC LIMIT 500",
            fetch=True,
        )
        if rows is None:
            return
        self.populate_table(rows)

    def search_students(self):
        text = self.search_var.get().strip()
        if not text:
            self.load_students()
            return

        rows = self.execute_query(
            """
            SELECT student_id, name, age, gender, course, email, phone, address
            FROM students
            WHERE student_id LIKE %s OR name LIKE %s
            ORDER BY created_at DESC
            LIMIT 500
            """,
            (f"%{text}%", f"%{text}%"),
            fetch=True,
        )
        if rows is None:
            return
        self.populate_table(rows)

    def populate_table(self, rows):
        self.student_table.delete(*self.student_table.get_children())
        for row in rows:
            self.student_table.insert("", "end", values=tuple(row[col] for col in row))

    def clear_fields(self):
        for var in self.student_vars.values():
            var.set("")
        self.search_var.set("")

    def on_row_select(self, _event):
        selected = self.student_table.focus()
        if not selected:
            return

        values = self.student_table.item(selected, "values")
        if not values:
            return

        for idx, key in enumerate(self.field_order):
            self.student_vars[key].set(values[idx])


def main():
    root = tk.Tk()
    StudentManagementSystem(root)
    root.mainloop()


if __name__ == "__main__":
    main()
