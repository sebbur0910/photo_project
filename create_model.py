from sqlalchemy import create_engine
from entities import Base

# Creates an SQL engine
engine = create_engine('sqlite:///database.sqlite', echo=True)
# Creates the tables form the entities
Base.metadata.create_all(engine)