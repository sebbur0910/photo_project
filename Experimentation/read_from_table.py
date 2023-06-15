import io
import sqlite3
from PIL import Image

conn = sqlite3.connect("SQLite_Python.db")

cursor = conn.cursor()

select_photos = """
SELECT photo
FROM employees
"""

photo = cursor.execute(select_photos).fetchone()[0]
print(photo)
conn.close()


with Image.open(io.BytesIO(photo)) as img:
    img.load()
    img.show()