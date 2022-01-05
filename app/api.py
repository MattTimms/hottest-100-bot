from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app import main
from app.db.database import get_db
from app.db.schema import Votes
from app.utils.models import SessionResults
from app.utils.logger import configure_logging

configure_logging()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "hello world"}


@app.get("/vote")
def vote(db: Optional[Session] = Depends(get_db)):
    response = main.vote()
    if db:
        db_votes = Votes(**response.dict())
        db.add(db_votes)
        db.commit()
    return {"data": response.json()}


@app.get("/test-playwright")
def _test_playwright():
    main.test_playwright()
    return {"message": "test passed"}


@app.get("/test-db")
def _test_db(db: Optional[Session] = Depends(get_db)):
    db_votes = Votes(**SessionResults(email='test@gmail.com', firstname='john', surname='doe', password='pass',
                                      gender='Male', dob=1990, postcode=4000, phone='0412 345 678', votes=[]).dict())
    if db is None:
        raise HTTPException(status_code=404)
    db.add(db_votes)
    db.commit()
    db.delete(db_votes)
    db.commit()
    return {"message": "test passed"}
