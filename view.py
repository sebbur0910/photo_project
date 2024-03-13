import customtkinter as ctk
from PIL import Image
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
        print(f"original screenwidth: {self.winfo_screenwidth()}")
        print(f"dimensions: {self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        self.geometry("{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight() - 100))
        self.show_frame("homescreen")
        self.tk.call('tk', 'scaling', 2)
        self.dpi_scale_factor = self.winfo_fpixels("1i") / 96

        self.frames = None

    #   def adjusted_screenwidth(self):
    #      print(f"dpi: { self.winfo_fpixels("1i")}")
    #     self.dpi_scale_factor = self.winfo_fpixels("1i") / 96
    #    return self.winfo_screenwidth()*self.dpi_scale_factor

    # def adjusted_screenheight(self):
    #   self.dpi_scale_factor = self.winfo_fpixels("1i") / 96
    #  return self.winfo_screenheight()*self.dpi_scale_factor

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
        elif current_frame == "new_photo":
            frame_to_show = ImportPhoto(self)
        else:
            frame_to_show = None
        frame_to_show.pack(expand=True, fill=ctk.BOTH)
    #   frame_to_show.set_up()


class HomeScreen(ctk.CTkFrame):

    def __init__(self, root):
        super().__init__(root)
        self.root = root
        if not database.get_image_from_caption("plus"):
            database.add_image(from_default_set="plus")
        plus_image = database.get_image_from_caption("plus")
        self.my_image = ctk.CTkImage(light_image=Image.open(plus_image),
                                     size=(150, 100))
        if not database.get_image_from_caption("images"):
            database.add_image(from_default_set="images")
        images_image = database.get_image_from_caption("images")
        self.my_image_2 = ctk.CTkImage(light_image=Image.open(images_image),
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
                                               #    width=self.my_image._size[0],
                                               #   height=self.my_image._size[1],
                                               text="",
                                               command=self.add_new_timeline)

        self.image_gallery_button = ctk.CTkButton(self,
                                                  text="",
                                                  image=self.my_image_2,
                                                  command=self.open_images)

        #  self.thumbnails = database.get_thumbnails()
        self.configure_grid()
        self.place()

    def configure_grid(self):
        self.grid_columnconfigure(0, minsize=int(self.winfo_screenwidth() / 5) - 10)
        self.grid_columnconfigure(1, minsize=int(self.winfo_screenwidth() / 5) - 10)
        self.grid_columnconfigure(2, minsize=int(self.winfo_screenwidth() / 5) - 10)
        self.grid_columnconfigure(3, minsize=int(self.winfo_screenwidth() / 5) - 10)
        self.grid_columnconfigure(4, minsize=int(self.winfo_screenwidth() / 5) - 10)

    def place(self):
        self.title_text.grid(row=0, column=1, columnspan=3, sticky="ew")
        self.sort_by_label.grid(row=1, column=0)
        self.sorter.grid(row=1, column=1)
        self.add_new_thumbnail.grid(row=2, column=0)
        self.sort_request("A-Z")
        self.add_new_thumbnail.grid()

    def open_images(self):
        self.root.show_frame("photo_gallery")

    def place_timelines(self, sorted_ids):
        count = 2
        for id in sorted_ids:
            thumbnail = database.get_thumbnail(id)
            thumbnail = ctk.CTkImage(light_image=Image.open(thumbnail),
                                     size=(150, 100))
            name = database.get_timeline_name(id)
            image_button = ctk.CTkButton(self,
                                         image=thumbnail,
                                         text=name,
                                         command=partial(self.open_timeline, id),
                                         width=150,
                                         compound="top"
                                         )
            image_button.grid(row=count // 5 + 2, column=count % 5)
            count += 1

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
            self.add_new_thumbnail.grid(row=2, column=0)
            self.place_timelines(database.sort_timelines(factor))
            self.image_gallery_button.grid(row=2, column=1)

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

        if database.timeline_exists(999) and self.timeline_id == 999:
            database.set_timeline_name(self.timeline_id, "")

        self.title_text = ctk.CTkLabel(self,
                                       text=title_text,
                                       font=("Arial Bold", 35),
                                       pady=20
                                       )

        self.name_text = ctk.CTkLabel(self,
                                      text="Name (mandatory):",
                                      font=("Arial", 20),
                                      anchor="e"
                                      )

        self.name_box = ctk.CTkEntry(self,
                                     bg_color="grey",
                                     width=300)

        self.line_colour_text = ctk.CTkLabel(self,
                                             text="Line colour (default: black):",
                                             font=("Arial", 20),
                                             anchor="e"
                                             )

        self.line_colour_box = ctk.CTkEntry(self,
                                            bg_color="grey",
                                            width=300)

        self.line_weight_text = ctk.CTkLabel(self,
                                             text="Line weight (default: 3):",
                                             font=("Arial", 20),
                                             anchor="e"
                                             )

        self.line_weight_box = ctk.CTkEntry(self,
                                            bg_color="grey",
                                            width=300)

        self.default_border_colour_text = ctk.CTkLabel(self,
                                                       text="Border colour (default: black):",
                                                       font=("Arial", 20),
                                                       anchor="e"
                                                       )

        self.default_border_colour_box = ctk.CTkEntry(self,
                                                      bg_color="grey",
                                                      width=300)

        self.default_border_weight_text = ctk.CTkLabel(self,
                                                       text="Border weight (default: 1):",
                                                       font=("Arial", 20),
                                                       anchor="e"
                                                       )

        self.default_border_weight_box = ctk.CTkEntry(self,
                                                      bg_color="grey",
                                                      width=300)

        self.background_colour_text = ctk.CTkLabel(self,
                                                   text="Background colour (default: white):",
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
        self.back_button = ctk.CTkButton(self,
                                         text="Back",
                                         font=("Arial", 15),
                                         corner_radius=3,
                                         command=self.back)

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
        else:
            database.set_timeline_line_colour(self.timeline_id, "black")
        if line_weight:
            database.set_timeline_line_weight(self.timeline_id, line_weight)
        else:
            database.set_timeline_line_weight(self.timeline_id, 3)
        if background_colour:
            database.set_timeline_background_colour(self.timeline_id, background_colour)
        else:
            database.set_timeline_background_colour(self.timeline_id, "white")
        if default_border_colour:
            database.set_timeline_default_border_colour(self.timeline_id, default_border_colour)
        else:
            database.set_timeline_default_border_colour(self.timeline_id, "black")
        if default_border_weight:
            database.set_timeline_default_border_weight(self.timeline_id, default_border_weight)
        else:
            database.set_timeline_default_border_weight(self.timeline_id, 1)

    def save(self):
        if not database.has_photos(self.timeline_id):
            return False
        if not database.has_thumbnail(self.timeline_id):
            database.auto_thumbnail(self.timeline_id)
        if self.validate_save():

            self.save_timeline_to_database()
            database.update_modified(self.timeline_id)
            if self.timeline_id == 999:
                database.transfer_to_new_timeline()
                self.root.show_frame("homescreen")
            else:
                self.root.show_frame("timeline", self.timeline_id)
        # update database
        # go back to original screen (parameterised exit)

    def validate_save(self):
        name = self.name_box.get()
        line_colour = self.line_colour_box.get()
        line_weight = self.line_weight_box.get()
        background_colour = self.background_colour_box.get()
        default_border_colour = self.default_border_colour_box.get()
        default_border_weight = self.default_border_weight_box.get()

        if len(name) not in range(1, 21):
            ...

    def back(self):
        if self.timeline_id == 999:
            self.root.show_frame("homescreen")
        else:
            self.root.show_frame("timeline", self.timeline_id)

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
        self.back_button.grid(row=9, column=0)


class PhotoGallery(ctk.CTkFrame):
    def __init__(self, root, timeline_id=None):
        self.active_tags = []
        self.being_deleted = False
        self.filter_placed = False
        super().__init__(root)
        self.root = root
        if not database.get_image_from_caption("tick"):
            database.add_image(from_default_set="tick")
        self.tick = database.get_image_from_caption("tick")
        self.timeline_id = timeline_id
        self.thumbnail_being_selected = False

        if not timeline_id:
            title = "All Images"
        else:
            title = database.get_timeline_name(self.timeline_id)
            self.select_thumbnail_button = ctk.CTkButton(self, text="Toggle thumbnail select",
                                                         command=self.thumbnail_toggle).grid()
            self.delete_toggle_button = ctk.CTkButton(self, text="Toggle deleting",
                                                      command=self.delete_toggle).grid(column=1, row=0)

        self.title_text = ctk.CTkLabel(self,
                                       text=title,
                                       font=("Arial Bold", 35),
                                       pady=20
                                       )
        self.image_frame = ctk.CTkScrollableFrame(self, width=self.winfo_screenwidth(),
                                                  height=int(self.winfo_screenheight() * 0.7))

        self.place()

        self.place_images(database.get_photo_thumbnails_and_ids(timeline_id=self.timeline_id))
        if not database.get_image_from_caption("plus"):
            database.add_image(from_default_set="plus")
        plus = database.get_image_from_caption("plus")
        self.filter_button = ctk.CTkButton(self, text="Filter", command=self.place_filter)
        self.filter_button.grid(column=0, row=1)
        self.filter = ctk.CTkScrollableFrame(self, bg_color="blue", fg_color="blue")
        self.sort_by_label = ctk.CTkLabel(self,
                                          text="Sort by:",
                                          font=("Arial", 13))

        self.sorter = ctk.CTkComboBox(self,
                                      values=["Photo ID", "Most used", "Date taken", "Custom (drag)"],
                                      command=self.sort_request
                                      )
        self.sort_by_label.grid(column=3, row=1)
        self.sorter.grid(column=4, row=1)
        self.pencil_image = ctk.CTkImage(light_image=Image.open(plus))
        self.add_image_button = ctk.CTkButton(self, image=self.pencil_image, command=self.add_image, text="")
        self.image_frame.grid(columnspan=5, sticky="ew")
        self.add_image_button.grid(column=4, row=3)
        self.back_button = ctk.CTkButton(self, text="Back", command=self.back)
        self.back_button.grid(row=3, column=3)
        self.filter_save = ctk.CTkButton(self.filter, text="Save", command=self.filter_save_command)

    def filter_save_command(self):
        for widget in self.image_frame.winfo_children():
            widget.grid_forget()
        self.place_images(database.get_photo_thumbnails_and_ids(timeline_id=self.timeline_id))
        self.place_filter()

    def sort_request(self, factor):
        self.forget_images()
        sorted_items = database.get_photo_thumbnails_and_ids(sort_factor=factor, timeline_id=self.timeline_id)
        self.place_images(sorted_items)

    def forget_images(self):
        for widget in self.image_frame.winfo_children():
            widget.grid_forget()

    def place_images(self, photo_thumbnails_and_ids):
        #     photo_thumbnails_and_ids = database.get_photo_thumbnails_and_ids(self.timeline_id)
        if self.active_tags:
            photo_thumbnails_and_ids = database.filter_thumbnails_and_ids(photo_thumbnails_and_ids, self.active_tags)
        count = 0
        for photo in photo_thumbnails_and_ids:
            image = ctk.CTkImage(Image.open(photo[0]))
            image.configure(size=[(self.winfo_screenwidth() - 50) / 5, (self.winfo_screenwidth() - 50) / 5])
            button = ctk.CTkButton(self.image_frame,
                                   image=image,
                                   text="",
                                   command=partial(self.open_image, photo[1]),
                                   height=image._size[0],
                                   width=image._size[0],
                                   border_spacing=0,
                                   round_width_to_even_numbers=False,
                                   round_height_to_even_numbers=False,
                                   corner_radius=0,
                                   border_width=0)
            button.grid(column=count % 5, row=count // 5 + 1)
            count += 1

    def place_filter(self):
        if self.filter_placed:
            for widget in self.filter.winfo_children():
                widget.grid_forget()
            self.filter.grid_forget()
        else:
            self.filter.grid(column=1, row=1)
            self.tag_search_box = ctk.CTkEntry(self.filter)
            self.tag_search_box.grid()
            self.tag_search_button = ctk.CTkButton(self.filter, text="Search", command=self.place_tags)
            self.tag_search_button.grid()
            self.place_tags()
        self.filter_placed = not self.filter_placed

    def forget_tags(self):
        for widget in self.filter.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget._command != self.place_tags:
                widget.grid_forget()

    def place_tags(self):
        self.forget_tags()
        search_key = self.tag_search_box.get()
        tags = database.get_tags(search_key=search_key)
        self.tick_image = ctk.CTkImage(light_image=Image.open(self.tick))
        for tag in tags:
            if tag in self.active_tags:
                image = self.tick_image
            else:
                image = None
            tag_button = ctk.CTkButton(self.filter,
                                       #  image=image,
                                       text=tag.name,
                                       command=partial(self.toggle_tag, tag),
                                       image=image,
                                       bg_color=tag.colour,
                                       fg_color=tag.colour,
                                       )
            tag_button.grid()
        self.filter_save.grid()

    def toggle_tag(self, tag):
        if tag in self.active_tags:
            self.active_tags.remove(tag)
        else:
            self.active_tags.append(tag)
        self.place_tags()

    def fill_filter_frame(self):
        ...

    def add_image(self):
        self.root.show_frame("new_photo")

    def back(self):
        if self.timeline_id:
            self.root.show_frame("customise_timeline", self.timeline_id)
        else:
            self.root.show_frame("homescreen")

    def open_image(self, id):
        if self.thumbnail_being_selected:
            database.add_thumbnail_to_timeline(id, self.timeline_id)
        elif self.being_deleted:
            database.delete_photo_from_timeline(id, self.timeline_id)
            self.sort_request(self)
        else:
            self.root.show_frame("view_photo", id, self.timeline_id)

    def delete_toggle(self):
        self.being_deleted = not self.being_deleted

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
        else:
            database.add_image_to_timeline(id, self.timeline_id)

    def back(self):
        self.root.show_frame("customise_timeline", id=self.timeline_id)


class TimelineView(ctk.CTkFrame):
    def __init__(self, root, timeline_id):
        super().__init__(root)
        self.root = root
        self.timeline_id = timeline_id
        self.combobox_packed = False
        self.name = database.get_timeline_name(timeline_id)
        self.thumbnail_photo_id = database.get_timeline_thumbnail_photo_id(timeline_id)
        self.date_modified = database.get_timeline_date_modified(timeline_id)
        self.background_photo_id = database.get_timeline_background_photo_id(timeline_id)
        self.background_colour = database.get_timeline_background_colour(timeline_id)
        self.line_colour = database.get_timeline_line_colour(timeline_id)
        self.line_weight = database.get_timeline_line_weight(timeline_id)
        self.default_border_colour = database.get_timeline_default_border_colour(timeline_id)
        self.default_border_weight = database.get_timeline_default_border_weight(timeline_id)
        self.text_colour = self.decide_text_colour()
        self.screen_height = self.root.winfo_screenheight() * self.root.dpi_scale_factor * 0.85
        self.screen_width = self.root.winfo_screenwidth() * self.root.dpi_scale_factor
        print(f"dpi scale factor: {self.root.dpi_scale_factor}")

        self.scrollbar = ctk.CTkScrollbar(self, orientation="horizontal", width=self.screen_width)
        self.place_canvas()
        self.scrollbar.pack(side="bottom")
        self.title_text = ctk.CTkLabel(self, text=self.name, font=("Arial", 30), text_color=self.text_colour,
                                       bg_color=self.background_colour)
        self.title_text.place(relx=0.45, y=5)
        if not database.get_image_from_caption("pencil"):
            database.add_image(from_default_set="pencil")
        if not database.get_image_from_caption("magnifying glass"):
            database.add_image(from_default_set="magnifying glass")
        magnifying_glass = database.get_image_from_caption("magnifying glass")
        pencil = database.get_image_from_caption("pencil")
        if not database.get_image_from_caption("home"):
            database.add_image(from_default_set="home")
        home = database.get_image_from_caption("home")
        self.pencil_image = ctk.CTkImage(light_image=Image.open(pencil))
        self.magnifying_glass_image = ctk.CTkImage(light_image=Image.open(magnifying_glass))
        self.home_image = ctk.CTkImage(light_image=Image.open(home))
        self.edit_button = ctk.CTkButton(self,
                                         corner_radius=40,
                                         bg_color=self.background_colour,
                                         width=30,
                                         height=30,
                                         text="",
                                         image=self.pencil_image,
                                         command=partial(self.root.show_frame, "customise_timeline", self.timeline_id))
        self.zoom_button = ctk.CTkButton(self,
                                         corner_radius=40,
                                         bg_color=self.background_colour,
                                         width=30,
                                         height=30,
                                         text="",
                                         image=self.magnifying_glass_image,
                                         command=self.zoom)
        self.home_button = ctk.CTkButton(self,
                                         corner_radius=40,
                                         bg_color=self.background_colour,
                                         width=30,
                                         height=30,
                                         text="",
                                         image=self.home_image,
                                         command=partial(self.root.show_frame, "homescreen"))
        self.zoom_combobox = ctk.CTkComboBox(self,
                                             values=["50%", "100%", "150%", "200%", "250%", "300%", "1000%"],
                                             command=self.zoom_command,
                                             )
        self.zoom_combobox.set("100%")
        self.edit_button.place(x=self.winfo_screenwidth() * 0.9, y=self.winfo_screenheight() * 0.8)
        self.zoom_button.place(x=self.winfo_screenwidth() * 0.95, y=self.winfo_screenheight() * 0.8)
        self.home_button.place(x=self.winfo_screenwidth() * 0.85, y=self.winfo_screenheight() * 0.8)

        #  self.test_button.place(relx=0.5, rely=0)

    def decide_text_colour(self):
        if self.background_colour.lower() == "white":
            return "black"
        elif self.background_colour.lower() == "grey":
            return "blue"
        elif self.background_colour.lower() == "black":
            return "white"
        else:
            return "grey"

    def zoom(self):
        if self.combobox_packed:
            self.zoom_combobox.pack_forget()

        else:
            self.canvas.pack_forget()
            self.zoom_combobox.pack(side="top")
            self.canvas.pack(side="top")
        self.combobox_packed = not self.combobox_packed

    def zoom_command(self, zoom):
        zoom = int(zoom[:-1]) / 100
        self.canvas.pack_forget()
        self.place_canvas(zoom)
        self.zoom_combobox.pack(side="top")

    def place_canvas(self, scale: float = 1):
        print(f"screen width: {self.screen_width}")
        print(f"actual screen width: {self.root.winfo_screenwidth()}")
        self.canvas = ctk.CTkCanvas(self, width=self.screen_width,
                                    height=self.screen_height,
                                    background=self.background_colour,
                                    xscrollcommand=self.scrollbar.set,
                                    scrollregion=(-5000 * scale, self.screen_height, 5000 * scale, 0),
                                    )
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
            if marker[0] != "":
                self.label = ctk.CTkLabel(self.canvas,
                                          text=marker[0],
                                          text_color=self.text_colour)
            self.canvas.create_window(marker[1], self.screen_height / 2 - 50, window=self.label)
            self.canvas.create_line(marker[1], self.screen_height / 2 - 40, marker[1],
                                    self.screen_height / 2 - self.line_weight * 5, width=self.line_weight,
                                    fill=self.text_colour)

        # size=(100, 100))

        self.scrollbar.configure(command=self.canvas.xview)
        self.canvas.pack(side="top")

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
        if not database.get_image_from_caption("tick"):
            database.add_image(from_default_set="tick")
        self.tick = database.get_image_from_caption("tick")
        self.temp_tags = []
        if self.photo_id:
            title = "View photo"
        else:
            title = "Import photo"

        self.title_text = ctk.CTkLabel(self,
                                       text=title,
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

        self.tag_entry_label = ctk.CTkLabel(self, text="Tag name: ")
        self.tag_colour_label = ctk.CTkLabel(self, text="Tag colour: ")
        self.tag_entry = ctk.CTkEntry(self)
        self.tag_colour_entry = ctk.CTkEntry(self)
        self.add_tag_button = ctk.CTkButton(self, text="Add tag", command=self.add_tag)

        self.place()
        if self.photo_id:
            self.date_taken_box.insert(index=0, string=database.get_photo_date_taken(self.photo_id))
            self.caption_box.insert(index=0, string=database.get_photo_caption(photo_id))
            self.show_image(self.photo_id)

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
        self.tag_entry_label.grid()
        self.tag_entry.grid()
        self.tag_colour_label.grid()
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
                # print("True")
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
                                 size=(250, 175))
            self.upload_button.grid_forget()
            ctk.CTkLabel(self,
                         image=photo, text=""
                         ).grid(row=3, column=0, columnspan=3, padx=60, pady=60)
        elif filepath:
            photo = ctk.CTkImage(light_image=Image.open(filepath), size=(250, 175))
            self.upload_button.grid_forget()
            ctk.CTkLabel(self, image=photo, text="", width=100, height=100).grid(row=3, column=0, columnspan=3, padx=60,
                                                                                 pady=60)

    def photo_upload(self):
        self.file_path = askopenfile(mode='r',
                                     filetypes=[('Image Files', '*jpeg'), ('Image Files', '*jpg'),
                                                ('Image Files', '*png')])
        self.show_image(photo_id=None, filepath=self.file_path.name)
        self.fill_date_taken(self.file_path.name)

    def fill_date_taken(self, filepath):
        date_taken = database.get_date_taken(filepath)
        self.date_taken_box.insert(0, date_taken)

    def save(self):
        save_blocked = False
        date_taken = self.date_taken_box.get()
        caption = self.caption_box.get()
        if not bool(re.match("[0123][0-9]/[01][0-9]/[0-9]{4}", date_taken)) or not date_taken:
            self.date_not_good_box.grid(row=1, column=2)
            save_blocked = True
        else:
            self.date_not_good_box.grid_forget()
        if not self.file_path and not self.photo_id:
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
            if not self.photo_id:
                new_photo_id = database.upload_photo(self.file_path.name, caption, date_taken)
                database.add_image_to_timeline(new_photo_id, self.timeline_id)
            elif not (self.photo_id or self.timeline_id):
                database.upload_photo(self.file_path.name, caption, date_taken)
            else:
                database.set_photo_caption(self.photo_id, caption)
                database.set_photo_date_taken(self.photo_id, date_taken)
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
