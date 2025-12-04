# Python FastAPI Gateway 教學文件

## 目錄
1. [簡介](#簡介)
2. [環境需求](#環境需求)
3. [專案結構](#專案結構)
4. [依賴套件說明](#依賴套件說明)
5. [程式碼架構](#程式碼架構)
6. [程式碼詳解](#程式碼詳解)
7. [執行步驟](#執行步驟)
8. [API 測試](#api-測試)
9. [Swagger 文件](#swagger-文件)
10. [常見問題](#常見問題)

---

## 簡介

FastAPI 是一個現代、高效能的 Python Web 框架，專為建立 API 設計。本專案使用 FastAPI 作為 API Gateway，串接後端的 Spring Boot API。

### 什麼是 API Gateway？

API Gateway 是一個位於客戶端和後端服務之間的中介層，負責：
- **請求路由**: 將請求轉發到正確的後端服務
- **協定轉換**: 統一對外的 API 介面
- **認證授權**: 集中管理 API 存取權限（本專案未實作）
- **流量控制**: 限流、熔斷等（本專案未實作）

### 在本專案中的角色

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Python FastAPI │────▶│ Java Spring Boot │────▶│   PostgreSQL    │
│   (Port 8000)   │     │   (Port 8080)    │     │   (Port 5432)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        ▲
        │
   您現在在這裡
```

### 為什麼使用 FastAPI？

| 特點 | 說明 |
|------|------|
| **高效能** | 基於 Starlette 和 Pydantic，效能媲美 Node.js 和 Go |
| **自動文件** | 自動產生 OpenAPI (Swagger) 和 ReDoc 文件 |
| **型別提示** | 充分利用 Python 型別提示，提供 IDE 自動完成 |
| **資料驗證** | 使用 Pydantic 自動驗證請求和回應資料 |
| **非同步支援** | 原生支援 async/await 非同步程式設計 |

---

## 環境需求

### 本地開發
- Python 3.11+
- pip 或 pipenv

### Docker 部署
- Docker Engine 20.10+
- Docker Compose 2.0+

---

## 專案結構

```
fastapi-gateway/
├── Dockerfile           # Docker 建置設定
├── requirements.txt     # Python 依賴套件
└── main.py             # 主程式（所有程式碼）
```

### 為什麼只有一個檔案？

本專案作為 API Gateway 較為簡單，所有程式碼集中在 `main.py`。
大型專案建議拆分為：

```
fastapi-gateway/
├── app/
│   ├── __init__.py
│   ├── main.py          # 應用程式進入點
│   ├── config.py        # 設定
│   ├── models/          # Pydantic 模型
│   │   ├── user.py
│   │   └── product.py
│   ├── routers/         # 路由處理
│   │   ├── users.py
│   │   └── products.py
│   └── services/        # 業務邏輯
│       └── backend.py
├── tests/
├── Dockerfile
└── requirements.txt
```

---

## 依賴套件說明

### requirements.txt

```
fastapi==0.109.0           # FastAPI 框架
uvicorn[standard]==0.27.0  # ASGI 伺服器
httpx==0.26.0              # 非同步 HTTP 客戶端
pydantic==2.5.3            # 資料驗證
python-dotenv==1.0.0       # 環境變數管理
```

### 套件詳細說明

| 套件 | 用途 |
|------|------|
| **FastAPI** | Web 框架核心，處理路由、請求、回應 |
| **Uvicorn** | ASGI 伺服器，用於執行 FastAPI 應用程式 |
| **HTTPX** | 非同步 HTTP 客戶端，用於呼叫後端 API |
| **Pydantic** | 資料驗證和序列化（FastAPI 內建依賴） |
| **python-dotenv** | 從 .env 檔案載入環境變數 |

### ASGI vs WSGI

| 類型 | 說明 | 範例 |
|------|------|------|
| WSGI | 同步介面，一次處理一個請求 | Gunicorn, uWSGI |
| ASGI | 非同步介面，可同時處理多個請求 | Uvicorn, Hypercorn |

FastAPI 使用 ASGI，因此需要 Uvicorn 作為伺服器。

---

## 程式碼架構

### 整體流程圖

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP Request
       ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Router    │───▶│  Pydantic   │───▶│   HTTPX     │     │
│  │  Endpoints  │    │  Validation │    │   Client    │     │
│  └─────────────┘    └─────────────┘    └──────┬──────┘     │
└─────────────────────────────────────────────────│───────────┘
                                                  │
                                                  ▼
                                        ┌─────────────────┐
                                        │  Spring Boot    │
                                        │     API         │
                                        └─────────────────┘
```

### 請求處理流程

1. **接收請求**: FastAPI 接收 HTTP 請求
2. **路由匹配**: 根據路徑找到對應的處理函數
3. **資料驗證**: Pydantic 驗證請求資料
4. **轉發請求**: HTTPX 非同步呼叫 Spring Boot API
5. **回傳結果**: 將後端回應轉換後回傳給客戶端

---

## 程式碼詳解

### 1. 匯入與設定

```python
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

# ========================================
# 配置設定
# ========================================

# 從環境變數取得後端 API URL，預設為 localhost
SPRING_BOOT_API_URL = os.getenv("SPRING_BOOT_API_URL", "http://localhost:8080")

# 全域 HTTP 客戶端（稍後在 lifespan 中初始化）
http_client: Optional[httpx.AsyncClient] = None
```

#### 說明

| 元素 | 說明 |
|------|------|
| `os.getenv()` | 從環境變數讀取設定，支援預設值 |
| `Optional[T]` | 型別提示，表示可能為 None |
| `httpx.AsyncClient` | 非同步 HTTP 客戶端，效能優於 requests |

---

### 2. 應用程式生命週期管理

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    應用程式生命週期管理器

    - 啟動時：初始化 HTTP 客戶端
    - 關閉時：關閉 HTTP 客戶端連線
    """
    global http_client

    # ===== 啟動時執行 =====
    http_client = httpx.AsyncClient(
        base_url=SPRING_BOOT_API_URL,
        timeout=30.0  # 請求超時時間（秒）
    )

    yield  # 應用程式運行中

    # ===== 關閉時執行 =====
    await http_client.aclose()


# 建立 FastAPI 應用程式實例
app = FastAPI(
    title="FastAPI Gateway",
    description="API Gateway that connects to Spring Boot backend",
    version="1.0.0",
    lifespan=lifespan  # 註冊生命週期管理器
)
```

#### Lifespan 說明

```
應用程式啟動
     │
     ▼
┌─────────────────┐
│  初始化資源     │ ← yield 之前的程式碼
│  (HTTP Client)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  應用程式運行   │ ← yield
│  (處理請求)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  釋放資源       │ ← yield 之後的程式碼
│  (關閉連線)     │
└─────────────────┘
```

---

### 3. CORS 中介軟體

```python
# CORS (跨來源資源共享) 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # 允許所有來源（生產環境應限制）
    allow_credentials=True,         # 允許攜帶憑證
    allow_methods=["*"],           # 允許所有 HTTP 方法
    allow_headers=["*"],           # 允許所有 HTTP 標頭
)
```

#### CORS 說明

CORS 是瀏覽器的安全機制，限制網頁只能向同源伺服器發送請求。
API Gateway 通常需要開放 CORS，讓前端應用程式可以跨域存取。

| 設定 | 生產環境建議 |
|------|--------------|
| `allow_origins` | 限制為特定域名 `["https://example.com"]` |
| `allow_methods` | 限制為需要的方法 `["GET", "POST"]` |
| `allow_headers` | 限制為需要的標頭 |

---

### 4. Pydantic 模型定義

```python
# ========================================
# Pydantic 模型 - 資料驗證與序列化
# ========================================

class UserCreate(BaseModel):
    """建立使用者的請求模型"""

    # 必填欄位：使用者名稱（3-50 字元）
    username: str = Field(..., min_length=3, max_length=50)

    # 必填欄位：Email（自動驗證格式）
    email: EmailStr

    # 選填欄位：全名（最長 100 字元）
    # alias="fullName" 表示 JSON 中使用 fullName，Python 中使用 full_name
    full_name: Optional[str] = Field(None, max_length=100, alias="fullName")

    class Config:
        # 允許使用欄位名稱或別名
        populate_by_name = True


class UserResponse(BaseModel):
    """使用者回應模型"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = Field(None, alias="fullName")

    class Config:
        populate_by_name = True


class ProductCreate(BaseModel):
    """建立產品的請求模型"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)  # 必須大於 0
    stock: int = Field(default=0, ge=0)  # 必須大於等於 0


class ProductResponse(BaseModel):
    """產品回應模型"""
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int


class ApiResponse(BaseModel):
    """統一 API 回應格式"""
    success: bool
    message: str
    data: Optional[dict | list] = None
```

#### Pydantic Field 驗證參數

| 參數 | 說明 | 範例 |
|------|------|------|
| `...` | 必填欄位 | `Field(...)` |
| `default` | 預設值 | `Field(default=0)` |
| `min_length` | 最小長度 | `Field(min_length=3)` |
| `max_length` | 最大長度 | `Field(max_length=50)` |
| `gt` | 大於 | `Field(gt=0)` |
| `ge` | 大於等於 | `Field(ge=0)` |
| `lt` | 小於 | `Field(lt=100)` |
| `le` | 小於等於 | `Field(le=100)` |
| `regex` | 正規表達式 | `Field(regex=r"^\d+$")` |
| `alias` | JSON 欄位別名 | `Field(alias="fullName")` |

---

### 5. 健康檢查端點

```python
# ========================================
# 健康檢查 API
# ========================================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Gateway 健康檢查

    回傳 Gateway 自身的狀態
    """
    return {
        "status": "UP",
        "service": "FastAPI Gateway",
        "backend_url": SPRING_BOOT_API_URL
    }


@app.get("/health/backend", tags=["Health"])
async def backend_health_check():
    """
    檢查 Spring Boot 後端健康狀態

    透過呼叫後端的 /api/health 端點確認後端是否可用
    """
    try:
        response = await http_client.get("/api/health")
        return response.json()
    except httpx.RequestError as e:
        # 後端不可用時回傳 503 Service Unavailable
        raise HTTPException(
            status_code=503,
            detail=f"Backend unavailable: {str(e)}"
        )
```

#### 裝飾器說明

| 語法 | 說明 |
|------|------|
| `@app.get("/path")` | 處理 GET 請求 |
| `@app.post("/path")` | 處理 POST 請求 |
| `@app.put("/path")` | 處理 PUT 請求 |
| `@app.delete("/path")` | 處理 DELETE 請求 |
| `tags=["Name"]` | Swagger 文件中的分類標籤 |

---

### 6. 使用者 API 端點

```python
# ========================================
# 使用者 API
# ========================================

@app.get("/api/users", tags=["Users"], response_model=ApiResponse)
async def get_all_users():
    """
    取得所有使用者

    從 Spring Boot API 取得使用者列表
    """
    try:
        # 非同步呼叫後端 API
        response = await http_client.get("/api/users")
        # 檢查 HTTP 狀態碼
        response.raise_for_status()
        # 回傳 JSON 資料
        return response.json()
    except httpx.HTTPStatusError as e:
        # 後端回傳錯誤狀態碼
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )
    except httpx.RequestError as e:
        # 網路錯誤、超時等
        raise HTTPException(
            status_code=503,
            detail=f"Backend unavailable: {str(e)}"
        )


@app.get("/api/users/{user_id}", tags=["Users"], response_model=ApiResponse)
async def get_user_by_id(user_id: int):
    """
    根據 ID 取得使用者

    Args:
        user_id: 使用者 ID（從路徑參數取得）
    """
    try:
        response = await http_client.get(f"/api/users/{user_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Backend unavailable: {str(e)}"
        )


@app.post("/api/users", tags=["Users"], response_model=ApiResponse, status_code=201)
async def create_user(user: UserCreate):
    """
    建立新使用者

    Args:
        user: 使用者資料（從請求 Body 取得，自動驗證）
    """
    try:
        # 準備要傳送的資料
        payload = {
            "username": user.username,
            "email": user.email,
            "fullName": user.full_name
        }
        # 發送 POST 請求
        response = await http_client.post("/api/users", json=payload)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Backend unavailable: {str(e)}"
        )


@app.put("/api/users/{user_id}", tags=["Users"], response_model=ApiResponse)
async def update_user(user_id: int, user: UserCreate):
    """
    更新使用者

    Args:
        user_id: 使用者 ID（路徑參數）
        user: 更新的使用者資料（請求 Body）
    """
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
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Backend unavailable: {str(e)}"
        )


@app.delete("/api/users/{user_id}", tags=["Users"], response_model=ApiResponse)
async def delete_user(user_id: int):
    """
    刪除使用者

    Args:
        user_id: 要刪除的使用者 ID
    """
    try:
        response = await http_client.delete(f"/api/users/{user_id}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Backend unavailable: {str(e)}"
        )
```

---

### 7. 產品 API 端點

```python
# ========================================
# 產品 API
# ========================================

@app.get("/api/products", tags=["Products"], response_model=ApiResponse)
async def get_all_products():
    """取得所有產品"""
    try:
        response = await http_client.get("/api/products")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Backend unavailable: {str(e)}"
        )


@app.get("/api/products/search", tags=["Products"], response_model=ApiResponse)
async def search_products(name: str = Query(..., min_length=1)):
    """
    搜尋產品

    Args:
        name: 搜尋關鍵字（Query 參數，必填，至少 1 字元）

    範例: GET /api/products/search?name=laptop
    """
    try:
        response = await http_client.get(
            "/api/products/search",
            params={"name": name}  # Query 參數
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Backend unavailable: {str(e)}"
        )


@app.post("/api/products", tags=["Products"], response_model=ApiResponse, status_code=201)
async def create_product(product: ProductCreate):
    """建立新產品"""
    try:
        # model_dump() 將 Pydantic 模型轉換為字典
        response = await http_client.post(
            "/api/products",
            json=product.model_dump()
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Backend unavailable: {str(e)}"
        )
```

---

### 8. 主程式進入點

```python
# ========================================
# 主程式進入點（本地開發用）
# ========================================

if __name__ == "__main__":
    import uvicorn

    # 啟動 Uvicorn 伺服器
    uvicorn.run(
        app,              # FastAPI 應用程式實例
        host="0.0.0.0",   # 監聽所有網路介面
        port=8000         # 埠號
    )
```

#### Uvicorn 參數說明

| 參數 | 說明 |
|------|------|
| `host` | 監聽的 IP 位址，0.0.0.0 表示所有介面 |
| `port` | 監聽的埠號 |
| `reload` | 開發模式，程式碼變更時自動重載 |
| `workers` | 工作程序數量（多核心處理） |

---

## 執行步驟

### 方式 1：使用 Docker Compose（推薦）

```bash
# 進入專案目錄
cd /path/to/java-api-test

# 啟動所有服務
docker-compose up --build

# 或在背景執行
docker-compose up -d --build

# 查看 FastAPI 日誌
docker-compose logs -f fastapi-gateway
```

### 方式 2：本地開發

```bash
# 1. 確保 Spring Boot API 正在運行
docker-compose up postgres spring-boot-api -d

# 2. 進入 FastAPI 專案目錄
cd fastapi-gateway

# 3. 建立虛擬環境（建議）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate   # Windows

# 4. 安裝依賴套件
pip install -r requirements.txt

# 5. 執行應用程式
uvicorn main:app --reload --port 8000

# --reload: 開發模式，程式碼變更時自動重載
```

### 驗證服務啟動

```bash
# 健康檢查
curl http://localhost:8000/health

# 預期回應
{
  "status": "UP",
  "service": "FastAPI Gateway",
  "backend_url": "http://spring-boot-api:8080"
}

# 檢查後端連線
curl http://localhost:8000/health/backend
```

---

## API 測試

### 使用 cURL

```bash
# ========================================
# 使用者 API
# ========================================

# 取得所有使用者
curl http://localhost:8000/api/users

# 取得特定使用者
curl http://localhost:8000/api/users/1

# 建立新使用者
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_user",
    "email": "newuser@example.com",
    "fullName": "New User"
  }'

# 更新使用者
curl -X PUT http://localhost:8000/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "username": "updated_user",
    "email": "updated@example.com",
    "fullName": "Updated User"
  }'

# 刪除使用者
curl -X DELETE http://localhost:8000/api/users/3


# ========================================
# 產品 API
# ========================================

# 取得所有產品
curl http://localhost:8000/api/products

# 搜尋產品
curl "http://localhost:8000/api/products/search?name=laptop"

# 建立新產品
curl -X POST http://localhost:8000/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tablet",
    "description": "10-inch tablet",
    "price": 499.99,
    "stock": 75
  }'
```

### 使用 Python requests

```python
import requests

BASE_URL = "http://localhost:8000"

# 取得所有使用者
response = requests.get(f"{BASE_URL}/api/users")
print(response.json())

# 建立新使用者
new_user = {
    "username": "python_user",
    "email": "python@example.com",
    "fullName": "Python User"
}
response = requests.post(f"{BASE_URL}/api/users", json=new_user)
print(response.json())
```

---

## Swagger 文件

FastAPI 自動產生互動式 API 文件：

### Swagger UI
```
http://localhost:8000/docs
```

![Swagger UI 示意](https://fastapi.tiangolo.com/img/index/index-01-swagger-ui-simple.png)

### ReDoc
```
http://localhost:8000/redoc
```

### OpenAPI JSON
```
http://localhost:8000/openapi.json
```

### Swagger UI 功能

1. **瀏覽所有 API**: 依標籤分類顯示
2. **查看請求/回應格式**: 自動從 Pydantic 模型產生
3. **線上測試**: 直接在網頁上發送請求
4. **下載規格**: 匯出 OpenAPI 規格檔

---

## Dockerfile 詳解

```dockerfile
# 使用 Python 3.11 精簡版映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製並安裝依賴套件（利用 Docker 快取）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY main.py .

# 建立非 root 使用者（安全性最佳實踐）
RUN useradd -m appuser
USER appuser

# 開放埠號
EXPOSE 8000

# 啟動指令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile 最佳實踐

| 技巧 | 說明 |
|------|------|
| 分層複製 | 先複製 requirements.txt，再複製程式碼，利用快取 |
| 非 root 使用者 | 避免使用 root 執行應用程式 |
| slim 映像 | 使用精簡版映像減少體積 |
| --no-cache-dir | pip 不快取套件，減少映像體積 |

---

## 常見問題

### Q1: 無法連線到後端 API

```python
# 錯誤訊息
HTTPException: 503 - Backend unavailable

# 解決方案
1. 確認 Spring Boot API 正在運行
   $ docker-compose ps

2. 確認環境變數設定正確
   $ echo $SPRING_BOOT_API_URL

3. 確認網路連通
   $ curl http://localhost:8080/api/health
```

### Q2: Pydantic 驗證失敗

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "username"],
      "msg": "String should have at least 3 characters",
      "input": "ab"
    }
  ]
}
```

請確認輸入資料符合驗證規則。

### Q3: CORS 錯誤

```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000'
has been blocked by CORS policy
```

確認 CORS 中介軟體已正確設定，或將前端來源加入 `allow_origins`。

### Q4: 非同步與同步

```python
# 錯誤：在非同步函數中使用同步的 requests
async def get_users():
    response = requests.get(...)  # 錯誤！會阻塞

