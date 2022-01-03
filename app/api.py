from fastapi import FastAPI

from app.main import vote, test_playwright
from app.logger import configure_logging

configure_logging()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "hello world"}


@app.get("/vote")
def vote():
    response = vote()
    return {"data": response.json()}


@app.get("/test-playwright")
def _test_playwright():
    test_playwright()
    return {"message": "test passed"}
