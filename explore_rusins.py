"""
Izpēta rusins.lv eļļu atlases API izmantojot Playwright.
"""
import asyncio, json
from playwright.async_api import async_playwright

API_CALLS = []

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()

        # Klausās visus network pieprasījumus
        async def on_request(request):
            if any(x in request.url for x in ['ajax', 'api', 'json', 'selector', 'oil', 'search', 'vehicle', 'brand', 'model']):
                print(f"REQ: {request.method} {request.url}")
                if request.method == 'POST':
                    try:
                        print(f"  POST data: {request.post_data}")
                    except:
                        pass

        async def on_response(response):
            url = response.url
            ct = response.headers.get('content-type', '')
            if 'json' in ct or any(x in url for x in ['ajax', 'api', 'oil', 'vehicle', 'brand', 'model', 'selector']):
                try:
                    body = await response.text()
                    if body and len(body) > 10 and body.strip().startswith(('[', '{')):
                        print(f"\nRESP JSON: {url}")
                        print(f"  {body[:500]}")
                        API_CALLS.append({'url': url, 'body': body[:2000]})
                except:
                    pass

        page.on('request', on_request)
        page.on('response', on_response)

        print("=== Atver rusins.lv ===")
        await page.goto('https://rusins.lv', timeout=30000)
        await page.screenshot(path='rusins_home.png')
        print("Ekrānuzņēmums: rusins_home.png")
        await asyncio.sleep(2)

        # Meklē eļļu atlases sadaļu
        print("\n=== Meklē eļļu atlases saiti ===")
        links = await page.eval_on_selector_all('a', 'els => els.map(e => ({href: e.href, text: e.textContent.trim()}))')
        for l in links:
            txt = l['text'].lower()
            if any(x in txt for x in ['eļļ', 'atlase', 'šķidr', 'oil', 'select', 'fluid']):
                print(f"  {l['text']!r} -> {l['href']}")

        # Mēģina atrast un noklikšķināt uz atlases
        for selector in ['text=Eļļas', 'text=atlase', 'text=Atlase', '[href*="oil"]', '[href*="selector"]', '[href*="atlase"]']:
            try:
                el = await page.query_selector(selector)
                if el:
                    href = await el.get_attribute('href')
                    text = await el.text_content()
                    print(f"Atrasts: {text!r} -> {href}")
                    await el.click()
                    await asyncio.sleep(3)
                    await page.screenshot(path='rusins_selector.png')
                    print("Ekrānuzņēmums: rusins_selector.png")
                    break
            except:
                pass

        await asyncio.sleep(2)

        # Saglabā API calls
        with open('rusins_api_calls.json', 'w', encoding='utf-8') as f:
            json.dump(API_CALLS, f, ensure_ascii=False, indent=2)
        print(f"\nSaglabāti {len(API_CALLS)} API pieprasījumi -> rusins_api_calls.json")

        await browser.close()

asyncio.run(main())
