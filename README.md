# PostgreSQL + Spring Boot + FastAPI 整合專案

這是一個完整的三層架構專案，包含：
- **PostgreSQL**: 資料庫層
- **Java Spring Boot**: 後端 REST API
- **Python FastAPI**: API Gateway

## 系統架構

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Python FastAPI │────▶│ Java Spring Boot │────▶│   PostgreSQL    │
│   (Port 8000)   │     │   (Port 8080)    │     │   (Port 5432)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
       Gateway              Backend API              Database
```

## 快速開始

### 使用 Docker Compose 啟動所有服務

```bash
# 建置並啟動所有服務
docker-compose up --build

# 在背景執行
docker-compose up -d --build
```

### 停止服務

```bash
docker-compose down

# 同時刪除資料卷
docker-compose down -v
```

## API 端點

### FastAPI Gateway (Port 8000)

訪問 Swagger 文件: http://localhost:8000/docs

#### 健康檢查
- `GET /health` - Gateway 健康狀態
- `GET /health/backend` - 檢查 Spring Boot 後端狀態

#### 使用者 API
- `GET /api/users` - 取得所有使用者
- `GET /api/users/{id}` - 根據 ID 取得使用者
- `POST /api/users` - 建立新使用者
- `PUT /api/users/{id}` - 更新使用者
- `DELETE /api/users/{id}` - 刪除使用者

#### 產品 API
- `GET /api/products` - 取得所有產品
- `GET /api/products/{id}` - 根據 ID 取得產品
- `GET /api/products/search?name=xxx` - 搜尋產品
- `POST /api/products` - 建立新產品
- `PUT /api/products/{id}` - 更新產品
- `DELETE /api/products/{id}` - 刪除產品

### Spring Boot API (Port 8080)

直接存取後端 API: http://localhost:8080/api

## 測試範例

### 建立使用者
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "fullName": "Test User"
  }'
```

### 取得所有使用者
```bash
curl http://localhost:8000/api/users
```

### 建立產品
```bash
curl -X POST http://localhost:8000/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Product",
    "description": "Product description",
    "price": 99.99,
    "stock": 100
  }'
```

### 搜尋產品
```bash
curl "http://localhost:8000/api/products/search?name=laptop"
```

## 專案結構

```
java-api-test/
├── docker-compose.yml          # Docker Compose 配置
├── init-db/
│   └── 01-init.sql            # 資料庫初始化腳本
├── spring-boot-api/           # Java Spring Boot 專案
│   ├── Dockerfile
│   ├── pom.xml
│   └── src/main/java/com/example/api/
│       ├── Application.java
│       ├── controller/        # REST Controllers
│       ├── service/           # Business Logic
│       ├── repository/        # Data Access
│       ├── entity/            # JPA Entities
│       └── dto/               # Data Transfer Objects
└── fastapi-gateway/           # Python FastAPI 專案
    ├── Dockerfile
    ├── requirements.txt
    └── main.py
```

## 技術棧

### 資料庫
- PostgreSQL 15

### 後端
- Java 17
- Spring Boot 3.2
- Spring Data JPA
- Lombok

### API Gateway
- Python 3.11
- FastAPI
- HTTPX (非同步 HTTP 客戶端)
- Pydantic (資料驗證)

## 開發模式

### 單獨啟動 PostgreSQL
```bash
docker-compose up postgres -d
```

### 本地開發 Spring Boot
```bash
cd spring-boot-api
./mvnw spring-boot:run
```

### 本地開發 FastAPI
```bash
cd fastapi-gateway
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## 環境變數

### Spring Boot
- `SPRING_DATASOURCE_URL`: 資料庫連線 URL
- `SPRING_DATASOURCE_USERNAME`: 資料庫使用者名稱
- `SPRING_DATASOURCE_PASSWORD`: 資料庫密碼

### FastAPI
- `SPRING_BOOT_API_URL`: Spring Boot API 基礎 URL

## 預設測試資料

系統啟動時會自動建立以下測試資料：

### 使用者
| ID | Username    | Email             | Full Name   |
|----|-------------|-------------------|-------------|
| 1  | john_doe    | john@example.com  | John Doe    |
| 2  | jane_smith  | jane@example.com  | Jane Smith  |
| 3  | bob_wilson  | bob@example.com   | Bob Wilson  |

### 產品
| ID | Name        | Price   | Stock |
|----|-------------|---------|-------|
| 1  | Laptop      | 999.99  | 50    |
| 2  | Smartphone  | 699.99  | 100   |
| 3  | Headphones  | 299.99  | 200   |
