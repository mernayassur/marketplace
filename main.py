import asyncio
from playwright.async_api import async_playwright
import requests, json, time

# =========== إعدادات ===========
SEARCH_URL = "https://www.facebook.com/marketplace/alexandria/search/?query=iphone"
KEYWORDS = ["iphone","Iphone","iPhone","ايفون","آيفون","أيفون"]
TELEGRAM_BOT_TOKEN = "8397343419:AAEqlCsfULBv-szP-JlYb8ETnP0cRr8jTnM"
TELEGRAM_CHAT_ID = "7222890321"
POLL_INTERVAL = 60
SEEN_FILE = "seen.json"

def send_telegram(title, url):
    try:
        r = requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                          data={"chat_id": TELEGRAM_CHAT_ID, "text": f"{title}\n{url}"}, timeout=15)
        if r.status_code != 200:
            print("Telegram push failed:", r.status_code, r.text)
    except Exception as e:
        print("Telegram error:", e)

def load_seen():
    try:
        with open(SEEN_FILE,"r",encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen(seen):
    try:
        with open(SEEN_FILE,"w",encoding="utf-8") as f:
            json.dump(list(seen), f, ensure_ascii=False)
    except Exception as e:
        print("Error saving seen:", e)

async def check_marketplace(seen):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(SEARCH_URL)
        await page.wait_for_timeout(5000)  # 5 ثواني للتحميل
        html = await page.content()
        await browser.close()
    new = []
    # ابحث عن الروابط داخل HTML
    for keyword in KEYWORDS:
        if keyword.lower() in html.lower():
            # تبسيط: لو وجدت الكلمة، اعتبر إعلان جديد
            new.append((keyword, SEARCH_URL))
    for title, url in new:
        if url not in seen:
            seen.add(url)
            send_telegram(title, url)
    if new:
        save_seen(seen)
    return seen

async def main():
    seen = load_seen()
    while True:
        seen = await check_marketplace(seen)
        await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