# 正確：使用非同步的 httpx
async def get_users():
    response = await http_client.get(...)  # 正確
```

---

## 進階主題

### 1. 錯誤處理優化

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(httpx.RequestError)
async def httpx_exception_handler(request: Request, exc: httpx.RequestError):
    return JSONResponse(
        status_code=503,
        content={"success": False, "message": f"Backend error: {exc}"}
    )
```

### 2. 請求日誌中介軟體

```python
import time
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        print(f"{request.method} {request.url.path} - {process_time:.3f}s")
        return response

app.add_middleware(LoggingMiddleware)
```

### 3. 依賴注入

```python
from fastapi import Depends

async def get_http_client():
    return http_client

@app.get("/api/users")
async def get_users(client: httpx.AsyncClient = Depends(get_http_client)):
    response = await client.get("/api/users")
    return response.json()
```

---

## 下一步

完成 FastAPI 設定後，您已經學會了完整的三層架構：

- [01-PostgreSQL-Tutorial.md](./01-PostgreSQL-Tutorial.md) - PostgreSQL 資料庫教學
- [02-SpringBoot-Tutorial.md](./02-SpringBoot-Tutorial.md) - Java Spring Boot API 教學

### 延伸學習

1. **認證授權**: 加入 JWT 驗證
2. **快取**: 使用 Redis 快取 API 回應
3. **監控**: 整合 Prometheus + Grafana
4. **訊息佇列**: 使用 RabbitMQ 或 Kafka
5. **API 版本控制**: 實作 /v1/, /v2/ 版本
