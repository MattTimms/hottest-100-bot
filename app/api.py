from typing import Optional, Iterator

from fastapi import FastAPI, Depends, HTTPException
from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session

from app import main
from app.db.database import SessionLocal
from app.db.schema import Votes
from app.utils.models import SessionResults
from app.utils.logger import configure_logging

configure_logging()
app = FastAPI()


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
    """ Test endpoint to ensure deployment can use playwright correctly. """
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto("https://mylogin.abc.net.au/account/index.html#/signup")

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
