
import grpc
import os

from dotenv import load_dotenv

load_dotenv()

import products_pb2
import products_pb2_grpc


products_host = os.environ.get('PRODUCTS_HOST', 'localhost')
products_port = os.environ.get('PRODUCTS_PORT', '50051')
print(f"gRPC server address: {products_host}:{products_port}")

# gRPC client setup
MAX_MESSAGE_SIZE = 512 * 1024 * 1024  # 512MB

channel = grpc.insecure_channel(
    f'{products_host}:{products_port}',
    options=[
        ('grpc.max_send_message_length', MAX_MESSAGE_SIZE),
        ('grpc.max_receive_message_length', MAX_MESSAGE_SIZE),
    ]
)
stub = products_pb2_grpc.ProductServiceStub(channel)

# gRPC request example
def get_products():
    try:
        # Set timeout for gRPC call (5 seconds)
        response = stub.GetProducts(
            products_pb2.GetProductsRequest(),
            timeout=360.0
        )
        serialized = response.SerializeToString()
        print(f"Serialized size: {len(serialized) / (1024 * 1024):.2f} MB")

        return response.products
    except grpc.RpcError as e:
        error_code = e.code() if hasattr(e, 'code') else None
        if error_code == grpc.StatusCode.UNAVAILABLE:
            print(f"gRPC server unavailable: {e}")
        elif error_code == grpc.StatusCode.DEADLINE_EXCEEDED:
            print(f"gRPC request timed out: {e}")
        else:
            print(f"gRPC request failed: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in gRPC request: {e}")
        return None
