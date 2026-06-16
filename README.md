# safeguard-web

`safeguard-web` 是一款面向服务器运维场景的 Web 端统一管理平台，涵盖用户权限、主机资产、OS 部署、系统迁移、网络负载均衡、安全部署、任务追踪及远程数据采集等能力。项目采用前后端分离架构，后端基于 Django + Django REST Framework，前端基于 Vue 3 + Vite，从 0 到 1 构建，可直接用于本地开发验证及生产环境扩展。

## 功能特性

- **用户与权限**：用户注册/登录、JWT 认证、角色与菜单权限、数据范围控制。
- **主机资产管理**：集群、主机、虚拟机、镜像的增删改查，支持硬件信息采集、LLDP 拓扑采集、密码批量更新、远程命令执行。
- **OS 部署**：ISO 镜像管理、Kickstart 配置、PXE 配置、自动安装任务、仓库同步、白名单管理。
- **系统迁移**：基于 x2cu 的迁移初始化、迁移执行、迁移回滚，支持单主机及多主机场景，任务异步执行。
- **网络负载均衡**：LoadBalancer、Listener、Pool、Member、HealthMonitor 的全生命周期管理。
- **安全部署**：安全组件配置与下发任务管理。
- **任务追踪**：Celery 异步任务状态跟踪与查询。
- **远程采集**：基于 gRPC 的 Sensor 服务，支持远程主机数据采集。
- **API 文档**：集成 drf-spectacular，自动生成 OpenAPI 3.0 文档。

## 软件架构

```text
┌─────────────────────────────────────────────────────────────┐
│                        前端 (Vue 3)                          │
│  Vite + Vue Router + Vuex + Axios + Element Plus 风格页面    │
└───────────────────────────┬─────────────────────────────────┘
                            │ RESTful API
┌───────────────────────────▼─────────────────────────────────┐
│                       后端 (Django)                          │
│  Django 4.2 + Django REST Framework + SimpleJWT              │
│  自定义 RedisJWTAuthentication + drf-spectacular 接口文档    │
└───────────────────────────┬─────────────────────────────────┘
                            │ SQLite / MySQL
┌───────────────────────────▼─────────────────────────────────┐
│                     数据 & 异步任务                          │
│  数据库 (SQLite 本地 / MySQL 生产) + Redis + Celery          │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

- **后端**：Python 3.x、Django 4.2、Django REST Framework 3.17、SimpleJWT 5.5、drf-spectacular 0.29、Celery 5.6、Paramiko 2.12、PyMySQL 1.1、gRPC 1.81
- **前端**：Vue 3.3、Vue Router 4、Vuex 4、Axios 1.16、Vite 5、Vitest 4
- **数据存储**：SQLite（本地开发）、MySQL（生产）
- **缓存 / 任务队列**：Redis + Celery
- **接口文档**：OpenAPI 3.0 / Swagger UI

## 目录结构

```text
safeguard-web/
├── backend/                 # Django 后端应用
│   ├── authentication/      # 自定义 JWT 认证
│   ├── common/              # 通用响应、错误码、基类视图
│   ├── grpc/                # gRPC Sensor 服务
│   ├── management/commands/ # 自定义管理命令（初始化权限、grpc_server）
│   ├── models/              # 数据模型
│   ├── permissions/         # 权限控制
│   ├── schemas/             # drf-spectacular 扩展
│   ├── serializers/         # DRF 序列化器
│   ├── services/            # 业务服务层
│   ├── tasks/               # Celery 异步任务
│   ├── tests/               # 单元测试与接口测试
│   ├── urls/                # 路由配置
│   ├── utils/               # 工具函数（SSH、邮件等）
│   └── views/               # DRF 视图集
├── frontend/                # Vue 3 前端应用
│   ├── src/views/           # 业务页面
│   └── package.json         # 前端依赖与脚本
├── docs/                    # 项目文档
├── safeguard_web/           # Django 项目配置
├── manage.py                # Django 管理入口
├── requirements.txt         # Python 依赖
├── pytest.ini               # pytest 配置
└── README.md                # 本文件
```

## 安装教程

### 环境要求

- Python 3.10+
- Node.js 18+
- Redis（生产环境必需；本地开发可通过 `IS_LOCAL=1` 使用内存模式）
- MySQL（生产环境必需；本地开发使用 SQLite）

### 后端启动

```shell
# 1. 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 切换到后端源码目录
cd /home/unicom/codes/atomgit/safeguard-web

