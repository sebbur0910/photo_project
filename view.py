import customtkinter as ctk
from PIL import Image
from entities import Tag, Timeline, Base, Photo
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import io
from controller import Database
from tkinter.filedialog import askopenfile
import re
import datetime

engine = create_engine('sqlite:///:memory:', echo=True)
Base.metadata.create_all(engine)
database = Database()


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.show_frame("homescreen")
        self.frames = None

    def show_frame(self, current_frame, id=None):
        self.frames = {
            "homescreen": HomeScreen(self),
            "add_timeline": CustomiseTimeline(self, 999),
            "photo_gallery": PhotoGallery(self, False),
            "timeline": TimelineView(self),
            "customise_timeline": CustomiseTimeline(self, id),
            "timeline_photos": PhotoGallery(self, True),
            "timeline_new_photo": ImportPhoto(self, id)
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
        self.place_timelines("")

    def place_timelines(self, sorted_ids):
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


class CustomiseTimeline(ctk.CTkFrame):
    def __init__(self, root, timeline_id):
        super().__init__(root)
        self.root = root
        self.timeline_id = timeline_id
        if self.timeline_id == 999:
            title_text = "Create new timeline"
        else:
            title_text = database.get_timeline_name(self.timeline_id)

        self.title_text = ctk.CTkLabel(self,
                                       text=title_text,
                                       font=("Arial Bold", 35),
                                       pady=20
                                       )

        self.name_text = ctk.CTkLabel(self,
                                      text="Name:",
                                      font=("Arial", 20),
                                      anchor="e"
                                      )

        self.name_box = ctk.CTkEntry(self,
                                     bg_color="grey",
                                     width=300)

        self.line_colour_text = ctk.CTkLabel(self,
                                             text="Line colour:",
                                             font=("Arial", 20),
                                             anchor="e"
                                             )

        self.line_colour_box = ctk.CTkEntry(self,
                                            bg_color="grey",
                                            width=300)

        self.line_weight_text = ctk.CTkLabel(self,
                                             text="Line weight:",
                                             font=("Arial", 20),
                                             anchor="e"
                                             )

        self.line_weight_box = ctk.CTkEntry(self,
                                            bg_color="grey",
                                            width=300)

        self.default_border_colour_text = ctk.CTkLabel(self,
                                                       text="Default border colour:",
                                                       font=("Arial", 20),
                                                       anchor="e"
                                                       )

        self.default_border_colour_box = ctk.CTkEntry(self,
                                                      bg_color="grey",
                                                      width=300)

        self.default_border_weight_text = ctk.CTkLabel(self,
                                                       text="Default border weight:",
                                                       font=("Arial", 20),
                                                       anchor="e"
                                                       )

        self.default_border_weight_box = ctk.CTkEntry(self,
                                                      bg_color="grey",
                                                      width=300)

        self.background_colour_text = ctk.CTkLabel(self,
                                                   text="Background colour:",
                                                   font=("Arial", 20),
                                                   anchor="e"
                                                   )

        self.background_colour_box = ctk.CTkEntry(self,
                                                  bg_color="grey",
                                                  width=300)

        self.photos_text = ctk.CTkLabel(self,
                                        text="Photos:",
                                        font=("Arial", 30))

        self.view_current_button = ctk.CTkButton(self,
                                                 text="View/delete current",
                                                 font=("Arial", 30),
                                                 width=350,
                                                 height=150,
                                                 command=self.view_current
                                                 )

        self.insert_existing_button = ctk.CTkButton(self,
                                                    text="Insert from photo gallery",
                                                    font=("Arial", 30),
                                                    width=350,
                                                    height=150,
                                                    command=self.insert_existing
                                                    )

        self.insert_new_button = ctk.CTkButton(self,
                                               text="Insert new",
                                               font=("Arial", 30),
                                               width=350,
                                               height=150,
                                               command=self.insert_new
                                               )

        self.save_button = ctk.CTkButton(self,
                                         text="Save",
                                         font=("Arial", 15),
                                         corner_radius=3,
                                         command=self.save)

        self.insert_existing_values()
        self.place()

    def insert_existing_values(self):
        print("goooooooooooooooooooooooooooooordb")
        print("\n\n" + database.get_timeline_name(self.timeline_id)+ "\n\n")
        self.name_box.insert(index=0, string=database.get_timeline_name(self.timeline_id))
        self.line_colour_box.insert(index=0, string=database.get_timeline_line_colour(self.timeline_id))
        self.line_weight_box.insert(index=0, string=database.get_timeline_line_weight(self.timeline_id))
        self.background_colour_box.insert(index=0, string=database.get_timeline_background_colour(self.timeline_id))
        self.default_border_colour_box.insert(index=0, string=database.get_timeline_default_border_colour(self.timeline_id))
        self.default_border_weight_box.insert(index=0, string=database.get_timeline_default_border_weight(self.timeline_id))
    def save_timeline_to_database(self):
        name = self.name_box.get()
        line_colour = self.line_colour_box.get()
        line_weight = self.line_weight_box.get()
        background_colour = self.background_colour_box.get()
        default_border_colour = self.default_border_colour_box.get()
        default_border_weight = self.default_border_weight_box.get()
    # Need to make sure I'm not overwriting values where there is no box:
        #individual setters :(
        if name:
            database.set_timeline_name(self.timeline_id, name)
        if line_colour:
            database.set_timeline_line_colour(self.timeline_id, line_colour)
        if line_weight:
            database.set_timeline_line_weight(self.timeline_id, line_weight)
        if background_colour:
            database.set_timeline_background_colour(self.timeline_id, background_colour)
        if default_border_colour:
            database.set_timeline_default_border_colour(self.timeline_id, default_border_colour)
        if default_border_weight:
            database.set_timeline_default_border_weight(self.timeline_id, default_border_weight)

    def save(self):
        ...
        # update database
        # go back to original screen (parameterised exit)

    def view_current(self):
        self.root.show_frame("timeline_photos")

    def insert_existing(self):
        self.root.show_frame("photo_gallery")

    def insert_new(self):
        self.save_timeline_to_database()
        self.root.show_frame("timeline_new_photo", self.timeline_id)

    def place(self):
        self.title_text.grid(row=0, column=1)
        self.name_text.grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.name_box.grid(row=1, column=1)
        self.line_colour_text.grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.line_colour_box.grid(row=2, column=1)
        self.line_weight_text.grid(row=3, column=0, sticky="e", padx=10, pady=5)
        self.line_weight_box.grid(row=3, column=1)
        self.default_border_colour_text.grid(row=4, column=0, sticky="e", padx=10, pady=5)
        self.default_border_colour_box.grid(row=4, column=1)
        self.default_border_weight_text.grid(row=5, column=0, sticky="e", padx=10, pady=5)
        self.default_border_weight_box.grid(row=5, column=1)
        self.background_colour_text.grid(row=6, column=0, sticky="e", padx=10, pady=5)
        self.background_colour_box.grid(row=6, column=1)
        self.photos_text.grid(row=7, column=0, pady=20)
        self.view_current_button.grid(row=8, column=0, pady=10, padx=20)
        self.insert_existing_button.grid(row=8, column=1, pady=10, padx=20)
        self.insert_new_button.grid(row=8, column=2, pady=10, padx=20)
        self.save_button.grid(row=9, column=2, sticky="e")


class PhotoGallery(ctk.CTkScrollableFrame):
    def __init__(self, root, master_filter):
        super().__init__(root)
        self.root = root

        if not master_filter:
            title = "All Images"
        else:
            title = "Testing"

        self.title_text = ctk.CTkLabel(self,
                                       text=title,
                                       font=("Arial Bold", 35),
                                       pady=20
                                       )

        self.place()

    def place(self):
        self.title_text.grid(row=0, column=0, columnspan=6)


class TimelineView(ctk.CTkFrame):
    def __init__(self, root):
        ...


class ImportPhoto(ctk.CTkFrame):

    def __init__(self, root, timeline_id=None):
        super().__init__(root)
        self.root = root
        self.timeline_id = timeline_id
        self.file_path = None

        self.title_text = ctk.CTkLabel(self,
                                       text="Import photo",
                                       font=("Arial Bold", 35),
                                       pady=20
                                       )

        self.date_taken_text = ctk.CTkLabel(self,
                                            text="Date taken:",
                                            font=("Arial", 20),
                                            anchor="e"
                                            )

        self.date_taken_box = ctk.CTkEntry(self,
                                           bg_color="grey",
                                           width=300)

        self.caption_text = ctk.CTkLabel(self,
                                         text="Caption:",
                                         font=("Arial", 20),
                                         anchor="e"
                                         )

        self.caption_box = ctk.CTkEntry(self,
                                        bg_color="grey",
                                        width=300,)

        self.upload_button = ctk.CTkButton(self,
                                           text="Upload",
                                           font=("Arial Bold", 35),
                                           width=700,
                                           height=300,
                                           command=self.photo_upload)

        self.save_button = ctk.CTkButton(self,
                                         text="Save",
                                         font=("Arial", 15),
                                         corner_radius=3,
                                         command=self.save)

        self.back_button = ctk.CTkButton(self,
                                         text="Back",
                                         font=("Arial", 15),
                                         corner_radius=3,
                                         command=self.back)

        self.date_not_good_box = ctk.CTkLabel(self,
                                              text="Please enter date in format DD/MM/YYY",
                                              text_color="red",
                                              font=("Arial", 10))

        self.photo_not_good_box = ctk.CTkLabel(self,
                                               text="Please upload a photo before saving",
                                               text_color="red",
                                               font=("Arial", 15)
                                               )

        self.caption_not_good_box = ctk.CTkLabel(self,
                                                 text="Please enter a caption before saving",
                                                 text_color="red",
                                                 font=("Arial", 10))

        self.place()

    def place(self):
        self.title_text.grid(row=0, column=1)
        self.date_taken_text.grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.date_taken_box.grid(row=1, column=1)
        self.caption_text.grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.caption_box.grid(row=2, column=1)
        self.upload_button.grid(row=3, column=0, columnspan=3, padx=60, pady=60)
        self.save_button.grid(row=4, column=2, pady=20)
        self.back_button.grid(row=4, column=0, pady=20)

    def photo_upload(self):
        self.file_path = askopenfile(mode='r',
                                     filetypes=[('Image Files', '*jpeg'), ('Image Files', '*jpg'),
                                                ('Image Files', '*png')])

    def save(self):
        save_blocked = False
        date_taken = self.date_taken_box.get()
        caption = self.caption_box.get()
        if not bool(re.match("[0123][1-9]\/[01][1-9]\/[0-9]{4}", date_taken)) or not date_taken:
            self.date_not_good_box.grid(row=1, column=2)
            save_blocked = True
        else:
            self.date_not_good_box.grid_forget()
        if not self.file_path:
            self.photo_not_good_box.grid(row=3, column=3)
            save_blocked = True
        else:
            self.photo_not_good_box.grid_forget()
        if not caption:
            self.caption_not_good_box.grid(row=2, column=2)
            save_blocked = True
        else:
            self.caption_not_good_box.grid_forget()
        if not save_blocked:
            [day, month, year] = date_taken.split("/")
            date_taken = datetime.date(int(year), int(month), int(day))
            database.upload_photo(self.file_path, caption, date_taken)

            self.back()

    def back(self):
        if self.timeline_id:
            self.root.show_frame("customise_timeline", self.timeline_id)
        else:
            self.root.show_frame("photo_gallery")



gui = App()
gui.mainloop()
