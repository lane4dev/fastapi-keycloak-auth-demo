# FastAPI Keycloak 认证与授权示例

[![FastAPI Shield](https://img.shields.io/badge/-FastAPI-009688?logo=fastapi&logoColor=white&style=flat-square)](https://fastapi.tiangolo.com/)
[![Keycloak Shield](https://img.shields.io/badge/-Keycloak-red?logo=keycloak&logoColor=white&style=flat-square)](https://www.keycloak.org/)
[![Python Shield](https://img.shields.io/badge/-Python-3776ab?logo=python&logoColor=white&style=flat-square)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

本项目是一个将 [Keycloak](https://www.keycloak.org/) 与 [FastAPI](https://fastapi.tiangolo.com/) 后端 API 集成以实现强大的认证和授权的综合演示。它展示了各种真实世界的场景，包括基于角色的访问控制 (RBAC)、基于属性的访问控制 (ABAC)、基于用户角色的动态内容，以及通过 Keycloak Admin API 进行的程序化用户/角色管理。

## 🌟 功能特性

*   **Keycloak 集成**：将 FastAPI 无缝连接到 Keycloak 以进行 JWT 令牌验证。
*   **基于环境的配置**：Keycloak 参数通过 `.env` 文件配置，易于管理。
*   **认证流程**：
    *   **资源所有者密码凭据授权 (Resource Owner Password Credentials Grant)**：使用用户名/密码进行用户登录。
    *   **客户端凭据授权 (Client Credentials Grant)**：机器对机器 (M2M) 认证，用于服务账号。
    *   **刷新令牌流程 (Refresh Token Flow)**：在不重新认证的情况下续订过期的访问令牌。
    *   **注销 (Logout)**：使 Keycloak 中的用户会话失效。
*   **授权策略**：
    *   **依赖注入的权限检查**：利用 FastAPI 的 `Depends` 实现细粒度的权限控制。
    *   **基于角色的访问控制 (RBAC)**：根据 Keycloak 领域角色 (`RoleChecker`) 保护路由。
    *   **基于属性的访问控制 (ABAC) / 所有权 (Ownership)**：实现细粒度的访问检查（例如，用户只能修改自己的数据）。
    *   **动态内容**：根据经过认证的用户角色返回不同的 API 响应。
*   **用户管理**：从 JWT 令牌中检索当前用户配置文件。
*   **Admin API 交互**：通过编程方式与 Keycloak 的 Admin API 交互，用于：
    *   按用户名或角色搜索用户。
    *   动态地为用户分配领域角色（例如，将用户提升为“经理”）。
*   **Swagger/OpenAPI 文档**：FastAPI 自动生成 API 文档，支持 Bearer Token 认证，方便测试。

## 🚀 快速开始

### 前提条件

在开始之前，请确保您已安装以下软件：

*   [Python 3.8+](https://www.python.org/)
*   [pip](https://pip.pypa.io/en/stable/) (或 [uv](https://github.com/astral-sh/uv))
*   [Docker](https://www.docker.com/) 和 [Docker Compose](https://docs.docker.com/compose/) (用于在本地运行 Keycloak)

### 1. Keycloak 设置 (使用 Docker Compose)

本项目将使用 Docker 在本地运行 Keycloak 实例。

1.  **在项目根目录 (或同级目录) 创建 `docker-compose.yml` 文件**：

    ```yaml
    version: '3.8'

    services:
      keycloak:
        image: quay.io/keycloak/keycloak:latest
        ports:
          - "9999:8080" # 将宿主机的 9999 端口映射到容器的 8080 端口
        environment:
          KEYCLOAK_ADMIN: admin
          KEYCLOAK_ADMIN_PASSWORD: admin
          KC_DB: dev-file
          KC_HEALTH_ENABLED: true
          KC_METRICS_ENABLED: true
          KC_HTTP_ENABLED: true # 如果本地开发不使用 HTTPS，则启用 HTTP
        command:
          - start-dev --hostname-strict=false
        volumes:
          - ./keycloak_data:/opt/keycloak/data
    ```

    *   `KEYCLOAK_ADMIN`, `KEYCLOAK_ADMIN_PASSWORD`: Keycloak UI 的默认管理员凭据。
    *   `9999:8080`: Keycloak 将通过 `http://localhost:9999` 访问。

2.  **启动 Keycloak**：
    ```bash
    docker-compose up -d
    ```

3.  **访问 Keycloak 管理控制台**：
    在浏览器中打开 `http://localhost:9999/admin` 并使用 `admin`/`admin` 登录。

### 2. Keycloak 领域、客户端、用户和角色配置

请在 Keycloak 管理控制台中按照以下步骤操作：

#### A. 创建领域 (Realm)

1.  将鼠标悬停在左上角的 "Master" 上，点击 "添加领域" (Add Realm)。
2.  将 **名称** (Name) 设置为 `dev`。点击 "创建" (Create)。

#### B. 配置客户端 (Client)

1.  导航到 `dev` 领域。转到 **客户端** (Clients) -> **创建客户端** (Create client)。
2.  **客户端 ID** (Client ID)：`backend-api-demo`
3.  **根 URL** (Root URL)：`http://localhost:8000` (您的 FastAPI 应用程序 URL)
4.  点击 **保存** (Save)。
5.  在客户端设置 (`backend-api-demo` 客户端) 中：
    *   **访问类型** (Access Type)：`confidential`
    *   **标准流已启用** (Standard flow enabled)：`OFF`
    *   **直接访问授权已启用** (Direct access grants enabled)：`ON` (`/auth/login` 密码授权所需)
    *   **服务账号已启用** (Service accounts enabled)：`ON` (从 FastAPI 进行 Admin API 调用所需)
    *   **有效重定向 URI** (Valid Redirect URIs)：`http://localhost:8000/*`
    *   **Web 来源** (Web origins)：`+` (允许所有来源进行本地开发，或指定 `http://localhost:8000`)
    *   点击 **保存** (Save)。
6.  转到 `backend-api-demo` 客户端的 **凭据** (Credentials) 选项卡。复制 **密钥** (Secret)。您将在 `.env` 文件中需要它。
7.  转到 **服务账号角色** (Service Account Roles) 选项卡 (针对 `backend-api-demo` 客户端的服务账号)。
    *   在 "客户端角色" (Client Roles) -> "realm-management" 下，选择 `realm-admin` 并将其添加到 "已分配角色" (Assigned Roles) 中。这允许您的 FastAPI 应用程序 (通过其服务账号) 管理 `dev` 领域中的用户和角色。

#### C. 创建领域角色 (Realm Roles)

1.  导航到 `dev` 领域。转到 **领域角色** (Realm Roles) -> **添加角色** (Add Role)。
2.  创建以下角色：
    *   `admin`
    *   `manager`
    *   `developer`

#### D. 创建用户 (Users)

1.  导航到 `dev` 领域。转到 **用户** (Users) -> **添加用户** (Add User)。
2.  创建 3 个用户（例如，`admin`、`manager`、`developer`），详细信息如下：
    *   **用户名** (Username)：`admin`、`manager`、`developer`
    *   **电子邮件** (Email)：(可选)
    *   **电子邮件已验证** (Email Verified)：`ON`
3.  对于每个用户，转到其 **凭据** (Credentials) 选项卡并设置密码（例如，所有用户都设置为 `password`）。确保 "临时" (Temporary) 为 `OFF`。

#### E. 为用户分配角色

1.  对于用户 `admin`：转到 **角色映射** (Role Mappings) 选项卡。在 "领域角色" (Realm Roles) 下，选择 `admin`、`manager`、`developer` 并将其添加到 "已分配角色" (Assigned Roles) 中。
2.  对于用户 `manager`：转到 **角色映射** (Role Mappings) 选项卡。在 "领域角色" (Realm Roles) 下，选择 `manager` 和 `developer` 并添加它们。
3.  对于用户 `developer`：转到 **角色映射** (Role Mappings) 选项卡。在 "领域角色" (Realm Roles) 下，选择 `developer` 并添加它。

### 3. FastAPI 项目设置

1.  **克隆仓库**：
    ```bash
    git clone <repository_url>
    cd fastapi-keycloak-auth # 假设这是您的项目目录
    ```

2.  **安装依赖**：
    ```bash
    pip install -r requirements.txt
    # 或 uv pip install -r requirements.txt
    ```

3.  **配置环境变量**：
    在项目根目录创建 `.env` 文件，并填写您的 Keycloak 详细信息。
    *   `KEYCLOAK_AUTH_SERVER_URL`: 应指向您的 Keycloak 实例。
    *   `KEYCLOAK_REALM`: 您创建的领域。
    *   `KEYCLOAK_CLIENT_ID`: 您创建的客户端 ID。
    *   `KEYCLOAK_SECRET`: Keycloak 客户端凭据选项卡中的客户端密钥。
    *   `KEYCLOAK_COOKIE_KEY`: 用于 Cookie 加密的唯一字符串（演示可随意设置）。

    `.env` 文件内容示例：
    ```
    KEYCLOAK_REALM=dev
    KEYCLOAK_AUTH_SERVER_URL=http://localhost:9999
    KEYCLOAK_CLIENT_ID=backend-api-demo
    KEYCLOAK_CLIENT_SECRET=YOUR_KEYCLOAK_CLIENT_SECRET_HERE
    KEYCLOAK_COOKIE_KEY=some-secret-cookie-key
    ```
    **重要提示**：将 `YOUR_KEYCLOAK_CLIENT_SECRET_HERE` 替换为您的 Keycloak 客户端的实际密钥。

4.  **运行 FastAPI 应用程序**：
    ```bash
    uvicorn src.main:app --reload
    ```
    应用程序将在 `http://localhost:8000` 上启动。

## 📚 API 端点与权限模型

访问 Swagger UI：`http://localhost:8000/docs` 以探索和测试 API。使用“Authorize”按钮（右上角）输入从 `/auth/login` 端点获取的 Bearer Token。

所有 API 路由都以 `/api` 为前缀。

### 🔐 认证模块 (`/api/auth`)

这些端点管理用户和机器认证流程。

*   `POST /auth/login`
    *   **描述**：使用用户名和密码进行用户登录（资源所有者密码凭据授权）。返回 `access_token`、`refresh_token` 等。
    *   **访问权限**：未受保护。
*   `POST /auth/client-login`
    *   **描述**：机器对机器登录（客户端凭据授权）。服务使用此功能为其自身获取访问令牌。返回 `access_token`。
    *   **访问权限**：未受保护。
*   `POST /auth/refresh`
    *   **描述**：使用有效的 `refresh_token` 刷新过期的 `access_token`。返回新的 `access_token` 和 `refresh_token`。
    *   **访问权限**：未受保护。
*   `POST /auth/logout`
    *   **描述**：使用 `refresh_token` 使 Keycloak 中的用户会话失效。
    *   **访问权限**：未受保护。

### 🧑‍💻 开发者模块 (`/api/developer`)

演示了混合 RBAC 和一些公共访问。

*   `POST /developer`
    *   **描述**：创建开发人员记录。
    *   **访问权限**：需要拥有 `realm:developer` 角色的认证用户。
*   `GET /developer`
    *   **描述**：获取所有开发人员记录。
    *   **访问权限**：未受保护（公开访问）。
*   `GET /developer/{id}`
    *   **描述**：按 ID 获取特定开发人员记录。
    *   **访问权限**：未受保护（公开访问）。
*   `PATCH /developer/{id}`
    *   **描述**：更新开发人员记录。
    *   **访问权限**：需要拥有 `realm:developer` 角色的认证用户。
*   `DELETE /developer/{id}`
    *   **描述**：删除开发人员记录。
    *   **访问权限**：需要拥有 `realm:admin` 角色的认证用户。

### 💼 经理模块 (`/api/manager`)

演示了严格的类级别 RBAC。

*   `POST /manager`
    *   **描述**：创建经理记录。
    *   **访问权限**：需要拥有 `realm:manager` 角色的认证用户。
*   `GET /manager`
    *   **描述**：获取所有经理记录。
    *   **访问权限**：需要拥有 `realm:manager` 角色的认证用户。
*   `GET /manager/{id}`
    *   **描述**：按 ID 获取特定经理记录。
    *   **访问权限**：需要拥有 `realm:manager` 角色的认证用户。
*   `PATCH /manager/{id}`
    *   **描述**：更新经理记录。
    *   **访问权限**：需要拥有 `realm:manager` 角色的认证用户。
*   `DELETE /manager/{id}`
    *   **描述**：删除经理记录。
    *   **访问权限**：需要拥有 `realm:manager` 角色的认证用户。

### 📊 资源模块 (`/api/resource`)

演示了基于用户角色的动态内容。

*   `GET /resource/dashboard`
    *   **描述**：返回一个仪表板，根据认证用户的角色（`realm:manager`、`realm:developer`、`realm:admin`）显示不同的部分。
    *   **访问权限**：仅限认证用户。

### 👤 用户模块 (`/api/user`)

演示了获取用户配置文件和 ABAC（所有权）检查。

*   `GET /user/me`
    *   **描述**：直接从 JWT 令牌获取当前认证用户的配置文件信息。
    *   **访问权限**：仅限认证用户。
*   `POST /user/update-bio`
    *   **描述**：更新用户的个人简介。此端点包含 ABAC 检查：只有其 ID 与请求体中 `userId` 匹配的用户（即所有者）才能更新其简介。
    *   **访问权限**：仅限认证用户。
*   `GET /user/admin-debug`
    *   **描述**：一个仅限拥有 `realm:admin` 角色的用户访问的示例端点，提供调试信息。
    *   **访问权限**：需要拥有 `realm:admin` 角色的认证用户。

### 👑 管理员模块 (`/api/admin`)

演示了与 Keycloak Admin API 进行程序化交互以进行用户和角色管理。**此整个模块的访问权限仅限于 `realm:admin` 用户。**

*   `POST /admin/assign-role`
    *   **描述**：动态地为用户分配指定的领域角色。这会使用后端客户端的服务账号调用 Keycloak 的 Admin API。
    *   **访问权限**：需要拥有 `realm:admin` 角色的认证用户。
    *   **请求体**：`{ "username": "someuser", "roleName": "realm:developer" }`
*   `GET /admin/users/search?username={username}&role_name={role_name}`
    *   **描述**：按用户名和/或角色在 Keycloak 中搜索用户并检索其完整的 Keycloak 用户对象。
    *   **访问权限**：需要拥有 `realm:admin` 角色的认证用户。

## 🧪 如何测试权限

1.  **启动 Keycloak 和 FastAPI 应用程序**，如上所述。
2.  **打开 Swagger UI**：`http://localhost:8000/docs`。
3.  **执行登录**：
    *   使用 `POST /auth/login` 和凭据：
        *   `username: admin`, `password: password`
        *   `username: manager`, `password: password`
        *   `username: developer`, `password: password`
    *   从响应中复制 `access_token`。
4.  **在 Swagger 中授权**：点击“Authorize”按钮（右上角），将您的 `access_token` 粘贴到 `Value` 字段中（前缀为 `Bearer `，例如，`Bearer <您的令牌>`），然后点击“Authorize”。
5.  **测试端点**：

    *   **`admin` 用户**：可以访问所有端点，包括 `/developer`、`/manager`、`/resource/dashboard`、`/user/*` 和所有 `/admin/*` 端点。
    *   **`manager` 用户**：
        *   可以访问所有 `manager` 端点。
        *   可以访问 `developer` (公共 `GET`，以及 `POST`/`PATCH`，因为他们也拥有 `developer` 角色)。
        *   可以访问 `/resource/dashboard` 并查看 `managerSection`。
        *   **无法**访问 `/admin/*` 端点或 `DELETE /developer/{id}`。
    *   **`developer` 用户**：
        *   可以访问 `developer` (公共 `GET`，以及 `POST`/`PATCH`)。
        *   可以访问 `/resource/dashboard` 并查看 `developerSection`。
        *   **无法**访问 `manager` 端点、`/admin/*` 端点或 `DELETE /developer/{id}`。
    *   **未认证用户**：只能访问 `GET /developer` 和 `GET /developer/{id}`（公共路由），以及所有 `/auth/*` 端点。

    *   **测试 ABAC (`POST /user/update-bio`)**：
        1.  以 `developer` 身份登录（获取 `developer` 的令牌）。
        2.  从 `GET /user/me` 响应中获取 `sub`（用户 ID）（例如，`developer` 的 UUID）。
        3.  调用 `POST /user/update-bio`，请求体为 `{ "userId": "developer-uuid", "bio": "我的新简介" }`。这应该会成功。
        4.  现在，尝试调用 `POST /user/update-bio`，但使用不同用户（例如，`manager` 的 UUID）的 `userId`。这应该会因为所有权检查而失败，并返回 `400 Bad Request`。

    *   **测试动态角色分配 (`POST /admin/assign-role`)**：
        1.  以 `admin` 身份登录并授权。
        2.  调用 `POST /admin/assign-role`，请求体为 `{ "username": "developer", "roleName": "realm:manager" }`。
        3.  此操作后，注销 `developer` 用户并重新登录。`developer` 的新令牌现在将包含 `realm:manager` 角色，他们应该能够访问 `manager` 端点并在仪表板中看到 `managerSection`。

## 📁 项目结构

```
.
├── src/
│   ├── admin/             # Keycloak Admin API 交互（用户/角色管理）
│   │   ├── __init__.py
│   │   └── router.py      # Admin 路由 (分配角色, 搜索用户)
│   ├── auth/              # 认证流程（登录、刷新、注销、客户端登录）
│   │   ├── __init__.py
│   │   ├── dependencies.py # 认证依赖项, 当前用户, 角色检查器
│   │   ├── router.py      # 认证路由 (登录, 注销等)
│   │   └── utils.py       # Keycloak 客户端初始化 (AuthService, AdminService)
│   ├── developer/         # 开发人员实体的功能模块（混合 RBAC）
│   │   ├── __init__.py
│   │   └── router.py      # RBAC 演示 (developer 角色)
│   ├── manager/           # 经理实体的功能模块（严格 RBAC）
│   │   ├── __init__.py
│   │   └── router.py      # RBAC 演示 (manager 角色)
│   ├── resource/          # 基于用户角色的动态内容
│   │   ├── __init__.py
│   │   └── router.py      # 动态内容演示
│   ├── users/             # 当前用户配置文件和 ABAC（所有权）示例
│   │   ├── __init__.py
│   │   └── router.py      # 用户配置文件和 ABAC 演示
│   ├── __init__.py
│   ├── config.py          # 全局应用程序设置 (Pydantic)
│   ├── dependencies.py    # 共享依赖项 (现在大部分为空, 可以删除或重新利用)
│   ├── exceptions.py      # 自定义错误处理
│   ├── main.py            # FastAPI 应用程序工厂和中间件设置
│   └── router.py          # 主路由器聚合器
├── .env.example           # 环境变量示例 (可以从 .env 文件手动创建)
├── .gitignore
├── .python-version
├── BEST_PRACTICES.md
├── GEMINI.md
├── main.py
├── pyproject.toml
├── README_nestjs.md
├── requirements.txt
├── uv.lock
└── docker-compose.yml     # 用于在本地运行 Keycloak (如果尚未创建)
```

## 🤝 贡献

欢迎贡献！欢迎提交 issue 或 pull request。

## 📄 许可证

本项目根据 MIT 许可。
