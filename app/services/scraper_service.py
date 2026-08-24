import sys
import asyncio
import re
import logging
from typing import List, Dict, Any, Optional

try:
    from playwright.async_api import async_playwright
    from bs4 import BeautifulSoup
except ImportError:
    pass

logger = logging.getLogger(__name__)

class YuedpaoScraperService:
    """
    Service for scraping products, categories, submenus, and details from Yuedpao.com.
    Designed for FastAPI/asyncio, with safety fallbacks for different environment loops.
    """
    
    def __init__(self, base_url: str = "https://www.yuedpao.com"):
        self.base_url = base_url
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        # Authoritative Hamburger SVG Path
        self.hamburger_svg_path = "M13,16H3a1,1,0,0,0,0,2H13a1,1,0,0,0,0-2ZM3,8H21a1,1,0,0,0,0-2H3A1,1,0,0,0,3,8Zm18,3H3a1,1,0,0,0,0,2H21a1,1,0,0,0,0-2Z"

    async def scrape_menu_structure(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Navigates to the homepage, opens the Mobile Hamburger Drawer,
        clicks through each main category name, and retrieves all visible subcategory names and links.
        Returns a dictionary mapping Main Category -> List of Subcategories (with name and url).
        """
        menu_structure = {}
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self.user_agent,
                viewport={"width": 375, "height": 812}
            )
            page = await context.new_page()
            
            logger.info("Opening homepage to scrape menu structure...")
            await page.goto(self.base_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)
            
            # 1. Open Hamburger Menu
            svgs = await page.query_selector_all("svg")
            drawer_opened = False
            for svg in svgs:
                has_path = await svg.evaluate(f"""
                    (el) => {{
                        const path = el.querySelector('path');
                        return path && path.getAttribute('d') === '{self.hamburger_svg_path}';
                    }}
                """)
                if has_path:
                    logger.info("Clicking Hamburger menu button...")
                    await svg.click()
                    await page.wait_for_timeout(2500)
                    drawer_opened = True
                    break
                    
            if not drawer_opened:
                logger.error("Failed to open Hamburger drawer menu.")
                await browser.close()
                return menu_structure
                
            # 2. Get all visible main category names
            spans = await page.query_selector_all("span.css-1dwwjt3")
            main_category_names = []
            for s in spans:
                if await s.is_visible():
                    text = (await s.inner_text()).strip()
                    if (text and 
                        text not in ["เกี่ยวกับ", "นโยบาย", "ช่วยเหลือ", "สนับสนุน"] and 
                        "cs_yuedpao" not in text):
                        main_category_names.append(text)
                        
            logger.info(f"Discovered {len(main_category_names)} main categories: {main_category_names}")
            
            # 3. For each category name, reopen drawer, click it, and extract visible subcategory links
            for cat_name in main_category_names:
                logger.info(f"Crawling category submenus for: {cat_name}")
                try:
                    # Reload page to start with a fresh Drawer state
                    await page.goto(self.base_url, wait_until="domcontentloaded", timeout=60000)
                    await page.wait_for_timeout(2000)
                    
                    # Reopen Hamburger Drawer
                    svgs = await page.query_selector_all("svg")
                    for svg in svgs:
                        has_path = await svg.evaluate(f"""
                            (el) => {{
                                const path = el.querySelector('path');
                                return path && path.getAttribute('d') === '{self.hamburger_svg_path}';
                            }}
                        """)
                        if has_path:
                            await svg.click()
                            await page.wait_for_timeout(2000)
                            break
                            
                    # Find category span by text and click it
                    spans = await page.query_selector_all("span.css-1dwwjt3")
                    target_el = None
                    for s in spans:
                        if await s.is_visible() and (await s.inner_text()).strip() == cat_name:
                            target_el = s
                            break
                            
                    if target_el:
                        await target_el.click()
                        await page.wait_for_timeout(2000)
                        
                        # Read all visible submenu links restricted to the Drawer element to avoid background page links
                        links = await page.query_selector_all(".MuiDrawer-paper a")
                        if not links:
                            links = await page.query_selector_all("div[role='presentation'] a")
                        if not links:
                            links = await page.query_selector_all("a")
                            
                        subs = []
                        seen_urls = set()
                        for link in links:
                            if await link.is_visible():
                                href = await link.get_attribute("href")
                                text = (await link.inner_text()).strip()
                                
                                if href and href != "/" and text and text != "ดูทั้งหมด" and "cs_yuedpao" not in text:
                                    full_url = href if href.startswith("http") else self.base_url + href
                                    if "facebook.com" not in href and "instagram.com" not in href and "line.me" not in href:
                                        if full_url not in seen_urls:
                                            seen_urls.add(full_url)
                                            subs.append({"name": text, "url": full_url})
                                        
                        menu_structure[cat_name] = subs
                        logger.info(f"Category '{cat_name}': Found {len(subs)} subcategories.")
                    else:
                        logger.warning(f"Category element not found for text: {cat_name}")
                except Exception as e:
                    logger.error(f"Error crawling category submenus for '{cat_name}': {e}")
                    
            await browser.close()
        return menu_structure

    async def scrape_catalog_page(self, url: str) -> List[Dict[str, Any]]:
        """
        Scrapes a list of products from a category page, handles scrolling for lazy loading,
        and follows pagination links to compile a complete list of products.
        """
        all_products = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=self.user_agent)
            page = await context.new_page()
            await page.set_viewport_size({"width": 1280, "height": 800})
            
            current_url = url
            page_num = 1
            
            while True:
                logger.info(f"Navigating to Page {page_num}: {current_url}")
                try:
                    await page.goto(current_url, wait_until="domcontentloaded", timeout=60000)
                    await page.wait_for_timeout(3000)
                    
                    # Scroll down to trigger lazy loading of product items
                    logger.info("Scrolling page to trigger lazy load...")
                    last_height = await page.evaluate("document.body.scrollHeight")
                    scroll_step = 700
                    for _ in range(15):
                        await page.evaluate(f"window.scrollBy(0, {scroll_step})")
                        await page.wait_for_timeout(500)
                        new_height = await page.evaluate("document.body.scrollHeight")
                        current_scroll_pos = await page.evaluate("window.pageYOffset + window.innerHeight")
                        if current_scroll_pos >= new_height and new_height == last_height:
                            break
                        last_height = new_height
                        
                    await page.wait_for_timeout(1500)
                    
                    # Parse the page content
                    html_content = await page.content()
                    products_in_page = self._parse_products_from_html(html_content)
                    logger.info(f"Page {page_num}: Found {len(products_in_page)} products")
                    all_products.extend(products_in_page)
                    
                    # Handle pagination
                    next_button = await page.query_selector('a[aria-label="Go to next page"]')
                    if not next_button:
                        logger.info("Pagination Next Button not found. Reached end of catalog.")
                        break
                        
                    is_disabled = await next_button.evaluate(
                        "(el) => el.classList.contains('Mui-disabled') || el.getAttribute('aria-disabled') === 'true'"
                    )
                    if is_disabled:
                        logger.info("Next button is disabled (last page reached).")
                        break
                        
                    next_href = await next_button.get_attribute("href")
                    if not next_href:
                        break
                        
                    if next_href.startswith("/"):
                        current_url = self.base_url + next_href
                    else:
                        current_url = next_href
                        
                    page_num += 1
                except Exception as e:
                    logger.error(f"Error scraping catalog page {current_url}: {e}")
                    break
                    
            await browser.close()
        return all_products

    async def scrape_product_detail(self, url: str) -> Dict[str, Any]:
        """
        Scrapes detailed product attributes, size stock, size charts, and gallery images.
        Also parses collection and category tags from the name.
        """
        detail_data = {}
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=self.user_agent)
            page = await context.new_page()
            await page.set_viewport_size({"width": 1280, "height": 800})
            
            logger.info(f"Navigating to product detail: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(4000)
            
            html_content = await page.content()
            soup = BeautifulSoup(html_content, "html.parser")
            
            # 1. Product Name
            title_tag = soup.find("h1")
            if not title_tag:
                title_tag = soup.find(lambda tag: tag.name in ["p", "div"] and "Ultrasoft" in tag.text and len(tag.text) < 150)
            product_name = title_tag.get_text(strip=True) if title_tag else "Yuedpao Premium Product"
            
            # 2. Price
            price_text = ""
            price_p = soup.find("p", class_=lambda x: x and "text-ci-primary" in x)
            if price_p:
                price_text = price_p.get_text(strip=True)
            else:
                p_fallback = soup.find(lambda tag: tag.name in ["p", "div", "span"] and "฿" in tag.text and len(tag.text) < 30)
                if p_fallback:
                    price_text = p_fallback.get_text(strip=True)
            
            price = re.sub(r"[^\d]", "", price_text)
            price = int(price) if price else 0
            
            # 3. Description (USP)
            desc_text = ""
            p_desc = soup.find(lambda tag: tag.name == "p" and len(tag.text) > 40 and "ยับยาก" in tag.text)
            if not p_desc:
                p_desc = soup.find(lambda tag: tag.name == "p" and len(tag.text) > 30)
            desc_text = p_desc.get_text(strip=True) if p_desc else "ผ้านุ่มใส่สบาย ยืดแต่ไม่ย้วย ยับยาก ไม่ต้องรีด"
            if len(desc_text) > 60:
                desc_text = desc_text[:57] + "..."
                
            # 4. Colors & Sizes Stock Status
            buttons = soup.find_all("button")
            colors = []
            sizes = {}
            size_pattern = re.compile(r"^(XS|S|M|L|XL|[2-9]XL)$", re.IGNORECASE)
            
            for btn in buttons:
                btn_text = btn.get_text(strip=True)
                classes = btn.get("class", [])
                is_disabled = "Mui-disabled" in classes
                
                if any(c in classes for c in ["mr-3", "mt-2", "min-w-[100px]"]):
                    if size_pattern.match(btn_text):
                        sizes[btn_text] = not is_disabled
                    else:
                        if btn_text and btn_text != "เข้าสู่ระบบ":
                            colors.append(btn_text)
                            
            # 5. Main Image URL
            image_url = ""
            img_div = soup.find("div", style=lambda x: x and "background-image" in x)
            if img_div and "style" in img_div.attrs:
                style_str = img_div["style"]
                match = re.search(r'url\((?:&quot;|\"|\')?(.*?)(?:&quot;|\"|\')?\)', style_str)
                if match:
                    image_url = match.group(1)
                    
            # 6. Size Chart Image URL
            size_chart_url = ""
            size_chart_img = soup.find("img", class_=lambda x: x and "mpe-no-image-placeholder" in x)
            if size_chart_img:
                size_chart_url = size_chart_img.get("src", "")
                
            # 7. Gallery Images (filtered)
            gallery_images = []
            divs = soup.find_all("div", style=lambda x: x and "background-image" in x)
            for div in divs:
                style_str = div.get("style", "")
                match = re.search(r'url\((?:&quot;|\"|\')?(.*?)(?:&quot;|\"|\')?\)', style_str)
                if match:
                    g_url = match.group(1)
                    if g_url and "galleries" in g_url:
                        if (g_url != image_url and 
                            g_url != size_chart_url and 
                            "size" not in g_url.lower() and 
                            "chart" not in g_url.lower() and 
                            g_url not in gallery_images):
                            gallery_images.append(g_url)

            # 8. Infer structural metadata from product name/URL
            category = self._infer_category(product_name, url)
            fabric_collection = self._infer_fabric_collection(product_name)
            style_fit = self._infer_style_fit(product_name)
            
            detail_data = {
                "name": product_name,
                "price": price,
                "description": desc_text,
                "category": category,
                "fabric_collection": fabric_collection,
                "style_fit": style_fit,
                "colors": colors,
                "sizes": sizes,
                "image_url": image_url,
                "size_chart_url": size_chart_url,
                "gallery_images": gallery_images,
                "product_url": url,
                "is_available": any(sizes.values()) if sizes else False
            }
            await browser.close()
        return detail_data

    def _parse_products_from_html(self, html_content: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, "html.parser")
        products = []
        items = soup.find_all("div", class_=lambda x: x and "vertical-product-item" in x)
        for item in items:
            product_id = item.get("data-product-id", "")
            name_div = item.find("div", class_=lambda x: x and "line-clamp-2" in x)
            name = name_div.get_text(strip=True) if name_div else ""
            
            price_text = ""
            price_p = item.find("p", class_=lambda x: x and ("text-ci-primary" in x or "css-6b2fbd" in x))
            if price_p:
                price_text = price_p.get_text(strip=True)
            else:
                p_fallback = item.find(lambda tag: tag.name in ["p", "div", "span"] and "฿" in tag.text)
                if p_fallback:
                    price_text = p_fallback.get_text(strip=True)
            
            price = re.sub(r"[^\d]", "", price_text)
            price = int(price) if price else 0
            
            image_url = ""
            img_div = item.find("div", style=lambda x: x and "background-image" in x)
            if img_div and "style" in img_div.attrs:
                style_str = img_div["style"]
                match = re.search(r'url\((?:&quot;|\"|\')?(.*?)(?:&quot;|\"|\')?\)', style_str)
                if match:
                    image_url = match.group(1)
            
            # ดึงลิงก์หน้าสินค้าจริง
            product_url = ""
            a_tag = item.find("a", href=True) if item.name != "a" else item
            if not a_tag:
                a_tag = item.find_parent("a", href=True)
            if a_tag:
                href = a_tag["href"]
                if href.startswith("/"):
                    product_url = self.base_url + href
                else:
                    product_url = href
            else:
                slug_name = name.replace(" ", "-").replace("_", "-")
                product_url = f"{self.base_url}/physical/{slug_name}-{product_id}"
                    
            products.append({
                "product_id": product_id,
                "name": name,
                "price": price,
                "image_url": image_url,
                "product_url": product_url
            })
        return products

    def _infer_category(self, name: str, url: str) -> str:
        name_lower = name.lower()
        if "คอกลม" in name or "round neck" in name_lower:
            return "เสื้อยืดคอกลม"
        elif "คอวี" in name or "v-neck" in name_lower:
            return "เสื้อยืดคอวี"
        elif "โปโล" in name or "polo" in name_lower:
            return "เสื้อโปโล"
        elif "กางเกง" in name or "pants" in name_lower or "shorts" in name_lower:
            return "กางเกง"
        return "เสื้อยืด"

    def _infer_fabric_collection(self, name: str) -> str:
        name_lower = name.lower()
        if "ultrasoft" in name_lower or "นุ่ม" in name:
            return "Ultrasoft"
        elif "non-iron" in name_lower or "ยับยาก" in name:
            return "Non-iron"
        elif "tailor cool" in name_lower:
            return "Tailor Cool"
        elif "supima" in name_lower:
            return "Supima Cotton"
        return "Classic Cotton"

    def _infer_style_fit(self, name: str) -> str:
        name_lower = name.lower()
        if "oversize" in name_lower:
            return "Oversize"
        elif "crop" in name_lower:
            return "Crop"
        elif "unisex" in name_lower:
            return "Unisex"
        elif "slim" in name_lower:
            return "Slim Fit"
        return "Unisex"

    @classmethod
    def run_sync_in_thread(cls, coro):
        """
        Helper method to run async coroutines synchronously in a separate thread.
        Crucial for Windows Jupyter environments to avoid NotImplementedError.
        """
        import threading
        result = []
        exception = []
        
        def worker():
            try:
                if sys.platform == 'win32':
                    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                res = loop.run_until_complete(coro)
                result.append(res)
            except Exception as e:
                exception.append(e)
            finally:
                loop.close()
                
        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()
        
        if exception:
            raise exception[0]
        return result[0]
