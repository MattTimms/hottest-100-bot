from playwright.sync_api import Page


class Tempmailo:
    url = "https://tempmailo.com/"

    def __init__(self, page: Page):
        self.page = page
        self.page.goto("https://tempmailo.com/")
        self.page.wait_for_selector("input[type=\"text\"]")
        self.email = self.page.eval_on_selector("input[type=\"text\"]", "el => el.value")

    def verify_email(self) -> Page:
        self.page.wait_for_timeout(5000)
        self.page.click("button:has-text(\"Refresh\")")
        self.page.click("text=Please complete your sign up")

        with self.page.expect_popup() as popup_info:
            self.page.frame(name="fullmessage").click("text=VERIFY EMAIL")
        new_page = popup_info.value

        self.page.wait_for_timeout(5000)
        self.page.click("button:has-text(\"Refresh\")")
        self.page.click("text=Welcome to your new ABC Account", timeout=60_000)
        new_page.goto("https://mylogin.abc.net.au/")

        # with self.page.expect_popup() as popup_info:
        #     self.page.frame(name="fullmessage").click("text=LOG IN TO YOUR ACCOUNT")

        return new_page
