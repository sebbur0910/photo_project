from sqlalchemy import create_engine
from entities import Base

engine = create_engine('sqlite:///database.sqlite', echo=True)
Base.metadata.create_all(engine)