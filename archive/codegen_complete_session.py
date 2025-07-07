import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.sylectus.net/")
    page.get_by_role("button", name="Accept All Cookies").click()
    page.get_by_role("link", name="LOG IN").click()
    page.get_by_role("textbox", name="Corporate ID").click()
    page.get_by_role("textbox", name="Corporate ID").fill("2103390")
    page.get_by_role("textbox", name="Corporate ID").press("Tab")
    page.locator("#ctl00_bodyPlaceholder_corpPasswordField").fill("Sn59042181#@")
    page.get_by_role("link", name="Continue").click()
    page.get_by_label("").click()
    page.get_by_role("option", name="SNICHOLS").click()
    page.get_by_placeholder(" ").click()
    page.get_by_placeholder(" ").fill("Sn59042181#@")
    page.get_by_role("link", name="Log in").click()
    page.get_by_role("link", name="Load Board").click()
    page.locator("#iframe1").content_frame.locator("#fromdate").click()
    page.locator("#iframe1").content_frame.locator("#todate").click()
    page.locator("#iframe1").content_frame.get_by_text("7", exact=True).nth(2).click()
    page.locator("#iframe1").content_frame.get_by_role("row", name="FROM CITY, STATE: Select").get_by_role("button").click()
    page.locator("#iframe1").content_frame.get_by_role("row", name="TO CITY, STATE: Select States").get_by_role("button").click()
    with page.expect_popup() as page1_info:
        page.locator("#iframe1").content_frame.get_by_role("link", name="Lake Erie Logistics LLC").first.click()
    page1 = page1_info.value
    page1.close()
    with page.expect_popup() as page2_info:
        page.locator("#iframe1").content_frame.get_by_role("row", name="Click for SaferWatch info. Lake Erie Logistics LLC   Days to Pay: 25 Credit Score: 95% S.A.F.E.R. Expedited Load 413198 91827 NORTH LITTLE ROCK, AR 72114 ASAP FORT WORTH, TX 76107 07/07/2025 07:00 07/06/2025 13:21 07/06/2025 13:50 SMALL STRAIGHT 355 1 2600 Bid Select All", exact=True).locator("input[name=\"bidbutton\"]").click()
    page2 = page2_info.value
    page2.get_by_role("button", name="Cancel").click()
    page2.close()
    page.locator("#iframe1").content_frame.get_by_role("button", name="SEARCH ALL POSTINGS").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
