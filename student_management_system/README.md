# Student Management System (Python + Tkinter + MySQL)

A desktop Student Management System with Tkinter GUI and MySQL backend.

## Features
- Add student records
- Update existing student records
- Delete student records
- Search students by ID or name
- View all student records in a table

## Tech Stack
- Python 3
- Tkinter
- MySQL
- mysql-connector-python

## Project Files
- `/home/runner/work/skills-introduction-to-github/skills-introduction-to-github/bhattunagavenkateshraju-blip/skills-introduction-to-github/student_management_system/app.py`
- `/home/runner/work/skills-introduction-to-github/skills-introduction-to-github/bhattunagavenkateshraju-blip/skills-introduction-to-github/student_management_system/db_schema.sql`
- `/home/runner/work/skills-introduction-to-github/skills-introduction-to-github/bhattunagavenkateshraju-blip/skills-introduction-to-github/student_management_system/requirements.txt`

## Setup
1. Install MySQL and create/update credentials.
2. Run schema:
   ```sql
   SOURCE db_schema.sql;
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure DB connection environment variables (optional):
   - `DB_HOST` (default: `localhost`)
   - `DB_PORT` (default: `3306`)
   - `DB_USER` (default: `root`)
   - `DB_PASSWORD` (default: empty)
   - `DB_NAME` (default: `student_management`)

## Run
```bash
python app.py
```

## Notes
- Ensure MySQL server is running before launching the application.
- Table is auto-created by the app if it does not exist.
