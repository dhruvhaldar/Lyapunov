import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://127.0.0.0:3000')
        await page.wait_for_timeout(2000)
        await page.screenshot(path='app.png', full_page=True)
        await browser.close()

asyncio.run(main())
