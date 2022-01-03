import time
import os

import dotenv
from playwright.sync_api import sync_playwright

dotenv.load_dotenv('.env')

GOOGLE_EMAIL = os.environ['GOOGLE_EMAIL']
GOOGLE_PASSWORD = os.environ['GOOGLE_PASSWORD']
SESSION_DIR = './workspace/playwright'

_multi_account_select_url = "https://www.youtube.com/signin_prompt?app=desktop&next=https%3A%2F%2Fwww.youtube.com%2F"


def sign_in():
    with sync_playwright() as p:
        browser = p.firefox.launch_persistent_context(SESSION_DIR, headless=False)
        page = browser.new_page()

        page.goto("https://youtube.com")
        is_signed_in = page.query_selector("[aria-label=\"Sign in\"]") is None

        if not is_signed_in:
            with page.expect_navigation():
                page.click("[aria-label=\"Sign in\"]")

            # page.wait_for_selector("[aria-label=\"Email or phone\"]")
            page.fill("[aria-label=\"Email or phone\"]", GOOGLE_EMAIL)
            with page.expect_navigation():
                page.press("[aria-label=\"Email or phone\"]", "Enter")

            time.sleep(2)  # needed

            page.fill("[aria-label=\"Enter your password\"]", GOOGLE_PASSWORD)
            with page.expect_navigation(url=_multi_account_select_url):
                page.press("[aria-label=\"Enter your password\"]", "Enter")

            print(page.url)
            print("t-15seconds to do mfa")
            time.sleep(30)  # fixme
            print(page.url)

            # page.wait_for_timeout(30000)

            # wait = page.expect_navigation(url=_multi_account_select_url)
            # print(1)
        else:
            page.goto(_multi_account_select_url)

        page.goto(_multi_account_select_url)
        with page.expect_navigation():
            page.click("text=AverageContent")


def inspect_video(video_id: str):
    video_url = f'https://studio.youtube.com/video/{video_id}/edit'

    sign_in()

    with sync_playwright() as p:
        browser = p.firefox.launch_persistent_context(SESSION_DIR, headless=False)
        page = browser.new_page()

        page.goto(video_url)
        print(1)


if __name__ == '__main__':
    inspect_video('o0ayfdb5he4')
