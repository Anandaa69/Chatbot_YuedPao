import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "yuedpao_chatbot.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Set items 1-9 as daily_deal (Signature Oversize series)
cursor.execute("UPDATE promotions SET deal_type = 'daily_deal' WHERE promo_id BETWEEN 1 AND 9")

# Set items 10-21 as monthly_deal (Y Collection Polo & Cargo series)
cursor.execute("UPDATE promotions SET deal_type = 'monthly_deal' WHERE promo_id BETWEEN 10 AND 21")

conn.commit()

cursor.execute("SELECT promo_id, name, deal_type, image_url FROM promotions")
rows = cursor.fetchall()
print(f"Updated {len(rows)} promotion rows:")
for r in rows:
    print(r)

conn.close()
