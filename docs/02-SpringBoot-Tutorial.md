# Java Spring Boot API 教學文件

## 目錄
1. [簡介](#簡介)
2. [環境需求](#環境需求)
3. [專案結構](#專案結構)
4. [Maven 設定檔詳解](#maven-設定檔詳解)
5. [應用程式設定](#應用程式設定)
6. [分層架構設計](#分層架構設計)
7. [程式碼詳解](#程式碼詳解)
8. [執行步驟](#執行步驟)
9. [API 測試](#api-測試)
10. [常見問題](#常見問題)

---

## 簡介

Spring Boot 是基於 Spring Framework 的快速開發框架，簡化了 Spring 應用程式的配置和部署。本專案使用 Spring Boot 3.2 建立 RESTful API，連接 PostgreSQL 資料庫。

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

### 主要功能
- 提供 RESTful API 端點
- 使用 JPA 進行資料庫操作
- 實作完整的 CRUD 功能
- 資料驗證和例外處理

---

## 環境需求

### 本地開發
- Java JDK 17+
- Maven 3.9+
- IDE (IntelliJ IDEA / Eclipse / VS Code)

### Docker 部署
- Docker Engine 20.10+
- Docker Compose 2.0+

---

## 專案結構

```
spring-boot-api/
├── Dockerfile                           # Docker 建置設定
├── pom.xml                              # Maven 設定檔
└── src/main/
    ├── java/com/example/api/
    │   ├── Application.java             # 應用程式進入點
    │   ├── controller/                  # 控制器層
    │   │   ├── UserController.java      # 使用者 API
    │   │   ├── ProductController.java   # 產品 API
    │   │   ├── HealthController.java    # 健康檢查 API
    │   │   └── GlobalExceptionHandler.java  # 全域例外處理
    │   ├── service/                     # 服務層
    │   │   ├── UserService.java
    │   │   └── ProductService.java
    │   ├── repository/                  # 資料存取層
    │   │   ├── UserRepository.java
    │   │   └── ProductRepository.java
    │   ├── entity/                      # 實體類別
    │   │   ├── User.java
    │   │   └── Product.java
    │   └── dto/                         # 資料傳輸物件
    │       ├── UserDTO.java
    │       ├── ProductDTO.java
    │       └── ApiResponse.java
    └── resources/
        └── application.yml              # 應用程式設定
```

---

## Maven 設定檔詳解

### pom.xml 完整解析

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <!-- ========================================
         父專案設定：繼承 Spring Boot 預設配置
         ======================================== -->
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>
    </parent>

    <!-- ========================================
         專案基本資訊
         ======================================== -->
    <groupId>com.example</groupId>
    <artifactId>spring-boot-api</artifactId>
    <version>1.0.0</version>
    <name>spring-boot-api</name>
    <description>Spring Boot REST API with PostgreSQL</description>

    <!-- ========================================
         屬性設定
         ======================================== -->
    <properties>
        <java.version>17</java.version>  <!-- 使用 Java 17 -->
    </properties>

    <!-- ========================================
         依賴套件
         ======================================== -->
    <dependencies>
        <!-- Spring Boot Web: 提供 REST API 功能 -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- Spring Data JPA: ORM 框架 -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>

        <!-- PostgreSQL 驅動程式 -->
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>

        <!-- 資料驗證 -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>

        <!-- Lombok: 減少樣板程式碼 -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>

        <!-- 測試套件 -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

### 依賴套件說明

| 依賴 | 用途 |
|------|------|
| `spring-boot-starter-web` | 建立 Web 應用程式，包含 Tomcat、Spring MVC |
| `spring-boot-starter-data-jpa` | JPA 支援，使用 Hibernate 作為 ORM |
| `postgresql` | PostgreSQL JDBC 驅動程式 |
| `spring-boot-starter-validation` | Bean Validation (JSR-380) 支援 |
| `lombok` | 自動產生 getter/setter、建構子等程式碼 |

---

## 應用程式設定

### application.yml 詳解

```yaml
# ========================================
# 伺服器設定
# ========================================
server:
  port: 8080                    # 服務埠號

# ========================================
# Spring 設定
# ========================================
spring:
  application:
    name: spring-boot-api       # 應用程式名稱

  # 資料庫連線設定
  datasource:
    # 使用環境變數，若無則使用預設值
    url: ${SPRING_DATASOURCE_URL:jdbc:postgresql://localhost:5432/userdb}
    username: ${SPRING_DATASOURCE_USERNAME:admin}
    password: ${SPRING_DATASOURCE_PASSWORD:admin123}
    driver-class-name: org.postgresql.Driver

  # JPA 設定
  jpa:
    hibernate:
      ddl-auto: validate        # 只驗證 Schema，不自動修改
    show-sql: true              # 在控制台顯示 SQL
    properties:
      hibernate:
        format_sql: true        # 格式化 SQL 輸出
        dialect: org.hibernate.dialect.PostgreSQLDialect

# ========================================
# 日誌設定
# ========================================
logging:
  level:
    org.springframework.web: INFO
    org.hibernate.SQL: DEBUG    # 顯示 SQL 語句
    com.example.api: DEBUG      # 專案日誌級別
```

### ddl-auto 選項說明

| 選項 | 說明 |
|------|------|
| `validate` | 驗證 Schema 是否符合 Entity 定義（推薦用於生產環境） |
| `update` | 自動更新 Schema（新增欄位，不會刪除） |
| `create` | 每次啟動時重新建立 Schema（會刪除資料） |
| `create-drop` | 啟動時建立，關閉時刪除 |
| `none` | 不做任何動作 |

---

## 分層架構設計

### 架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                      Controller 層                          │
│  (接收 HTTP 請求，回傳 HTTP 回應)                            │
│  UserController, ProductController, HealthController        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Service 層                            │
│  (業務邏輯處理，資料轉換)                                    │
│  UserService, ProductService                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Repository 層                          │
│  (資料庫存取，CRUD 操作)                                     │
│  UserRepository, ProductRepository                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Entity 層                             │
│  (資料庫表格對應，JPA 實體)                                  │
│  User, Product                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      PostgreSQL                             │
└─────────────────────────────────────────────────────────────┘
```

### 各層職責

| 層級 | 職責 | 註解 |
|------|------|------|
| Controller | 處理 HTTP 請求與回應 | `@RestController` |
| Service | 業務邏輯、資料轉換 | `@Service` |
| Repository | 資料庫 CRUD 操作 | `@Repository` |
| Entity | 對應資料庫表格 | `@Entity` |
| DTO | 資料傳輸物件 | 無註解 |

---

## 程式碼詳解

### 1. 應用程式進入點 (Application.java)

```java
package com.example.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Spring Boot 應用程式進入點
 *
 * @SpringBootApplication 是一個組合註解，包含：
 * - @Configuration: 標記為配置類別
 * - @EnableAutoConfiguration: 啟用自動配置
 * - @ComponentScan: 自動掃描元件
 */
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        // 啟動 Spring Boot 應用程式
        SpringApplication.run(Application.class, args);
    }
}
```

---

### 2. Entity 層 - 實體類別

#### User.java

```java
package com.example.api.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

/**
 * 使用者實體類別 - 對應資料庫 users 表
 */
@Entity                          // 標記為 JPA 實體
@Table(name = "users")           // 指定對應的資料表名稱
@Data                            // Lombok: 自動產生 getter/setter/toString/equals/hashCode
@NoArgsConstructor               // Lombok: 產生無參數建構子
@AllArgsConstructor              // Lombok: 產生全參數建構子
public class User {

    @Id                          // 標記為主鍵
    @GeneratedValue(strategy = GenerationType.IDENTITY)  // 使用資料庫自動遞增
    private Long id;

    @Column(nullable = false, unique = true, length = 50)
    private String username;     // 使用者名稱：必填、唯一、最長50字

    @Column(nullable = false, unique = true, length = 100)
    private String email;        // 電子郵件：必填、唯一、最長100字

    @Column(name = "full_name", length = 100)
    private String fullName;     // 全名：對應 full_name 欄位

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    /**
     * 在儲存前自動設定時間戳記
     */
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    /**
     * 在更新前自動更新時間戳記
     */
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
```

#### JPA 註解說明

| 註解 | 說明 |
|------|------|
| `@Entity` | 標記類別為 JPA 實體 |
| `@Table` | 指定對應的資料表名稱 |
| `@Id` | 標記主鍵欄位 |
| `@GeneratedValue` | 主鍵產生策略 |
| `@Column` | 自訂欄位屬性 |
| `@PrePersist` | 在新增資料前執行 |
| `@PreUpdate` | 在更新資料前執行 |

---

### 3. Repository 層 - 資料存取

#### UserRepository.java

```java
package com.example.api.repository;

import com.example.api.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

/**
 * 使用者資料存取介面
 *
 * 繼承 JpaRepository 自動獲得：
 * - save(): 新增或更新
 * - findById(): 根據 ID 查詢
 * - findAll(): 查詢全部
 * - deleteById(): 根據 ID 刪除
 * - count(): 計算總數
 * 等方法
 */
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    // Spring Data JPA 會根據方法名稱自動產生 SQL
    // findByUsername -> SELECT * FROM users WHERE username = ?
    Optional<User> findByUsername(String username);

    // findByEmail -> SELECT * FROM users WHERE email = ?
    Optional<User> findByEmail(String email);

    // existsByUsername -> SELECT EXISTS(SELECT 1 FROM users WHERE username = ?)
    boolean existsByUsername(String username);

    // existsByEmail -> SELECT EXISTS(SELECT 1 FROM users WHERE email = ?)
    boolean existsByEmail(String email);
}
```

#### 方法命名規則

| 方法名稱模式 | 產生的 SQL |
|--------------|------------|
| `findByXxx` | `WHERE xxx = ?` |
| `findByXxxAndYyy` | `WHERE xxx = ? AND yyy = ?` |
| `findByXxxOrYyy` | `WHERE xxx = ? OR yyy = ?` |
| `findByXxxContaining` | `WHERE xxx LIKE '%?%'` |
| `findByXxxLessThan` | `WHERE xxx < ?` |
| `findByXxxGreaterThanEqual` | `WHERE xxx >= ?` |
| `existsByXxx` | `SELECT EXISTS(...)` |
| `countByXxx` | `SELECT COUNT(*)` |

---

### 4. DTO 層 - 資料傳輸物件

#### UserDTO.java

```java
package com.example.api.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 使用者資料傳輸物件
 *
 * 用途：
 * 1. 接收前端傳入的資料
 * 2. 回傳給前端的資料格式
 * 3. 隔離 Entity 與外部介面
 * 4. 資料驗證
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserDTO {

    private Long id;

    @NotBlank(message = "Username is required")
    @Size(min = 3, max = 50, message = "Username must be between 3 and 50 characters")
    private String username;

    @NotBlank(message = "Email is required")
    @Email(message = "Email should be valid")
    private String email;

    @Size(max = 100, message = "Full name must not exceed 100 characters")
    private String fullName;
}
```

#### 驗證註解說明

| 註解 | 說明 |
|------|------|
| `@NotBlank` | 不可為空或空白字串 |
| `@NotNull` | 不可為 null |
| `@Size` | 限制字串長度或集合大小 |
| `@Email` | 必須符合 Email 格式 |
| `@Min` / `@Max` | 數值最小/最大值 |
| `@DecimalMin` / `@DecimalMax` | 小數最小/最大值 |
| `@Pattern` | 符合正規表達式 |

#### ApiResponse.java - 統一回應格式

```java
package com.example.api.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * API 統一回應格式
 *
 * 範例回應：
 * {
 *   "success": true,
 *   "message": "Success",
 *   "data": { ... }
 * }
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ApiResponse<T> {
    private boolean success;     // 操作是否成功
    private String message;      // 回應訊息
    private T data;              // 回傳資料（泛型）

    // 成功回應的工廠方法
    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(true, "Success", data);
    }

    public static <T> ApiResponse<T> success(String message, T data) {
        return new ApiResponse<>(true, message, data);
    }

    // 錯誤回應的工廠方法
    public static <T> ApiResponse<T> error(String message) {
        return new ApiResponse<>(false, message, null);
    }
}
```

---

### 5. Service 層 - 業務邏輯

#### UserService.java

```java
package com.example.api.service;

import com.example.api.dto.UserDTO;
import com.example.api.entity.User;
import com.example.api.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 使用者業務邏輯服務
 */
@Service                              // 標記為 Service 元件
@RequiredArgsConstructor              // Lombok: 產生 final 欄位的建構子（用於依賴注入）
public class UserService {

    private final UserRepository userRepository;  // 透過建構子注入

    /**
     * 取得所有使用者
     */
    public List<UserDTO> getAllUsers() {
        return userRepository.findAll().stream()
                .map(this::convertToDTO)          // Entity 轉 DTO
                .collect(Collectors.toList());
    }

    /**
     * 根據 ID 取得使用者
     */
    public UserDTO getUserById(Long id) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("User not found with id: " + id));
        return convertToDTO(user);
    }

    /**
     * 建立新使用者
     */
    @Transactional                    // 交易管理：發生錯誤時自動回滾
    public UserDTO createUser(UserDTO userDTO) {
        // 檢查使用者名稱是否已存在
        if (userRepository.existsByUsername(userDTO.getUsername())) {
            throw new RuntimeException("Username already exists");
        }
        // 檢查 Email 是否已存在
        if (userRepository.existsByEmail(userDTO.getEmail())) {
            throw new RuntimeException("Email already exists");
        }

        User user = convertToEntity(userDTO);
        User savedUser = userRepository.save(user);
        return convertToDTO(savedUser);
    }

    /**
     * 更新使用者
     */
    @Transactional
    public UserDTO updateUser(Long id, UserDTO userDTO) {
        User existingUser = userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("User not found with id: " + id));

        existingUser.setUsername(userDTO.getUsername());
        existingUser.setEmail(userDTO.getEmail());
        existingUser.setFullName(userDTO.getFullName());

        User updatedUser = userRepository.save(existingUser);
        return convertToDTO(updatedUser);
    }

    /**
     * 刪除使用者
     */
    @Transactional
    public void deleteUser(Long id) {
        if (!userRepository.existsById(id)) {
            throw new RuntimeException("User not found with id: " + id);
        }
        userRepository.deleteById(id);
    }

    // ========================================
    // 私有方法：Entity 與 DTO 相互轉換
    // ========================================

    private UserDTO convertToDTO(User user) {
        UserDTO dto = new UserDTO();
        dto.setId(user.getId());
        dto.setUsername(user.getUsername());
        dto.setEmail(user.getEmail());
        dto.setFullName(user.getFullName());
        return dto;
    }

    private User convertToEntity(UserDTO dto) {
        User user = new User();
        user.setUsername(dto.getUsername());
        user.setEmail(dto.getEmail());
        user.setFullName(dto.getFullName());
        return user;
    }
}
```

---

### 6. Controller 層 - REST API

#### UserController.java

```java
package com.example.api.controller;

import com.example.api.dto.ApiResponse;
import com.example.api.dto.UserDTO;
import com.example.api.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

/**
 * 使用者 REST API 控制器
 */
@RestController                       // 標記為 REST 控制器（回傳 JSON）
@RequestMapping("/api/users")         // 基礎路徑
@RequiredArgsConstructor              // 依賴注入
public class UserController {

    private final UserService userService;

    /**
     * GET /api/users - 取得所有使用者
     */
    @GetMapping
    public ResponseEntity<ApiResponse<List<UserDTO>>> getAllUsers() {
        List<UserDTO> users = userService.getAllUsers();
        return ResponseEntity.ok(ApiResponse.success(users));
    }

    /**
     * GET /api/users/{id} - 根據 ID 取得使用者
     */
    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<UserDTO>> getUserById(@PathVariable Long id) {
        UserDTO user = userService.getUserById(id);
        return ResponseEntity.ok(ApiResponse.success(user));
    }

    /**
     * GET /api/users/username/{username} - 根據使用者名稱查詢
     */
    @GetMapping("/username/{username}")
    public ResponseEntity<ApiResponse<UserDTO>> getUserByUsername(
            @PathVariable String username) {
        UserDTO user = userService.getUserByUsername(username);
        return ResponseEntity.ok(ApiResponse.success(user));
    }

    /**
     * POST /api/users - 建立新使用者
     *
     * @Valid: 啟用 DTO 中的驗證註解
     * @RequestBody: 從 HTTP Body 取得 JSON 資料
     */
    @PostMapping
    public ResponseEntity<ApiResponse<UserDTO>> createUser(
            @Valid @RequestBody UserDTO userDTO) {
        UserDTO createdUser = userService.createUser(userDTO);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("User created successfully", createdUser));
    }

    /**
     * PUT /api/users/{id} - 更新使用者
     */
    @PutMapping("/{id}")
    public ResponseEntity<ApiResponse<UserDTO>> updateUser(
            @PathVariable Long id,
            @Valid @RequestBody UserDTO userDTO) {
        UserDTO updatedUser = userService.updateUser(id, userDTO);
        return ResponseEntity.ok(ApiResponse.success("User updated successfully", updatedUser));
    }

    /**
     * DELETE /api/users/{id} - 刪除使用者
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
        return ResponseEntity.ok(ApiResponse.success("User deleted successfully", null));
    }
}
```

#### HTTP 方法對應

| HTTP 方法 | 用途 | 註解 |
|-----------|------|------|
| GET | 讀取資源 | `@GetMapping` |
| POST | 建立資源 | `@PostMapping` |
| PUT | 更新資源（完整） | `@PutMapping` |
| PATCH | 更新資源（部分） | `@PatchMapping` |
| DELETE | 刪除資源 | `@DeleteMapping` |

---

### 7. 全域例外處理

#### GlobalExceptionHandler.java

```java
package com.example.api.controller;

import com.example.api.dto.ApiResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import java.util.HashMap;
import java.util.Map;

/**
 * 全域例外處理器
 *
 * @RestControllerAdvice: 攔截所有 Controller 的例外
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * 處理業務邏輯例外
     */
    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<ApiResponse<Void>> handleRuntimeException(RuntimeException ex) {
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(ApiResponse.error(ex.getMessage()));
    }

    /**
     * 處理驗證例外
     * 當 @Valid 驗證失敗時觸發
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Map<String, String>>> handleValidationExceptions(
            MethodArgumentNotValidException ex) {
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getAllErrors().forEach((error) -> {
            String fieldName = ((FieldError) error).getField();
            String errorMessage = error.getDefaultMessage();
            errors.put(fieldName, errorMessage);
        });
        ApiResponse<Map<String, String>> response =
                new ApiResponse<>(false, "Validation failed", errors);
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * 處理其他未預期的例外
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleException(Exception ex) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.error("An unexpected error occurred: " + ex.getMessage()));
    }
}
```

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

# 查看日誌
docker-compose logs -f spring-boot-api
```

### 方式 2：本地開發

```bash
# 1. 先啟動 PostgreSQL
docker-compose up postgres -d

# 2. 進入 Spring Boot 專案目錄
cd spring-boot-api

# 3. 使用 Maven 執行
./mvnw spring-boot:run

# 或使用 Maven 命令
mvn spring-boot:run
```

### 驗證服務啟動

```bash
# 健康檢查
curl http://localhost:8080/api/health

# 預期回應
{
  "status": "UP",
  "service": "Spring Boot API",
  "timestamp": 1701676800000
}
```

---

## API 測試

### 使用者 API

```bash
# 取得所有使用者
curl http://localhost:8080/api/users

# 取得特定使用者
curl http://localhost:8080/api/users/1

# 建立新使用者
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_user",
    "email": "newuser@example.com",
    "fullName": "New User"
  }'

# 更新使用者
curl -X PUT http://localhost:8080/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "username": "updated_user",
    "email": "updated@example.com",
    "fullName": "Updated User"
  }'

# 刪除使用者
curl -X DELETE http://localhost:8080/api/users/3
```

### 產品 API

```bash
# 取得所有產品
curl http://localhost:8080/api/products

# 搜尋產品
curl "http://localhost:8080/api/products/search?name=laptop"

# 建立新產品
curl -X POST http://localhost:8080/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tablet",
    "description": "10-inch tablet",
    "price": 499.99,
    "stock": 75
  }'
```

---

## 常見問題

### Q1: 無法連線到資料庫

```
確認 PostgreSQL 是否正在運行：
$ docker-compose ps

確認連線參數是否正確：
- URL: jdbc:postgresql://localhost:5432/userdb
- Username: admin
- Password: admin123
```

### Q2: 驗證失敗

```json
{
  "success": false,
  "message": "Validation failed",
  "data": {
    "username": "Username must be between 3 and 50 characters",
    "email": "Email should be valid"
  }
}
```
請確認傳入的資料符合驗證規則。

### Q3: Entity 與資料表不匹配

```
確認 application.yml 中的 ddl-auto 設定：
- 開發環境可使用 update
- 生產環境應使用 validate
```

---

## 下一步

完成 Spring Boot 設定後，請參考以下文件：

- [01-PostgreSQL-Tutorial.md](./01-PostgreSQL-Tutorial.md) - PostgreSQL 資料庫教學
- [03-FastAPI-Tutorial.md](./03-FastAPI-Tutorial.md) - Python FastAPI 教學
