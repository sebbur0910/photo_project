import sqlite3
from PIL import Image

filename = "C:/Users/sebbur0910/OneDrive - Highgate School/School/Year 12/paging.jpeg"

with Image.open(filename) as img:
    img.load()
    img.save("paging.jpeg")
 #   img.show()

with open(filename, 'rb') as file:
    blobData = file.read()
print(blobData)

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

def insertBLOB(empId, name, photo):
    try:
        sqliteConnection = sqlite3.connect('SQLite_Python.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")
        sqlite_insert_blob_query = """ INSERT INTO employees
                                  (id, name, photo) VALUES (?, ?, ?)"""

        empPhoto = convertToBinaryData(photo)
        # Convert data into tuple format
        data_tuple = (empId, name, empPhoto)
        cursor.execute(sqlite_insert_blob_query, data_tuple)
        sqliteConnection.commit()
        print("Image and file inserted successfully as a BLOB into a table")
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert blob data into sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("the sqlite connection is closed")