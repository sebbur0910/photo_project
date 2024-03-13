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
            return_list.append([name, photo_data])

        return return_list

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

    def get_timeline_background_photo_id(self, id):
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id).first()
        if timeline and timeline.background_photo_ID:
            return timeline.background_photo_ID
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
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id).first()
        if timeline and timeline.default_border_colour:
            return timeline.default_border_colour
        else:
            return ""

    def get_timeline_default_border_weight(self, id):
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id).first()
        if timeline and timeline.default_border_weight:
            return timeline.default_border_weight
        else:
            return ""

    def create_timeline(self, name, thumbnail_photo_id, date_modified, background_photo_id, background_colour, line_colour,
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
        default_border_weight

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
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id)
        if timeline.first():
            timeline.update({Timeline.name: name})
            sess.commit()
        else:
            timeline = Timeline(timeline_ID=id, name=name)
            sess.add(timeline)
            sess.commit()

    def set_timeline_thumbnail_photo_id(self, id, thumbnail_photo_id):
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id)
        if timeline:
            timeline.update({Timeline.thumbnail_photo_ID: thumbnail_photo_id})
            sess.commit()
        else:
            timeline = Timeline(thumbnail_photo_ID=thumbnail_photo_id)
            sess.add(timeline)
            sess.commit()

    def set_timeline_date_modified(self, id, date_modified):
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id)
        if timeline:
            timeline.update({Timeline.date_modified: date_modified})
            sess.commit()
        else:
            timeline = Timeline(date_modified=date_modified)
            sess.add(timeline)
            sess.commit()

    def set_timeline_background_photo_id(self, id, background_photo_id):
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id)
        if timeline:
            timeline.update({Timeline.background_photo_ID: background_photo_id})
            sess.commit()
        else:
            timeline = Timeline(background_photo_ID=background_photo_id)
            sess.add(timeline)
            sess.commit()

    def set_timeline_background_colour(self, id, background_colour):
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id)
        if timeline:
            timeline.update({Timeline.background_colour: background_colour})
            sess.commit()
        else:
            timeline = Timeline(background_colour=background_colour)
            sess.add(timeline)
            sess.commit()

    def set_timeline_line_colour(self, id, line_colour):
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id)
        if timeline:
            timeline.update({Timeline.line_colour: line_colour})
            sess.commit()
        else:
            timeline = Timeline(line_colour=line_colour)
            sess.add(timeline)
            sess.commit()

    def set_timeline_line_weight(self, id, line_weight):
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id)
        if timeline:
            timeline.update({"line_weight": line_weight})
            sess.commit()
        else:
            timeline = Timeline(line_weight=line_weight)
            sess.add(timeline)
            sess.commit()

    def set_timeline_default_border_colour(self, id, default_border_colour):
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id)
        if timeline:
            timeline.update({Timeline.default_border_colour: default_border_colour})
            sess.commit()
        else:
            timeline = Timeline(default_border_colour=default_border_colour)
            sess.add(timeline)
            sess.commit()

    def set_timeline_default_border_weight(self, id, default_border_weight):
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == id)
        if timeline:
            timeline.update({"default_border_weight": default_border_weight})
            sess.commit()
        else:
            timeline = Timeline(default_border_weight=default_border_weight)
            sess.add(timeline)
            sess.commit()

    def has_photos(self, timeline_id):
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        return bool(timeline.photos_on_line)

    def has_thumbnail(self, timeline_id):
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        return bool(timeline.thumbnail_photo_ID)


    def auto_thumbnail(self, timeline_id):
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        first_photo_id = timeline.photos_on_line[0].photo_ID
        self.add_thumbnail_to_timeline(first_photo_id, timeline_id)

    def add_thumbnail_to_timeline(self, photo_id, timeline_id):
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        timeline.thumbnail_photo_ID = photo_id
        sess.commit()

    def make_blank_timeline(self):
        timeline = Timeline()
        sess.add(timeline)
        sess.commit()
        return timeline.timeline_ID

    def drop_timeline(self, timeline_id):
        sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).delete()
        sess.commit()

    def transfer_to_new_timeline(self):
        new_timeline_id = self.make_blank_timeline()
        self.drop_timeline(new_timeline_id)
        timeline_query = sess.query(Timeline).filter(Timeline.timeline_ID == 999)
        timeline = timeline_query.first()
        photos = [photo for photo in timeline.photos_on_line]
        timeline_query.update({"timeline_ID": new_timeline_id})
        timeline.photos_on_line += photos
        self.clear_photos(999)
        self.drop_timeline(999)
        sess.commit()

    def delete_photo_from_timeline(self, photo_id, timeline_id):
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
        timeline.photos_on_line.remove(photo)
        sess.commit()

    def clear_photos(self, timeline_id):
        photos = sess.query(Photo).all()
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        timeline.photos_on_line = []
        sess.commit()

    def get_thumbnail(self, id):
        thumbnail_id = sess.query(Timeline).filter(Timeline.timeline_ID == id).first().thumbnail_photo_ID
        photo = sess.query(Photo).filter(Photo.photo_ID == thumbnail_id).first()
        if photo:
            return io.BytesIO(photo.data)

    def get_x_coords(self, timeline_id, scale):
        self.showmonth = True
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        photos = timeline.photos_on_line
        sorted_dates = self.merge_sort([photo.date_taken for photo in photos], False)
      #  print(sorted_dates)
        most_recent = sorted_dates[0]
        least_recent = sorted_dates[-1]
        return_list = {}
        master_timedelta = most_recent - least_recent
        for photo in photos:
            timedelta = photo.date_taken - least_recent
            x_coord = (timedelta/master_timedelta)*1500*scale
            return_list[photo.photo_ID] = x_coord
        first_year = least_recent.year
        last_year = most_recent.year + 1
        incrementer = datetime.datetime(first_year-1,12,1)

        month_timedelta = datetime.timedelta(days=30)
        if (month_timedelta/master_timedelta)*8000*scale < 75:
            self.showmonth=False
        markers = []
        while incrementer <= datetime.datetime(last_year, 1, 1):
            incrementer = datetime.datetime((incrementer.year + incrementer.month // 12), ((incrementer.month % 12) + 1), 1)
            print(incrementer)
            if incrementer.month==1:
                label=incrementer.year
            elif self.showmonth:
                label=incrementer.strftime("%B")
                print(f"label: {label}")
            else:
                label=""
            timedelta = incrementer - least_recent
            x_coord = (timedelta/master_timedelta)*8000*scale
            markers.append( (label, x_coord))

        return return_list, markers

    def easy_space_coords_out(self, x_coords_dict, middle):
        y_dict = {}
        for id in x_coords_dict:
            y = middle + random.randint(100,300)*random.choice([-1, 1])
            y_dict[id] = y
        return y_dict

    def space_coords_out(self, x_coords_dict, tolerance):
        y_dict = {}
        for id in x_coords_dict:
            y=200
            for other_coord in x_coords_dict:
                if x_coords_dict[other_coord] in range(int(x_coords_dict[id])-tolerance, int(x_coords_dict[id])+tolerance) and id != other_coord:
                    y+=random.randint(100,400)
            y_dict[id] = y
         #   x_coords_dict.pop(id)
        return y_dict

    def timelines_exist(self):
        return bool(sess.query(Timeline).first())

    def timeline_exists(self, timeline_id):
        return bool(sess.query(Timeline).filter(Timeline.timeline_ID==timeline_id).first())


    def update_modified(self, timeline_id):
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        timeline.date_modified = datetime.datetime.now()

    def sort_timelines(self, factor):
        sorted_ids = None
        if factor == "A-Z":
            names = [timeline.name for timeline in sess.query(Timeline).filter(Timeline.timeline_ID != 999).all()]
            sorted_names = self.merge_sort(names, True)
            sorted_ids = [sess.query(Timeline).filter(Timeline.name == name).first().timeline_ID for name in
                          sorted_names]
        elif factor == "Z-A":
            names = [timeline.name for timeline in sess.query(Timeline).filter(Timeline.timeline_ID != 999).all()]
            sorted_names = self.merge_sort(names, False)
            sorted_ids = [sess.query(Timeline).filter(Timeline.name == name).first().timeline_ID for name in
                          sorted_names]
        elif factor == "Recently modified":
            dates = [timeline.date_modified for timeline in
                     sess.query(Timeline).filter(Timeline.timeline_ID != 999).all()]
            sorted_dates = self.merge_sort(dates, False)
            sorted_ids = [sess.query(Timeline).filter(Timeline.date_modified == date).first().timeline_ID for date in
                          sorted_dates]
        elif factor == "Favourites":
            ...
        return sorted_ids

    def merge_sort(self, items, reverse):
        length = len(items)

        if length == 1 or length == 0:
            return items

        else:
            first = self.merge_sort(items[:length // 2], reverse)
            second = self.merge_sort(items[length // 2:], reverse)
            sort = []

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

    def upload_photo(self, filepath, caption: str = None, date_taken: datetime.date = None):
        with open(filepath, 'rb') as file:
            binary_data = file.read()
        # need to add extra matadata (resolved i think)
        return self.add_image(data=binary_data, caption=caption, date_taken=date_taken)

    def add_image_to_timeline(self, photo_id, timeline_id):
        photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        if timeline and photo:
            timeline.photos_on_line.append(photo)
            sess.commit()

    def remove_image_from_timeline(self, photo_id, timeline_id):
        photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        timeline.photos_on_line.remove(photo)
        sess.commit()

    def image_in_timeline(self, photo_id, timeline_id):
        photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
        timeline = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first()
        return photo in timeline.photos_on_line

    def get_photo_thumbnails_and_ids(self, timeline_id=None, sort_factor=None):
        if sort_factor == "Most used":
            factor = Photo.num_uses
        elif sort_factor == "Date taken":
            factor = Photo.date_taken
        else:
            factor=None
        if not timeline_id:
            photos = sess.query(Photo).filter(Photo.date_taken != None).order_by(factor).all()
        elif sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first():
            photos = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first().photos_on_line
        else:
            return []
        return [[self.make_thumbnail(photo), photo.photo_ID] for photo in photos if photo]

    def filter_thumbnails_and_ids(self, thumbnails_and_ids, tags):
        return_list = []
        for item in thumbnails_and_ids:
            photo = sess.query(Photo).filter(Photo.photo_ID == item[1]).first()
            for tag in tags:
                if tag in photo.tags:
                    return_list.append(item)
        return return_list

    def get_photos_and_ids(self, timeline_id=None):
        if not timeline_id:
            photos = sess.query(Photo).all()
        elif sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first():
            photos = sess.query(Timeline).filter(Timeline.timeline_ID == timeline_id).first().photos_on_line
        else:
            return []
        return [[io.BytesIO(photo.data), photo.photo_ID] for photo in photos if photo]

    def get_photo_caption(self, id):
        photo = sess.query(Photo).filter(Photo.photo_ID == id).first()
        if photo and photo.caption:
            return photo.caption
        else:
            return ""

    def get_photo_date_taken(self, id):
        photo = sess.query(Photo).filter(Photo.photo_ID == id).first()
        if photo and photo.date_taken:
            date_taken = f"{photo.date_taken.strftime('%d')}/{photo.date_taken.strftime('%m')}/{photo.date_taken.year}"
            return date_taken
        else:
            return ""

    def get_photo_num_uses(self, id):
        photo = sess.query(Photo).filter(Photo.photo_ID == id).first()
        if photo and photo.num_uses:
            return photo.num_uses
        else:
            return ""

    def make_thumbnail(self, photo):
        photo = io.BytesIO(photo.data)
        photo = Image.open(photo)
        width, height = photo.size
        if width > height:
            photo = photo.resize((height, height))
        else:
            photo = photo.resize((width, width))
        stream = io.BytesIO()
        photo.save(stream, format='PNG')
        return io.BytesIO(stream.getvalue())

    def add_tag(self, name, colour):
        tag = Tag(name=name, colour=colour)
        sess.add(tag)
        sess.commit()
        return tag.tag_ID
    def add_tag_to_photo(self, tag_id, photo_id):
        tag = sess.query(Tag).filter(Tag.tag_ID == tag_id).first()
        photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
        photo.tags.append(tag)
        sess.commit()

    def remove_tag_from_photo(self, tag_id, photo_id):
        tag = sess.query(Tag).filter(Tag.tag_ID == tag_id).first()
        photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
        photo.tags.remove(tag)
        sess.commit()
    def get_tags(self, photo_id=None, search_key=""):
        if photo_id:
            photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
            tags = photo.tags
        else:
            tags = sess.query(Tag).all()
        tags = [item for item in tags if search_key.lower() in item.name.lower()]
        return tags

    def tag_in_photo(self, tag, photo_id):
        photo = sess.query(Photo).filter(Photo.photo_ID == photo_id).first()
        return tag in photo.tags

    def get_date_taken(self, filepath):
        metadata = Image.open(filepath)._getexif()
        date_string = metadata[36867]
        date = date_string.split(" ")[0]
        year, month, day = date.split(":")
        return f"{day}/{month}/{year}"

