import os
import sys
import argparse
import sqlite3
import json
import logging
import re
import asyncio
from typing import Optional
from tqdm import tqdm

# Ensure project root is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)

from app.services.scraper_service import YuedpaoScraperService
from playwright.async_api import async_playwright

# Set logging level for console output to WARNING or ERROR when running interactive progress bars
# to prevent logs from cluttering the progress bar display.
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ScraperRunner")

DB_FILE = "yuedpao_chatbot.db"
VOCAB_FILE = os.path.join(project_root, "app", "data", "domain_vocab.json")

def init_db():
    """Initializes the database schema if tables do not exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Create categories table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        category_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        parent_name TEXT,
        url TEXT UNIQUE NOT NULL
    );
    """)
    
    # 2. Create products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        fabric_collection TEXT NOT NULL,
        style_fit TEXT NOT NULL,
        price INTEGER NOT NULL,
        description TEXT,
        image_url TEXT,
        size_chart_url TEXT,
        product_url TEXT,
        is_available BOOLEAN DEFAULT 1
    );
    """)
    
    # 3. Create product-category mapping table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_category_mappings (
        product_id TEXT,
        category_id TEXT,
        PRIMARY KEY (product_id, category_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
    );
    """)
    
    # 4. Create product_variants table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_variants (
        variant_id TEXT PRIMARY KEY,
        product_id TEXT,
        color_name TEXT,
        size TEXT,
        is_in_stock BOOLEAN DEFAULT 1,
        FOREIGN KEY(product_id) REFERENCES products(product_id) ON DELETE CASCADE
    );
    """)
    
    # 5. Create fabric_specs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fabric_specs (
        fabric_id TEXT PRIMARY KEY,
        collection_name TEXT UNIQUE NOT NULL,
        size_chart_image_url TEXT
    );
    """)
    
    conn.commit()
    conn.close()

def save_category_to_db(cat_id: str, cat_name: str, parent_name: Optional[str], url: str):
    """Saves a category to the categories table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO categories (category_id, name, parent_name, url)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(category_id) DO UPDATE SET
        name=excluded.name,
        parent_name=excluded.parent_name,
        url=excluded.url;
    """, (cat_id, cat_name, parent_name, url))
    conn.commit()
    conn.close()

def check_product_exists(product_id: str) -> bool:
    """Checks if a product details were already scraped and inserted."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM products WHERE product_id = ?", (product_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def save_product_category_mapping(product_id: str, category_id: str):
    """Inserts a mapping between a product and a category."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR IGNORE INTO product_category_mappings (product_id, category_id)
    VALUES (?, ?)
    """, (product_id, category_id))
    conn.commit()
    conn.close()

def save_product_to_db(p_data: dict, current_category_id: Optional[str] = None):
    """Inserts or updates scraped product detail into the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    product_id = p_data["product_url"].split("-")[-1] if "-" in p_data["product_url"] else p_data["name"]
    
    category_name = p_data["category"]
    if current_category_id:
        cursor.execute("SELECT name FROM categories WHERE category_id = ?", (current_category_id,))
        row = cursor.fetchone()
        if row:
            category_name = row[0]
            
    # 1. Save product master
    cursor.execute("""
    INSERT INTO products (
        product_id, name, category, fabric_collection, style_fit, 
        price, description, image_url, size_chart_url, product_url, is_available
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(product_id) DO UPDATE SET
        name=excluded.name,
        category=excluded.category,
        fabric_collection=excluded.fabric_collection,
        style_fit=excluded.style_fit,
        price=excluded.price,
        description=excluded.description,
        image_url=excluded.image_url,
        size_chart_url=excluded.size_chart_url,
        product_url=excluded.product_url,
        is_available=excluded.is_available;
    """, (
        product_id, p_data["name"], category_name, p_data["fabric_collection"], p_data["style_fit"],
        p_data["price"], p_data["description"], p_data["image_url"], p_data["size_chart_url"],
        p_data["product_url"], 1 if p_data["is_available"] else 0
    ))
    
    # 2. Save product-category mapping
    if current_category_id:
        cursor.execute("""
        INSERT OR IGNORE INTO product_category_mappings (product_id, category_id)
        VALUES (?, ?)
        """, (product_id, current_category_id))
        
    # 3. Save fabric spec
    if p_data["fabric_collection"] and p_data["size_chart_url"]:
        fabric_id = p_data["fabric_collection"].lower().replace(" ", "_")
        cursor.execute("""
        INSERT INTO fabric_specs (fabric_id, collection_name, size_chart_image_url)
        VALUES (?, ?, ?)
        ON CONFLICT(collection_name) DO UPDATE SET
            size_chart_image_url=excluded.size_chart_image_url;
        """, (fabric_id, p_data["fabric_collection"], p_data["size_chart_url"]))
        
    # 4. Save variants
    cursor.execute("DELETE FROM product_variants WHERE product_id = ?", (product_id,))
    
    for color in p_data["colors"]:
        for size, is_in_stock in p_data["sizes"].items():
            variant_id = f"{product_id}_{color.replace(' ', '_')}_{size}"
            cursor.execute("""
            INSERT INTO product_variants (variant_id, product_id, color_name, size, is_in_stock)
            VALUES (?, ?, ?, ?, ?)
            """, (variant_id, product_id, color, size, 1 if is_in_stock else 0))
            
    conn.commit()
    conn.close()

