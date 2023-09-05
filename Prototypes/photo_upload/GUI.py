import PIL.Image
import io
import tkinter as tk
from tkinter.filedialog import askopenfile
import sqlite3
import binascii


class UploadScreen(tk.Tk):

#Sets up the button to be pressed to upload a file
    def __init__(self):
        super().__init__()

        self.button = tk.Button(
            self,
            text='Choose File',
            command=self.open_file)
        self.button.pack()

#The button calls this command, which grabs the file then saves it to the database
    def open_file(self):
        file_path = askopenfile(mode='r',
                                filetypes=[('Image Files', '*jpeg'), ('Image Files', '*jpg'), ('Image Files', '*png')])
#Finds the name
        name = ""
        adding = False
        for index in range(len(file_path.name) - 1, -1, -1):
            character = file_path.name[index]
            if character == "/":
                break
            elif adding == True:
                name = character + name
            elif character == ".":
                adding = True
        with PIL.Image.open(file_path.name) as img:
#Converts the image to 1s and 0s
            img.load()
            bytestream = io.BytesIO()
            img.save(bytestream, format='JPEG')
            hex_data = bytestream.getvalue()
            data = binascii.hexlify(hex_data)
            img = bin(int(data, 16))
            img = img[2:].zfill(32)

            self.save_to_database(name, img)

    def save_to_database(self, photo_name, img):
        create_photos_table = """
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(30),
            photo BLOB
        )
        """
        add_to_table = f"""
        INSERT INTO photos (name, photo)
        VALUES ('{photo_name}', {img})
        """

        conn = sqlite3.connect("SQLite_Python.db")
        cursor = conn.cursor()
        cursor.execute(create_photos_table)
        cursor.execute(add_to_table)
        conn.commit()


gui = UploadScreen()
gui.mainloop()