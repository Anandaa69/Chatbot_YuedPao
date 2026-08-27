import sys
import sqlite3
import os

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('yuedpao_chatbot.db')
cursor = conn.cursor()

print("=== 1. CHECKING PRODUCTS IN DB ===")
cursor.execute("SELECT category, COUNT(*) FROM products GROUP BY category")
rows = cursor.fetchall()
for cat, count in rows:
    print(f"  Category: '{cat}' -> {count} items")

print("\n=== 2. CHECKING JEANS & BAGS ===")
cursor.execute("SELECT product_id, name, category FROM products WHERE LOWER(name) LIKE '%bag%' OR LOWER(category) LIKE '%bag%' OR name LIKE '%กระเป๋า%'")
bags = cursor.fetchall()
print(f"  Found {len(bags)} Bag items:")
for b in bags:
    print(f"    - {b[1]} (Cat: {b[2]})")

cursor.execute("SELECT product_id, name, category FROM products WHERE LOWER(name) LIKE '%jeans%' OR LOWER(category) LIKE '%jeans%' OR name LIKE '%ยีนส์%'")
jeans = cursor.fetchall()
print(f"  Found {len(jeans)} Jeans items:")
for j in jeans[:5]:
    print(f"    - {j[1]} (Cat: {j[2]})")

print("\n=== 3. CHECKING COUPONS TABLE IN DB ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='coupons'")
if cursor.fetchone():
    cursor.execute("SELECT coupon_code, discount_title, min_spend, valid_duration FROM coupons")
    coupons = cursor.fetchall()
    print(f"  Found {len(coupons)} coupons in SQLite 'coupons' table:")
    for c in coupons:
        print(f"    - [{c[0]}] {c[1]} | Min: {c[2]} | Duration: {c[3]}")
else:
    print("  Table 'coupons' does NOT exist in DB!")

print("\n=== 4. CHECKING PROMOTIONS TABLE IN DB ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='promotions'")
if cursor.fetchone():
    cursor.execute("SELECT promo_id, title, deal_type, price FROM promotions")
    promos = cursor.fetchall()
    print(f"  Found {len(promos)} promotion items in SQLite 'promotions' table:")
    for p in promos:
        print(f"    - [{p[2]}] {p[1]} | Price: {p[3]}")
else:
    print("  Table 'promotions' does NOT exist in DB!")

print("\n=== 5. CHECKING CHROMADB COLLECTIONS ===")
try:
    import chromadb
    chroma_path = os.path.join(os.getcwd(), "data", "chroma")
    if os.path.exists(chroma_path):
        client = chromadb.PersistentClient(path=chroma_path)
        collections = client.list_collections()
        print(f"  ChromaDB collections found: {[c.name for c in collections]}")
        for col in collections:
            c_obj = client.get_collection(col.name)
            print(f"    - Collection '{col.name}': {c_obj.count()} documents indexed")
    else:
        print("  ChromaDB directory 'data/chroma' not found!")
except Exception as e:
    print(f"  Could not load ChromaDB: {e}")
