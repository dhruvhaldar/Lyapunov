import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        iphone_13 = p.devices['iPhone 13']
        context = await browser.new_context(**iphone_13)
        page = await context.new_page()
        await page.goto("http://localhost:8000")
        await page.wait_for_timeout(2000)

        kbd_visible = await page.evaluate('''document.querySelector('.kbd-shortcut') ? getComputedStyle(document.querySelector('.kbd-shortcut')).display : "not found"''')
        print(f"KBD shortcut display on mobile: {kbd_visible}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
