import PIL
import PIL.Image
import io
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfile
import sqlite3
import binascii

class UploadScreen(tk.Tk):

    def __init__(self):
        super().__init__()

        self.button = tk.Button(
            self,
            text='Choose File',
            command=self.open_file)
        self.button.pack()


    def open_file(self):
        file_path = askopenfile(mode='r', filetypes=[('Image Files', '*jpeg'),('Image Files', '*jpg'),('Image Files', '*png') ])
        if file_path is not None:
            pass
        print(file_path.name)
        with PIL.Image.open(file_path.name) as img:
            img.load()
      #      print(img)
            output = io.BytesIO()
            img.save(output, format='JPEG')
            hex_data = output.getvalue()
  #          print(f"hex data: {hex_data}")
 #           self.save_to_database(hex_data)
            data = binascii.hexlify(hex_data)

            binary = bin(int(data, 16))
            binary = binary[2:].zfill(32)
            print(binary)
            self.save_to_database(binary)

    def save_to_database(self, img):
        create_photos_table = """
        CREATE TABLE photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(30),
            photo BLOB
        )
        """
        add_to_table = """
        INSERT INTO photos (name, photo)
        VALUES (%s, %s);
        """

        conn = sqlite3.connect("SQLite_Python.db")
        cursor = conn.cursor()
        try:
            cursor.execute(create_photos_table)
        except:
            pass
  #      cursor.execute("""
   #     INSERT INTO photos (name, photo)
    #    VALUES ("ababb", 010100101010100100010)
     #   """)
        cursor.execute(f"""
        INSERT INTO photos (name, photo)
        VALUES ("name", {img})
        """)
        conn.commit()

gui = UploadScreen()
gui.mainloop()