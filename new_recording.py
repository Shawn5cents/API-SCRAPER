from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.sylectus.net/")
    page.get_by_role("button", name="Accept All Cookies").click()
    page.get_by_role("link", name="LOG IN").click()
    page.get_by_label("Corporate ID").fill("2103390")
    page.get_by_label("Corporate ID").press("Tab")
    page.locator("#ctl00_bodyPlaceholder_corpPasswordField").fill("Sn59042181#@")
    page.get_by_placeholder(" ").fill("Sn59042181#@")
    page.goto("https://www.sylectus.com/main_page.aspx")
    page.get_by_role("link", name="Load Board").click()
    with page.expect_popup() as page1_info:
        page.frame_locator("#iframe1").get_by_role("link", name="Nolan Transportation Group,").click()
    page1 = page1_info.value
    page1.get_by_role("cell", name="E-MAIL:", exact=True).click()
    page1.get_by_role("link", name="angel.teran@ntgfreight.com").click()
    page1.get_by_role("cell", name="POSTED BY PHONE:").click()
    page1.get_by_role("cell", name="ext.").click()
    page1.get_by_role("cell", name="POSTED BY:").click()
    page1.get_by_role("cell", name="Angel Teran").click()
    page1.get_by_role("cell", name="BROKER NAME:").click()
    page1.get_by_role("cell", name="Nolan Transportation Group,").click()
    page1.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
