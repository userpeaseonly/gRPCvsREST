import httpx
import time
import grpc
import os
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from gRPC_client import get_products

load_dotenv()

templates = Jinja2Templates(directory="templates")
app = FastAPI()

rest_url = os.getenv("REST_URL", "http://188.245.209.201:8001/products")


@app.get("/rest", response_class=HTMLResponse)
async def home(request: Request):
    print("Request to REST API:", rest_url)
    data = None
    response = None
    duration = None
    
    timeout = httpx.Timeout(60.0, read=360.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            start_time = time.perf_counter()
            response = await client.get(rest_url)
            end_time = time.perf_counter()
            duration = end_time - start_time
            query_time = response.json().get("duration_seconds") if response.status_code == 200 else None
            data = response.json()["products"] if response.status_code == 200 else None
            if query_time:
                print(f"Query time: {query_time:.2f} seconds")
            else:
                print("Query time: Unknown")
            print("============== REST API response ==============")
            print(f"{duration:.2f} seconds")
            print("============== REST API response ==============", end="\n\n")
        except httpx.RequestError as e:
            return templates.TemplateResponse("index.html", {"request": request, "message": f"Request failed: {str(e)}"})
    
    print("Response count:", len(data))
    
    context = {
        "request": request,
        "data": {
            "count": len(data) if data else 0,
            "duration_ms": f"{duration * 1000:.2f}" if duration else "Unknown",  # Convert duration to milliseconds
            "request_time": f"{(duration * 1000 - query_time * 1000):.2f}" if duration and query_time else "Unknown",
            "query_time": f"{query_time * 1000:.2f}" if query_time else "Unknown",  # Convert query_time to milliseconds
            "status": response.status_code if response else "Unknown", 
            "preview": data[:2] if isinstance(data, list) else data,
        }
    }
    
    return templates.TemplateResponse("index.html", context=context)


@app.get("/grpc", response_class=HTMLResponse)
async def grpc_home(request: Request):
    # Placeholder for gRPC request handling
    print("Request to gRPC API")
    data = None
    response = None
    query_time = None
    duration = None
    try:
        start_time = time.perf_counter()
        data, query_time = get_products()
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        if query_time:
            print(f"Query time: {query_time:.2f} seconds")
        else:
            print("Query time: Unknown")
        
        print("============== gRPC API response ==============")
        print(f"{duration:.2f} seconds")
        print("============== gRPC API response ==============", end="\n\n")
    except grpc.RpcError as e:
        return templates.TemplateResponse("index.html", {"request": request, "message": f"gRPC request failed: {str(e)}"})
    
    try:
        length = len(data)
        data = data[:2]
    except TypeError:
        length = 0
        data = data
    
    context = {
        "request": request,
        "data": {
            "count": length,
            "duration_ms": f"{duration * 1000:.2f}" if duration else "Unknown",  # Convert duration to milliseconds
            "request_time": f"{(duration * 1000 - query_time * 1000):.2f}" if duration and query_time else "Unknown",
            "query_time": f"{query_time * 1000:.2f}" if query_time else "Unknown",  # Convert query_time to milliseconds
            "status": "200" if data else "Unknown", 
            "preview": data,
        }
    }
    return templates.TemplateResponse("index.html", context=context)
