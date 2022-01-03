import os
import re
import random
import string
from collections import namedtuple
from typing import List

import names
import pandas as pd
from loguru import logger
from playwright.sync_api import sync_playwright, Page
from pydantic import BaseModel

Song = namedtuple("Song", ['artist', 'track'])
target_songs = [Song(*x) for x in [
    ('Billie Eilish', 'Getting Older'),  # defaults to #1 track in vote
]]


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

        self.page.click("text=Welcome to your new ABC Account")
        with self.page.expect_popup() as popup_info:
            self.page.frame(name="fullmessage").click("text=LOG IN TO YOUR ACCOUNT")
        new_page = popup_info.value
        # new_page.click("text=Continue to abc.net.au")
        # new_page.click("[data-testid=\"continue-to-abc-btn\"]")
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


class SessionResults(BaseModel):
    email: str
    password: str
    name: str
    gender: str
    dob: int
    postcode: int
    votes: List[Song]


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
        email = email_client.email
        password = generate_password()

        page.fill("[data-testid=\"email-field\"]", email)
        page.fill("[data-testid=\"password-field\"]", password)

        is_valid_email = page.query_selector("#email-error") is None
        is_valid_pass = page.query_selector("#password-error") is None

        if not (is_valid_email and is_valid_pass):
            raise ValueError("email or pass was bad")

        print(1)

        with page.expect_navigation():
            page.click("[data-testid=\"signup-with-email-btn\"]")

        gender = random.choice(['Male', 'Female', 'Prefer not to say'])
        name = names.get_first_name(gender=gender.lower())
        surname = names.get_last_name()
        dob = random.randint(2021 - 30, 2021 - 18)
        postcode = get_postcode()

        page.fill("[data-testid=\"first-name-field\"]", name)
        page.fill("[data-testid=\"year-of-birth-field\"]", str(dob))

        page.click("text=Select gender identity")
        page.click(f"text={gender}")

        page.fill("[placeholder=\"Enter suburb or postcode\"]", str(postcode))
        page.click("#screen-location-field-menu > ul > li:nth-child(1)")

        # t's & c's
        page.click("rect")

        # Click [data-testid="create-account-btn"]
        # with page.expect_navigation(url="https://mylogin.abc.net.au/account/index.html#/signup-verification-sent"):
        with page.expect_navigation():
            page.click("[data-testid=\"create-account-btn\"]")

        new_page = email_client.verify_email()

        new_page.goto("https://www.abc.net.au/triplej/hottest100/21/")
        with new_page.expect_navigation():
            new_page.click("text=Vote Now")
        new_page.click("text=Search")

        for song in target_songs:
            new_page.fill("[placeholder=\"Enter the artist's name\"]", song.artist)
            new_page.fill("[placeholder=\"Enter the track title\"]", song.track)
            new_page.click(f"[aria-label=\"Add {song.track} by {song.artist} to your shortlist\"]")

        new_page.click("text=Submit Votes")
        new_page.fill("text=Last nameYour last name is required >> input[type=\"text\"]", surname)
        new_page.fill("text=Phone numberYour phone number is required >> input[type=\"text\"]", phone_no)
        new_page.check("text=Can we call you to chat on-air? (Required for competition entry)Yes >> input[type=\"checkbox\"]")
        # new_page.query_selector("#recaptcha-element").click("span[role=\"checkbox\"]", button="right")
        with new_page.expect_navigation():
            new_page.click("text=Complete Voting")

        print(1)

        # FIXME lots more todo

    results = SessionResults(email=email, password=password,
                             name=name, gender=gender, dob=dob, postcode=postcode,
                             votes=target_songs)
    logger.info(results.json())
    return results


if __name__ == '__main__':
    vote(headless=False)
