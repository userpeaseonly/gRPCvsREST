# run_once_insert.py
from database import SessionLocal
from models import Product

db = SessionLocal()
for i in range(1_000_000):
    db.add(Product(name=f"Product {i}", description=f"Description {i}"))
    print(f"Inserted product {i}", end=" | ")
    if i % 100000 == 0:
        db.commit()
        print(f"Committed after inserting {i} products.")

db.commit()
db.close()
print("Inserted 1,000,000 products into the database.")