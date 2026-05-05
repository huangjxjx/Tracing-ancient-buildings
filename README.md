# Tracing Ancient Buildings Docker Deployment

“寻迹古建”是一个前后端分离的古建筑病害检测、数字孪生、知识库和监管大屏演示系统。

本仓库提供 Docker 化部署文件：

- `backend`：FastAPI API 服务，使用 SQLite 存储业务数据。
- `frontend`：React + Vite 构建后的静态页面，由 Nginx 托管并反向代理 `/api`。
- `gujian-data`：Docker volume，持久化 `/data/local.db` 和上传文件 `/data/storage`。

## 快速启动

如果镜像已经发布到阿里云容器镜像服务：

```bash
docker compose -f docker-compose.deploy.yml up -d
```

如果你的 Docker Desktop 只提供旧命令，也可以把 `docker compose` 换成 `docker-compose`。

打开：

```text
http://localhost:8080
```

健康检查：

```bash
curl http://localhost:8080/healthz
```

## 从源码构建

```bash
docker compose up -d --build
```

查看日志：

```bash
docker compose logs -f
```

停止服务：

```bash
docker compose down
```

如需同时删除数据库和上传文件：

```bash
docker compose down -v
```

## 镜像说明

默认镜像名：

```text
registry.cn-hangzhou.aliyuncs.com/huangjxjx/tracing-ancient-buildings-backend:latest
registry.cn-hangzhou.aliyuncs.com/huangjxjx/tracing-ancient-buildings-frontend:latest
```

如果你使用自己的镜像仓库，可以创建 `.env` 覆盖：

```bash
cp .env.docker.example .env
```

然后修改：

```env
BACKEND_IMAGE=your-registry/your-namespace/tracing-ancient-buildings-backend:latest
FRONTEND_IMAGE=your-registry/your-namespace/tracing-ancient-buildings-frontend:latest
```

再运行：

```bash
docker compose --env-file .env -f docker-compose.deploy.yml up -d
```

## 数据库

本项目当前使用 SQLite，数据库文件在容器内：

```text
/data/local.db
```

上传文件在容器内：

```text
/data/storage
```

二者都通过 Docker volume `gujian-data` 持久化。容器重启不会丢失数据。

## 发布镜像到阿里云

登录阿里云容器镜像服务：

```bash
docker login registry.cn-hangzhou.aliyuncs.com
```

构建镜像：

```bash
docker compose build
```

打标签：

```bash
docker tag tracing-ancient-buildings-backend:latest registry.cn-hangzhou.aliyuncs.com/huangjxjx/tracing-ancient-buildings-backend:latest
docker tag tracing-ancient-buildings-frontend:latest registry.cn-hangzhou.aliyuncs.com/huangjxjx/tracing-ancient-buildings-frontend:latest
```

推送：

```bash
docker push registry.cn-hangzhou.aliyuncs.com/huangjxjx/tracing-ancient-buildings-backend:latest
docker push registry.cn-hangzhou.aliyuncs.com/huangjxjx/tracing-ancient-buildings-frontend:latest
```

其他人拉取部署：

```bash
git clone https://github.com/huangjxjx/Tracing-ancient-buildings.git
cd Tracing-ancient-buildings
docker compose -f docker-compose.deploy.yml up -d
```

## 端口

- 对外访问端口：`8080`
- 后端内部端口：`8000`
- 前端容器内部端口：`80`

正常使用时只需要访问 `http://localhost:8080`。
