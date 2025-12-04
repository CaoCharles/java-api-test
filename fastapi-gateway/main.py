"""
FastAPI Gateway - 串接 Spring Boot API
"""
import os
from typing import Optional
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

# 配置
SPRING_BOOT_API_URL = os.getenv("SPRING_BOOT_API_URL", "http://localhost:8080")

# HTTP Client
http_client: Optional[httpx.AsyncClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global http_client
    http_client = httpx.AsyncClient(base_url=SPRING_BOOT_API_URL, timeout=30.0)
    yield
    await http_client.aclose()


# FastAPI Application
app = FastAPI(
    title="FastAPI Gateway",
    description="API Gateway that connects to Spring Boot backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100, alias="fullName")

    class Config:
        populate_by_name = True


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = Field(None, alias="fullName")

    class Config:
        populate_by_name = True


class ProductCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict | list] = None


# Health Check
@app.get("/health", tags=["Health"])
async def health_check():
    """Gateway health check"""
    return {
        "status": "UP",
        "service": "FastAPI Gateway",
        "backend_url": SPRING_BOOT_API_URL
    }


@app.get("/health/backend", tags=["Health"])
async def backend_health_check():
    """Check Spring Boot backend health"""
    try:
        response = await http_client.get("/api/health")
        return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Backend unavailable: {str(e)}")


# User Endpoints
@app.get("/api/users", tags=["Users"], response_model=ApiResponse)
async def get_all_users():
    """Get all users from Spring Boot API"""
    try:
        response = await http_client.get("/api/users")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Backend unavailable: {str(e)}")


@app.get("/api/users/{user_id}", tags=["Users"], response_model=ApiResponse)
async def get_user_by_id(user_id: int):
    """Get user by ID from Spring Boot API"""
    try:
        response = await http_client.get(f"/api/users/{user_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Backend unavailable: {str(e)}")


@app.post("/api/users", tags=["Users"], response_model=ApiResponse, status_code=201)
async def create_user(user: UserCreate):
    """Create a new user via Spring Boot API"""
    try:
        payload = {
            "username": user.username,
            "email": user.email,
            "fullName": user.full_name
        }
        response = await http_client.post("/api/users", json=payload)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Backend unavailable: {str(e)}")


@app.put("/api/users/{user_id}", tags=["Users"], response_model=ApiResponse)
async def update_user(user_id: int, user: UserCreate):
    """Update user via Spring Boot API"""
    try:
        payload = {
            "username": user.username,
            "email": user.email,
            "fullName": user.full_name
        }
        response = await http_client.put(f"/api/users/{user_id}", json=payload)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Backend unavailable: {str(e)}")


@app.delete("/api/users/{user_id}", tags=["Users"], response_model=ApiResponse)
async def delete_user(user_id: int):
    """Delete user via Spring Boot API"""
    try:
        response = await http_client.delete(f"/api/users/{user_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Backend unavailable: {str(e)}")


# Product Endpoints
@app.get("/api/products", tags=["Products"], response_model=ApiResponse)
async def get_all_products():
    """Get all products from Spring Boot API"""
    try:
        response = await http_client.get("/api/products")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Backend unavailable: {str(e)}")


@app.get("/api/products/search", tags=["Products"], response_model=ApiResponse)
async def search_products(name: str = Query(..., min_length=1)):
    """Search products by name via Spring Boot API"""
    try:
        response = await http_client.get("/api/products/search", params={"name": name})
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Backend unavailable: {str(e)}")


@app.get("/api/products/{product_id}", tags=["Products"], response_model=ApiResponse)
async def get_product_by_id(product_id: int):
    """Get product by ID from Spring Boot API"""
    try:
        response = await http_client.get(f"/api/products/{product_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Backend unavailable: {str(e)}")


@app.post("/api/products", tags=["Products"], response_model=ApiResponse, status_code=201)
async def create_product(product: ProductCreate):
    """Create a new product via Spring Boot API"""
    try:
        response = await http_client.post("/api/products", json=product.model_dump())
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Backend unavailable: {str(e)}")


@app.put("/api/products/{product_id}", tags=["Products"], response_model=ApiResponse)
async def update_product(product_id: int, product: ProductCreate):
    """Update product via Spring Boot API"""
    try:
        response = await http_client.put(f"/api/products/{product_id}", json=product.model_dump())
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Backend unavailable: {str(e)}")


@app.delete("/api/products/{product_id}", tags=["Products"], response_model=ApiResponse)
async def delete_product(product_id: int):
    """Delete product via Spring Boot API"""
    try:
        response = await http_client.delete(f"/api/products/{product_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Backend unavailable: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
