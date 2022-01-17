import os

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .schema import Base

DB_URL = os.getenv('DB_URL')
DB_URL = DB_URL.replace('postgres://', 'postgresql://')  # fix for render's env vars
DB_URL = None  # quick disable the whole thing
logger.info(f"{DB_URL=}")


def _init_session_maker():
    if DB_URL is not None:
        engine = create_engine(DB_URL, echo=True)
        Base.metadata.create_all(bind=engine)
        return sessionmaker(autocommit=False, autoflush=False, bind=engine)
    else:
        return None


SessionLocal = _init_session_maker()



