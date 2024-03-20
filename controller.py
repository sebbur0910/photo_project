import datetime
import random
from PIL import Image
from entities import Tag, Timeline, Base, Photo
from default_image_binary import default_images
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import io

engine = create_engine('sqlite:///database.sqlite', echo=False)
Base.metadata.create_all(engine)
sess = Session(engine)


class Database:

    def add_image(self, **kwargs):
        """
        This function adds an image to the database, taking keyword arguments for possible attributes of a photo
        object


        Parameters
        ----------
        kwargs:
            data
            caption
            name
            date_taken

        Returns
        -------
        photo.photo_ID
            the ID of the photo that has just been added to the database.

        """
        default_image = None
        if "from_default_set" in kwargs:
            default_image = kwargs.pop("from_default_set")

        if default_image:
            photo = Photo(
                caption=default_image,
                data=default_images[default_image])
            sess.add(photo)
            return "plus photo added"
        elif default_image == "settings":
            ...
        else:
            photo = Photo(num_uses=0)

            if "data" in kwargs:
                photo.data = kwargs.pop("data")

            if "caption" in kwargs:
                photo.caption = kwargs.pop("caption")

            if "name" in kwargs:
                photo.name = kwargs.pop("name")

            if "date_taken" in kwargs:
                photo.date_taken = kwargs.pop("date_taken")

            sess.add(photo)
            sess.commit()
            return photo.photo_ID

    def set_photo_caption(self, photo_id, caption):
        """
        Sets the caption in the database for a given photo, identified by the photo_id

        Parameters
        ----------
        photo_id
            The ID of the photo to be modified
        caption
            The desired new caption of the photo

        Returns
        -------

        """
        photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
        photo.caption = caption
        sess.commit()

    def set_photo_date_taken(self, photo_id, date_taken):
        """
        Sets the date_taken in the database for a given photo, identified by the photo_id

        Parameters
        ----------
        photo_id
            The ID of the photo to be modified
        date_taken
            The desired new date_taken of the photo

        Returns
        -------

        """
        photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
        photo.date_taken = date_taken
        sess.commit()

    def drop_photo(self, photo_id):
        """
        Deletes a photo entirely from the database

        Parameters
        ----------
        photo_id
            The ID of the photo to be deleted

        Returns
        -------

        """
        photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
        sess.delete(photo)
        sess.commit()
        # Makes sure that all the timelines still have enough images
        self.check_timelines_have_images()
        # Makes sure that all the timelines still have a valid thumbnail
        self.check_thumbnails()

    def check_timelines_have_images(self):
        """
        Checks that all the timelines in the database have a sufficient number of images
        If one does not, it is removed

        Returns
        -------

        """
        timelines = sess.query(Timeline).filter(Timeline.timeline_ID != 999).all()
        for timeline in timelines:
            if self.count_photos(timeline.timeline_ID) < 2:
                self.delete_timeline(timeline.timeline_ID)

    def check_thumbnails(self):
        """
        Checks that all the timelines in the database have valid thumbnails
        If not, it adds a valid thumbnail

        Returns
        -------

        """
        # Gets all the timelines apart from the temporary timeline
        timelines = sess.query(Timeline).filter(Timeline.timeline_ID != 999).all()
        # Goes through each, checking that its thumbnail ID references a valid photo
        for timeline in timelines:
            if not self.get_image_from_id(timeline.thumbnail_photo_ID):
                # If it does not, it automatically creates a thumbnail for the timeline
                self.auto_thumbnail(timeline.timeline_ID)

    def count_photos(self, timeline_id):
        """
        Counts the number of photos in a given timeline

        Parameters
        ----------
        timeline_id
            The ID of the timeline for which to count photos

        Returns
        -------
        The number of photos on the timeline

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        return len(timeline.photos_on_line)

    def get_image_from_caption(self, caption):
        """

        Parameters
        ----------
        caption
            The caption of the photo to be returned

        Returns
        -------
        io.BytesIO(image_binary)
            An IO bytestream of the binary code for the requested image
            Returned if an image exists with the specified caption

        False
            Boolean False value
            Returned if no image exists with the specified caption

        """
        plus_image = sess.query(Photo).filter(Photo.caption == caption).first()
        if plus_image:
            plus_image_binary = plus_image.data
            return io.BytesIO(plus_image_binary)
        return False

    def get_image_from_id(self, id):
        """

        Parameters
        ----------
        id
            The ID of the photo that is being requested.

        Returns
            io.BytesIO(image_binary)
                IO bytestream representing the raw binary of the requested image
        -------

        """
        if sess.query(Photo).filter(Photo.photo_ID == id).first():
            image_binary = sess.query(Photo).filter(Photo.photo_ID == id).first().data
            return io.BytesIO(image_binary)
        else:
            return None

    def get_thumbnails(self):
        """
        Queries all the thumbnails in the database, then iterates through their IDs
        For each timeline ID, grabs the associated name and binary of the thumbnail.

        Returns
        -------
        return_list
            Two dimensional list with each item representing the information for a timeline
            Each item contains 'name' and 'photo_data'
            The name represents the name of the timeline
            photo_data is a bytestream representing the binary of the timeline thumbnail.

        """
        return_list = []
        thumbnail_ids = [timeline.thumbnail_photo_ID for timeline in sess.query(Timeline).all()]

        for timeline_number in range(len(thumbnail_ids)):
            name = sess.query(Timeline)[timeline_number].name
            photo_data = sess.query(Photo).filter(Photo.photo_ID == thumbnail_ids[timeline_number]).first()
            if photo_data:
                photo_data = photo_data.data
                photo_data = io.BytesIO(photo_data)
            return_list.append((name, photo_data))

        return return_list

    def drop_timeline(self, timeline_id):
        """
        Deletes a timeline from the database

        Parameters
        ----------
        timeline_id
            The ID of the timeline to be deleted

        Returns
        -------

        """
        # Grabs the necessary timeline
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        # Clears all the photos from the timeline
        self.clear_photos(timeline.timeline_ID)
        # Deleted the timeline from the database
        sess.delete(timeline)
        sess.commit()

    def get_timeline_name(self, id):
        """
        Grabs the timeline name for a specified ID

        Parameters
        ----------
        id
            The ID of the requested timeline

        Returns
        -------
        timeline.name
            The name of the requested timeline
            Returned if there is a valid timeline associated with the ID

        Empty string
            Returned if there is no valid timeline associated with the ID

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id).first()
        if timeline and timeline.name:
            return timeline.name
        else:
            return ""

    def get_timeline_thumbnail_photo_id(self, id):
        """
        Grabs the timeline thumbnail photo ID for a specified ID

        Parameters
        ----------
        id
            The ID of the requested timeline

        Returns
        -------
        timeline.thumbnail_photo_ID
            The photo ID for the thumbnail of the requested timeline
            Returned if there is a valid timeline associated with the ID

        Empty string
            Returned if there is no valid timeline associated with the ID

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id).first()
        if timeline and timeline.thumbnail_photo_ID:
            return timeline.thumbnail_photo_ID
        else:
            return ""

    def get_timeline_date_modified(self, id):
        """
        Grabs the timeline date_modified for a specified ID

        Parameters
        ----------
        id
            The ID of the requested timeline

        Returns
        -------
        timeline.date_modified
            The date_modified of the requested timeline
            Returned if there is a valid timeline associated with the ID

        Empty string
            Returned if there is no valid timeline associated with the ID

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id).first()
        if timeline and timeline.date_modified:
            return timeline.date_modified
        else:
            return ""

    def get_timeline_background_colour(self, id):
        """
        Grabs the timeline background colour for a specified ID

        Parameters
        ----------
        id
            The ID of the requested timeline

        Returns
        -------
        timeline.background_colour
            The background colour of the requested timeline
            Returned if there is a valid timeline associated with the ID

        Empty string
            Returned if there is no valid timeline associated with the ID

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id).first()
        if timeline and timeline.background_colour:
            return timeline.background_colour
        else:
            return ""

    def get_timeline_line_colour(self, id):
        """
        Grabs the timeline line colour for a specified ID

        Parameters
        ----------
        id
            The ID of the requested timeline

        Returns
        -------
        timeline.line_colour
            The line colour of the requested timeline
            Returned if there is a valid timeline associated with the ID

        Empty string
            Returned if there is no valid timeline associated with the ID

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id).first()
        if timeline and timeline.line_colour:
            return timeline.line_colour
        else:
            return ""

    def get_timeline_line_weight(self, id):
        """
        Grabs the timeline line weight for a specified ID

        Parameters
        ----------
        id
            The ID of the requested timeline

        Returns
        -------
        timeline.line_weight
            The line weight of the requested timeline
            Returned if there is a valid timeline associated with the ID

        Empty string
            Returned if there is no valid timeline associated with the ID

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id).first()
        if timeline and timeline.line_weight:
            return timeline.line_weight
        else:
            return ""

    def get_timeline_default_border_colour(self, id):
        """
        Grabs the border colour of the photos in the timeline

        Parameters
        ----------
        id
            The timeline for which the information is to be accessed

        Returns
        -------

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id).first()
        if timeline and timeline.default_border_colour:
            return timeline.default_border_colour
        else:
            return ""

    def get_timeline_default_border_weight(self, id):
        """
        Grabs the border colour of the photos in the timeline

        Parameters
        ----------
        id
            The timeline for which the information is to be accessed

        Returns
        -------

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id).first()
        if timeline and timeline.default_border_weight or timeline.default_border_weight == 0:
            return timeline.default_border_weight
        else:
            return ""

    def create_timeline(self, name, thumbnail_photo_id, date_modified, background_photo_id, background_colour,
                        line_colour,
                        line_weight, default_border_colour, default_border_weight):
        """
        Provides an option to create a timeline all in one go, with every field filled.
        Different to individual setters because this is used for creating, rather than modifying

        Parameters
        ----------
        name
            The name of the timeline
        thumbnail_photo_id
            The ID of the photo to be used as a thumbnail for the timeline
        date_modified
            The date the timeline was last modified
        background_photo_id
        background_colour
            The background colour for the timeline
        line_colour
            The colour of the actual line
        line_weight
            The weight of the actual line
        default_border_colour
            The colour of the borders for the photos
        default_border_weight
            The weight of the borders for the photos

        Returns
        -------

        """
        timeline = Timeline(name=name, background_photo_ID=background_photo_id, background_colour=background_colour,
                            line_colour=line_colour,
                            line_weight=line_weight, default_border_colour=default_border_colour,
                            default_border_weight=default_border_weight, thumbnail_photo_ID=thumbnail_photo_id,
                            date_modified=date_modified)
        sess.add(timeline)
        sess.commit()

    def set_timeline_name(self, id, name):
        """
        Sets the name of the timeline specified by the id, creates a new timeline if one doesn't exist

        Parameters
        ----------
        id
            The id of the timeline to be updated
        name
            The desired name

        Returns
        -------

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id)
        # Adds to an existing timeline if one exists
        if timeline.first():
            timeline.update({Timeline.name: name})
            sess.commit()
        # Otherwise creates a new timeline
        else:
            timeline = Timeline(timeline_ID=id, name=name)
            sess.add(timeline)
            sess.commit()

    def set_timeline_thumbnail_photo_id(self, id, thumbnail_photo_id):
        """
        Sets the thumbnail photo ID of the timeline specified by the id, creates a new timeline if one doesn't exist

        Parameters
        ----------
        id
            The id of the timeline to be updated
        thumbnail_photo_id
            The desired thumbnail photo ID

        Returns
        -------

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id)
        # Adds to a timeline if one exists
        if timeline:
            timeline.update({Timeline.thumbnail_photo_ID: thumbnail_photo_id})
            sess.commit()
        # Otherwise creates a new timeline
        else:
            timeline = Timeline(thumbnail_photo_ID=thumbnail_photo_id)
            sess.add(timeline)
            sess.commit()

    def set_timeline_date_modified(self, id, date_modified):
        """
        Sets the date modified of the timeline specified by the id, creates a new timeline if one doesn't exist

        Parameters
        ----------
        id
            The id of the timeline to be updated
        date_modified
            The desired date modified

        Returns
        -------

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id)
        # Adds to a timeline if one exists
        if timeline:
            timeline.update({Timeline.date_modified: date_modified})
            sess.commit()
        # Otherwise creates a new timeline
        else:
            timeline = Timeline(date_modified=date_modified)
            sess.add(timeline)
            sess.commit()

    def set_timeline_background_colour(self, id, background_colour):
        """
        Sets the background colour of the timeline specified by the id, creates a new timeline if one doesn't exist

        Parameters
        ----------
        id
            The id of the timeline to be updated
        background_colour
            The desired background colour

        Returns
        -------

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id)
        if timeline:
            timeline.update({Timeline.background_colour: background_colour})
            sess.commit()
        else:
            timeline = Timeline(background_colour=background_colour)
            sess.add(timeline)
            sess.commit()

    def set_timeline_line_colour(self, id, line_colour):
        """
        Sets the line colour of the timeline specified by the id, creates a new timeline if one doesn't exist

        Parameters
        ----------
        id
            The id of the timeline to be updated
        line_colour
            The desired name

        Returns
        -------

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id)
        if timeline:
            timeline.update({Timeline.line_colour: line_colour})
            sess.commit()
        else:
            timeline = Timeline(line_colour=line_colour)
            sess.add(timeline)
            sess.commit()

    def set_timeline_line_weight(self, id, line_weight):
        """
        Sets the line weight of the timeline specified by the id, creates a new timeline if one doesn't exist

        Parameters
        ----------
        id
            The id of the timeline to be updated
        line_weight
            The desired line weight

        Returns
        -------

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id)
        if timeline:
            timeline.update({"line_weight": line_weight})
            sess.commit()
        else:
            timeline = Timeline(line_weight=line_weight)
            sess.add(timeline)
            sess.commit()

    def set_timeline_default_border_colour(self, id, default_border_colour):
        """
        Sets the border colour for the photos of the timeline specified by the id
        creates a new timeline if one doesn't exist

        Parameters
        ----------
        id
            The id of the timeline to be updated
        default_border_colour
            The desired border colour

        Returns
        -------

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id)
        if timeline:
            timeline.update({Timeline.default_border_colour: default_border_colour})
            sess.commit()
        else:
            timeline = Timeline(default_border_colour=default_border_colour)
            sess.add(timeline)
            sess.commit()

    def set_timeline_default_border_weight(self, id, default_border_weight):
        """
        Sets the border weight for the photos of the timeline specified by the id
        creates a new timeline if one doesn't exist

        Parameters
        ----------
        id
            The id of the timeline to be updated
        default_border_weight
            The desired border weight

        Returns
        -------

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id)
        if timeline:
            timeline.update({"default_border_weight": default_border_weight})
            sess.commit()
        else:
            timeline = Timeline(default_border_weight=default_border_weight)
            sess.add(timeline)
            sess.commit()

    def has_photos(self, timeline_id):
        """
        Checks if the timeline specified by the ID has any photos (or is blank)

        Parameters
        ----------
        timeline_id
            The ID of the timeline to be checked

        Returns
        -------
        True
            If the timeline has photos associated
        False
            If not

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        return bool(timeline.photos_on_line)

    def has_thumbnail(self, timeline_id):
        """
        Checks if the timeline specified by the ID has a thumbnail photo

        Parameters
        ----------
        timeline_id
            The ID of the timeline to be checked

        Returns
        -------
        True
            If the timeline has a thumbnail photo

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        return bool(timeline.thumbnail_photo_ID)

    def auto_thumbnail(self, timeline_id):
        """
        Sets the thumbnail of the specified timeline as the first photo in the timeline

        Parameters
        ----------
        timeline_id
            The ID of the timeline to be modified

        Returns
        -------

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        first_photo_id = timeline.photos_on_line[0].photo_ID
        self.add_thumbnail_to_timeline(first_photo_id, timeline_id)

    def add_thumbnail_to_timeline(self, photo_id, timeline_id):
        """
        Makes the thumbnail of the specified timeline the specified photo

        Parameters
        ----------
        photo_id
            The ID of the photo to become the thumbnail
        timeline_id
            The ID of the timeline to be modified

        Returns
        -------

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        timeline.thumbnail_photo_ID = photo_id
        sess.commit()

    def make_blank_timeline(self):
        """
        Creates a blank timeline (with no data)

        Returns
        -------
        timeline.timeline_ID
            The ID of the newly created timeline

        """
        timeline = Timeline()
        sess.add(timeline)
        sess.commit()
        return timeline.timeline_ID

    def delete_timeline(self, timeline_id):
        """
        Deletes the specified timeline from the database

        Parameters
        ----------
        timeline_id
            The ID of the timeline to be deleted

        Returns
        -------

        """
        sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).delete()
        sess.commit()

    def transfer_to_new_timeline(self):
        """
        Transfers all the data from timeline 999 (used as a placeholder) to a new timeline

        Returns
        -------

        """
        # Creates a new timeline and stores the associated ID, then deletes it.
        # This allows the algorithm to check the next available timeline ID.
        new_timeline_id = self.make_blank_timeline()
        self.delete_timeline(new_timeline_id)
        # Finds timeline 999 and stores its photos in the variable 'photos'
        timeline_query = sess.query(Timeline).filter(Timeline.timeline_ID == 999)
        timeline = timeline_query.first()
        photos = [photo for photo in timeline.photos_on_line]
        self.clear_photos(999)
        # Changes the ID of timeline 999 to the available ID, effectively transferring its data
        timeline_query.update({"timeline_ID": new_timeline_id})
        # Transfers the associated photos across, then clears timeline 999
        new_timeline = sess.query(Timeline).filter(Timeline.timeline_ID == new_timeline_id).first()
        new_timeline.photos_on_line += photos
        self.delete_timeline(999)
        sess.commit()

    def delete_photo_from_timeline(self, photo_id, timeline_id):
        """
        Deletes the specified photo from the specified timeline.

        Parameters
        ----------
        photo_id
            The ID of the photo to be deleted
        timeline_id
            The ID of the timeline to be deleted from

        Returns
        -------

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
        timeline.photos_on_line.remove(photo)
        sess.commit()

    def clear_photos(self, timeline_id):
        """
        Clears all the photos from the specified timeline

        Parameters
        ----------
        timeline_id
            The ID of the timeline to clear

        Returns
        -------

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        timeline.photos_on_line = []
        sess.commit()

    def get_thumbnail(self, timeline_id):
        """
        Gets the data of the thumbnail associated with the specified timeline.
        Parameters
        ----------
        timeline_id
            The ID of the timeline from which to retrieve the thumbnail

        Returns
        -------
        io.BytesIO(photo.data)
            An IO bytestream representing the binary of the thumbnail photo

        """
        thumbnail_id = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first().thumbnail_photo_ID
        photo = sess.query(Photo).filter(Photo.photo_ID == thumbnail_id).first()
        if photo:
            return io.BytesIO(photo.data)

    def get_x_coords(self, timeline_id, scale):
        """
        Calculates where images and date markers should be placed on the timeline view
        For the specified timeline, calculates the x-coordinates of all photos on the timeline and regular date markers

        Parameters
        ----------
        timeline_id
            The ID of the timeline for which to calculate coordinates
        scale
            The relative scale of the coordinates (allowing zooming)

        Returns
        -------
        photo_dict
            A dictionary, where the key is the ID of each photo, and the value is its x-coordinate
        markers
            A two-dimensional list for the date markers, where each element has two elements:
            The label (e.g. "February")
            Its corresponding x-coordinate (e.g. 864)

        """
        # Sets the show_month variable to True: by default, the timeline shows markers for the month
        self.show_month = True
        # Queries the database to find all the photos on the specified timeline
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        photos = timeline.photos_on_line
        # Sorts all the dates (as datetime objects) of these photos using the merge sort algorithm (see below)
        sorted_dates = self.merge_sort([photo.date_taken for photo in photos], False)
        # From this list, retrieves both ends of the range of dates
        # This allows x-coordinates to be calculated relative to the range
        most_recent = sorted_dates[0]
        least_recent = sorted_dates[-1]
        photo_dict = {}
        # Creates a timedelta (float representing a duration of time) representing the total range
        master_timedelta = most_recent - least_recent
        # Iterates through each of the photos
        for photo in photos:
            # Finds the duration between this photo and the least recent
            timedelta = photo.date_taken - least_recent
            # Finds this duration as a proportion of the range then scales to an x-coordinate
            x_coord = (timedelta / master_timedelta) * 1500 * scale
            # Adds to the photo_dict the ID of the photo and its corresponding x-coordinate
            photo_dict[photo.photo_ID] = x_coord

        # Now the algorithm does a similar thing for the date markers (e.g. "February" or "2021")
        first_year = least_recent.year
        last_year = most_recent.year + 1
        # Initialises the incrementer as the bottom of the range
        # This incrementer will increase a month at a time, in order to generate labels for each monthly interval
        incrementer = datetime.datetime(first_year - 1, 12, 1)
        month_timedelta = datetime.timedelta(days=30)
        # Checks if the month labels will squish together when displayed
        # Calculates the distance between month labels and checks if it is too small
        # If it is too small, self.show_month is set to False, telling the algorithm not the show months on the timeline
        if (month_timedelta / master_timedelta) * 8000 * scale < 75:
            self.show_month = False
        markers = []
        # Steps the incrementer up by a month at a time, until it reaches the end of the range
        while incrementer <= datetime.datetime(last_year, 1, 1):
            incrementer = datetime.datetime((incrementer.year + incrementer.month // 12),
                                            ((incrementer.month % 12) + 1), 1)
            # If the incrementer arrives a January, it outputs the year instead
            # e.g. "November", "December", "2021", "February"
            if incrementer.month == 1:
                label = incrementer.year
            # If show_month is True, the algorithm uses datetime methods to grab the month label
            elif self.show_month:
                label = incrementer.strftime("%B")
            else:
                label = ""
            # Again, calculates the x-coordinate by working out the timedelta as a proportion then scaling
            timedelta = incrementer - least_recent
            x_coord = (timedelta / master_timedelta) * 8000 * scale
            markers.append((label, x_coord))

        return photo_dict, markers

    def easy_space_coords_out(self, x_coords_dict, middle):
        """
        Generates y-coordinates for the images by randomising to create an organic look

        Parameters
        ----------
        x_coords_dict
            A dictionary containing the photo IDs and their x-coordinates (as returned by get_x_coords)
        middle
            The y-coordinate of the middle of the screen (where the timeline lies)

        Returns
        -------
        y-dict
            A dictionary, where the keys are the photo IDs and the values are their assigned y-coordinates

        """
        y_dict = {}
        for id in x_coords_dict:
            # Finds a random value betweeen 100 and 300, then randomly chooses if this value becomes negative
            # This means that images are placed either side of the timeline, between 100 and 300 pixels away
            y = middle + random.randint(100, 300) * random.choice([-1, 1])
            y_dict[id] = y
        return y_dict

    def timelines_exist(self):
        """
        Determines if there are any timeline in existence

        Returns
        -------
        True
            If there are any timelines in the database
        False
            Otherwise

        """
        return bool(sess.query(Timeline).first())

    def timeline_exists(self, timeline_id):
        """
        Determines if a timeline exists with the specified timeline ID

        Parameters
        ----------
        timeline_id
            The ID to check

        Returns
        -------
        True
            If a timeline exists with the specified ID
        False
            Otherwise

        """
        return bool(sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first())

    def update_modified(self, timeline_id):
        """
        Tells the database that a timeline has just been modified by updating the date modified to now

        Parameters
        ----------
        timeline_id
            The ID of the timeline that has just been modified

        Returns
        -------

        """
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        timeline.date_modified = datetime.datetime.now()
        sess.commit()

    def sort_timelines(self, factor):
        """
        Sorts all the timelines in the database according to the factor to be sorted by

        Parameters
        ----------
        factor
            The factor to sort according to (e.g. "A-Z")

        Returns
        -------
        sorted_ids
            The IDs of the timelines, but sorted

        """
        # Initialises sorted_ids so that the return statement never calls a nonexistent variable
        sorted_ids = None
        if factor == "A-Z":
            # Grabs all the timeline names, then calls merge sort to sort them
            # The parameter 'reverse' is set to True in the merge_sort because it must sort in descending order
            # A-Z is equivalent to going from lower values to higher values
            names = [timeline.name for timeline in sess.query(Timeline).filter(Timeline.timeline_ID != 999).all()]
            sorted_names = self.merge_sort(names, True)
            # Uses list comprehension to generate a list of ids from the list of timeline names
            sorted_ids = [sess.query(Timeline).filter(Timeline.name == name).first().timeline_ID for name in
                          sorted_names]
        elif factor == "Z-A":
            # The same is done for Z-A, but reverse is set to False
            names = [timeline.name for timeline in sess.query(Timeline).filter(Timeline.timeline_ID != 999).all()]
            sorted_names = self.merge_sort(names, False)
            sorted_ids = [sess.query(Timeline).filter(Timeline.name == name).first().timeline_ID for name in
                          sorted_names]
        elif factor == "Recently modified":
            # The same is done for recently modified
            # But the sorting is done for a list of dates, rather than a list of names
            # Note that datetime allows comparisons
            # Note also that reverse is set to False
            # This is because it is necessary to put the most recent dates (highest values) in front
            dates = [timeline.date_modified for timeline in
                     sess.query(Timeline).filter(Timeline.timeline_ID != 999).all()]
            sorted_dates = self.merge_sort(dates, False)
            sorted_ids = [sess.query(Timeline).filter(Timeline.date_modified == date).first().timeline_ID for date in
                          sorted_dates]
        elif factor == "Favourites":
            ...
        return sorted_ids

    def merge_sort(self, items, reverse):
        """
        Recursive merge sort algorithm
        Sorts a list by continually splitting it in half, then merging them while sorting
        This is acheived by repeatedly calling itself

        Parameters
        ----------
        items
            A list containing the items to be sorted
        reverse
            True if the list should be sorted lowest to highest
            False if the list should be sorted highest to lowest

        Returns
        -------
        sort
            The sorted list

        """
        length = len(items)

        # Base case: if the list of the items is a single element (or no element), the base case is hit
        # The item is returned as it is
        if length == 1 or length == 0:
            return items

        else:
            # Splits the list into two halves, then recursively calls itself
            first = self.merge_sort(items[:length // 2], reverse)
            second = self.merge_sort(items[length // 2:], reverse)
            sort = []
            # Once the base case is hit, this second half is executed
            # While there are items in the halves, combine the halves
            # This is done by continually adding the larger heads, which produces a sorted list
            while first or second:
                if not second:
                    sort.append(first.pop(0))
                elif not first:
                    sort.append(second.pop(0))
                elif (first[0] > second[0] and not reverse) or (first[0] < second[0] and reverse):
                    sort.append(first.pop(0))
                else:
                    sort.append(second.pop(0))

            return sort

    def upload_photo(self, filepath, caption: str = None, date_taken: datetime.datetime = None):
        """
        Uploads a photo to the database from the filepath

        Parameters
        ----------
        filepath
            The filepath of the photo to be uploaded
        caption
            The caption of the photo to be uploaded
        date_taken
            The date the photo was taken

        Returns
        -------
        The new photo ID of the item in the database

        """
        with open(filepath, 'rb') as file:
            binary_data = file.read()
        return self.add_image(data=binary_data, caption=caption, date_taken=date_taken)

    def add_image_to_timeline(self, photo_id, timeline_id):
        """
        Adds a specified image to the specified timeline

        Parameters
        ----------
        photo_id
            The ID of the photo to be added
        timeline_id
            The ID of the timeline to add to

        Returns
        -------

        """
        photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        if timeline and photo:
            timeline.photos_on_line.append(photo)
            photo.num_uses = photo.num_uses + 1
            sess.commit()

    def remove_image_from_timeline(self, photo_id, timeline_id):
        """
        Removes a specified image from the specified timeline

        Parameters
        ----------
        photo_id
            The ID of the photo to be removed
        timeline_id
            The ID of the timeline to remove from

        Returns
        -------

        """
        photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        timeline.photos_on_line.remove(photo)
        photo.num_uses = photo.num_uses - 1
        sess.commit()

    def image_in_timeline(self, photo_id, timeline_id):
        """
        Checks if the specified image is in the specified timeline

        Parameters
        ----------
        photo_id
            The ID of the photo to be checked
        timeline_id
            The ID of the timeline to be checked

        Returns
        -------
        True
            If the photo is in the timeline
        False
            Otherwise

        """
        photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        return photo in timeline.photos_on_line

    def get_photo_thumbnails_and_ids(self, timeline_id=None, sort_factor=None):
        """
        Gets all the sorted thumbnails (square-shaped previews) and ids of the photos

        Parameters
        ----------
        timeline_id
            The timeline ID to get photos from
            If None, the algorithm gets all available photos
        sort_factor
            The factor by which to sort the photo thumbnails and IDs

        Returns
        -------
        A list of thumbnails and the corresponding IDs of the photos
        """
        if sort_factor == "Most used":
            factor = Photo.num_uses
        elif sort_factor == "Date taken":
            factor = Photo.date_taken
        else:
            factor = None
        # If there is a timeline_id, the algorithm only grabs photos from that timeline
        # Otherwise, it grabs everything
        if not timeline_id:
            photos = sess.query(Photo).filter(Photo.date_taken != None).order_by(factor).all()
        elif sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first():
            photos = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first().photos_on_line
        else:
            return []
        # List comprehension to create a tuple list of thumbnails and photo IDs
        return [(self.make_thumbnail(photo), photo.photo_ID) for photo in photos if photo]

    def filter_thumbnails_and_ids(self, thumbnails_and_ids, tags):
        print(tags)
        """
        Filters thumbnails and IDs according to the given tags

        Parameters
        ----------
        thumbnails_and_ids
            The thumbnails and corresponding IDs to filter
        tags
            The tags to filter by

        Returns
        -------
        return_list
            A list containing only the thumbnails and corresponding IDs of the photos with the tags

        """
        return_list = []
        # Iterates through the photo thumbnails and IDs
        for item in thumbnails_and_ids:
            photo = sess.query(Photo).filter(Photo.photo_ID == item[1]).first()
            # Goes through each tag to check if the photo has any of the tags
            print(photo)
            print(photo.tags)
            if set(tags) <= set(photo.tags):
                # Only returns the photos and IDs which have all the tags
                return_list.append(item)
                print(return_list)
        return return_list

    def get_photos_and_ids(self, timeline_id=None):
        """
        Gets all the photo data BLOBs and IDs from the specified timeline
        If there is no specified timeline, then it will get all photos

        Parameters
        ----------
        timeline_id
            The ID of the timeline to get photo data from

        Returns
        -------
        A two-dimensional list, where the first elements are IO Bytestreams representing the photos
        And the second are IDs of the photos

        """
        if not timeline_id:
            photos = sess.query(Photo).all()
        elif sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first():
            photos = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first().photos_on_line
        else:
            return []
        return [[io.BytesIO(photo.data), photo.photo_ID] for photo in photos if photo]

    def get_photo_caption(self, id):
        """
        Gets the caption of a specified photo

        Parameters
        ----------
        id
            The ID of the photo from which to get the caption

        Returns
        -------
        The caption of the specified photo, if the specified photo exists
        Empty string otherwise

        """
        photo = sess.query(Photo).filter(Photo.photo_ID == id).first()
        if photo and photo.caption:
            return photo.caption
        else:
            return ""

    def get_photo_date_taken(self, id):
        """
        Gets the date taken of a specified photo

        Parameters
        ----------
        id
            The ID of the photo from which to get the caption

        Returns
        -------
        The date taken of the specified photo, if the specified photo exists
        Empty string otherwise

        """
        photo = sess.query(Photo).filter(Photo.photo_ID == id).first()
        if photo and photo.date_taken:
            date_taken = f"{photo.date_taken.strftime('%d')}/{photo.date_taken.strftime('%m')}/{photo.date_taken.year}"
            return date_taken
        else:
            return ""

    def get_photo_num_uses(self, id):
        """
        Gets the number of uses of a specified photo

        Parameters
        ----------
        id
            The ID of the photo from which to get the caption

        Returns
        -------
        The number of uses of the specified photo, if the specified photo exists
        Empty string otherwise

        """
        photo = sess.query(Photo).filter(Photo.photo_ID == id).first()
        if photo and photo.num_uses:
            return photo.num_uses
        else:
            return ""

    def make_thumbnail(self, photo):
        """
        Creates a thumbnail (square shaped preview) for a photo

        Parameters
        ----------
        photo
            A Photo object, to create a thumbnail from

        Returns
        -------
        An IO Bytestream of the resized photo in PNG format

        """
        # Creates a bytestream of the data
        photo = io.BytesIO(photo.data)
        photo = Image.open(photo)
        # Resizes the photo into a square by reducing the larger of width and height
        width, height = photo.size
        if width > height:
            photo = photo.resize((height, height))
        else:
            photo = photo.resize((width, width))
        # Creates a blank bytestream
        stream = io.BytesIO()
        # Saves the photo under the bytestream in PNG format
        photo.save(stream, format='PNG')
        # Gets the value of the stream then creates a seperate BytesIO object to return
        return io.BytesIO(stream.getvalue())

    def add_tag(self, name, colour):
        """
        Adds a new tag to the database

        Parameters
        ----------
        name
            The name of the new tag
        colour
            The colour of the new tag

        Returns
        -------
        The ID of the newly created tag

        """
        tag = Tag(name=name, colour=colour, num_uses=0)
        sess.add(tag)
        sess.commit()
        return tag.tag_ID

    def add_tag_to_photo(self, tag_id, photo_id):
        """
        Creates an association between an existing tag and photo

        Parameters
        ----------
        tag_id
            The ID of the tag
        photo_id
            The ID of the photo

        Returns
        -------

        """
        tag = sess.query(Tag).filter(Tag.tag_ID == tag_id).first()
        photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
        photo.tags.append(tag)
        tag.num_uses += 1
        sess.commit()

    def remove_tag_from_photo(self, tag_id, photo_id):
        """
        Removes an association between an existing tag and photo

        Parameters
        ----------
        tag_id
            The ID of the tag
        photo_id
            The ID of the photo

        Returns
        -------

        """
        tag = sess.query(Tag).filter(Tag.tag_ID == tag_id).first()
        photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
        photo.tags.remove(tag)
        tag.num_uses -= 1
        sess.commit()

    def get_tags(self, photo_id=None, search_key=""):
        """
        Gets all the tags associated with a photo containing a search key, or all tags if no photo is specified
        e.g. Gets all the tags containing the letters "hap" such as the tag named "happy"

        Parameters
        ----------
        photo_id
            The ID of the photo
        search_key
            A desired substring for the tags

        Returns
        -------
        tags
            A list of filtered tag objects

        """
        if photo_id:
            photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
            tags = photo.tags
        else:
            tags = sess.query(Tag).all()
        tags = [item for item in tags if search_key.lower() in item.name.lower()]
        return tags

    def tag_in_photo(self, tag, photo_id):
        """
        Checks if a photo contains the specified tag

        Parameters
        ----------
        tag
            A tag object to check
        photo_id
            The ID of the photo to check

        Returns
        -------
        True
            If the tag is in the photo
        False
            Otherwise

        """
        photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
        return tag in photo.tags

    def get_date_taken(self, filepath):
        """
        Uses EXIF information to grab the date taken from a photo specified by the filepath

        Parameters
        ----------
        filepath
            The filepath of the photo to get the data from

        Returns
        -------
        A string representing the date in form DD/MM/YYYY

        """
        # Gets all the metadata for the image
        metadata = Image.open(filepath)._getexif()
        # Accesses the datetime using the exif tag 36867
        date_string = metadata[36867]
        # Gets just the date, without the time
        date = date_string.split(" ")[0]
        # Gets and formats the day, month and year
        year, month, day = date.split(":")
        return f"{day}/{month}/{year}"
