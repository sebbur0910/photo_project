from sqlalchemy import Column, Integer, String, DateTime, BLOB, Table, UniqueConstraint, ForeignKey
from sqlalchemy.orm import declarative_base, validates
import re

Base = declarative_base()


class Photo(Base):
    __tablename__ = "photos"
    photo_ID = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(BLOB)
    date_taken = Column(DateTime)
    caption = Column(String)
    num_uses = Column(Integer)


class Tag(Base):
    __tablename__ = "tags"
    tag_ID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    colour = Column(String)
    num_uses = Column(Integer)

    @validates("colour")
    def validate_colour(self, key, address):
        if address not in ["red", "green", "yellow", "blue", "white", "orange", "pink"]:
            raise ValueError("Colour must be:\n red, green, yellow, blue, white, orange, pink")
        return address


class Timeline(Base):
    __tablename__ = "timelines"
    timeline_ID = Column(Integer, primary_key=True)
    name = Column(String)
    background_photo_ID = Column(Integer)
    background_colour = Column(String)
    line_colour = Column(String)
    line_weight = Column(Integer)
    default_border_colour = Column(String)
    default_border_weight = Column(Integer)


timeline_photos = Table("timeline_photos",
                        Base.metadata,
                        Column("photo_ID", ForeignKey("photos.photo_ID")),
                        Column("timeline_ID", ForeignKey("timelines.timeline_ID")),
                        UniqueConstraint("photo_ID", "timeline_ID")
                        )

phototag = Table("photo_tags",
                 Base.metadata,
                 Column("photo_ID", ForeignKey("photos.photo_ID")),
                 Column("tag_ID", ForeignKey("tags.tag_ID")),
                 UniqueConstraint("photo_ID", "tag_ID")
                 )