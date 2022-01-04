from typing import Optional

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.main import vote, test_playwright
from app.db.database import get_db
from app.db.schema import Votes
from app.utils.logger import configure_logging

configure_logging()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "hello world"}


@app.get("/vote")
def vote(db: Optional[Session] = Depends(get_db)):
    response = vote()
    if db:
        db_votes = Votes(**response.dict())
        db.add(db_votes)
        db.commit()
    return {"data": response.json()}


@app.get("/test-playwright")
def _test_playwright():
    test_playwright()
    return {"message": "test passed"}
