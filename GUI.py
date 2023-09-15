import customtkinter as ctk
from PIL import Image
from entities import Tag, Timeline, Base, Photo

def add_image_to_database(**kwargs):
    if "from_default_set" in kwargs:
        default_image = kwargs.pop("from_default_set")

    if default_image == "plus":
        photo = Photo(data=b'10101010101')
class HomeScreen(ctk.CTk):

    def __init__(self):
        super().__init__()

        add_image_to_database(from_default_set = "plus")

      #  self.my_image = ctk.CTkImage(light_image=Image.open(filepath),
       #                              size=(150, 100))

        self.configure(background="white")
        self.title("Home")

        self.title_text = ctk.CTkLabel(self,
                                       text="Home",
                                       font=("Arial Bold", 35),
                                       pady=20
                                       )

        self.sort_by_label = ctk.CTkLabel(self,
                                          text="Sort by:",
                                          font=("Arial", 13))

        self.sorter = ctk.CTkComboBox(self,
                                      values=["A-Z", "Z-A", "Recently modified", "Custom (drag)"],
                                      command=self.sort_request
                                      )

        self.add_new_thumbnail = ctk.CTkButton(self,
                                               image)

        self.place()

    def place(self):
        self.title_text.grid(row=0, column=0, columnspan=3)
        self.sort_by_label.grid(row=1, column=0)
        self.sorter.grid(row=1, column=1)

    def sort_request(self):
        ...


gui = HomeScreen()
gui.mainloop()