# 4. 启用本地开发模式（SQLite + Celery 同步执行 + 控制台邮件）
export IS_LOCAL=1

# 5. 数据库迁移
python manage.py migrate

# 6. 初始化权限与默认角色
python manage.py init_authority

# 7. 重建系统菜单树（首次部署或菜单结构需要重置时执行）
python manage.py rebuild_menus

# 8. 启动后端服务
python manage.py runserver 0.0.0.0:8000
```

生产环境请配置 MySQL 与 Redis，并启动 Celery Worker：

```shell
celery -A safeguard_web worker -l info
```

如需启用 gRPC Sensor 服务，可执行：

```shell
python manage.py grpc_server
```

### 前端启动

```shell
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产包
npm run build

# 运行前端单元测试
npm run test:run
```

默认前端开发服务器地址为 `http://localhost:5173`，后端 API 地址为 `http://localhost:8000`，请根据实际部署情况配置代理或环境变量。

## 使用说明

1. 打开前端页面，使用默认管理员账号登录，或前往注册页面创建新用户。
2. 登录后若侧边栏缺少某些模块（如 OS 部署、网络 LB、系统迁移等），请确认已执行 `python manage.py rebuild_menus` 重建菜单树，且当前账号已绑定“超级管理员”角色。
   - **系统管理**：用户、角色、菜单、权限
   - **主机管理**：集群、主机、虚拟机、镜像
   - **OS 部署**：ISO、Kickstart、PXE、自动安装、仓库、白名单
   - **系统迁移**：迁移任务管理
   - **网络 LB**：负载均衡、监听器、资源池、成员、健康检查
   - **安全部署**：安全组件任务
   - **任务中心**：Celery 任务状态
3. 在浏览器中访问 `/api/docs/` 可查看并在线调试所有后端接口。

## API 文档

项目已集成 drf-spectacular，启动后端后访问：

- Swagger UI：`http://localhost:8000/api/docs/`
- OpenAPI Schema：`http://localhost:8000/api/schema/`

## 测试

### 后端测试

```shell
export IS_LOCAL=1
python -m pytest backend/tests/ -q
```

### 前端测试

```shell
cd frontend
npm run test:run
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `IS_LOCAL` | 本地开发模式（`1` 启用 SQLite + 同步 Celery + 控制台邮件） | `0` |
| `BACKEND_PORT` | 后端服务端口，用于本地验证链接生成 | `8000` |
| `REDIS_HOST` | Redis 主机地址 | `localhost` |
| `REDIS_PORT` | Redis 端口 | `6379` |
| `REDIS_DB` | Redis 数据库索引 | `0` |
| `REDIS_PASSWORD` | Redis 密码 | 空 |
| `CELERY_BROKER_URL` | Celery Broker URL | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery 结果后端 | `redis://localhost:6379/0` |
| `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | SMTP 邮件服务配置 | 见 `settings.py` |
| `EMAIL_FROM` | 邮件发送方地址 | `noreply@example.com` |
| `DEFAULT_USER_AUTHORITY_ID` | 新用户注册时默认角色 ID | `890` |
| `SSH_TIMEOUT` | SSH 连接超时时间（秒） | `10` |
| `REPO_SAFEGUARDX86` / `REPO_SAFEGUARDARM` | x86 / ARM 仓库包地址 | 见 `settings.py` |

## 参与贡献

1.  Fork 本仓库
2.  新建功能分支：`git checkout -b feat/xxx`
3.  提交代码：`git commit -m "feat: xxx"`
4.  推送分支：`git push origin feat/xxx`
5.  新建 Pull Request

## 开源协议
