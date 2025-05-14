# server.py
import time
import grpc
import os
from concurrent import futures
from sqlalchemy.orm import Session

import products_pb2
import products_pb2_grpc
from database import SessionLocal, engine, Base
from models import Product

PRODUCTS_PORT = os.getenv("PRODUCTS_PORT", 50051)

class ProductService(products_pb2_grpc.ProductServiceServicer):
    def GetProducts(self, request, context):
        print("Received request for products")
        db: Session = SessionLocal()
        try:
            start_time = time.perf_counter()

            products = db.query(Product.id, Product.name, Product.description).limit(100_000).all()
            
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time

            print(f"Query executed in {execution_time:.2f} seconds")
            
            response = products_pb2.GetProductsResponse(
                duration_seconds=execution_time,
            )
            response.products.extend(
                products_pb2.Product(
                    id=product.id,
                    name=product.name,
                    description=product.description
                ) for product in products
            )
            
            print(f"Returning {len(products)} products")
            return response
        except Exception as e:
            print(f"Error occurred: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal server error')
            return products_pb2.GetProductsResponse()
        finally:
            db.close()

def serve():
    Base.metadata.create_all(bind=engine)
    print("Database tables created")
    MAX_MESSAGE_SIZE = 512 * 1024 * 1024
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', MAX_MESSAGE_SIZE),
            ('grpc.max_receive_message_length', MAX_MESSAGE_SIZE),
        ]
    )
    print("gRPC server starting...", end="")
    products_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)
    server.add_insecure_port(f'[::]:{PRODUCTS_PORT}')
    server.start()
    print(f"gRPC server running at [::]:{PRODUCTS_PORT}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
