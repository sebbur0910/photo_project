import customtkinter as ctk
from PIL import Image


class SpecialButton(ctk.CTkButton):

    def _on_enter(self, event=None):
        self._image.configure(size=(300, 200))

    def _on_leave(self, event=None):
        self._image.configure(size=(150, 100))


class PhotoScreen(ctk.CTk):
    def __init__(self):
        super().__init__()

        filepath = "/home/burbidgesebastian/pycharm-2022.2.2/photo_project/Prototypes/photo_upload/sample.jpg"
        self.my_image = ctk.CTkImage(light_image=Image.open(filepath),

                                     size=(150, 100))

        self.button = SpecialButton(self, image=self.my_image, text=None)

        self.button.pack()


window = PhotoScreen()
window.mainloop()
