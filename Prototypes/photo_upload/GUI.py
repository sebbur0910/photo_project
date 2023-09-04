import PIL
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfile

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


gui = UploadScreen()
gui.mainloop()