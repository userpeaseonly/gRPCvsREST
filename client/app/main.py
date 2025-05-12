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

rest_url = os.getenv("REST_URL", "http://0.0.0.0:8001/products")


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
            print(f"Request duration: {duration:.2f} seconds")
            if response.status_code == 200:
                data = response.json()
            else:
                data = "Error: Received unexpected status code."
        except httpx.RequestError as e:
            return templates.TemplateResponse("index.html", {"request": request, "message": f"Request failed: {str(e)}"})
    
    print("Response count:", len(data))
    
    context = {
        "request": request,
        "data": {
            "count": len(data) if data else 0,
            "duration_ms": f"{duration:.2f}" if duration else "Unknown",
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
    duration = None
    try:
        start_time = time.perf_counter()
        
        data = get_products()
        
        end_time = time.perf_counter()
        duration = end_time - start_time
        print(f"Request duration: {duration:.2f} seconds")
    except grpc.RpcError as e:
        return templates.TemplateResponse("index.html", {"request": request, "message": f"gRPC request failed: {str(e)}"})
    
    try:
        data = data[:2]
        length = len(data)
    except TypeError:
        length = 0
        data = data
    
    print("Response count:", len(data) if data else 0)
    print("Response data:", data)
    context = {
        "request": request,
        "data": {
            "count": length,
            "duration_ms": f"{duration:.2f}" if duration else "Unknown",
            "status": "200" if data else "Unknown", 
            "preview": data,
        }
    }
    return templates.TemplateResponse("index.html", context=context)
