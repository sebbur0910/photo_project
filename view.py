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
from functools import partial

database = Database()


class SpecialButton(ctk.CTkButton):

    def _on_enter(self, event=None):
        new_width = self._image._size[0] * 2
        new_height = self._image._size[1] * 2
        self._image.configure(size=(new_width, new_height))
        # self.configure(width=new_width+400, height=new_height+400)

    def _on_leave(self, event=None):
        new_width = self._image._size[0] / 2
        new_height = self._image._size[1] / 2
        self._image.configure(size=(new_width, new_height))
        # self.configure(width=new_width, height=new_height)


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.show_frame("homescreen")
        self.frames = None

    def show_frame(self, current_frame, id=None, secondary_id=None):
        # self.frames = {
        #   "homescreen": HomeScreen(self),
        #  "add_timeline": CustomiseTimeline(self, 999),
        # "photo_gallery": PhotoGallery(self, False),
        # "timeline": TimelineView(self, id),
        # "customise_timeline": CustomiseTimeline(self, id),
        # "timeline_photos": PhotoGallery(self, id),
        # "timeline_new_photo": ImportPhoto(self, timeline_id=id),
        # "view_photo": ImportPhoto(self, photo_id=id),
        # "photo_picker": PhotoPicker(self, timeline_id=id)
        # }
        widgets = self.winfo_children()
        for widget in widgets:
            #  print(widget.winfo_class)
            if widget.winfo_class() == "Frame":
                widget.pack_forget()
        if current_frame == "homescreen":
            frame_to_show = HomeScreen(self)
        elif current_frame == "add_timeline":
            frame_to_show = CustomiseTimeline(self, 999)
        elif current_frame == "photo_gallery":
            frame_to_show = PhotoGallery(self)
        elif current_frame == "timeline":
            frame_to_show = TimelineView(self, id)
        elif current_frame == "customise_timeline":
            frame_to_show = CustomiseTimeline(self, id)
        elif current_frame == "timeline_photos":
            frame_to_show = PhotoGallery(self, id)
        elif current_frame == "timeline_new_photo":
            frame_to_show = ImportPhoto(self, timeline_id=id)
        elif current_frame == "view_photo":
            frame_to_show = ImportPhoto(self, photo_id=id, timeline_id=secondary_id)
        elif current_frame == "photo_picker":
            frame_to_show = PhotoPicker(self, timeline_id=id)
        frame_to_show.pack(expand=True, fill=ctk.BOTH)
    #   frame_to_show.set_up()


