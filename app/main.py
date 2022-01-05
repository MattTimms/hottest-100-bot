
from loguru import logger
from playwright.sync_api import sync_playwright

from app.utils.email import Tempmailo
from app.utils.models import Song, Account, SessionResults

target_songs = [Song(*x) for x in [
    ('Gang Of Youths', 'the angel of 8th ave.'),  # defaults to #1 track in vote
]]


def test_playwright():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)

        page = browser.new_page()

        page.goto("https://mylogin.abc.net.au/account/index.html#/signup")


def vote(headless=True) -> SessionResults:
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=headless)  #, proxy={'server': '149.19.224.36:3128'})

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

        new_page.wait_for_timeout(3000)
        with new_page.expect_navigation():
            new_page.click("text=Complete Voting")

        logger.info("Vote complete")

    results = SessionResults(**account.dict(), votes=target_songs)
    logger.info(results.json())
    return results


if __name__ == '__main__':
    vote(headless=False)
