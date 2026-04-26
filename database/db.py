from sqlalchemy import create_engine
from config.settings import DB_URL
from database.models import Base
from database import models

engine=create_engine(DB_URL, echo=False)

def init_db():
    Base.metadata.create_all(engine)
