import customtkinter as ctk
from PIL import Image
from entities import Tag, Timeline, Base, Photo
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import io
from controller import Database

engine = create_engine('sqlite:///:memory:', echo=True)
Base.metadata.create_all(engine)
database = Database()


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.show_frame("homescreen")
        self.frames = None

    def show_frame(self, current_frame):
        self.frames = {
            "homescreen": HomeScreen(self),
            "add_timeline": AddTimeline(self),
            "photo_gallery": PhotoGallery(self),
            "timeline": TimelineView(self)
        }
        widgets = self.winfo_children()
        for widget in widgets:
            if widget.winfo_class() == "Frame":
                widget.pack_forget()
        frame_to_show = self.frames[current_frame]
        frame_to_show.pack(expand=True, fill=ctk.BOTH)
     #   frame_to_show.set_up()


class HomeScreen(ctk.CTkFrame):

    def __init__(self, root):
        super().__init__(root)
        self.root = root
        database.add_image(from_default_set="plus")
        plus_image = database.get_image("plus")
        self.my_image = ctk.CTkImage(light_image=Image.open(plus_image),
                                     size=(150, 100))
  #      self.configure(background="white")
   #     self.title("Home")

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
                                               image=self.my_image,
                                               command=self.add_new_timeline)

        self.thumbnails = database.get_thumbnails()


        self.place()

    def place(self):
        self.title_text.grid(row=0, column=0, columnspan=3)
        self.sort_by_label.grid(row=1, column=0)
        self.sorter.grid(row=1, column=1)
        self.add_new_thumbnail.grid(row=2, column=1)
        self.place_timelines()

    def place_timelines(self,sorted_ids):
        for id in sorted_ids:
            thumbnail = database.get_thumbnail(id)
            thumbnail = ctk.CTkImage(light_image=Image.open(thumbnail),
                                     size=(150, 100))
            name = database.get_timeline_name(id)
            ctk.CTkButton(self,
                          image=thumbnail,
                          text=name,
                          command=self.open_timeline
                          ).grid()

    def open_timeline(self):
        ...
    def sort_request(self, factor):
        self.place_timelines(database.sort_timelines(factor))

    def add_new_timeline(self):
        self.root.show_frame("add_timeline")


class AddTimeline(ctk.CTkFrame):
    def __init__(self, root):
        ...


class PhotoGallery(ctk.CTkFrame):
    def __init__(self, root):
        ...


class TimelineView(ctk.CTkFrame):
    def __init__(self, root):
        ...


gui = App()
gui.mainloop()
