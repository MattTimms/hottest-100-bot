from sqlalchemy import Column, String, Integer, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr

Base = declarative_base()


class Votes(Base):
    email = Column(String)
    password = Column(String)
    firstname = Column(String)
    surname = Column(String)
    gender = Column(String)
    dob = Column(Integer)
    postcode = Column(Integer)
    phone = Column(String)
    votes = Column(JSON)
    created_at = Column(DateTime(timezone=True), primary_key=True)
    src_addr = Column(String)

    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()
