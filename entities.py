from sqlalchemy import Column, Integer, String, DateTime, BLOB, Table, UniqueConstraint, ForeignKey
from sqlalchemy.orm import declarative_base, validates, relationship
import re

Base = declarative_base()

timeline_photos = Table("timeline_photos",
                        Base.metadata,
                        Column("photo_ID", ForeignKey("photos.photo_ID")),
                        Column("timeline_ID", ForeignKey("timelines.timeline_ID")),
                        UniqueConstraint("photo_ID", "timeline_ID")
                        )

photo_tags = Table("photo_tags",
                   Base.metadata,
                   Column("photo_ID", ForeignKey("photos.photo_ID")),
                   Column("tag_ID", ForeignKey("tags.tag_ID")),
                   UniqueConstraint("photo_ID", "tag_ID")
                   )


class Photo(Base):
    __tablename__ = "photos"
    photo_ID = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(BLOB)
    date_taken = Column(DateTime)
    caption = Column(String)
    num_uses = Column(Integer)


    timelines = relationship("Timeline",
                             secondary=timeline_photos,
                             order_by="Timeline.timeline_ID",
                             back_populates="photos_on_line")

    tags = relationship("Tag",
                        secondary=photo_tags,
                        order_by="Tag.tag_ID",
                        back_populates="photos_with_tag")

    @validates("data")
    def validate_data(self, key, address):
        if not isinstance(address, bytes):
            raise TypeError("The data must be in bytes form")
        else:
            return address
    def __repr__(self):
        return f"Photo(photo_ID='{self.photo_ID}'," \
               f"date_taken={self.date_taken}), " \
               f"caption={self.caption}, " \
               f"num_uses={self.num_uses})"


class Tag(Base):
    __tablename__ = "tags"
    tag_ID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    colour = Column(String)
    num_uses = Column(Integer)

    @validates("name")
    def validate_name(self, key, address):
        if len(address) not in range(1, 21):
            raise ValueError("Tag name must be between 1 and 20 characters")
        return address

    @validates("colour")
    def validate_colour(self, key, address):
        if address not in ["red", "green", "yellow", "blue", "white", "orange", "pink"]:
            raise ValueError("Colour must be:\n red, green, yellow, blue, white, orange, pink")
        return address

    photos_with_tag = relationship("Photo",
                                   secondary=photo_tags,
                                   order_by="Photo.photo_ID",
                                   back_populates="tags")

    def __repr__(self):
        return f"Tag(tag_ID='{self.tag_ID}'," \
               f"name={self.name}), " \
               f"colour={self.colour}, " \
               f"num_uses={self.num_uses})"

    def tag_used(self):
        self.num_uses += 1


class Timeline(Base):
    __tablename__ = "timelines"
    timeline_ID = Column(Integer, primary_key=True)
    name = Column(String)
    thumbnail_photo_ID = Column(Integer)
    date_modified = Column(DateTime)
    background_photo_ID = Column(Integer)
    background_colour = Column(String)
    line_colour = Column(String)
    line_weight = Column(Integer)
    default_border_colour = Column(String)
    default_border_weight = Column(Integer)

    @validates("background_colour", "line_colour", "default_border_colour")
    def validate_background_colour(self, key, address):
        if not re.fullmatch("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", address):
            raise ValueError(f"{key} must be in hex colour code format")
        return address

    photos_on_line = relationship("Photo",
                                  secondary=timeline_photos,
                                  order_by="Photo.photo_ID",
                                  back_populates="timelines")

    def __repr__(self):
        return f"Timeline(timeline_ID='{self.timeline_ID}'," \
               f"name={self.name}), " \
               f"background_photo_ID={self.background_photo_ID}, " \
               f"background_colour={self.background_colour})" \
               f"line_colour={self.line_colour}, " \
               f"line_weight={self.line_weight}, " \
               f"default_border_colour={self.default_border_colour}, " \
               f"default_border_weight={self.default_border_weight}, "
