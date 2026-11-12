
import sqlite3
import json

db = sqlite3.connect("db.sqlite3")
db.row_factory = sqlite3.Row

tables = [
    "auth_user",
    "product_product",
    "product_category",
    "product_cart",
    "product_cartitem",
    "product_order",
    "product_orderitem",
    "product_profile",
    "product_wishlist",
    "product_review",
    "product_size",
]

backup = {}

for table in tables:
    rows = db.execute(f'SELECT * FROM "{table}"').fetchall()
    backup[table] = [dict(row) for row in rows]
    print(table, ":", len(rows), "records")

with open("velora_raw_backup.json", "w", encoding="utf-8") as f:
    json.dump(backup, f, indent=2, default=str)

db.close()

print("VELORA RAW BACKUP COMPLETED")
