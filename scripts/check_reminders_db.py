import sqlite3
from api.csv_handler import DB_PATH

def print_reminders():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title, is_completed, reminder_time FROM reminders")
    rows = c.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Title: {row[1]}, Completed: {row[2]}, Time: {row[3]}")
    conn.close()

if __name__ == "__main__":
    print_reminders()
