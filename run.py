"""
🤖 Chatbot YuedPao - Master CLI & Task Runner Script
Centralized command-line entry point to manage server, scrapers, vector indexing, tests, and rich menu generation.

Usage Examples:
    python run.py serve                   # Start Flask LINE Webhook Server
    python run.py scrape-products --all   # Scrape product catalog & update domain vocab
    python run.py scrape-coupons          # Scrape coupons & re-index promotion engine
    python run.py reindex                 # Re-build BM25 & ChromaDB Product Vector Index
    python run.py test                    # Run Pytest suite (16 intent tests)
    python run.py status                  # Display database & system status
"""

import os
import sys
import argparse
import sqlite3
import subprocess

# Ensure UTF-8 output encoding on Windows CLI
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

DB_PATH = os.path.join(PROJECT_ROOT, "yuedpao_chatbot.db")


def cmd_serve(args):
    """Starts the Flask LINE Webhook server."""
    port = args.port or 5000
    print(f"🚀 Starting YuedPao Chatbot Webhook Server on port {port}...")
    from app.main import app
    app.run(host="0.0.0.0", port=port, debug=True)


def cmd_scrape_products(args):
    """Executes the Playwright product scraper pipeline."""
    print("📦 Starting YuedPao Product Scraper Pipeline...")
    script_path = os.path.join(PROJECT_ROOT, "app", "scripts", "run_scraper.py")
    cmd = [sys.executable, script_path]
    if args.all:
        cmd.append("--all")
    if args.limit:
        cmd.extend(["--limit", str(args.limit)])
    if args.force:
        cmd.append("--force")
        
    subprocess.run(cmd, check=True)


def cmd_scrape_coupons(args):
    """Executes the coupon scraper & re-indexes promotion engine."""
    print("🎟️ Starting YuedPao Coupon Scraper & Promotion Re-indexing...")
    from app.services.promotion_service import PromotionService
    promo_service = PromotionService.get_instance()
    docs = promo_service.reload_and_index()
    print(f"✅ Successfully re-indexed {len(docs)} promotion coupon passages into ChromaDB & BM25.")


def cmd_reindex(args):
    """Re-builds BM25 and ChromaDB vector indices from SQLite database."""
    print("🔄 Re-building BM25 & ChromaDB Product Vector Indices from SQLite Database...")
    from app.services.product_service import ProductService
    product_service = ProductService.get_instance()
    product_service.reload_and_index()
    print(f"✅ Successfully indexed {len(product_service.documents)} products into ChromaDB & BM25.")


def cmd_test(args):
    """Executes the automated Pytest test suite."""
    print("🧪 Executing YuedPao Automated Pytest Suite...")
    test_path = os.path.join(PROJECT_ROOT, "tests", "test_all_intents.py")
    cmd = [sys.executable, "-m", "pytest", test_path, "-v"]
    subprocess.run(cmd, check=True)


def cmd_status(args):
    """Displays comprehensive database and system status."""
    print("==================================================")
    print("🤖 Chatbot YuedPao System Status Report")
    print("==================================================")
    
    if not os.path.exists(DB_PATH):
        print("❌ SQLite Database File Not Found!")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Total Products
    cursor.execute("SELECT COUNT(*), MIN(price), MAX(price), AVG(price) FROM products")
    p_count, p_min, p_max, p_avg = cursor.fetchone()
    print(f"📦 Total Scraped Products: {p_count:,} items")
    print(f"   Price Range: ฿{p_min:.0f} - ฿{p_max:.0f} (Avg: ฿{p_avg:.1f})")
    
    # 2. Total Categories
    cursor.execute("SELECT COUNT(*) FROM categories")
    c_count = cursor.fetchone()[0]
    print(f"📂 Total Categories: {c_count} categories")
    
    # 3. Total Variants
    cursor.execute("SELECT COUNT(*) FROM product_variants")
    v_count = cursor.fetchone()[0]
    print(f"🎨 Total Color/Size Variants: {v_count:,} variants")
    
    # 4. Total Coupons
    try:
        cursor.execute("SELECT COUNT(*) FROM coupons")
        cp_count = cursor.fetchone()[0]
        print(f"🎟️ Total Active Coupons: {cp_count} coupons")
    except Exception:
        print("🎟️ Total Active Coupons: Table not found")
        
    conn.close()
    
    # 5. Domain Vocab
    vocab_path = os.path.join(PROJECT_ROOT, "app", "data", "domain_vocab.json")
    if os.path.exists(vocab_path):
        import json
        with open(vocab_path, "r", encoding="utf-8") as f:
            v_data = json.load(f)
        total_vocab = sum(len(v) for v in v_data.values())
        print(f"📚 Domain Vocabulary: {total_vocab} terms across 4 NLP groups")
    
    print("==================================================")


def main():
    parser = argparse.ArgumentParser(
        description="🤖 Master CLI Runner for Chatbot YuedPao Project",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available Commands")
    
    # 1. Serve Command
    p_serve = subparsers.add_parser("serve", help="Start Flask Webhook Server")
    p_serve.add_argument("--port", type=int, default=5000, help="Port to listen on (Default: 5000)")
    p_serve.set_defaults(func=cmd_serve)
    
    # 2. Scrape Products Command
    p_sp = subparsers.add_parser("scrape-products", help="Scrape product catalog & update NLP domain vocab")
    p_sp.add_argument("--all", action="store_true", help="Scrape all categories dynamically")
    p_sp.add_argument("--limit", type=int, default=None, help="Limit items to scrape per category")
    p_sp.add_argument("--force", action="store_true", help="Force re-scraping existing items")
    p_sp.set_defaults(func=cmd_scrape_products)
    
    # 3. Scrape Coupons Command
    p_sc = subparsers.add_parser("scrape-coupons", help="Scrape coupons & re-index promotion engine")
    p_sc.set_defaults(func=cmd_scrape_coupons)
    
    # 4. Reindex Command
    p_reindex = subparsers.add_parser("reindex", help="Re-build BM25 & ChromaDB Product Vector Indices")
    p_reindex.set_defaults(func=cmd_reindex)
    
    # 5. Test Command
    p_test = subparsers.add_parser("test", help="Run automated Pytest test suite (16 intent tests)")
    p_test.set_defaults(func=cmd_test)
    
    # 6. Status Command
    p_status = subparsers.add_parser("status", help="Display database & system status report")
    p_status.set_defaults(func=cmd_status)
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    args.func(args)


if __name__ == "__main__":
    main()
