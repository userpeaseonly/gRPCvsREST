# run_once_insert.py
from database import SessionLocal
from models import Product

db = SessionLocal()
for i in range(1_000_000):
    db.add(Product(name=f"Product {i}", description=f"Description {i}"))
    if i % 1000000 == 0:
        db.commit()
db.commit()
db.close()
