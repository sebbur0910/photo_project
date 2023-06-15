import sqlite3

create_employees_table = """
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name VARCHAR(30),
    photo BLOB
)
"""

conn = sqlite3.connect("SQLite_Python.db")
cursor = conn.cursor()
cursor.execute(create_employees_table)