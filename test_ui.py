from playwright.sync_api import sync_playwright

def run_cuj(page):
    page.goto("http://localhost:8000")
    page.wait_for_timeout(1000)
    page.screenshot(path="screenshot_home.png")

    # Select Lorenz
    page.select_option("#system-select", "Lorenz")
    page.wait_for_timeout(1000)
    page.screenshot(path="screenshot_lorenz.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        run_cuj(page)
        browser.close()