class HomeScreen(ctk.CTkFrame):

    def __init__(self, root):
        super().__init__(root)
        self.root = root
        if not database.get_image("plus"):
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
                                               width=self.my_image._size[0],
                                               height=self.my_image._size[1],
                                               text=None,
                                               command=self.add_new_timeline)

        self.image_gallery_button = ctk.CTkButton(self,
                                                  text="Image Gallery",
                                                  command=self.open_images)

        #  self.thumbnails = database.get_thumbnails()

        self.place()

    def place(self):
        self.title_text.grid(row=0, column=0, columnspan=3)
        self.sort_by_label.grid(row=1, column=0)
        self.sorter.grid(row=1, column=1)
        self.add_new_thumbnail.grid(row=2, column=1)
        self.sort_request("A-Z")
        self.add_new_thumbnail.grid()

    def open_images(self):
        self.root.show_frame("photo_gallery")

    def place_timelines(self, sorted_ids):
        for id in sorted_ids:
            thumbnail = database.get_thumbnail(id)
            thumbnail = ctk.CTkImage(light_image=Image.open(thumbnail),
                                     size=(150, 100))
            name = database.get_timeline_name(id)
            ctk.CTkButton(self,
                          image=thumbnail,
                          text=name,
                          command=partial(self.open_timeline, id)
                          ).grid()

    def open_timeline(self, id):
        self.root.show_frame("timeline", id)

    def forget_timelines(self):
        widgets = self.winfo_children()
        for widget in widgets:
            if isinstance(widget, ctk.CTkButton):
                widget.grid_forget()

    def sort_request(self, factor):
        if database.timelines_exist():
            self.forget_timelines()
            self.add_new_thumbnail.grid(row=2, column=1)
            self.place_timelines(database.sort_timelines(factor))
            self.image_gallery_button.grid()

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
        self.name_box.insert(index=1, string=database.get_timeline_name(self.timeline_id))
        self.line_colour_box.insert(index=0, string=database.get_timeline_line_colour(self.timeline_id))
        self.line_weight_box.insert(index=0, string=database.get_timeline_line_weight(self.timeline_id))
        self.background_colour_box.insert(index=0, string=database.get_timeline_background_colour(self.timeline_id))
        self.default_border_colour_box.insert(index=0,
                                              string=database.get_timeline_default_border_colour(self.timeline_id))
        self.default_border_weight_box.insert(index=0,
                                              string=database.get_timeline_default_border_weight(self.timeline_id))

    def save_timeline_to_database(self):
        name = self.name_box.get()
        line_colour = self.line_colour_box.get()
        line_weight = self.line_weight_box.get()
        background_colour = self.background_colour_box.get()
        default_border_colour = self.default_border_colour_box.get()
        default_border_weight = self.default_border_weight_box.get()
        # Need to make sure I'm not overwriting values where there is no box:
        # individual setters :(
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
        if not database.has_photos(self.timeline_id):
            return False
        if not database.has_thumbnail(self.timeline_id):
            database.auto_thumbnail(self.timeline_id)
        self.save_timeline_to_database()
        database.update_modified(self.timeline_id)
        if self.timeline_id == 999:
            database.transfer_to_new_timeline()
        self.root.show_frame("homescreen")
        # update database
        # go back to original screen (parameterised exit)

    def view_current(self):
        self.save_timeline_to_database()
        self.root.show_frame("timeline_photos", self.timeline_id)

    def insert_existing(self):
        self.save_timeline_to_database()
        self.root.show_frame("photo_picker", self.timeline_id)

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
    def __init__(self, root, timeline_id=None):
        super().__init__(root)
        self.root = root
        self.timeline_id = timeline_id
        self.thumbnail_being_selected = False

        if not timeline_id:
            title = "All Images"
        else:
            title = database.get_timeline_name(self.timeline_id)
            self.select_thumbnail_button = ctk.CTkButton(self, text="Toggle thumbnail select",
                                                         command=self.thumbnail_toggle).grid()

        self.title_text = ctk.CTkLabel(self,
                                       text=title,
                                       font=("Arial Bold", 35),
                                       pady=20
                                       )

        self.place()

        photo_thumbnails_and_ids = database.get_photo_thumbnails_and_ids(self.timeline_id)
        count=0
        for photo in photo_thumbnails_and_ids:
            image = ctk.CTkImage(Image.open(photo[0]))
            image.configure(size=[(self.winfo_screenwidth()-50)/5, (self.winfo_screenwidth()-50)/5])
            button = ctk.CTkButton(self,
                                   image=image,
                                   text=None,
                                   command=partial(self.open_image, photo[1]),
                                   height=image._size[0],
                                   width=image._size[0],
                                   border_spacing=0,
                                   round_width_to_even_numbers=False,
                                   round_height_to_even_numbers=False,
                                   corner_radius=0,
                                   border_width=0)
            button.grid(column=count%5, row=count//5+1)
            count+=1

        self.back_button = ctk.CTkButton(self, text="Back", command=self.back)
        self.back_button.grid(columnspan=5)

    def back(self):
        if self.timeline_id:
            self.root.show_frame("customise_timeline", self.timeline_id)
        else:
            self.root.show_frame("homescreen")

    def open_image(self, id):
        if self.thumbnail_being_selected:
            database.add_thumbnail_to_timeline(id, self.timeline_id)
        else:
            self.root.show_frame("view_photo", id)

    def thumbnail_toggle(self):
        self.thumbnail_being_selected = not self.thumbnail_being_selected

    def place(self):
        self.title_text.grid(columnspan=5)


class PhotoPicker(PhotoGallery):
    def __init__(self, root, timeline_id):
        super().__init__(root)
        self.timeline_id = timeline_id

    def open_image(self, id):
        #   if self.thumbnail_being_selected:
        #       database.add_thumbnail_to_timeline(id, self.timeline_id)

        if database.image_in_timeline(id, self.timeline_id):
            database.remove_image_from_timeline(id, self.timeline_id)
        database.add_image_to_timeline(id, self.timeline_id)

    def back(self):
        self.root.show_frame("customise_timeline", id=self.timeline_id)


class TimelineView(ctk.CTkFrame):
    def __init__(self, root, timeline_id):
        super().__init__(root)
        self.root = root
        self.timeline_id = timeline_id
        self.name = database.get_timeline_name(timeline_id)
        self.thumbnail_photo_id = database.get_timeline_thumbnail_photo_id(timeline_id)
        self.date_modified = database.get_timeline_date_modified(timeline_id)
        self.background_photo_id = database.get_timeline_background_photo_id(timeline_id)
        self.background_colour = database.get_timeline_background_colour(timeline_id)
        self.line_colour = database.get_timeline_line_colour(timeline_id)
        self.line_weight = database.get_timeline_line_weight(timeline_id)
        self.default_border_colour = database.get_timeline_default_border_colour(timeline_id)
        self.default_border_weight = database.get_timeline_default_border_weight(timeline_id)

        self.screen_height = self.root.winfo_screenheight()
        self.screen_width = self.root.winfo_screenwidth()

        self.scrollbar = ctk.CTkScrollbar(self, orientation="horizontal")
        self.place_canvas()
        self.scrollbar.pack(side="bottom")
        if not database.get_image("pencil"):
            database.add_image(from_default_set="pencil")
        if not database.get_image("magnifying glass"):
            database.add_image(from_default_set="magnifying glass")
        magnifying_glass = database.get_image("magnifying glass")
        pencil = database.get_image("pencil")
        if not database.get_image("home"):
            database.add_image(from_default_set="home")
        home = database.get_image("home")
        self.pencil_image = ctk.CTkImage(light_image=Image.open(pencil))
        self.magnifying_glass_image = ctk.CTkImage(light_image=Image.open(magnifying_glass))
        self.home_image = ctk.CTkImage(light_image=Image.open(home))
        self.edit_button = ctk.CTkButton(self,
                                         corner_radius=40,
                                         width=30,
                                         height=30,
                                         text="",
                                         image=self.pencil_image,
                                         command=partial(self.root.show_frame, "customise_timeline", self.timeline_id))
        self.zoom_button = ctk.CTkButton(self,
                                         corner_radius=40,
                                         width=30,
                                         height=30,
                                         text="",
                                         image=self.magnifying_glass_image,
                                         command=self.zoom)
        self.home_button = ctk.CTkButton(self,
                                         corner_radius=40,
                                         width=30,
                                         height=30,
                                         text="",
                                         image=self.home_image,
                                         command=partial(self.root.show_frame, "homescreen"))
        self.edit_button.pack(side="bottom")
        self.zoom_button.pack(side="bottom")
        self.home_button.pack(side="bottom")

        #  self.test_button.place(relx=0.5, rely=0)

    def zoom(self):
        self.canvas.pack_forget()
        self.place_canvas(3)

    def place_canvas(self, scale: int = 1):
        self.canvas = ctk.CTkCanvas(self, width=self.screen_width,
                                    height=self.screen_height, background=self.background_colour,
                                    xscrollcommand=self.scrollbar.set,
                                    scrollregion=(-5000 * scale, self.screen_height, 5000 * scale, 0))
        self.canvas.create_polygon((-5000 * scale, self.screen_height / 2 - self.line_weight * 5),
                                   (-5000 * scale, self.screen_height / 2 + self.line_weight * 5),
                                   (5000 * scale, self.screen_height / 2 + self.line_weight * 5),
                                   (5000 * scale, self.screen_height / 2 - self.line_weight * 5),
                                   fill=self.line_colour,
                                   )

        photos_and_ids = database.get_photos_and_ids(self.timeline_id)
        x_coords_dict, dates = database.get_x_coords(self.timeline_id, scale)
        if scale == 1:
            self.y_coords_dict = database.easy_space_coords_out(x_coords_dict, self.screen_height / 2)

        for photo in photos_and_ids:
            photo_id = photo[1]
            photo_caption = database.get_photo_caption(photo_id)
            date_taken = database.get_photo_date_taken(photo_id)
            aspect_ratio = Image.open(photo[0]).size[0] / Image.open(photo[0]).size[1]
            image = ctk.CTkImage(Image.open(photo[0]), size=(int(30 * aspect_ratio), 30), )
            a = ctk.CTkButton(self)
            self.button = SpecialButton(self.canvas,
                                        image=image,
                                        text="",
                                        command=partial(self.open_image, photo[1]),
                                        width=image._size[0],
                                        height=image._size[1],
                                        fg_color="transparent",
                                        border_width=self.default_border_weight,
                                        border_color=self.default_border_colour,
                                        corner_radius=0
                                        )
            x = x_coords_dict[photo_id]
            y = self.y_coords_dict[photo_id]
            self.canvas.create_window(x, y, window=self.button, tags=["image_button"])
            self.canvas.create_line(x, y, x, self.screen_height / 2, width=self.line_weight, fill=self.line_colour)

        for marker in dates:
            self.label = ctk.CTkLabel(self.canvas,
                                      text=marker[0])
            self.canvas.create_window(marker[1], self.screen_height / 2 - 50, window=self.label)

        # size=(100, 100))

        self.scrollbar.configure(command=self.canvas.xview)
        self.canvas.pack()

    def get_free_y_coord(self):
        y = 50
        y_list = []
        self.root.update()
     #   print(self.canvas.coords(tag_or_id="image_button"))
      #  print(y_list)
        while y - 300 + 34 in y_list:
       #     print("aaa")
            y += 50
        return y

    def open_image(self, id):
        self.root.show_frame("view_photo", id=id, secondary_id=self.timeline_id)


class ImportPhoto(ctk.CTkScrollableFrame):

    def __init__(self, root, timeline_id=None, photo_id=None):
        super().__init__(root)
        self.root = root
        self.timeline_id = timeline_id
        self.photo_id = photo_id
        self.file_path = None
        if not database.get_image("tick"):
            database.add_image(from_default_set="tick")
        self.tick = database.get_image("tick")
        self.temp_tags = []

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
                                        width=300, )

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

        if self.photo_id:
            self.date_taken_box.insert(index=0, string=database.get_photo_date_taken(self.photo_id))
            self.caption_box.insert(index=0, string=database.get_photo_caption(photo_id))
            self.show_image(self.photo_id)

        self.tag_entry = ctk.CTkEntry(self)
        self.tag_colour_entry = ctk.CTkEntry(self)
        self.add_tag_button = ctk.CTkButton(self, text="Add tag", command=self.add_tag)

        self.place()

    def add_tag(self):
        tag_name = self.tag_entry.get()
        tag_colour = self.tag_colour_entry.get()
        if tag_name and tag_colour:
            tag_id = database.add_tag(tag_name, tag_colour)
            if self.photo_id:
                database.add_tag_to_photo(tag_id, self.photo_id)
            else:
                self.temp_tags.append([tag_id, tag_name, tag_colour])

        self.place_tags()

    def place(self):
        self.title_text.grid(row=0, column=1)
        self.date_taken_text.grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.date_taken_box.grid(row=1, column=1)
        self.caption_text.grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.caption_box.grid(row=2, column=1)
        self.upload_button.grid(row=3, column=0, columnspan=3, padx=60, pady=60)
        self.save_button.grid(row=4, column=2, pady=20)
        self.back_button.grid(row=4, column=0, pady=20)
        self.tag_entry.grid()
        self.tag_colour_entry.grid()
        self.add_tag_button.grid()
        self.place_tags()

    def forget_tags(self):
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget._command not in [self.back,
                                                                             self.save,
                                                                             self.add_tag,
                                                                             self.photo_upload]:
               # print(widget._command)
                #print("True")
                widget.grid_forget()

    def place_tags(self):
        self.forget_tags()
        tags = database.get_tags()
        self.tick_image = ctk.CTkImage(light_image=Image.open(self.tick))
        for tag in tags:
            if self.photo_id and database.tag_in_photo(tag, self.photo_id):
                image = self.tick_image
            else:
                image = None
            tag_button = ctk.CTkButton(self,
                                       image=image,
                                       text=tag.name,
                                       command=partial(self.toggle_tag, tag),
                                       bg_color=tag.colour,
                                       fg_color=tag.colour,
                                       )
            tag_button.grid()

    def toggle_tag(self, tag):
        if not database.tag_in_photo(tag, self.photo_id):
            database.add_tag_to_photo(tag.tag_ID, self.photo_id)
        else:
            database.remove_tag_from_photo(tag.tag_ID, self.photo_id)
        self.place_tags()

    def show_image(self, photo_id, filepath=None):
        photo = database.get_image_from_id(photo_id)
        if photo:
            photo = ctk.CTkImage(light_image=Image.open(photo),
                                 size=(150, 100))
            ctk.CTkLabel(self,
                         image=photo,
                         ).grid()
        elif filepath:
            photo = ctk.CTkImage(light_image=Image.open(filepath))
            ctk.CTkLabel(self, image=photo, text=None, width=100, height=100).grid()

    def photo_upload(self):
        self.file_path = askopenfile(mode='r',
                                     filetypes=[('Image Files', '*jpeg'), ('Image Files', '*jpg'),
                                                ('Image Files', '*png')])
        self.show_image(photo_id=None, filepath=self.file_path.name)

    def save(self):
        save_blocked = False
        date_taken = self.date_taken_box.get()
        caption = self.caption_box.get()
        if not bool(re.match("[0123][1-9]/[01][1-9]/[0-9]{4}", date_taken)) or not date_taken:
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
            new_photo_id = database.upload_photo(self.file_path.name, caption, date_taken)
            database.add_image_to_timeline(new_photo_id, self.timeline_id)
            self.back()

    def back(self):
        if self.timeline_id and not self.photo_id:
            self.root.show_frame("customise_timeline", self.timeline_id)
        elif self.timeline_id and self.photo_id:
            self.root.show_frame("timeline", self.timeline_id)
        else:
            self.root.show_frame("photo_gallery")


gui = App()
gui.mainloop()
