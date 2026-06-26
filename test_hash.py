import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        # Go to URL with hash
        await page.goto('http://127.0.0.1:3000/#Pendulum')
        await page.wait_for_timeout(1000)

        # Check select value
        val = await page.locator('#system-select').input_value()
        print(f"Select value: {val}")

        # Check URL hash
        url = page.url
        print(f"URL: {url}")

        await browser.close()

asyncio.run(main())
