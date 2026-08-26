import json
import os

nb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "notebooks", "03_promotion_scraper.ipynb")

with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

cell_4_code = '''def scrape_deep_product_detail(driver: webdriver.Chrome, product_url: str) -> Dict[str, Any]:
    """
    กดเข้าไปในลิงก์สินค้าเพื่อสกัดรายละเอียดเชิงลึก เช่น คำอธิบายผ้า (USP), รายการสี, รายการไซส์และสต็อก, รูปแกลเลอรี, และรูปภาพหลัก (PNG/JPEG)
    """
    try:
        driver.get(product_url)
        time.sleep(4)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # 1. คำอธิบายสินค้า / คุณสมบัติผ้า
        desc_text = ""
        p_desc = soup.find(lambda tag: tag.name == "p" and len(tag.text) > 30)
        if p_desc:
            desc_text = p_desc.get_text(strip=True)
            
        # 2. สี และ ไซส์ คงเหลือ
        buttons = soup.find_all("button")
        colors = []
        sizes = {}
        size_pattern = re.compile(r"^(XS|S|M|L|XL|[2-9]XL|28|30|32|34|36|38|40)$", re.IGNORECASE)
        ignore_btns = {"เข้าสู่ระบบ", "สั่งซื้อสินค้า", "หยิบใส่ตะกร้า", "ดูทั้งหมด", "ใส่ตะกร้า", "ซื้อ", "ดูร้านค้า"}
        
        for btn in buttons:
            btn_text = btn.get_text(strip=True)
            classes = btn.get("class", [])
            is_disabled = "Mui-disabled" in classes
            
            if size_pattern.match(btn_text):
                sizes[btn_text] = not is_disabled
            elif btn_text and btn_text not in ignore_btns:
                if len(btn_text) < 35 and btn_text not in colors:
                    colors.append(btn_text)
                    
        # 3. รูปภาพสินค้าหลัก (Main PNG/JPEG Image), ตารางไซส์ (Size Chart Image) & Gallery Images
        main_image_url = ""
        img_div = soup.find("div", style=lambda x: x and "background-image" in x)
        if img_div and "style" in img_div.attrs:
            style_str = img_div["style"]
            match = re.search(r'url\((?:&quot;|\"|\')?(.*?)(?:&quot;|\"|\')?\)', style_str)
            if match and not match.group(1).endswith(".svg"):
                main_image_url = match.group(1)
                
        size_chart_url = ""
        gallery_images = []
        images = soup.find_all("img")
        for img in images:
            src = img.get("src") or img.get("data-src") or img.get("srcset") or ""
            if "size" in src.lower() or "chart" in src.lower():
                size_chart_url = src
            elif "galleries" in src.lower() or "products" in src.lower() or "mp-static" in src.lower():
                if not src.endswith(".svg") and "badge" not in src.lower():
                    if not main_image_url:
                        main_image_url = src
                    if src not in gallery_images:
                        gallery_images.append(src)
                    
        return {
            "description": desc_text,
            "colors": ", ".join(colors),
            "sizes_json": json.dumps(sizes, ensure_ascii=False),
            "main_image_url": main_image_url,
            "size_chart_url": size_chart_url,
            "gallery_images_json": json.dumps(gallery_images, ensure_ascii=False)
        }
    except Exception as e:
        print(f"⚠️ เกิดข้อผิดพลาดดึงรายละเอียดจาก {product_url}: {e}")
        return {
            "description": "",
            "colors": "",
            "sizes_json": "{}",
            "main_image_url": "",
            "size_chart_url": "",
            "gallery_images_json": "[]"
        }'''

