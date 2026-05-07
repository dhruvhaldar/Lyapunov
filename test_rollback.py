from playwright.sync_api import sync_playwright

def run_test(page):
    page.goto("http://localhost:8000")
    page.wait_for_timeout(1000)

    # Check initial title
    title = page.locator("#heading-phase").inner_text()
    print("Initial title:", title)

    # Select Lorenz
    page.select_option("#system-select", "Lorenz")
    page.wait_for_timeout(1000)

    title = page.locator("#heading-phase").inner_text()
    print("Title after selecting Lorenz:", title)

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        run_test(page)
        browser.close()
