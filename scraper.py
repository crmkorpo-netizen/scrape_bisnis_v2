import asyncio
import random
import time
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree

from playwright.async_api import async_playwright
import asyncio
import random
import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree

async def scrape_bisnis_playwright(start_page=1, end_page=17):
    async with async_playwright() as p:
        # Launch Chromium with args to avoid automation flags
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-infobars",
                "--window-size=1280,720"
            ]
        )

        # Create context mimicking a normal desktop browser on Windows
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            locale="id-ID",
            timezone_id="Asia/Jakarta",
            extra_http_headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1"
            }
        )

        page = await context.new_page()

        # Advanced Anti-bot override scripting
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = {
                runtime: {}
            };
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['id-ID', 'id', 'en-US', 'en']
            });
        """)

        article_urls = []

        # -------------------------------------------------------------
        # STEP 1: Extract article links from index pages
        # -------------------------------------------------------------
        print(f"--- STARTING LINK EXTRACTION (PAGES {start_page} TO {end_page}) ---")
        for page_num in range(start_page, end_page + 1):
            index_url = f"https://www.bisnis.com/index?page={page_num}"
            print(f"Navigating to index page [{page_num}/{end_page}]: {index_url}")

            try:
                # Human-like natural delay before visiting next page
                await asyncio.sleep(random.uniform(3.0, 5.0))

                response = await page.goto(index_url, wait_until="networkidle", timeout=45000)
                if response.status != 200:
                    print(f"Page {page_num} failed with status: {response.status}")
                    continue

                # Scroll down in increments to mimic actual reading behavior
                for _ in range(3):
                    await page.evaluate("window.scrollBy(0, window.innerHeight)")
                    await asyncio.sleep(random.uniform(0.5, 1.2))

                html = await page.content()
                index_soup = BeautifulSoup(html, "html.parser")

                article_elements = index_soup.select(".list-news, .col-sm-8 .list-news, .list-berita, .artList, article, .item-news")
                page_links_found = 0

                for art in article_elements:
                    link_tag = art.find("a", href=True)
                    if link_tag:
                        url = link_tag["href"]
                        if not url.startswith("http"):
                            url = "https://www.bisnis.com" + url

                        if ("/read/" in url or "bisnis.com/" in url) and url not in article_urls:
                            if not url.endswith(f"/index?page={page_num}"):
                                article_urls.append(url)
                                page_links_found += 1

                if page_links_found == 0:
                    for a in index_soup.find_all("a", href=True):
                        href = a["href"]
                        if "/read/" in href:
                            full_url = href if href.startswith("http") else "https://www.bisnis.com" + href
                            if full_url not in article_urls:
                                article_urls.append(full_url)
                                page_links_found += 1

                print(f"Found {page_links_found} new articles on page {page_num}.")

            except Exception as e:
                print(f"Error scraping index page {page_num}: {e}")
                continue

        print(f"\nTotal unique articles collected: {len(article_urls)}")
        print("--- STARTING DETAIL EXTRACTION ---")

        # -------------------------------------------------------------
        # STEP 2: Extract article details
        # -------------------------------------------------------------
        results = []

        for idx, article_url in enumerate(article_urls, 1):
            # Give a robust, organic delay (4 to 8 seconds) to prevent triggering 403 blocks
            await asyncio.sleep(random.uniform(4.0, 8.0))
            print(f"[{idx}/{len(article_urls)}] Fetching: {article_url}")

            try:
                res = await page.goto(article_url, wait_until="domcontentloaded", timeout=45000)
                if res.status != 200:
                    print(f"Failed to load details. Status: {res.status}")
                    # If blocked with 403, sleep longer before continuing
                    if res.status == 403:
                        await asyncio.sleep(10.0)
                    continue

                # Briefly scroll to page center to trigger dynamic content loading naturally
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
                await asyncio.sleep(random.uniform(1.0, 2.5))

                html = await page.content()
                dom = etree.HTML(html)

                # Title
                title_list = dom.xpath('//h1[contains(@class, "detailsTitleCaption")]/text()') or dom.xpath('//h1/text()')
                title = title_list[0].strip() if title_list else 'na'

                # Date
                date_list = dom.xpath('//div[contains(@class, "detailsAttributeDates")]/text()') or dom.xpath('//span[contains(@class, "date")]/text()')
                date = date_list[0].strip() if date_list else 'na'

                # Link
                link_list = dom.xpath('//link[@rel="canonical"]/@href')
                link = link_list[0].strip() if link_list else article_url

                # Category
                category_list = dom.xpath('//ul[@class="breadcrumbList"]/li[2]/a/text()')
                category = category_list[0].strip() if category_list else 'na'

                # Subcategory
                subcategory_list = dom.xpath('//ul[@class="breadcrumbList"]/li[contains(@class, "-active")]/a/text()')
                subcategory = subcategory_list[0].strip() if subcategory_list else 'na'

                # Content paragraph cleaning
                raw_paragraph = dom.xpath('//article[contains(@class, "detailsContent force-17 mt40")]') or \
                                dom.xpath('//div[contains(@class, "detailsContent")]') or \
                                dom.xpath('//article')

                clean_text = "na"
                if raw_paragraph:
                    html_block = etree.tostring(raw_paragraph[0], encoding='utf-8').decode('utf-8')
                    soup = BeautifulSoup(html_block, "html.parser")
                    for tag in soup(['a']):
                        tag.decompose()
                    classes = ['baca-juga-box', None]
                    for c in classes:
                        for data in soup('div', {'class': c}):
                            data.decompose()
                    p_tags = soup.find_all('p')
                    if p_tags:
                        paragraphs = [p.get_text(strip=True) for p in p_tags if p.get_text(strip=True)]
                        clean_text = "\n\n".join(paragraphs) if paragraphs else "na"
                    else:
                        clean_text = soup.get_text(strip=True)

                results.append({
                    'Judul': title,
                    'Detail': clean_text,
                    'Tanggal': date,
                    'Link': link,
                    'Kategori': category,
                    'Sub Kategori': subcategory
                })
                print(f"Success scraping [{idx}]: {title[:40]}...")

            except Exception as e:
                print(f"Error parsing article {article_url}: {e}")
                continue

        await browser.close()
        return results

# Run the Playwright Async Loop
import asyncio
scraped_data = asyncio.run(scrape_bisnis_playwright(start_page=1, end_page=17)) # Try with 1 page first to confirm success
df = pd.DataFrame(scraped_data)
df.head()

df

df = df[df['Tanggal']!= "na"]
df

# df.drop('Page', axis=1, inplace=True)
# df

df = df.drop_duplicates()
df

from datetime import datetime

# 1. Get current system date and time
now = datetime.now()

# 2. Format it safely for a filename (Year-Month-Day_Hour-Minute-Second)
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

df.to_excel(f"Bisnis_{timestamp}.xlsx", index=False)
