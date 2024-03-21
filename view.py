import customtkinter as ctk
from PIL import Image
from controller import Database
from tkinter.filedialog import askopenfile
import re
import datetime
from functools import partial

database = Database()


class SpecialButton(ctk.CTkButton):
    """
    Polymorphic button for use in the timeline view
    This button expands when hovered upon
    """

    # Changes the binding of hover to expand the button's image
    def _on_enter(self, event=None):
        new_width = self._image._size[0] * 2
        new_height = self._image._size[1] * 2
        self._image.configure(size=(new_width, new_height))

    # Changes the binding of leaving hover to reduce the size of the button's image
    def _on_leave(self, event=None):
        new_width = self._image._size[0] / 2
        new_height = self._image._size[1] / 2
        self._image.configure(size=(new_width, new_height))


class App(ctk.CTk):
    """
    The main application, which hosts the different frames
    """

    def __init__(self):
        super().__init__()
        # Makes the window fill the screen
        self.geometry("{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight() - 100))
        # Shows the homescreen frame
        self.show_frame("homescreen")
        # After the frame is called, tkinter gets confused with its geometry manager
        # This enables the program to adjust for virtual / physical pixel disparity
        self.tk.call('tk', 'scaling', 2)
        self.dpi_scale_factor = self.winfo_fpixels("1i") / 96

    def show_frame(self, current_frame, id=None, secondary_id=None):
        """
        Fills the app window with the necessary frame

        Parameters
        ----------
        current_frame
            The frame to display
        id
            General ID parameter, often necessary for setting up the frame
        secondary_id
            General secondary ID parameter, often necessary for setting up the frame

        Returns
        -------

        """
        widgets = self.winfo_children()
        # Clears the previous frame
        for widget in widgets:
            if widget.winfo_class() == "Frame":
                widget.pack_forget()
        # If statement converts the string input into the necessary class
        if current_frame == "homescreen":
            frame_to_show = HomeScreen(self)
        elif current_frame == "add_timeline":
            # For a timeline to be added, the CustomiseTimeline screen is called
            # But with the ID of 999, representing the temporary timeline
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
        # Makes the frame fill out the window
        frame_to_show.pack(expand=True, fill=ctk.BOTH)


class HomeScreen(ctk.CTkScrollableFrame):

    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.deleting = False
        self.column_width = int(self.winfo_screenwidth() / 5) - 20
        # Gets the plus image and the 'images' image for the add timeline and image gallery buttons
        if not database.get_image_from_caption("plus"):
            database.add_image(from_default_set="plus")
        plus_image = database.get_image_from_caption("plus")
        self.my_image = ctk.CTkImage(light_image=Image.open(plus_image),
                                     size=(self.column_width, int(self.column_width * 2 / 3)))
        if not database.get_image_from_caption("images"):
            database.add_image(from_default_set="images")
        images_image = database.get_image_from_caption("images")
        self.my_image_2 = ctk.CTkImage(light_image=Image.open(images_image),
                                       size=(self.column_width, int(self.column_width * 2 / 3)))
        # Makes a label for the title
        self.title_text = ctk.CTkLabel(self,
                                       text="Home",
                                       font=("Arial Bold", 35),
                                       pady=20
                                       )
        self.toggle_delete_button = ctk.CTkButton(self,
                                                  text="Click to delete: off",
                                                  command=self.toggle_delete)

        self.sort_by_label = ctk.CTkLabel(self,
                                          text="Sort by:",
                                          font=("Arial", 13))
        # Creates a combobox from which the user can select the sorting factor
        self.sorter = ctk.CTkComboBox(self,
                                      values=["A-Z", "Z-A", "Recently modified"],
                                      command=self.sort_request
                                      )
        # Button to add a new thumbnail
        self.add_new_thumbnail = ctk.CTkButton(self,
                                               image=self.my_image,
                                               command=self.add_new_timeline,
                                               text="Create a new timeline",
                                               compound="top",
                                               fg_color="transparent")
        # Button to open the image gallery
        self.image_gallery_button = ctk.CTkButton(self,
                                                  image=self.my_image_2,
                                                  text="Open gallery",
                                                  command=self.open_images,
                                                  compound="top",
                                                  fg_color="transparent")

        self.configure_grid()
        self.place()

    def toggle_delete(self):
        """
        Switches 'delete mode' on and off, changing the deleting button appropriately.

        Returns
        -------

        """
        # If the program is in deleting mode already when the button is pressed, deleting mode is turned off
        # The message on the button is then changed accordingly
        if self.deleting:
            self.deleting = False
            self.toggle_delete_button.configure(require_redraw=True, text="Click to delete: off")
        # If the program is not already in deleting mode, the reverse occurs
        else:
            self.deleting = True
            self.toggle_delete_button.configure(require_redraw=True, text="Click to delete: on")

    def configure_grid(self):
        """
        Configures the columns of the grid so that they are regular

        Returns
        -------

        """
        self.grid_columnconfigure(0, minsize=self.column_width)
        self.grid_columnconfigure(1, minsize=self.column_width)
        self.grid_columnconfigure(2, minsize=self.column_width)
        self.grid_columnconfigure(3, minsize=self.column_width)
        self.grid_columnconfigure(4, minsize=self.column_width)

    def place(self):
        """
        Places everything on the screen

        Returns
        -------

        """
        self.title_text.grid(row=0, column=1, columnspan=3, sticky="ew")
        self.toggle_delete_button.grid(row=0, column=0)
        self.sort_by_label.grid(row=1, column=0)
        self.sorter.grid(row=1, column=1)
        self.add_new_thumbnail.grid(row=2, column=0)
        # Calls the sort_request method, which places the timelines in A-Z order
        self.sort_request("A-Z")

    def open_images(self):
        """
        Navigates to a page where the user can view the images on the timeline.

        Returns
        -------

        """
        self.root.show_frame("photo_gallery")

    def place_timelines(self, sorted_ids):
        """
        Places the thumbnails of the timelines in order, for the user to view.

        Parameters
        ----------
        sorted_ids
            All the IDs of the timeline, sorted in the order that they are to be displayed

        Returns
        -------

        """
        # The 'count' variable decides the position of the timeline thumbnails in the grid.
        # The first two spaces are taken up by the image library and add timeline buttons, so the count starts at two.
        count = 2
        # Iterates through the sorted ids. For each ID, a thumbnail is placed
        for id in sorted_ids:
            # Receives the thumbnail from the database as an io.BytesIO object
            thumbnail = database.get_thumbnail(id)
            # Converts this into a ctk image
            thumbnail = ctk.CTkImage(light_image=Image.open(thumbnail),
                                     size=(self.column_width, int(self.column_width * 2 / 3)))
            name = database.get_timeline_name(id)
            # Creates a button for this timeline
            # The button displays the timeline thumbnail and name
            # When clicked on, the program opens the timeline
            image_button = ctk.CTkButton(self,
                                         image=thumbnail,
                                         text=name,
                                         command=partial(self.timeline_click, id),
                                         width=self.column_width,
                                         compound="top"
                                         )
            # The timeline is placed on the grid.
            # The row is decided by finding the next lowest multiple of 5, then adding 2
            # 2 is added because two rows of the grid are already taken up by the title and other buttons
            # The column is decided by the remainder of this operation
            # In short, the number representing [row, column] is calculated by converting to base 5.
            image_button.grid(row=count // 5 + 2, column=count % 5)
            count += 1

    def timeline_click(self, id):
        """
        This method tells the program what to do when a timeline has been clicked on.
        This depends on initial conditions.

        Parameters
        ----------
        id
            The ID of the timeline that has been clicked on

        Returns
        -------

        """
        # If deleting mode is on, the click tells the program to delete the timeline
        if self.deleting:
            database.drop_timeline(id)
            # The program then replaces all the timelines by calling a sort request again.
            sort_var = self.sorter.get()
            self.sort_request(sort_var)
        # If deleting mode is off, the program shows the timeline that has been clicked on.
        else:
            self.root.show_frame("timeline", id)

    def forget_timelines(self):
        """
        Clears all the timelines from the screen

        Returns
        -------

        """

        widgets = self.winfo_children()
        # Checks which widgets are timeline buttons
        for widget in widgets:
            # The only buttons are timeline buttons and the toggle_delete_button, so this statement can check
            # what is an isn't a timeline
            if isinstance(widget, ctk.CTkButton) and widget != self.toggle_delete_button:
                widget.grid_forget()

    def sort_request(self, factor):
        """
        Tells the program what to do when a value is clicked in the 'sort by' combobox

        Parameters
        ----------
        factor
            The value selected in the combobox (e.g. "A-Z")

        Returns
        -------

        """
        # Only performs these actions if timelines exist to operate on
        if database.timelines_exist():
            # First, clears all the timelines from the grid
            self.forget_timelines()
            # Then places the buttons to make a new timeline and open the images library
            self.add_new_thumbnail.grid(row=2, column=0)
            self.image_gallery_button.grid(row=2, column=1)
            # Calls the sort_timelines subroutine to get the sorted ids, then places timelines accordingly
            self.place_timelines(database.sort_timelines(factor))

    def add_new_timeline(self):
        """
        Tells the program what to do when the add new timeline button is clicked

        Returns
        -------

        """
        self.root.show_frame("add_timeline")


class CustomiseTimeline(ctk.CTkFrame):
    """
    Screen to customise or create a new timeline
    """

    def __init__(self, root, timeline_id):
        """
        Initialises the screen

        Parameters
        ----------
        root
            The instance of the parent
        timeline_id
            The ID of the timeline being edited
            NB: timeline_ID 999 represents the temporary placeholder for a new timeline
        """
        super().__init__(root)
        self.root = root
        self.timeline_id = timeline_id
        # Timeline ID 999 represents the placeholder for a new timeline before creation
        if self.timeline_id == 999:
            title_text = "Create new timeline"
        else:
            # The title is set to the name of the timeline
            title_text = database.get_timeline_name(self.timeline_id)
        # If the ID has been set to 999 but the placeholder timeline has not yet been created
        # A new blank timeline is made
        if (not database.timeline_exists(999)) and self.timeline_id == 999:
            database.set_timeline_name(self.timeline_id, "")
        # Label for the timeline title
        self.title_text = ctk.CTkLabel(self,
                                       text=title_text,
                                       font=("Arial Bold", 35),
                                       pady=20
                                       )
        # Label to illustrate the name entrybox
        self.name_text = ctk.CTkLabel(self,
                                      text="Name (mandatory):",
                                      font=("Arial", 20),
                                      anchor="e"
                                      )
        # Entrybox for the timeline name
        self.name_box = ctk.CTkEntry(self,
                                     bg_color="grey",
                                     width=300)
        # Label to illustrate the line colour entrybox
        self.line_colour_text = ctk.CTkLabel(self,
                                             text="Line colour (default: black):",
                                             font=("Arial", 20),
                                             anchor="e"
                                             )
        # Entrybox for the timeline line colour
        self.line_colour_box = ctk.CTkEntry(self,
                                            bg_color="grey",
                                            width=300)
        # Label for the line weight entry box
        self.line_weight_text = ctk.CTkLabel(self,
                                             text="Line weight (default: 3):",
                                             font=("Arial", 20),
                                             anchor="e"
                                             )
        # Entry box for the line weight
        self.line_weight_box = ctk.CTkEntry(self,
                                            bg_color="grey",
                                            width=300)
        # Label for the default border colour entry box
        self.default_border_colour_text = ctk.CTkLabel(self,
                                                       text="Border colour (default: black):",
                                                       font=("Arial", 20),
                                                       anchor="e"
                                                       )
        # Entry box for the timeline default border colour
        self.default_border_colour_box = ctk.CTkEntry(self,
                                                      bg_color="grey",
                                                      width=300)
        # Label for the default border weight entry box
        self.default_border_weight_text = ctk.CTkLabel(self,
                                                       text="Border weight (default: 1):",
                                                       font=("Arial", 20),
                                                       anchor="e"
                                                       )
        # Entry box for the timeline default border weight
        self.default_border_weight_box = ctk.CTkEntry(self,
                                                      bg_color="grey",
                                                      width=300)
        # Label for the background colour entry box
        self.background_colour_text = ctk.CTkLabel(self,
                                                   text="Background colour (default: white):",
                                                   font=("Arial", 20),
                                                   anchor="e"
                                                   )
        # Entry box for the timeline background colour
        self.background_colour_box = ctk.CTkEntry(self,
                                                  bg_color="grey",
                                                  width=300)
        # Label for the start of the 'photos' section of the timeline editing
        self.photos_text = ctk.CTkLabel(self,
                                        text="Photos:",
                                        font=("Arial", 30))
        # Button to view the current photos in the timeline
        self.view_current_button = ctk.CTkButton(self,
                                                 text="View/delete current",
                                                 font=("Arial", 30),
                                                 width=350,
                                                 height=150,
                                                 command=self.view_current
                                                 )
        # Button to insert photos into the timeline from the image gallery
        self.insert_from_gallery_button = ctk.CTkButton(self,
                                                        text="Insert from photo gallery",
                                                        font=("Arial", 30),
                                                        width=350,
                                                        height=150,
                                                        command=self.insert_existing
                                                        )
        # Button to upload a new photo (from the computer's files)
        self.insert_new_button = ctk.CTkButton(self,
                                               text="Upload from files",
                                               font=("Arial", 30),
                                               width=350,
                                               height=150,
                                               command=self.insert_new
                                               )
        # Button to go back to the previous screen (without saving the timeline)
        self.back_button = ctk.CTkButton(self,
                                         text="Back",
                                         font=("Arial", 15),
                                         corner_radius=3,
                                         command=self.back)
        # Button to commit changes to the database
        self.save_button = ctk.CTkButton(self,
                                         text="Save",
                                         font=("Arial", 15),
                                         corner_radius=3,
                                         command=self.save)

        # The following labels are to be displayed if the validation fails for their field
        self.no_photos_label = ctk.CTkLabel(self,
                                            text="Timeline must have at least two photos",
                                            text_color="red")
        self.name_bad_length_label = ctk.CTkLabel(self,
                                                  text="Name must be between 1 and 20 characters long",
                                                  text_color="red")
        self.name_taken_label = ctk.CTkLabel(self, text="Name already in use",
                                             text_color="red")
        self.line_colour_bad_label = ctk.CTkLabel(self,
                                                  text="Colour must be red, green, yellow, blue, white, orange, pink, "
                                                       "black",
                                                  text_color="red")
        self.line_weight_bad_label = ctk.CTkLabel(self, text="Must be a numerical value between 0.5 and 20",
                                                  text_color="red")
        self.background_colour_bad_label = ctk.CTkLabel(self,
                                                        text="Colour must be red, green, yellow, blue, white, orange, "
                                                             "pink, black",
                                                        text_color="red")
        self.default_border_colour_bad_label = ctk.CTkLabel(self,
                                                            text="Colour must be red, green, yellow, blue, white, "
                                                                 "orange, pink, black",
                                                            text_color="red")
        self.default_border_weight_bad_label = ctk.CTkLabel(self,
                                                            text="Must be a numerical value between 0.5 and 10",
                                                            text_color="red"
                                                            )
        # Prefills the entry boxes with the values in the database
        # For example, if the name of the timeline is already set, it is put into the name box
        self.insert_existing_values()
        # Places everything
        self.place()

    def insert_existing_values(self):
        """
        Inserts all the existing values from the database into the entry boxes
        For example, if the name of the timeline is already set, it is put into the name box

        Returns
        -------

        """
        self.name_box.insert(index=1, string=database.get_timeline_name(self.timeline_id))
        self.line_colour_box.insert(index=0, string=database.get_timeline_line_colour(self.timeline_id))
        self.line_weight_box.insert(index=0, string=database.get_timeline_line_weight(self.timeline_id))
        self.background_colour_box.insert(index=0, string=database.get_timeline_background_colour(self.timeline_id))
        self.default_border_colour_box.insert(index=0,
                                              string=database.get_timeline_default_border_colour(self.timeline_id))
        self.default_border_weight_box.insert(index=0,
                                              string=database.get_timeline_default_border_weight(self.timeline_id))

    def save_timeline_to_database(self):
        """
        Saves all the data about the timeline to the database
        Note that this is different to the save method, which validates then calls this function

        Returns
        -------

        """
        # Gets all the values from the entry boxes to save to the timeline
        name = self.name_box.get()
        line_colour = self.line_colour_box.get()
        line_weight = self.line_weight_box.get()
        background_colour = self.background_colour_box.get()
        default_border_colour = self.default_border_colour_box.get()
        default_border_weight = self.default_border_weight_box.get()
        if name:
            database.set_timeline_name(self.timeline_id, name)
        # If nothing has been entered, the program fills in defaults
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
        """
        Tells the program what to do when the save button is clicked

        Returns
        -------

        """
        # Only does anything if the save is successfully validated
        if self.validate_save():
            # If the timeline does not have a thumbnail, the database automatically selects one from its photos
            if not database.has_thumbnail(self.timeline_id):
                database.auto_thumbnail(self.timeline_id)
            # Saves the timeline data to the database
            self.save_timeline_to_database()
            # Sets the new data modified of the timeline
            database.update_modified(self.timeline_id)
            # If the timeline was the placeholder, the program transfers it to a new timeline
            if self.timeline_id == 999:
                database.transfer_to_new_timeline()
                # Goes back to the homescreen if it was a new timeline
                self.root.show_frame("homescreen")
            # Otherwise, goes to the timeline view
            else:
                self.root.show_frame("timeline", self.timeline_id)

    def validate_save(self):
        """
        Validates the timeline save

        Returns
        -------
        True
            If the data entered by the user is acceptable
        False
            Otherwise

        """
        # By default, the data is accepted
        accept = True
        # If no photos have been added to the timeline, it is rejected
        if database.count_photos(self.timeline_id) < 2:
            accept = False
            # The corresponding message is then placed
            self.no_photos_label.grid(row=7, column=1)
        # Gets all the data in order to validate it
        name = self.name_box.get()
        line_colour = self.line_colour_box.get()
        line_weight = self.line_weight_box.get()
        background_colour = self.background_colour_box.get()
        default_border_colour = self.default_border_colour_box.get()
        default_border_weight = self.default_border_weight_box.get()
        # Checks if the name is an acceptable length (between 1 and 20 characters inclusive)
        if len(name) not in range(1, 21):
            self.name_bad_length_label.grid(column=2, row=1)
            accept = False
        else:
            self.name_bad_length_label.grid_forget()
        # Checks if the line colour is in the list of accepted colours
        # This is not case-sensitive
        # As it converts the input to lower case and then checks it against other lower case things
        if line_colour.lower() not in ["", "red", "green", "yellow", "blue", "white", "orange", "pink", "black"]:
            self.line_colour_bad_label.grid(column=2, row=2)
            accept = False
        else:
            self.line_colour_bad_label.grid_forget()
        # The line weight must either be an empty string (in which case it is autofilled by the default)
        # Or it is a numerical value between 0.5 and 20
        # This statement checks accordingly
        if not (line_weight == "" or (line_weight.isnumeric() and 0.5 <= float(line_weight) <= 20)):
            self.line_weight_bad_label.grid(column=2, row=3)
            accept = False
        else:
            self.line_weight_bad_label.grid_forget()
        # Checks the background colour in the same manner as the line colour
        if background_colour.lower() not in ["", "red", "green", "yellow", "blue", "white", "orange", "pink", "black"]:
            self.background_colour_bad_label.grid(column=2, row=6)
            accept = False
        else:
            self.background_colour_bad_label.grid_forget()
        # Checks the default border colour in the same manner as the line colour
        if default_border_colour not in ["", "red", "green", "yellow", "blue", "white", "orange", "pink", "black"]:
            self.default_border_colour_bad_label.grid(column=2, row=4)
            accept = False
        else:
            self.default_border_colour_bad_label.grid_forget()
        # Checks the default border weight in the same manner as the line weight
        if not (default_border_weight == "" or (
                default_border_weight.isnumeric() and 0 <= float(default_border_weight) <= 20)):
            self.default_border_weight_bad_label.grid(column=2, row=5)
            accept = False
        else:
            self.default_border_weight_bad_label.grid_forget()

        return accept

    def back(self):
        """
        Tells the program what to do when the back button is clicked

        Returns
        -------

        """
        # If it was a new timeline being created, the program goes back to the homescreen
        if self.timeline_id == 999:
            self.root.show_frame("homescreen")
        # Otherwise, it goes back to the timeline view
        else:
            self.root.show_frame("timeline", self.timeline_id)

    def view_current(self):
        """
        Tells the program what to do when the user views wants to view the photos currently in the timeline

        Returns
        -------

        """
        # Temporarily saves the values entered into the database
        # So that when the user comes back, their progress has not been lost
        # This is without validation
        self.save_timeline_to_database()
        # Shows the appropriate screen
        self.root.show_frame("timeline_photos", self.timeline_id)

    def insert_existing(self):
        """
        Tells the program what to do when the user wishes to insert a photo from the gallery into the timeline

        Returns
        -------

        """
        # Saves progress on the entry boxes
        self.save_timeline_to_database()
        # Shows the screen from which photos are picked
        self.root.show_frame("photo_picker", self.timeline_id)

    def insert_new(self):
        """
        Tells the program what to do when the user wishes to upload a photo from their files

        Returns
        -------

        """
        # Saves entry box progress
        self.save_timeline_to_database()
        # Shows the screen from which a user can upload a photo
        self.root.show_frame("timeline_new_photo", self.timeline_id)

    def place(self):
        """
        Places all the widgets onto the frame

        Returns
        -------

        """
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
        self.insert_from_gallery_button.grid(row=8, column=1, pady=10, padx=20)
        self.insert_new_button.grid(row=8, column=2, pady=10, padx=20)
        self.save_button.grid(row=9, column=2, sticky="e")
        self.back_button.grid(row=9, column=0)


class PhotoGallery(ctk.CTkFrame):
    """
    Screen to view all the photos from: the photo gallery
    Can be filtered by timeline
    """

    def __init__(self, root, timeline_id=None):
        """
        Initialises an instance

        Parameters
        ----------
        root
            The instance of the parent
        timeline_id
            The ID of the timeline for which photos are being viewed
            If None, the user is viewing the whole image gallery
        """
        # self.active tags represents the list of tags that are currently being applied to filter the photos by
        self.active_tags = []
        # self.being_deleted tells the program if it is currently in delete mode
        self.being_deleted = False
        # self.thumbnail_being_selected tells the program if it is currently in select thumbnail mode
        self.thumbnail_being_selected = False
        # self.filter_placed tells the program if the filter dialogue is currently open
        self.filter_placed = False
        super().__init__(root)
        self.root = root
        # If the tick image is not already in the database, then the program adds it
        if not database.get_image_from_caption("tick"):
            database.add_image(from_default_set="tick")
        self.tick = database.get_image_from_caption("tick")
        self.timeline_id = timeline_id
        # Creates and places the button to turn delete mode on and off
        self.delete_toggle_button = ctk.CTkButton(self, text="Click to delete: off",
                                                  command=self.delete_toggle)
        self.delete_toggle_button.grid(column=1, row=0)
        # If a timeline ID has not been specified, the user is viewing the whole image gallery
        if not timeline_id:
            title = "All Images"
        else:
            # Otherwise, the user is viewing only the images of a certain timeline
            title = database.get_timeline_name(self.timeline_id)
            # Creates the button to turn thumbnail selecting mode on and off
            # This button is only created when it is a timeline being viewed
            self.select_thumbnail_button = ctk.CTkButton(self, text="Click to select thumbnail: off",
                                                         command=self.thumbnail_toggle)
            self.select_thumbnail_button.grid(column=0, row=0)

        self.title_text = ctk.CTkLabel(self,
                                       text=title,
                                       font=("Arial Bold", 35),
                                       pady=20
                                       )
        # Creates another frame in which to place the image
        # This is a scrollable frame
        # This allows the images to scroll independently to the rest of the screen
        self.image_frame = ctk.CTkScrollableFrame(self, width=self.winfo_screenwidth(),
                                                  height=int(self.winfo_screenheight() * 0.7))
        # Places the title
        self.title_text.grid(columnspan=5)
        # Places all the images into the image frame
        # The program calls the controller method 'get_photo_thumbnails_and_ids'
        # This gets it all the thumbnails of the photos and their IDs
        # This is then passed into the place_images method
        self.place_images(database.get_photo_thumbnails_and_ids(timeline_id=self.timeline_id))
        # Gets the plus image
        if not database.get_image_from_caption("plus"):
            database.add_image(from_default_set="plus")
        plus = database.get_image_from_caption("plus")
        # Button to open the filter dialogue
        self.filter_button = ctk.CTkButton(self, text="Filter", command=self.place_filter)
        self.filter_button.grid(column=0, row=1)
        # Frame for the filter dialogue
        self.filter = ctk.CTkScrollableFrame(self, bg_color="blue", fg_color="blue")
        # Label and combobox for the sorting dialogue
        self.sort_by_label = ctk.CTkLabel(self,
                                          text="Sort by:",
                                          font=("Arial", 13))
        self.sorter = ctk.CTkComboBox(self,
                                      values=["Photo ID", "Most used", "Date taken"],
                                      command=self.sort_request
                                      )
        # Places many of the items just initialised
        self.sort_by_label.grid(column=3, row=1)
        self.sorter.grid(column=4, row=1)
        self.pencil_image = ctk.CTkImage(light_image=Image.open(plus))
        self.add_image_button = ctk.CTkButton(self, image=self.pencil_image, command=self.add_image, text="")
        self.image_frame.grid(columnspan=5, sticky="ew")
        self.add_image_button.grid(column=4, row=3)
        # Button to enable 'back' functionality
        self.back_button = ctk.CTkButton(self, text="Back", command=self.back)
        self.back_button.grid(row=3, column=3)

    def filter_save_command(self):
        """
        Tells the program what to do when the 'save' button is clicked in the filter dialogue

        Returns
        -------

        """
        # Clears all the images in the image frame
        for widget in self.image_frame.winfo_children():
            widget.grid_forget()
        # Re-places all the images, according to the new filters
        self.place_images(database.get_photo_thumbnails_and_ids(timeline_id=self.timeline_id))
        # Re-places the filter
        self.place_filter()

    def sort_request(self, factor):
        """
        Tells the program what to do when an option is selected in the 'sort by' combobox

        Parameters
        ----------
        factor
            The factor by which to sort (e.g. "A-Z")

        Returns
        -------

        """
        # Clears all the images from the image frames
        self.forget_images()
        # Gets the sorted items, according to the factor and filtered by timeline ID (if it applies)
        sorted_items = database.get_photo_thumbnails_and_ids(sort_factor=factor, timeline_id=self.timeline_id)
        # Places the images according to these sorted items
        self.place_images(sorted_items)

    def forget_images(self):
        """
        Clears all the images from the image frame

        Returns
        -------

        """
        # Iterates through all the items in the image frame, clearing each
        for widget in self.image_frame.winfo_children():
            widget.grid_forget()

    def place_images(self, photo_thumbnails_and_ids):
        """
        Places the images in the image frame

        Parameters
        ----------
        photo_thumbnails_and_ids
            The sorted thumbnails of and corresponding IDs of each photo

        Returns
        -------

        """
        # If there are tags active, the thumbnails and IDs are filtered accordingly
        if self.active_tags:
            photo_thumbnails_and_ids = database.filter_thumbnails_and_ids(photo_thumbnails_and_ids, self.active_tags)
        # The count represents the image number. It decides where each image is placed
        count = 0
        # Iterates through the thumbnails and IDs, creating a button for each one
        for photo in photo_thumbnails_and_ids:
            # Note that photo[0] represents the photo data of the timeline thumbnail
            # photo[1] represents the timeline ID
            image = ctk.CTkImage(Image.open(photo[0]))
            # Sets the size of the thumbnail so that it fills up a fifth of the screen
            image.configure(size=[(self.winfo_screenwidth() - 50) / 5, (self.winfo_screenwidth() - 50) / 5])
            # Creates a button for the thumbnail
            # Note that the button is made to be the same size as the image
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
            # Places the button
            # The row is decided by integer division on the count
            # The column is decided by the remainder
            # This allows the program to lay the images out row-by-row in ascending order
            button.grid(column=count % 5, row=count // 5 + 1)
            # Increments the count
            count += 1

    def place_filter(self):
        """
        Tells the program what to do when the user presses the 'filter' button.
        In most cases, this will open the filter dialogue.
        If it is already open, it will close it.

        Returns
        -------

        """
        # If the filter has already been placed
        # The program clears the filter of its items then clears the filter itself
        if self.filter_placed:
            for widget in self.filter.winfo_children():
                widget.grid_forget()
            self.filter.grid_forget()
        else:
            # Places the filter dialogue frame
            self.filter.grid(column=1, row=1)
            # Creates and places the entry box to search tags
            self.tag_search_box = ctk.CTkEntry(self.filter)
            self.tag_search_box.grid(row=0)
            # Creates and places the button to perform the search
            self.tag_search_button = ctk.CTkButton(self.filter, text="Search", command=self.place_tags)
            self.tag_search_button.grid(row=1)
            # Creates the save button
            self.filter_save = ctk.CTkButton(self.filter, text="Save filters", command=self.filter_save_command)
            # Places the tags into the filter dialogue box
            self.place_tags()
        # Alternates the value of self.filter_places
        self.filter_placed = not self.filter_placed

    def forget_tags(self):
        """
        Clears the tags from the filter dialogue box

        Returns
        -------

        """
        # Iterates through all the widgets in the filter dialogue
        for widget in self.filter.winfo_children():
            # If the widget is a button, and it is not the save button, it is a filter
            # The save button has the place_tags command, so this specifies it
            # All such filters are cleared
            if isinstance(widget, ctk.CTkButton) and widget._command != self.place_tags:
                widget.grid_forget()

    def place_tags(self):
        """
        Places the tags into the filter dialogue

        Returns
        -------

        """
        # Clears the currently placed tags, if any
        self.forget_tags()
        # Places the save button for the filters
        self.filter_save.grid(row=2, pady=30)
        # If there's a value in the search filters box, this is grabbed
        search_key = self.tag_search_box.get()
        # Gets all the tag objects, filtered by the search key
        tags = database.get_tags(search_key=search_key)
        # Gets the tick image, used to indicate if a tag has been selected
        self.tick_image = ctk.CTkImage(light_image=Image.open(self.tick))
        # Iterates through each tag, creating a tag button for each
        for tag in tags:
            # If the tag is in the list of active tags, it is placed with a tick image
            if tag in self.active_tags:
                image = self.tick_image
            else:
                image = None
            # Each tag button calls the command which toggles if it is an active tag
            tag_button = ctk.CTkButton(self.filter,
                                       text=tag.name,
                                       command=partial(self.toggle_tag, tag),
                                       image=image,
                                       bg_color=tag.colour,
                                       fg_color=tag.colour,
                                       )
            # Places the tag
            # By default, the grid method simply places in the next available row down
            tag_button.grid()

    def toggle_tag(self, tag):
        """
        Tells the program what to do when a tag is clicked on
        Toggles its status from active to inactive or vice versa

        Parameters
        ----------
        tag
            The tag that has been clicked on, as a Tag object

        Returns
        -------

        """
        # If the tag is already active, it is made inactive
        # This is done by removing it from the list of active tags
        if tag in self.active_tags:
            self.active_tags.remove(tag)
        # If the tag is not currently inactive, it is made active
        else:
            self.active_tags.append(tag)
        # The tags are replaced, according to the new list of active tags
        self.place_tags()

    def fill_filter_frame(self):
        ...

    def add_image(self):
        """
        Tells the program what to do when the user presses the add image button

        Returns
        -------

        """
        # Shows the screen where a user can upload a photo
        self.root.show_frame("timeline_new_photo", self.timeline_id)

    def back(self):
        """
        Tells the program what to do when the user presses the back button

        Returns
        -------

        """
        # If there is a timeline ID, the screen came from a timeline so this timeline is reopened
        if self.timeline_id:
            self.root.show_frame("customise_timeline", self.timeline_id)
        # Otherwise, the program returns to the home screen
        else:
            self.root.show_frame("homescreen")

    def open_image(self, id):
        """
        Tells the program what to do when the user clicks on an image from the gallery

        Parameters
        ----------
        id
            The ID of the image that was clicked on

        Returns
        -------

        """
        # If thumbnail select mode is on, clicking an image selects it as a thumbnail
        if self.thumbnail_being_selected:
            database.add_thumbnail_to_timeline(id, self.timeline_id)
        # If delete mode is on and this is a timeline gallery, clicking an image removes it from the timeline
        elif self.being_deleted and self.timeline_id:
            database.delete_photo_from_timeline(id, self.timeline_id)
            # The images are then re-placed, without the removed image
            self.sort_request(factor=None)
        # If delete mode is on but this is not a timeline gallery, clicking an image deletes it from the database
        elif self.being_deleted:
            database.drop_photo(id)
            # The images are then re-placed, without the removed image
            self.sort_request(factor=None)
        else:
            # Otherwise, nothing special happens and clicking on an image opens it for viewing
            self.root.show_frame("view_photo", id, self.timeline_id)

    def delete_toggle(self):
        """
        Tells the program what to do when the user selects the deleting button
        Toggles deleting mode

        Returns
        -------

        """
        # If delete mode is on, it is turned off
        if self.being_deleted:
            self.being_deleted = False
            # The deleting button is reconfigured accordingly
            self.delete_toggle_button.configure(require_redraw=True, text="Click to delete: off")
        # Otherwise, it is turned on
        else:
            self.being_deleted = True
            # The deleting button is reconfigured accordingly
            self.delete_toggle_button.configure(require_redraw=True, text="Click to delete: on")
            # Thumbnail select mode and deleting mode cannot both be on simultaneously
            # So if the thumbnail select mode is on when the deleting mode is turned on
            # The thumbnail select mode is turned off
            if self.thumbnail_being_selected:
                self.thumbnail_toggle()

    def thumbnail_toggle(self):
        """
        Tells the program what to do when the user clicks on the selecting thumbnail button
        Toggles thumbnail selecting mode

        Returns
        -------

        """
        # If the thumbnail selecting mode is on, it is turned off
        if self.thumbnail_being_selected:
            self.thumbnail_being_selected = False
            # The thumbnail select button is updated accordingly
            self.select_thumbnail_button.configure(require_redraw=True, text="Selecting thumbnail: off")
        # If the thumbnail selecting mode is off, it is turned on
        else:
            self.thumbnail_being_selected = True
            # The thumbnail select button is updated accordingly
            self.select_thumbnail_button.configure(require_redraw=True, text="Selecting thumbnail: on")
            # Thumbnail select mode and deleting mode cannot both be on simultaneously
            # So if the deleting mode is on when the thumbnail select mode is turned on
            # The deleting mode is turned off
            if self.being_deleted:
                self.delete_toggle()


class PhotoPicker(PhotoGallery):
    """
    Class for picking a photo to add to a timeline
    Inherits from PhotoGallery: it is the same, but open_image is different
    This is an example of polymorphism
    """

    def __init__(self, root, timeline_id):
        """
        Initialises an object

        Parameters
        ----------
        root
            The instance of the parent
        timeline_id
            The ID for which the timeline is being picked
        """
        super().__init__(root)
        self.timeline_id = timeline_id

    def open_image(self, id):
        """
        Tells the program what to do when an image is clicked on
        Overrides the previous method

        Parameters
        ----------
        id
            The ID of the photo that was clicked on

        Returns
        -------

        """
        # If the clicked image was already in the timeline, it is removed
        if database.image_in_timeline(id, self.timeline_id):
            database.remove_image_from_timeline(id, self.timeline_id)
        # Otherwise, it is added to the timeline
        else:
            database.add_image_to_timeline(id, self.timeline_id)

    def back(self):
        """
        Tells the program what to do when the back button is clicked
        Overrides the previous method

        Returns
        -------

        """
        # Shows the timeline customisation screen
        self.root.show_frame("customise_timeline", id=self.timeline_id)


class TimelineView(ctk.CTkFrame):
    """
    A class for the screen where the user can view a timeline
    """

    def __init__(self, root, timeline_id):
        """
        Initialises an object

        Parameters
        ----------
        root
            The instance of the parent
        timeline_id
            The ID of the timeline to de displayed
        """
        super().__init__(root)
        self.root = root
        self.timeline_id = timeline_id
        # self.combobox_packed tells the program if the combobox for the zoom is visible
        # By default, the zoom combobox is not placed
        self.combobox_packed = False
        # Gets all the information for the timeline from the controller
        self.name = database.get_timeline_name(timeline_id)
        self.thumbnail_photo_id = database.get_timeline_thumbnail_photo_id(timeline_id)
        self.date_modified = database.get_timeline_date_modified(timeline_id)
        self.background_colour = database.get_timeline_background_colour(timeline_id)
        self.line_colour = database.get_timeline_line_colour(timeline_id)
        self.line_weight = database.get_timeline_line_weight(timeline_id)
        self.default_border_colour = database.get_timeline_default_border_colour(timeline_id)
        self.default_border_weight = database.get_timeline_default_border_weight(timeline_id)
        # Decides what text colour will be used in the timeline
        self.text_colour = self.decide_text_colour()
        # Sets the screen height in tkinter canvas units
        # There is a discrepancy between the canvas units and other units in certain cases
        # So it must be adjusted by multiplying by the dpi scale factor
        # This adjusts it to run parallel with a set reference point
        # It is multiplied by 0.85 to make sure it doesn't obstruct the screen's toolbar
        self.screen_height = self.root.winfo_screenheight() * self.root.dpi_scale_factor * 0.85
        self.screen_width = self.root.winfo_screenwidth() * self.root.dpi_scale_factor
        # Creates the scrollbar for the timeline
        self.scrollbar = ctk.CTkScrollbar(self, orientation="horizontal", width=self.screen_width)
        # Places the canvas, upon which is placed the timeline
        self.place_canvas()
        # Places the scrollbar
        self.scrollbar.pack(side="bottom")
        # Creates the title and places it in the middle top of the screen
        self.title_text = ctk.CTkLabel(self, text=self.name, font=("Arial", 30), text_color=self.text_colour,
                                       bg_color=self.background_colour)
        self.title_text.place(relx=0.45, y=5)
        # Gets the pencil, magnifying glass and home icons from the controller
        if not database.get_image_from_caption("pencil"):
            database.add_image(from_default_set="pencil")
        if not database.get_image_from_caption("magnifying glass"):
            database.add_image(from_default_set="magnifying glass")
        magnifying_glass = database.get_image_from_caption("magnifying glass")
        pencil = database.get_image_from_caption("pencil")
        if not database.get_image_from_caption("home"):
            database.add_image(from_default_set="home")
        home = database.get_image_from_caption("home")
        # Creates the corresponding ctk images
        self.pencil_image = ctk.CTkImage(light_image=Image.open(pencil))
        self.magnifying_glass_image = ctk.CTkImage(light_image=Image.open(magnifying_glass))
        self.home_image = ctk.CTkImage(light_image=Image.open(home))
        # Creates the corresponding buttons for each functionality, using the icons
        # Each button is small and round, creating an icon effect
        # Button to edit the timeline
        self.edit_button = ctk.CTkButton(self,
                                         corner_radius=40,
                                         bg_color=self.background_colour,
                                         width=30,
                                         height=30,
                                         text="",
                                         image=self.pencil_image,
                                         command=partial(self.root.show_frame, "customise_timeline", self.timeline_id))
        # Button to zoom the timeline
        self.zoom_button = ctk.CTkButton(self,
                                         corner_radius=40,
                                         bg_color=self.background_colour,
                                         width=30,
                                         height=30,
                                         text="",
                                         image=self.magnifying_glass_image,
                                         command=self.zoom)
        # Button to go back to the homescreen
        self.home_button = ctk.CTkButton(self,
                                         corner_radius=40,
                                         bg_color=self.background_colour,
                                         width=30,
                                         height=30,
                                         text="",
                                         image=self.home_image,
                                         command=partial(self.root.show_frame, "homescreen"))
        # Combobox to create the zoom factor
        self.zoom_combobox = ctk.CTkComboBox(self,
                                             values=["50%", "100%", "150%", "200%", "250%", "300%", "1000%"],
                                             command=self.zoom_command,
                                             )
        # By default, the zoom is 100%
        self.zoom_combobox.set("100%")
        # Places all the buttons using coordinates in the bottom right of the screen
        # DPI scale factor is not used because these are not canvas items
        self.edit_button.place(x=self.winfo_screenwidth() * 0.9, y=self.winfo_screenheight() * 0.8)
        self.zoom_button.place(x=self.winfo_screenwidth() * 0.95, y=self.winfo_screenheight() * 0.8)
        self.home_button.place(x=self.winfo_screenwidth() * 0.85, y=self.winfo_screenheight() * 0.8)

    def decide_text_colour(self):
        """
        Decides what text colour to use in the timeline, so that it does not blend into items

        Returns
        -------
        The colour to be used, in string format

        """
        # If the background colour is black, text is made white
        if self.background_colour.lower() == "white":
            return "black"
        # Grey background colour means blue
        elif self.background_colour.lower() == "grey":
            return "blue"
        # Black background colour means white
        elif self.background_colour.lower() == "black":
            return "white"
        # Anything else means grey
        else:
            return "grey"

    def zoom(self):
        """
        Tells the program what to do when the zoom button is clicked on

        Returns
        -------

        """
        # If the combobox is already visible, it is cleared
        if self.combobox_packed:
            self.zoom_combobox.pack_forget()
        # Otherwise, it is placed, and the canvas is replaced, so that they do not overlap
        else:
            self.canvas.pack_forget()
            self.zoom_combobox.pack(side="top")
            self.canvas.pack(side="top")
        # Changes the status of the combobox_packed variable
        self.combobox_packed = not self.combobox_packed

    def zoom_command(self, zoom):
        """
        Tells the program what to do when a value is selected in the zoom combobox

        Parameters
        ----------
        zoom
            The value selected in the zoom combobox (e.g. 200%)

        Returns
        -------

        """
        # Converts the string value of zoom into a proportion
        zoom = int(zoom[:-1]) / 100
        # Clears the screen of the canvas
        self.canvas.pack_forget()
        # Re-places the canvas, in a zoomed version
        self.place_canvas(zoom)
        # Reshuffles the layers so that the icons are on top of the canvas
        self.home_button.tkraise()
        self.edit_button.tkraise()
        self.zoom_button.tkraise()
        self.title_text.tkraise()
        self.zoom_combobox.tkraise()

    def place_canvas(self, scale: float = 1):
        """
        Places the canvas and its items

        Parameters
        ----------
        scale
            The scale with which to place the canvas
            e.g. scale=1 means the canvas will be placed with normal proportions
                 scale=2 means that the gap between January and February will be twice as large

        Returns
        -------

        """
        # Creates the canvas
        self.canvas = ctk.CTkCanvas(self, width=self.screen_width,
                                    height=self.screen_height,
                                    background=self.background_colour,
                                    # Sets the scroll to be managed by the scrollbar
                                    xscrollcommand=self.scrollbar.set,
                                    # Sets the region which can be scrolled to
                                    scrollregion=(-16000 * scale, self.screen_height, 16000 * scale, 0),
                                    )
        # Creates the line for the timeline
        # The bottom left corner of the timeline rectangle is at:
        # 5000 pixels multiplied by the scale to the left
        # And the line weight multiplied by 5 below the horizontal centre
        # Other corners are set similarly
        self.canvas.create_polygon((-16000 * scale, self.screen_height / 2 - self.line_weight * 5),
                                   (-16000 * scale, self.screen_height / 2 + self.line_weight * 5),
                                   (16000 * scale, self.screen_height / 2 + self.line_weight * 5),
                                   (16000 * scale, self.screen_height / 2 - self.line_weight * 5),
                                   fill=self.line_colour,
                                   )
        # Gets the photos and their corresponding IDs for the timeline
        photos_and_ids = database.get_photos_and_ids(self.timeline_id)
        # Gets the list of x-coordinates and the list of month markers from the controller, inputting the scale
        x_coords_dict, dates = database.get_x_coords(self.timeline_id, scale)
        # Sets the y-coordinates only when the scale is 1, which occurs when the timeline is opened
        # This means that the user zooming will not make the y-coordinates jump about
        if scale == 1:
            self.y_coords_dict = database.easy_space_coords_out(x_coords_dict, self.screen_height / 2)
        # Iterates through the list of photos and photo IDs
        for photo in photos_and_ids:
            photo_id = photo[1]
            # Finds the aspect ratio (width:height)
            aspect_ratio = Image.open(photo[0]).size[0] / Image.open(photo[0]).size[1]
            # Expands the ratio, making the height 90 but keeping the aspect ratio the same
            image = ctk.CTkImage(Image.open(photo[0]), size=(int(60 * aspect_ratio), 60), )
            # Creates an image button, which is how the program displays each image on the timeline
            self.button = SpecialButton(self.canvas,
                                        image=image,
                                        text="",
                                        # The command of the button is to open the image
                                        command=partial(self.open_image, photo[1]),
                                        # The width and height of the button are the same as the image
                                        width=image._size[0],
                                        height=image._size[1],
                                        fg_color="transparent",
                                        # The borders are set according to previous input
                                        border_width=self.default_border_weight,
                                        border_color=self.default_border_colour,
                                        corner_radius=0
                                        )
            # Gets the x and y coordinates from the dictionaries
            x = x_coords_dict[photo_id]
            y = self.y_coords_dict[photo_id]
            # Creates an item on the canvas with the image button
            self.canvas.create_window(x, y, window=self.button, tags=["image_button"])
            # Draws a line from the timeline to the image button
            self.canvas.create_line(x, y, x, self.screen_height / 2, width=self.line_weight, fill=self.line_colour)
        # This section places the markers (e.g. "February" or "2022")
        # Iterates through the list of markers and x-coordinates
        for marker in dates:
            # Only creates a label if there is actually text to show
            if marker[0] != "":
                self.label = ctk.CTkLabel(self.canvas,
                                          text=marker[0],
                                          text_color=self.text_colour)
            # Creates a canvas window with the label
            self.canvas.create_window(marker[1], self.screen_height / 2 - 50, window=self.label)
            # Creates a line from the timeline to the label
            self.canvas.create_line(marker[1], self.screen_height / 2 - 40, marker[1],
                                    self.screen_height / 2 - self.line_weight * 5, width=self.line_weight,
                                    fill=self.text_colour)
        # Configures the scrollbar so that it affects the canvas
        self.scrollbar.configure(command=self.canvas.xview)
        # Places the actual canvas
        self.canvas.pack(side="top")

    def open_image(self, id):
        """
        Tells the program what to do when an image is clicked on

        Parameters
        ----------
        id
            The ID of the image that was clicked upon

        Returns
        -------

        """
        # Shows the frame from which a photo can be viewed, also giving the timeline ID
        # This allows the timeline to be returned to from this frame
        self.root.show_frame("view_photo", id=id, secondary_id=self.timeline_id)


class ImportPhoto(ctk.CTkScrollableFrame):
    """
    Screen to import or edit the properties of a photo
    """

    def __init__(self, root, timeline_id=None, photo_id=None):
        """
        Initialises an object

        Parameters
        ----------
        root
            The instance of the parent class
        timeline_id
            The ID of the timeline to return to
        photo_id
            The ID of the photo
        """
        super().__init__(root)
        self.root = root
        self.timeline_id = timeline_id
        self.photo_id = photo_id
        self.file_path = None
        # Gets the tick image, needed for labelling tags
        if not database.get_image_from_caption("tick"):
            database.add_image(from_default_set="tick")
        self.tick = database.get_image_from_caption("tick")
        # self.temp_tags holds tags in the case that this is a new photo and cannot yet be attributed tags
        self.temp_tags = []
        # If this is a photo being edited, the title is View photo
        if self.photo_id:
            title = "View photo"
        # Otherwise, a new photo is being imported
        else:
            title = "Import photo"
        # Creates the label for the title
        self.title_text = ctk.CTkLabel(self,
                                       text=title,
                                       font=("Arial Bold", 35),
                                       pady=20
                                       )
        # Creates the label for the date taken entry box
        self.date_taken_text = ctk.CTkLabel(self,
                                            text="Date taken:",
                                            font=("Arial", 20),
                                            anchor="e"
                                            )
        # Creates the date taken entry box
        self.date_taken_box = ctk.CTkEntry(self,
                                           bg_color="grey",
                                           width=300)
        # Creates the label for the caption entry box
        self.caption_text = ctk.CTkLabel(self,
                                         text="Caption:",
                                         font=("Arial", 20),
                                         anchor="e"
                                         )
        # Creates the caption entry box
        self.caption_box = ctk.CTkEntry(self,
                                        bg_color="grey",
                                        width=300, )
        # Creates the button to open the file dialogue and upload a file
        self.upload_button = ctk.CTkButton(self,
                                           text="Upload",
                                           font=("Arial Bold", 35),
                                           width=700,
                                           height=300,
                                           command=self.photo_upload)
        # Creates the button to save the photo and its properties
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
        # Creates a label to be shown if the date validation fails
        self.date_not_good_box = ctk.CTkLabel(self,
                                              text="Please enter a valid date in format DD/MM/YYYY",
                                              text_color="red",
                                              font=("Arial", 10))

        self.photo_not_good_box = ctk.CTkLabel(self,
                                               text="Please upload a photo before saving",
                                               text_color="red",
                                               font=("Arial", 15)
                                               )
        # Creates a label to be shown if the caption validation fails
        self.caption_not_good_box = ctk.CTkLabel(self,
                                                 text="Please enter a caption before saving",
                                                 text_color="red",
                                                 font=("Arial", 10))
        # Creates a label for the tag name entry box
        self.tag_entry_label = ctk.CTkLabel(self, text="Tag name: ")
        # Creates the tag colour entry box
        self.tag_colour_label = ctk.CTkLabel(self, text="Tag colour: ")
        # Creates the tag name entry box
        self.tag_entry = ctk.CTkEntry(self)
        # Creates the tag colour entry box
        self.tag_colour_entry = ctk.CTkEntry(self)
        # Creates the button to add a tag, according to the values in the tag entry boxes
        self.add_tag_button = ctk.CTkButton(self, text="Add tag", command=self.add_tag)
        # Places everything
        self.place()
        # If this is editing a photo, the existing values are prefilled
        if self.photo_id:
            # This is done through the controller
            self.date_taken_box.insert(index=0, string=database.get_photo_date_taken(self.photo_id))
            self.caption_box.insert(index=0, string=database.get_photo_caption(photo_id))
            # Places the image in the screen
            self.show_image(self.photo_id)

    def add_tag(self):
        """
        Adds a tag to the database, according to the information in the entry boxes

        Returns
        -------

        """
        # Gets the tag name and colour
        tag_name = self.tag_entry.get()
        tag_colour = self.tag_colour_entry.get()
        # If both of these have been inputted by the user, the tag is added to the database
        if tag_name and tag_colour:
            tag_id = database.add_tag(tag_name, tag_colour)
            tag = database.get_tag(tag_id)
            # The tag is then added to the photo
            if self.photo_id:
                database.add_tag_to_photo(tag_id, self.photo_id)
            else:
                # If there is no photo yet, this tag is added to a temporary store
                self.temp_tags.append(tag)
        # Re-places the tags
        self.place_tags()

    def place(self):
        """
        Places the widgets

        Returns
        -------

        """
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
        # Places the tags
        self.place_tags()

    def forget_tags(self):
        """
        Clears all the tags from the screen

        Returns
        -------

        """
        # Goes through all the widgets
        for widget in self.winfo_children():
            # Checks if it is a tag by excluding all other possibilities
            if isinstance(widget, ctk.CTkButton) and widget._command not in [self.back,
                                                                             self.save,
                                                                             self.add_tag,
                                                                             self.photo_upload]:
                # Clears it from the screen
                widget.grid_forget()

    def place_tags(self):
        """
        Places all the tags on the screen, showing if they are added to the photo

        Returns
        -------

        """
        # First, clears all tags that might already be placed
        self.forget_tags()
        # Gets all the tags from the database
        tags = database.get_tags()
        self.tick_image = ctk.CTkImage(light_image=Image.open(self.tick))
        # Iterates through these tags
        for tag in tags:
            # Checks if the tags belong to the photo
            # This is true if:
            # There is already a photo, and it has these tags
            # Or, a new photo has been created and the tag is in the temporary store
            if self.photo_id and database.tag_in_photo(tag, self.photo_id) or tag in self.temp_tags:
                # If true, includes a tick in the tag button to show the user that it belongs to the photo
                image = self.tick_image
            else:
                image = None
            # Creates the widget for each individual tag
            tag_button = ctk.CTkButton(self,
                                       image=image,
                                       text=tag.name,
                                       command=partial(self.toggle_tag, tag),
                                       bg_color=tag.colour,
                                       fg_color=tag.colour,
                                       )
            # Places the tag button
            tag_button.grid()

    def toggle_tag(self, tag):
        """
        Tells the program what to do when a user clicks on a tag
        This means adding it to or removing it from the photo

        Parameters
        ----------
        tag
            The tag object, which's widget has been clicked on

        Returns
        -------

        """
        # If this is a photo being viewed and the tag is active, it is deactivated
        if self.photo_id and database.tag_in_photo(tag, self.photo_id):
            # This is done by changing the relationship in the database
            database.remove_tag_from_photo(tag.tag_ID, self.photo_id)
        # If this is a photo being created, and the tag is inactive, it is added to the temporary store
        elif not self.photo_id and tag not in self.temp_tags:
            self.temp_tags.append(tag)
        # If this is a photo being created, and the tag is active, it is removed from the temporary store
        elif not self.photo_id and tag in self.temp_tags:
            self.temp_tags.remove(tag)
        # Otherwise, the tag is added to the photo in the database
        else:
            database.add_tag_to_photo(tag.tag_ID, self.photo_id)
        # The tags are re-placed, reflecting these changed
        self.place_tags()

    def show_image(self, photo_id, filepath=None):
        """
        Shows an image once the user has uploaded it

        Parameters
        ----------
        photo_id
            The ID of the photo to be displayed
        filepath
            The filepath of the photo just uploaded

        Returns
        -------

        """
        # Gets the photo from the database
        photo = database.get_image_from_id(photo_id)
        # If this is a photo already in the system that is being viewed, it is placed as follows
        if photo:
            # Creates a ctk image for the photo
            photo = ctk.CTkImage(light_image=Image.open(photo),
                                 size=(250, 175))
            # Places this image in a label where the upload button was placed
            self.upload_button.grid_forget()
            ctk.CTkLabel(self,
                         image=photo, text=""
                         ).grid(row=3, column=0, columnspan=3, padx=60, pady=60)
        # If this is a new photo being uploaded, it has an associated filepath and is placed as follows
        elif filepath:
            # Creates a ctk image for the photo
            photo = ctk.CTkImage(light_image=Image.open(filepath), size=(250, 175))
            # Places it in plave of the upload button
            self.upload_button.grid_forget()
            ctk.CTkLabel(self, image=photo, text="", width=100, height=100).grid(row=3, column=0, columnspan=3, padx=60,
                                                                                 pady=60)

    def photo_upload(self):
        """
        Tells the program what to do when the upload button is clicked

        Returns
        -------

        """
        # Opens the file explorer, accepting common image filetypes
        self.file_path = askopenfile(mode='r',
                                     filetypes=[('Image Files', '*jpeg'), ('Image Files', '*jpg'),
                                                ('Image Files', '*png')])
        # Shows the image, with the new filepath
        self.show_image(photo_id=None, filepath=self.file_path.name)
        # Fills in the date taken entry box with the metadata
        self.fill_date_taken(self.file_path.name)

    def fill_date_taken(self, filepath):
        """
        Fills the date taken entry box with the photo metadata

        Parameters
        ----------
        filepath
            The filepath of the newly uploaded photo

        Returns
        -------

        """
        # Calls the controller to get the relevant metadata
        date_taken = database.get_date_taken(filepath)
        # Fills in the date taken entry box
        self.date_taken_box.insert(0, date_taken)

    def save(self):
        """
        Validates and saves the photo upload information inputted by the user.

        Returns
        -------

        """
        # By default, the save is not blocked. This is then changed if the inputs are rejected
        save_blocked = False
        # Gets the necessary values
        date_taken = self.date_taken_box.get()
        caption = self.caption_box.get()
        # Uses regex to match valid dates
        # This regex only matches dates in the form DD/MM/YYYY, from the year 0 to the year 2100
        # Anything past 2100 is deemed an invalid year
        # The expression matches (in order):
        # The start of the expression
        # A number from 0-3, then a number from 0-9 (representing the date)
        # 0 or 1, then a number from 0-9 (for the month)
        # Two digits from 00 to 20 followed by two digits from 0-9 (for the year)
        # The end of the string
        if not bool(re.match("^[0123][0-9]/[01][0-9]/(([01])[0-9]|(20))[0-9]{2}$", date_taken)) or not date_taken:
            # If this condition is not met, it is rejected by blocking the save and placing the appropriate label
            self.date_not_good_box.grid(row=1, column=2)
            save_blocked = True
        else:
            self.date_not_good_box.grid_forget()
        # Checks that there is a valid filepath or photo ID (there is a photo)
        if not self.file_path and not self.photo_id:
            # If this condition is not met, it is rejected by blocking the save and placing the appropriate label
            self.photo_not_good_box.grid(row=3, column=3)
            save_blocked = True
        else:
            self.photo_not_good_box.grid_forget()
        # The caption can be anything, so the program simply checks that there is a caption
        if not caption:
            # If this condition is not met, it is rejected by blocking the save and placing the appropriate label
            self.caption_not_good_box.grid(row=2, column=2)
            save_blocked = True
        else:
            self.caption_not_good_box.grid_forget()
        # If the save is not blocked, the program saves the information into the database as follows
        if not save_blocked:
            # Splits the date by the slashes into the day, month and year
            [day, month, year] = date_taken.split("/")
            # Creates a datetime object from these
            # The datetime validation catches the gaps in the above RegEx
            # This try except only goes through if the date passes the datetime validation
            try:
                date_taken = datetime.date(int(year), int(month), int(day))
            except:
                self.date_not_good_box.grid(row=1, column=2)
                return
            # If this is a new photo being created, the program uploads the photo into the database
            if not self.photo_id:
                new_photo_id = database.upload_photo(self.file_path.name, caption, date_taken)
                # The photo is then added to the timeline
                database.add_image_to_timeline(new_photo_id, self.timeline_id)
                # The temporary tag store is unloaded and all tags are added to the photo
                for tag in self.temp_tags:
                    print(tag)
                    database.add_tag_to_photo(tag.tag_ID, new_photo_id)
            # If this is a new photo and this is not for a specific timeline
            # The photo is just uploaded into the image gallery
            elif not (self.photo_id or self.timeline_id):
                database.upload_photo(self.file_path.name, caption, date_taken)
            # Otherwise, the new values are simply saved
            else:
                database.set_photo_caption(self.photo_id, caption)
                database.set_photo_date_taken(self.photo_id, date_taken)
            # The program exits the screen, returning to the previous
            self.back()

    def back(self):
        """
        Tells the program what to do when the back button is clicked
        Returns to the previous screen

        Returns
        -------

        """
        # If there is a timeline ID but not a photo ID, the previous screen was timeline customisation
        if self.timeline_id and not self.photo_id:
            self.root.show_frame("customise_timeline", self.timeline_id)
        # If there is a timeline ID and a photo ID, the previous screen was the timeline view
        elif self.timeline_id and self.photo_id:
            self.root.show_frame("timeline", self.timeline_id)
        # Otherwise, the previous screen was the photo gallery
        else:
            self.root.show_frame("photo_gallery")


# Creates an instance of the app
gui = App()
# Runs the GUI
gui.mainloop()
