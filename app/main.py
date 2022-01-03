import string
import random
from collections import namedtuple
from typing import List

import names
import pandas as pd
from playwright.sync_api import sync_playwright, Page
from pydantic import BaseModel

Song = namedtuple("Song", ['artist', 'track'])
target_songs = [Song(*x) for x in [
    'Billie Eilish', 'Getting Older'
]]


class Tempmailo:
    url = "https://tempmailo.com/"

    def __init__(self, page: Page):
        self.page = page
        self.page.goto("https://tempmailo.com/")
        self.email = self.page.eval_on_selector("input[type=\"text\"]", "el => el.value")
        self._is_verified = False

    def verify_email(self) -> bool:
        if self._is_verified:
            return self._is_verified

        self.page.click("text=ABC <abc@accounts.abc.net.au>")
        # Click text=VERIFY EMAIL
        # with page1.expect_navigation(url="https://hottest100.abc.net.au/authenticate"):
        with self.page.expect_navigation():
            with self.page.expect_popup() as popup_info:
                self.page.frame(name="fullmessage").click("text=VERIFY EMAIL")
            page2: Page = popup_info.value
        page2.close()


def generate_password() -> str:
    # pw 6-50 chars, number, upper, & lower
    # re.compile(r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{6,50}')

    length = random.randint(6, 50)
    password = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=length))
    return password


def get_postcode() -> int:
    df = pd.read_csv('australian-postcodes-2021-04-23.csv')
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
        browser = p.firefox.launch(headless=False)

        page = browser.new_page()

        page.goto("https://mylogin.abc.net.au/account/index.html#/signup")


def vote() -> SessionResults:
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)

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

        email_client.verify_email()

        page.goto("https://www.abc.net.au/triplej/hottest100/21/")
        with page.expect_navigation():
            page.click("text=Vote Now")
        page.click("text=Search")

        for song in target_songs:
            page.fill("[placeholder=\"Enter the artist's name\"]", song.artist)
            page.fill("[placeholder=\"Enter the track title\"]", song.track)
            page.click(f"[aria-label=\"Add {song.track} by {song.artist} to your shortlist\"]")

        page.click("text=Submit Votes")

    results = SessionResults(email=email, password=password,
                             name=name, gender=gender, dob=dob, postcode=postcode,
                             votes=target_songs)
    print(results.json())
    return results


if __name__ == '__main__':
    vote()
