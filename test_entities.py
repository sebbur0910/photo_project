import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from entities import Tag, Timeline, Base, Photo


@pytest.fixture()
def setup_db():
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)
    with Session(engine) as sess:
        yield sess

def test_photo(setup_db):
    photo = Photo(data=10101010101, date_taken="11/12/2021", caption="hello world", num_uses=0)
    assert photo.data == 10101010101

def test_tag(setup_db):
    tag = Tag(name="me", colour="pink", num_uses=0)
    assert tag.colour == "pink"

def test_timeline(setup_db):
    timeline = Timeline(name="tester", background_photo_ID=1, background_colour="#32a852", line_colour="#32a852",
                          line_weight=1, default_border_colour="#32a852", default_border_weight=1)
    assert timeline.background_colour == "#32a852"


def test_database(setup_db):
    sess = setup_db
    photo_1 = Photo(data=1, date_taken="11/12/2021", caption="hello world", num_uses=0)
    photo_2 = Photo(data=10, date_taken="11/12/2021", caption="hello world", num_uses=0)
    tag_1 = Tag(name="cars", colour="red", num_uses=0)
    tag_2 = Tag(name="people", colour="blue", num_uses=0)
    timeline_1 = Timeline(name="my life", background_photo_ID=1, background_colour="#32a852", line_colour="#32a852", line_weight=1, default_border_colour="#32a852", default_border_weight=1)
    timeline_2 = Timeline(name="my other life", background_photo_ID=2, background_colour="#32b852", line_colour="#32b852", line_weight=2, default_border_colour="#32b852", default_border_weight=2)
    photo_1.tags.append(tag_1)
    photo_1.tags.append(tag_2)
    photo_2.tags.append(tag_2)
    timeline_1.photos_on_line.append(photo_1)
    timeline_2.photos_on_line.append(photo_1)
    timeline_2.photos_on_line.append(photo_2)
    sess.add(photo_1)
    sess.add(photo_2)
    sess.add(tag_1)
    sess.add(tag_2)
    sess.add(timeline_1)
    sess.add(timeline_2)
    sess.commit()
    assert sess.query(Photo).count() == 2
    assert sess.query(Tag).count() == 2
    assert sess.query(Timeline).count() == 2
    assert photo_1.tags[0].name == "cars"
    assert len(photo_2.tags) == 1
    assert timeline_1.photos_on_line[0].data == 1
    assert timeline_2.photos_on_line[1].background_photo_ID == 2

