from fastapi import FastAPI

from .main import vote, test_playwright

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "hello world"}


@app.get("/vote")
async def vote():
    response = vote()
    return {"data": response.json()}


@app.get("/test-playwright")
async def _test_playwright():
    test_playwright()
    return {"message": "test passed"}
