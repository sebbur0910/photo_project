import customtkinter as ctk
from PIL import Image


# Creates a modified class button with different hovering properties
class SpecialButton(ctk.CTkButton):

    def _on_enter(self, event=None):
        self._image.configure(size=(300, 200))

    def _on_leave(self, event=None):
        self._image.configure(size=(150, 100))


# Creates an instance of this class and displays it with a photo
class PhotoScreen(ctk.CTk):
    def __init__(self):
        super().__init__()

        filepath = "G:/My Drive/School/Year 13/Computer Science/Sample database images/tree 2.jpg"
        self.my_image = ctk.CTkImage(light_image=Image.open(filepath),

                                     size=(150, 100))

        self.button = SpecialButton(self, image=self.my_image)

        self.button.pack()


window = PhotoScreen()
window.mainloop()
