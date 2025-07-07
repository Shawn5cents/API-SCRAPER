import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.sylectus.net/")
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
    page.locator("#iframe1").content_frame.locator("#todate").click()
    page.locator("#iframe1").content_frame.get_by_text("7", exact=True).first.click()
    page.locator("#iframe1").content_frame.get_by_role("button", name="SEARCH ALL POSTINGS").click()
    with page.expect_popup() as page1_info:
        page.locator("#iframe1").content_frame.get_by_role("link", name="ANDREY'S DELIVERY EXPRESS").click()
    page1 = page1_info.value
    page1.get_by_role("link", name="bids@andreysdelivery.com").click()
    page1.close()
    with page.expect_popup() as page2_info:
        page.locator("#iframe1").content_frame.get_by_role("row", name="Click for SaferWatch info. ANDREY'S DELIVERY EXPRESS   TEANA Member Days to Pay").locator("input[name=\"bidbutton\"]").click()
    page2 = page2_info.value
    page2.get_by_role("textbox", name="My bid / Spot quote *").click()
    page2.locator("#BidCalcMiles").click()
    page2.locator("#BidCalcAmount").click()
    page2.get_by_role("textbox", name="Vehicle current location *").click()
    page2.get_by_placeholder("L").click()
    page2.locator("#VehicleHeight").click()
    page2.locator("#DoorWidth").click()
    page2.locator("#DoorHeight").click()
    page2.get_by_role("radio", name="Empty", exact=True).check()
    page2.locator("span").filter(has_text="Not Empty").click()
    page2.get_by_role("radio", name="Solo").check()
    page2.get_by_role("radio", name="Team").check()
    page2.locator("#BidNotes").click()
    page2.get_by_role("button", name="Cancel").click()
    page2.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
