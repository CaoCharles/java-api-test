# PostgreSQL 資料庫教學文件

## 目錄
1. [簡介](#簡介)
2. [環境需求](#環境需求)
3. [Docker 設定說明](#docker-設定說明)
4. [資料庫結構設計](#資料庫結構設計)
5. [初始化腳本詳解](#初始化腳本詳解)
6. [執行步驟](#執行步驟)
7. [連線與測試](#連線與測試)
8. [常用指令](#常用指令)

---

## 簡介

PostgreSQL 是一個功能強大的開源物件關聯式資料庫系統。本專案使用 PostgreSQL 15 Alpine 版本作為資料儲存層，透過 Docker 容器化部署，提供穩定且可移植的資料庫環境。

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

---

## 環境需求

- Docker Engine 20.10+
- Docker Compose 2.0+
- 至少 512MB 可用記憶體
- 1GB 可用磁碟空間

---

## Docker 設定說明

### docker-compose.yml 中的 PostgreSQL 設定

```yaml
services:
  postgres:
    image: postgres:15-alpine          # 使用輕量級 Alpine 版本
    container_name: postgres-db        # 容器名稱
    environment:
      POSTGRES_DB: userdb              # 預設資料庫名稱
      POSTGRES_USER: admin             # 資料庫管理員帳號
      POSTGRES_PASSWORD: admin123      # 資料庫管理員密碼
    ports:
      - "5432:5432"                    # 對外開放埠號
    volumes:
      - postgres_data:/var/lib/postgresql/data    # 資料持久化
      - ./init-db:/docker-entrypoint-initdb.d     # 初始化腳本目錄
    networks:
      - app-network                    # 內部網路
    healthcheck:                       # 健康檢查設定
      test: ["CMD-SHELL", "pg_isready -U admin -d userdb"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### 設定參數說明

| 參數 | 說明 |
|------|------|
| `image: postgres:15-alpine` | 使用 PostgreSQL 15 版本的 Alpine Linux 映像，體積小、啟動快 |
| `POSTGRES_DB` | 容器啟動時自動建立的資料庫名稱 |
| `POSTGRES_USER` | 超級使用者帳號（非 postgres） |
| `POSTGRES_PASSWORD` | 超級使用者密碼 |
| `volumes: postgres_data` | 將資料庫檔案儲存在 Docker Volume，確保容器重啟後資料不遺失 |
| `volumes: ./init-db` | 掛載初始化腳本目錄，容器首次啟動時會執行其中的 SQL 檔案 |
| `healthcheck` | 定期檢查資料庫是否可用，供其他服務判斷依賴狀態 |

---

## 資料庫結構設計

### 實體關係圖 (ERD)

```
┌──────────────────────────────┐
│           users              │
├──────────────────────────────┤
│ id          SERIAL      PK   │
│ username    VARCHAR(50) UQ   │
│ email       VARCHAR(100) UQ  │
│ full_name   VARCHAR(100)     │
│ created_at  TIMESTAMP        │
│ updated_at  TIMESTAMP        │
└──────────────────────────────┘

┌──────────────────────────────┐
│          products            │
├──────────────────────────────┤
│ id          SERIAL      PK   │
│ name        VARCHAR(100)     │
│ description TEXT             │
│ price       DECIMAL(10,2)    │
│ stock       INTEGER          │
│ created_at  TIMESTAMP        │
│ updated_at  TIMESTAMP        │
└──────────────────────────────┘
```

### 資料表設計原則

1. **主鍵設計**: 使用 `SERIAL` 自動遞增整數作為主鍵
2. **唯一約束**: `username` 和 `email` 設定唯一約束，避免重複
3. **時間戳記**: 每個表都有 `created_at` 和 `updated_at` 欄位，追蹤資料異動
4. **預設值**: `stock` 欄位預設為 0，`timestamp` 欄位預設為當前時間

---

## 初始化腳本詳解

### 檔案位置
```
init-db/
└── 01-init.sql    # 初始化腳本（依檔名順序執行）
```

### 01-init.sql 完整解析

```sql
-- =============================================
-- 第一部分：建立 users 資料表
-- =============================================
CREATE TABLE IF NOT EXISTS users (
    -- 主鍵：自動遞增的整數 ID
    id SERIAL PRIMARY KEY,

    -- 使用者名稱：必填、唯一、最長 50 字元
    username VARCHAR(50) NOT NULL UNIQUE,

    -- 電子郵件：必填、唯一、最長 100 字元
    email VARCHAR(100) NOT NULL UNIQUE,

    -- 全名：選填、最長 100 字元
    full_name VARCHAR(100),

    -- 建立時間：預設為當前時間
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 更新時間：預設為當前時間
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- 第二部分：建立 products 資料表
-- =============================================
CREATE TABLE IF NOT EXISTS products (
    -- 主鍵：自動遞增的整數 ID
    id SERIAL PRIMARY KEY,

    -- 產品名稱：必填、最長 100 字元
    name VARCHAR(100) NOT NULL,

    -- 產品描述：選填、無長度限制
    description TEXT,

    -- 價格：必填、最多 10 位數，小數點後 2 位
    price DECIMAL(10, 2) NOT NULL,

    -- 庫存數量：預設為 0
    stock INTEGER DEFAULT 0,

    -- 時間戳記欄位
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- 第三部分：插入測試資料
-- =============================================

-- 使用者測試資料
INSERT INTO users (username, email, full_name) VALUES
    ('john_doe', 'john@example.com', 'John Doe'),
    ('jane_smith', 'jane@example.com', 'Jane Smith'),
    ('bob_wilson', 'bob@example.com', 'Bob Wilson');

-- 產品測試資料
INSERT INTO products (name, description, price, stock) VALUES
    ('Laptop', 'High-performance laptop', 999.99, 50),
    ('Smartphone', 'Latest smartphone model', 699.99, 100),
    ('Headphones', 'Wireless noise-canceling headphones', 299.99, 200);
```

### SQL 語法說明

| 語法 | 說明 |
|------|------|
| `SERIAL` | PostgreSQL 特有語法，等同於 `INTEGER` + 自動遞增序列 |
| `VARCHAR(n)` | 可變長度字串，最多 n 個字元 |
| `TEXT` | 無限長度文字 |
| `DECIMAL(p, s)` | 精確小數，p 為總位數，s 為小數位數 |
| `TIMESTAMP` | 日期時間型態 |
| `NOT NULL` | 欄位不可為空 |
| `UNIQUE` | 欄位值必須唯一 |
| `DEFAULT` | 設定預設值 |
| `IF NOT EXISTS` | 如果表已存在則不建立（避免重複執行錯誤） |

---

## 執行步驟

### 步驟 1：僅啟動 PostgreSQL

```bash
# 進入專案目錄
cd /path/to/java-api-test

# 僅啟動 PostgreSQL 服務
docker-compose up postgres -d

# 查看服務狀態
docker-compose ps
```

### 步驟 2：確認服務啟動

```bash
# 查看容器日誌
docker-compose logs postgres

# 預期輸出（節錄）：
# postgres-db  | PostgreSQL init process complete; ready for start up.
# postgres-db  | database system is ready to accept connections
```

### 步驟 3：驗證健康狀態

```bash
# 檢查健康狀態
docker inspect --format='{{.State.Health.Status}}' postgres-db

# 預期輸出：healthy
```

---

## 連線與測試

### 方法 1：使用 docker exec 進入容器

```bash
# 進入 PostgreSQL 容器
docker exec -it postgres-db psql -U admin -d userdb

# 現在您已進入 PostgreSQL 互動式介面
```

### 方法 2：使用外部工具連線

使用 pgAdmin、DBeaver 或其他資料庫管理工具：

| 參數 | 值 |
|------|------|
| Host | localhost |
| Port | 5432 |
| Database | userdb |
| Username | admin |
| Password | admin123 |

### 連線後的測試指令

```sql
-- 列出所有資料表
\dt

-- 查看 users 資料表結構
\d users

-- 查詢所有使用者
SELECT * FROM users;

-- 查詢所有產品
SELECT * FROM products;

-- 查詢特定產品（價格低於 500）
SELECT name, price FROM products WHERE price < 500;

-- 離開 psql
\q
```

---

## 常用指令

### Docker 相關指令

```bash
# 啟動服務
docker-compose up postgres -d

# 停止服務
docker-compose stop postgres

# 重啟服務
docker-compose restart postgres

# 查看日誌（即時追蹤）
docker-compose logs -f postgres

# 移除容器（保留資料）
docker-compose rm postgres

# 移除容器和資料卷（⚠️ 資料將被刪除）
docker-compose down -v
```

### PostgreSQL 管理指令

```bash
# 備份資料庫
docker exec postgres-db pg_dump -U admin userdb > backup.sql

# 還原資料庫
docker exec -i postgres-db psql -U admin userdb < backup.sql

# 查看連線數
docker exec postgres-db psql -U admin -d userdb -c "SELECT count(*) FROM pg_stat_activity;"

# 查看資料庫大小
docker exec postgres-db psql -U admin -d userdb -c "SELECT pg_size_pretty(pg_database_size('userdb'));"
```

### psql 內部指令

| 指令 | 說明 |
|------|------|
| `\l` | 列出所有資料庫 |
| `\dt` | 列出當前資料庫的所有資料表 |
| `\d table_name` | 顯示資料表結構 |
| `\du` | 列出所有使用者 |
| `\c database_name` | 切換資料庫 |
| `\q` | 離開 psql |
| `\?` | 顯示所有指令說明 |

---

## 故障排除

### 問題 1：容器無法啟動

```bash
# 查看詳細錯誤訊息
docker-compose logs postgres

# 常見原因：埠號被佔用
# 解決方案：修改 docker-compose.yml 中的 ports 設定
```

### 問題 2：無法連線到資料庫

```bash
# 確認容器正在運行
docker ps | grep postgres

# 確認健康狀態
docker inspect --format='{{.State.Health.Status}}' postgres-db

# 測試連線
docker exec postgres-db pg_isready -U admin -d userdb
```

### 問題 3：資料遺失

確認使用了持久化 Volume：
```bash
# 查看 Volume
docker volume ls | grep postgres

# 檢查 Volume 詳情
docker volume inspect java-api-test_postgres_data
```

---

## 下一步

完成 PostgreSQL 設定後，請參考以下文件繼續學習：

- [02-SpringBoot-Tutorial.md](./02-SpringBoot-Tutorial.md) - Java Spring Boot API 教學
- [03-FastAPI-Tutorial.md](./03-FastAPI-Tutorial.md) - Python FastAPI 教學