cell_5_code = '''def scrape_deal_products_with_details(driver: webdriver.Chrome, deal_info: Dict[str, str]) -> List[Dict[str, Any]]:
    deal_url = deal_info["url"]
    deal_type = deal_info["deal_type"]
    deal_title = deal_info["title"]
    
    print(f"\\n⏳ กำลังสแครปสินค้าหมวด '{deal_title}' ที่ {deal_url}...")
    driver.get(deal_url)
    time.sleep(5)
    
    product_anchors = driver.find_elements(By.XPATH, "//a[contains(@href, '/physical/') or contains(@href, '/product/')] ")
    
    items_summary = []
    seen_urls = set()
    
    for a in product_anchors:
        p_url = a.get_attribute("href")
        if not p_url or p_url in seen_urls:
            continue
            
        raw_text = a.text.strip()
        if not raw_text:
            continue
            
        seen_urls.add(p_url)
        p_id = p_url.split("-")[-1].split("?")[0]
        lines = [line.strip() for line in raw_text.split("\\n") if line.strip()]
        
        discount_tag = ""
        product_name = ""
        deal_price = 0
        original_price = 0
        
        for line in lines:
            if "-" in line and "%" in line:
                discount_tag = line
            elif "฿" in line or "บาท" in line:
                p_match = re.search(r'(?:฿|บาท)\\s*([\\d\\.,]+)', line)
                if p_match:
                    try:
                        deal_price = float(p_match.group(1).replace(",", ""))
                    except:
                        pass
            elif line.replace(",", "").isdigit() and len(line) <= 6:
                try:
                    original_price = float(line.replace(",", ""))
                except:
                    pass
            elif not product_name and "ส่งฟรี" not in line:
                product_name = line
                
        img_url = ""
        try:
            img_div = a.find_element(By.XPATH, ".//div[contains(@style, 'background-image')]")
            style_str = img_div.get_attribute("style")
            match = re.search(r'url\((?:&quot;|\"|\')?(.*?)(?:&quot;|\"|\')?\)', style_str)
            if match and not match.group(1).endswith(".svg"):
                img_url = match.group(1)
        except:
            pass
            
        if not img_url:
            try:
                img_el = a.find_element(By.TAG_NAME, "img")
                src = img_el.get_attribute("src") or img_el.get_attribute("data-src") or ""
                if src and not src.endswith(".svg") and "badge" not in src.lower():
                    img_url = src
            except:
                pass
            
        if product_name and (deal_price > 0 or original_price > 0):
            items_summary.append({
                "product_id": p_id,
                "name": product_name,
                "deal_type": deal_type,
                "deal_title": deal_title,
                "discount_tag": discount_tag,
                "deal_price": deal_price if deal_price > 0 else original_price,
                "original_price": original_price if original_price > 0 else deal_price,
                "image_url": img_url,
                "product_url": p_url
            })
            
    print(f"✅ พบสินค้าในหมวด '{deal_title}' รวม {len(items_summary)} รายการ -> กำลังเริ่มกดเข้าไปดึงรายละเอียดเชิงลึก...")
    
    for item in items_summary:
        print(f"  👉 กำลังเข้าหน้าสินค้า: {item['name']} ({item['product_url']})...")
        detail = scrape_deep_product_detail(driver, item["product_url"])
        if detail.get("main_image_url") and not detail["main_image_url"].endswith(".svg"):
            item["image_url"] = detail["main_image_url"]
            
        # Fallback to products catalog table in SQLite if image is still missing or .svg
        if not item["image_url"] or item["image_url"].endswith(".svg") or "badge" in item["image_url"].lower():
            try:
                db_p = "yuedpao_chatbot.db"
                if os.path.exists(db_p):
                    conn = sqlite3.connect(db_p)
                    cursor = conn.cursor()
                    cursor.execute("SELECT image_url FROM products WHERE product_id = ? AND image_url NOT LIKE '%.svg%'", (item["product_id"],))
                    row = cursor.fetchone()
                    if row and row[0]:
                        item["image_url"] = row[0]
                    conn.close()
            except Exception:
                pass
                
        item.update(detail)
        
    return items_summary'''

nb['cells'][3]['source'] = [line + '\n' for line in cell_4_code.split('\n')]
nb['cells'][4]['source'] = [line + '\n' for line in cell_5_code.split('\n')]

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"✅ Updated {nb_path} cells successfully!")