def slugify(text: str) -> str:
    """Helper to convert names into clean database IDs."""
    text_clean = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", text_clean)

def generate_nlp_vocabulary():
    """Generates the domain vocabulary JSON file from SQLite for NLP correction."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Extract unique colors
    cursor.execute("SELECT DISTINCT color_name FROM product_variants WHERE color_name IS NOT NULL")
    brand_colors = [row[0] for row in cursor.fetchall() if row[0]]
    
    # Extract unique styles/fits
    cursor.execute("SELECT DISTINCT style_fit FROM products WHERE style_fit IS NOT NULL")
    product_styles = [row[0] for row in cursor.fetchall() if row[0]]
    
    # Extract unique fabric collections
    cursor.execute("SELECT DISTINCT fabric_collection FROM products WHERE fabric_collection IS NOT NULL")
    fabric_technologies = [row[0] for row in cursor.fetchall() if row[0]]
    
    # Extract unique category names
    cursor.execute("SELECT DISTINCT name FROM categories WHERE name IS NOT NULL")
    apparel_types = [row[0] for row in cursor.fetchall() if row[0]]
    
    if not apparel_types:
        cursor.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL")
        apparel_types = [row[0] for row in cursor.fetchall() if row[0]]
    
    conn.close()
    
    vocab_data = {
        "brand_colors": brand_colors,
        "product_styles": product_styles,
        "fabric_technologies": fabric_technologies,
        "apparel_types": apparel_types
    }
    
    os.makedirs(os.path.dirname(VOCAB_FILE), exist_ok=True)
    with open(VOCAB_FILE, "w", encoding="utf-8") as f:
        json.dump(vocab_data, f, ensure_ascii=False, indent=2)

async def main_async():
    parser = argparse.ArgumentParser(description="Yuedpao E-commerce Scraper & DB Pipeline")
    parser.add_argument("--url", type=str, 
                        default="https://www.yuedpao.com/UnisexRoundNeck(%E0%B8%84%E0%B8%AD%E0%B8%81%E0%B8%A5%E0%B8%A1)2026-cat.0ycq8v-92pdg6?sorter=PRODUCT_SORTER_POPULAR",
                        help="Single Category Catalog URL to scrape (if not using --all)")
    parser.add_argument("--all", action="store_true",
                        help="Scrape all categories dynamically by crawling the Hamburger menu structure from the home page first")
    parser.add_argument("--limit", type=int, default=None, 
                        help="Limit the number of detailed products to scrape per category (useful for fast testing)")
    parser.add_argument("--limit-categories", type=int, default=None,
                        help="Limit the number of categories to crawl when using --all (useful for fast testing)")
    parser.add_argument("--force", action="store_true",
                        help="Force re-scraping and updating product details even if product already exists in database")
    args = parser.parse_args()
    
    # Step 1: Initialize Database
    init_db()
    
    # Step 2: Instantiate Scraper Service
    scraper = YuedpaoScraperService()
    
    # Define tasks to run
    tasks = []
    
    async with async_playwright() as p:
        # Launch single browser instance for the entire run
        browser = await p.chromium.launch(headless=True)
        # Create standard context and page
        context = await browser.new_context(user_agent=scraper.user_agent)
        page = await context.new_page()
        
        if args.all:
            # Reuses standard viewport size for menu structure crawl inside Drawer
            await page.set_viewport_size({"width": 375, "height": 812})
            print("Step 1/3: Crawling website Hamburger menu structure from homepage...")
            menu_structure = await scraper.scrape_menu_structure(page=page)
            print(f"Discovered {len(menu_structure)} main category branches.")
            
            # Flatten structure into a list of categories to scrape and save to DB
            category_count = 0
            for main_cat, subcategories in menu_structure.items():
                for sub in subcategories:
                    if args.limit_categories and category_count >= args.limit_categories:
                        break
                        
                    sub_id = slugify(sub["name"])
                    # Save Category to database
                    save_category_to_db(sub_id, sub["name"], main_cat, sub["url"])
                    
                    tasks.append({
                        "category_id": sub_id,
                        "category_name": sub["name"],
                        "url": sub["url"]
                    })
                    category_count += 1
                    
                if args.limit_categories and category_count >= args.limit_categories:
                    print(f"Applied limit of {args.limit_categories} categories.")
                    break
        else:
            # Fallback to single category URL
            sub_id = slugify("เสื้อยืดคอกลม")
            save_category_to_db(sub_id, "เสื้อยืดคอกลม", "เสื้อยืด", args.url)
            tasks.append({
                "category_id": sub_id,
                "category_name": "เสื้อยืดคอกลม",
                "url": args.url
            })
            
        print(f"Step 2/3: Prepared {len(tasks)} categories to scrape.")
        
        # Set desktop viewport size for catalogs and product details
        await page.set_viewport_size({"width": 1280, "height": 800})
        
        total_success_count = 0
        total_skipped_count = 0
        
        # Step 3: Run pipeline with interactive progress bars
        pbar_categories = tqdm(tasks, desc="Overall Progress (Categories)", unit="category")
        for task in pbar_categories:
            cat_id = task["category_id"]
            cat_name = task["category_name"]
            cat_url = task["url"]
            
            pbar_categories.set_postfix_str(f"Current: {cat_name}")
            
            try:
                # Scrape catalog list reusing the same page
                catalog_products = await scraper.scrape_catalog_page(cat_url, page=page)
                
                # Deduplicate items
                unique_products = []
                seen_ids = set()
                for p_item in catalog_products:
                    if p_item["product_id"] and p_item["product_id"] not in seen_ids:
                        seen_ids.add(p_item["product_id"])
                        unique_products.append(p_item)
                        
                if args.limit:
                    unique_products = unique_products[:args.limit]
                    
                # Inner progress bar for products in current category
                pbar_products = tqdm(unique_products, desc=f"   Scraping {cat_name[:20]}", leave=False, unit="item")
                for p_item in pbar_products:
                    p_id = p_item["product_id"]
                    pbar_products.set_postfix_str(f"Product: {p_item['name'][:15]}")
                    
                    # Optimization 1: Cache checking in database
                    # If this product has already been fully scraped from another category, 
                    # we just add the category mapping and skip launching/visiting the network page.
                    if check_product_exists(p_id) and not args.force:
                        save_product_category_mapping(p_id, cat_id)
                        total_success_count += 1
                        total_skipped_count += 1
                        continue
                    
                    detail_url = p_item.get("product_url")
                    if not detail_url:
                        slug_name = p_item["name"].replace(" ", "-").replace("_", "-")
                        detail_url = f"https://www.yuedpao.com/physical/{slug_name}-{p_id}"
                        
                    try:
                        # Scrape product details reusing the same page
                        p_detail = await scraper.scrape_product_detail(detail_url, page=page)
                        if p_detail and p_detail.get("name"):
                            save_product_to_db(p_detail, current_category_id=cat_id)
                            total_success_count += 1
                    except Exception as e:
                        # Keep tqdm clean by avoiding prints
                        pass
                pbar_products.close()
            except Exception as e:
                pass
                
        pbar_categories.close()
        await browser.close()
        
    print(f"Scraping pipeline completed. Successfully imported {total_success_count} products (Skipped {total_skipped_count} repeats from cache).")
    
    # Step 4: Generate NLP Vocab
    print("Step 3/3: Re-generating NLP Domain Vocabulary from latest Database...")
    generate_nlp_vocabulary()
    print("NLP Domain Vocabulary generated successfully.")

def main():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
