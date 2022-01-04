import os
import re
import random
import string
from collections import namedtuple
from typing import List, Optional

import arrow
import names
import pandas as pd
import requests
from databases import Database
from loguru import logger
from playwright.sync_api import sync_playwright, Page
from pydantic import BaseModel, IPvAnyAddress

Song = namedtuple("Song", ['artist', 'track'])
target_songs = [Song(*x) for x in [
    ('Billie Eilish', 'Getting Older'),  # defaults to #1 track in vote
]]

database: Optional[Database] = None
if (DB_URL := os.getenv('DB_URL')) is not None:
    logger.info(DB_URL)
    database = Database(DB_URL)
    database.connect()


class Tempmailo:
    url = "https://tempmailo.com/"

    def __init__(self, page: Page):
        self.page = page
        self.page.goto("https://tempmailo.com/")
        self.email = self.page.eval_on_selector("input[type=\"text\"]", "el => el.value")

    def verify_email(self) -> Page:
        self.page.wait_for_timeout(5000)
        self.page.click("button:has-text(\"Refresh\")")
        self.page.click("text=Please complete your sign up")

        with self.page.expect_popup() as popup_info:
            self.page.frame(name="fullmessage").click("text=VERIFY EMAIL")

        self.page.wait_for_timeout(5000)
        self.page.click("button:has-text(\"Refresh\")")
        self.page.click("text=Welcome to your new ABC Account", timeout=60_000)
        with self.page.expect_popup() as popup_info:
            self.page.frame(name="fullmessage").click("text=LOG IN TO YOUR ACCOUNT")
        new_page = popup_info.value
        return new_page


def generate_password() -> str:
    # pw 6-50 chars, number, upper, & lower
    pattern = re.compile(r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{6,50}')

    password = ''
    length = random.randint(6, 50)
    while pattern.match(password) is None:
        password = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=length))
    return password


def get_postcode() -> int:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    df = pd.read_csv(os.path.join(dir_path, 'australian-postcodes-2021-04-23.csv'))
    return int(df.sample().Zip.values)


def get_ip() -> str:
    resp = requests.get('https://api.ipify.org?format=json')
    return resp.json().get('ip')


def get_phone_no() -> str:
    phone = "04## ### ###"
    n = phone.count('#')
    for _ in range(n):
        phone = phone.replace('#', str(random.randint(0, 9)), 1)
    return phone


class Account(BaseModel):
    email: str
    password: str
    firstname: str
    surname: str
    gender: str
    dob: int
    postcode: int
    phone: str

    @classmethod
    def generate(cls, email: str) -> 'Account':
        gender = random.choice(['Male', 'Female', 'Prefer not to say'])
        return cls(
            email=email,
            password=generate_password(),
            firstname=names.get_first_name(gender=gender.lower()),
            surname=names.get_last_name(),
            gender=gender,
            dob=random.randint(2021 - 30, 2021 - 18),
            postcode=get_postcode(),
            phone=get_phone_no(),
        )


class SessionResults(Account):
    votes: List[Song]
    created_at: arrow.Arrow = arrow.now()
    src_addr: IPvAnyAddress = get_ip()

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {arrow.Arrow: lambda x: x.for_json()}


def test_playwright():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)

        page = browser.new_page()

        page.goto("https://mylogin.abc.net.au/account/index.html#/signup")


def vote(headless=True) -> SessionResults:
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=headless)

        page = browser.new_page()

        page.goto("https://mylogin.abc.net.au/account/index.html#/signup")
        page.click("[data-testid=\"signup-with-email-btn\"]")

        email_client = Tempmailo(page=browser.new_page())
        account = Account.generate(email=email_client.email)
        logger.info(f"account={account.json()}")

        page.fill("[data-testid=\"email-field\"]", account.email)
        page.fill("[data-testid=\"password-field\"]", account.password)

        is_valid_email = page.query_selector("#email-error") is None
        is_valid_pass = page.query_selector("#password-error") is None

        if not (is_valid_email and is_valid_pass):
            raise ValueError("email or pass was bad")

        with page.expect_navigation():
            page.click("[data-testid=\"signup-with-email-btn\"]")

        logger.info("Sign-up page 1 - complete")

        page.fill("[data-testid=\"first-name-field\"]", account.firstname)
        page.fill("[data-testid=\"year-of-birth-field\"]", str(account.dob))

        page.click("text=Select gender identity")
        page.click(f"text={account.gender}")

        page.fill("[placeholder=\"Enter suburb or postcode\"]", str(account.postcode))
        page.click("#screen-location-field-menu > ul > li:nth-child(1)")

        # t's & c's
        page.click("rect")

        # Click [data-testid="create-account-btn"]
        # with page.expect_navigation(url="https://mylogin.abc.net.au/account/index.html#/signup-verification-sent"):
        with page.expect_navigation():
            page.click("[data-testid=\"create-account-btn\"]")

        logger.info("Sign-up page 2 - complete")

        new_page = email_client.verify_email()
        logger.info("Email verified")

        new_page.goto("https://www.abc.net.au/triplej/hottest100/21/")
        with new_page.expect_navigation():
            new_page.click("text=Vote Now")
        new_page.click("text=Search")

        for song in target_songs:
            new_page.fill("[placeholder=\"Enter the artist's name\"]", song.artist)
            new_page.fill("[placeholder=\"Enter the track title\"]", song.track)
            new_page.click(f"[aria-label=\"Add {song.track} by {song.artist} to your shortlist\"]")

        new_page.click("text=Submit Votes")
        new_page.fill("text=Last nameYour last name is required >> input[type=\"text\"]", account.surname)
        new_page.fill("text=Phone numberYour phone number is required >> input[type=\"text\"]", account.phone)
        new_page.check("text=Can we call you to chat on-air? (Required for competition entry)Yes >> input[type=\"checkbox\"]")
        new_page.query_selector("#recaptcha-element").query_selector('iframe').click()
        with new_page.expect_navigation():
            new_page.click("text=Complete Voting")

        logger.info("Vote complete")

    results = SessionResults(**account.dict(), votes=target_songs)
    logger.info(results.json())
    return results


if __name__ == '__main__':
    vote(headless=False)
