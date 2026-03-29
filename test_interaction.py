from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})

        print("Navigating to local server...")
        page.goto("http://localhost:8000")

        print("Waiting for select element...")
        page.wait_for_selector("#system-select")

        print("Taking initial screenshot...")
        page.screenshot(path="screenshot_initial.png")

        print("Selecting 'Pendulum'...")
        page.select_option("#system-select", "Pendulum")

        print("Waiting for network idle to ensure requests complete...")
        page.wait_for_load_state("networkidle")

        print("Taking final screenshot...")
        page.screenshot(path="screenshot_final.png", full_page=True)

        browser.close()
        print("Done!")

run()
