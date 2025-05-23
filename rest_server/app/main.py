from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Product, Base
from typing import List
import time


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str

class ProductResponseWithDuration(BaseModel):
    duration_seconds: float
    products: List[ProductResponse]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/products", response_model=ProductResponseWithDuration)
def get_products(db: Session = Depends(get_db)):
    start_time = time.perf_counter()

    products = db.query(Product.id, Product.name, Product.description).limit(1_000_000).all()
    
    end_time = time.perf_counter()
    
    execution_time = end_time - start_time

    print(f"Query time: {execution_time:.2f} seconds")
    
    return ProductResponseWithDuration(
        duration_seconds=execution_time,
        products=[ProductResponse(id=p.id, name=p.name, description=p.description) for p in products]
    )
