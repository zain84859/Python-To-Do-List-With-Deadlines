import sqlite3
from constants import DB_NAME  # imports the database name
from datetime import datetime
from plyer import notification

def init_database():
    # this sets up the database and makes sure tables and columns exist

    conn = sqlite3.connect(DB_NAME)  # connects to the sqlite database file
    c = conn.cursor()  # creates a cursor to run sql commands

    # creates the users table if it doesn't exist already
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL)
              """)

    # creates the tasks table if it doesn't exist already
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            time TEXT,
            difficulty TEXT,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id))
              """)

    # creates the revision_tasks table for spaced revision sessions
    c.execute("""
        CREATE TABLE IF NOT EXISTS revision_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task_id INTEGER,
            original_date TEXT NOT NULL,
            revision_date TEXT NOT NULL,
            description TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            method TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id))
              """)

    # this checks if revision_tasks is missing new columns, and adds them (so we don't wipe the db)
    c.execute("PRAGMA table_info(revision_tasks)")  # gets the columns in revision_tasks
    rev_cols = [row[1] for row in c.fetchall()]  # pulls out the column names

    if "task_id" not in rev_cols:  # checks if task_id is missing
        c.execute("ALTER TABLE revision_tasks ADD COLUMN task_id INTEGER")  # adds task_id column

    if "method" not in rev_cols:  # checks if method is missing
        c.execute("ALTER TABLE revision_tasks ADD COLUMN method TEXT")  # adds method column

    conn.commit()  # saves the changes to the database
    conn.close()  # closes the database connection

def load_tasks_from_db(user_id):
    # this gets all tasks for one user and puts them into a dictionary for the calendar

        conn = sqlite3.connect(DB_NAME)  # opens a connection to the database file
        c = conn.cursor()  # gets a cursor so we can run SQL commands

     # gets every row from the tasks table for this user
        c.execute("SELECT id, date, description, time, difficulty, completed FROM tasks WHERE user_id = ?", (user_id,))
        rows = c.fetchall()  # fetches all rows into a list

        conn.close()  # closes the connection to the database

        tasks = {}  # this will look like: { "YYYY-MM-DD": [ {"id":.., "desc":.., "time":.., "diff":..}, ... ] }

        for tid, date, desc, time_val, diff, completed in rows:  # loops through each task row
            if date not in tasks:  # if this date isn't in the dictionary yet
                tasks[date] = []  # make a new empty list for this date
                # adds this task to the list for that date
            tasks[date].append({"id": tid, "desc": desc, "time": time_val, "diff": diff, "completed": bool(completed)})

        return tasks  # returns the whole tasks dictionary back to the calendar


def load_revision_tasks_from_db(user_id):
    # loads all revision sessions for one user into a dictionary

    conn = sqlite3.connect(DB_NAME)  # opens db
    c = conn.cursor()  # gets cursor

    c.execute("SELECT revision_date, description, difficulty, method FROM revision_tasks WHERE user_id = ?",(user_id,))
    rows = c.fetchall()  # gets all revision rows
    conn.close()  # closes db

    rev = {}  # {"YYYY-MM-DD": [{"revision_date":..., "desc":..., "diff":..., "method":...}, ...]}

    for date, desc, diff, method in rows:  # loops through each revision row
        if date not in rev:  # if this date not added yet
            rev[date] = []  # make new list
            # add this revision session
        rev[date].append({"revision_date": date, "desc": desc, "diff": diff, "method": method}) 

    return rev  # returns dictionary of revision sessions


def save_task_to_db(user_id, date_str, desc, time_str, diff):
    # this saves a single task into the database and returns its new id

    conn = sqlite3.connect(DB_NAME)  # opens a connection to the database
    c = conn.cursor()  # cursor for executing SQL

    # inserts the new task into the tasks table
    c.execute("INSERT INTO tasks (user_id, date, description, time, difficulty) VALUES (?, ?, ?, ?, ?)", (user_id, date_str, desc, time_str, diff))

    new_task_id = c.lastrowid  # gets the id that SQLite gave to this new row

    conn.commit()  # saves the changes
    conn.close()  # closes the database connection

    return new_task_id  # returns the new task id so we can store it in memory too


def update_task_in_db(task_id, desc, time_str, diff, completed):
    # this updates an existing task row in the database

    conn = sqlite3.connect(DB_NAME)  # opens database connection
    c = conn.cursor()  # gets cursor

    # updates the description, time, difficulty and completed flag for this task id
    c.execute("UPDATE tasks SET description = ?, time = ?, difficulty = ?, completed = ? WHERE id = ?", (desc, time_str, diff, int(completed), task_id))

    conn.commit()  # saves changes to the file
    conn.close()  # closes the connection


def delete_task_from_db(task_id):
    # this deletes a task from the database using its id

    conn = sqlite3.connect(DB_NAME)  # connects to database
    c = conn.cursor()  # gets cursor

    # deletes the row with this id
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    conn.commit()  # saves the change
    conn.close()  # closes connection

def delete_revision_for_task(task_id):
    # this deletes all revision sessions linked to a specific task

    conn = sqlite3.connect(DB_NAME)  # opens database connection
    c = conn.cursor()  # gets cursor

    # deletes all revision rows linked to this task
    c.execute(
        "DELETE FROM revision_tasks WHERE task_id = ?",
        (task_id,)
    )

    conn.commit()  # saves changes
    conn.close()  # closes database connection

def check_task_notifications(user_id, already_notified):
    # this checks upcoming task deadlines and sends multiple reminders

    now = datetime.now()  # gets current date and time
    now_minutes = now.hour * 60 + now.minute  # converts current time to minutes

    conn = sqlite3.connect(DB_NAME)  # opens database
    c = conn.cursor()  # gets cursor

    # gets all uncompleted tasks with a time
    c.execute(
        "SELECT id, date, description, time FROM tasks "
        "WHERE user_id = ? AND completed = 0 AND time IS NOT NULL",
        (user_id,)
    )
    rows = c.fetchall()  # fetches results
    conn.close()  # closes database

    for task_id, date_str, desc, time_str in rows:
        try:
            task_date = datetime.strptime(date_str, "%Y-%m-%d").date()  # converts task date
            hh, mm = map(int, time_str.split(":"))  # splits HH:MM
        except:
            continue  # skips invalid data

        task_time_minutes = hh * 60 + mm  # converts task time to minutes
        today = now.date()  # gets today's date

        # calculate how many days until task
        days_until = (task_date - today).days

        # calculate minutes difference only if today
        if days_until == 0:
            diff_minutes = task_time_minutes - now_minutes
        else:
            diff_minutes = None

        # ---- 1 DAY BEFORE ----
        if days_until == 1:
            key = (task_id, "1_day")
            if key not in already_notified:
                notification.notify(title="Task Reminder (Tomorrow)", message=f"{desc} is due tomorrow at {time_str}", timeout=10)
                already_notified.add(key)

        # ---- 1 HOUR BEFORE ----
        if days_until == 0 and diff_minutes is not None:
            if 55 <= diff_minutes <= 65:
                key = (task_id, "1_hour")
                if key not in already_notified:
                    notification.notify(title="Task Reminder (1 Hour)", message=f"{desc} is due in 1 hour at {time_str}", timeout=10)
                    already_notified.add(key)

        # ---- 5 MINUTES BEFORE ----
        if days_until == 0 and diff_minutes is not None:
            if 0 <= diff_minutes <= 5:
                key = (task_id, "5_min")
                if key not in already_notified:
                    notification.notify(title="Task Reminder (Soon)", message=f"{desc} is due at {time_str}", timeout=10)
                    already_notified.add(key)
