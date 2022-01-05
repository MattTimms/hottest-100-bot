import os
from typing import Optional, Iterator

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .schema import Base

DB_URL = os.getenv('DB_URL')
DB_URL = DB_URL.replace('postgres://', 'postgresql://')
logger.info(f"{DB_URL=}")


def _init():
    if DB_URL is not None:
        engine = create_engine(DB_URL, echo=True)
        Base.metadata.create_all(bind=engine)
        return sessionmaker(autocommit=False, autoflush=False, bind=engine)
    else:
        return None


SessionLocal = _init()


# Dependency
def get_db() -> Iterator[Optional[Session]]:
    if SessionLocal is not None:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    else:
        yield None
