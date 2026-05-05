# Docker 部署说明

## 部署目标

将前端、后端和 SQLite 数据库统一放入 Docker 环境：

- 前端：Nginx 托管静态页面，并代理 `/api` 到后端。
- 后端：FastAPI + Uvicorn。
- 数据库：SQLite 文件挂载在 Docker volume 中。
- 上传文件：和数据库同一个 volume 持久化。

## 一键部署

```bash
docker compose -f docker-compose.deploy.yml up -d
```

如果本机只支持旧版命令，将 `docker compose` 替换成 `docker-compose` 即可。

访问：

```text
http://localhost:8080
```

## 从源码构建部署

```bash
docker compose up -d --build
```

## 目录和持久化

容器内路径：

```text
/data/local.db
/data/storage
```

Compose volume：

```text
gujian-data
```

查看 volume：

```bash
docker volume inspect tracing-ancient-buildings_gujian-data
```

## 常用命令

查看容器状态：

```bash
docker compose ps
```

查看日志：

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

重启：

```bash
docker compose restart
```

停止但保留数据：

```bash
docker compose down
```

停止并删除数据库、上传文件：

```bash
docker compose down -v
```

## 发布镜像

默认发布到 GitHub Container Registry：

```text
ghcr.io/huangjxjx/tracing-ancient-buildings-backend:latest
ghcr.io/huangjxjx/tracing-ancient-buildings-frontend:latest
```

仓库包含 `.github/workflows/docker-publish.yml`，推送到 `main` 后会自动构建并发布上述镜像。

也可以手动发布到阿里云杭州区域：

```text
registry.cn-hangzhou.aliyuncs.com/huangjxjx/tracing-ancient-buildings-backend:latest
registry.cn-hangzhou.aliyuncs.com/huangjxjx/tracing-ancient-buildings-frontend:latest
```

构建并推送：

```bash
docker login registry.cn-hangzhou.aliyuncs.com
docker compose build
docker tag tracing-ancient-buildings-backend:latest registry.cn-hangzhou.aliyuncs.com/huangjxjx/tracing-ancient-buildings-backend:latest
docker tag tracing-ancient-buildings-frontend:latest registry.cn-hangzhou.aliyuncs.com/huangjxjx/tracing-ancient-buildings-frontend:latest
docker push registry.cn-hangzhou.aliyuncs.com/huangjxjx/tracing-ancient-buildings-backend:latest
docker push registry.cn-hangzhou.aliyuncs.com/huangjxjx/tracing-ancient-buildings-frontend:latest
```

如果换成其他镜像仓库，只需要修改 `.env` 中的 `BACKEND_IMAGE` 和 `FRONTEND_IMAGE`。

## 本地已有数据库迁移

如果要把本机 `backend/local.db` 放进 Docker volume，可以先启动一次容器，然后复制数据库：

```bash
docker compose up -d
docker cp backend/local.db tracing-ancient-buildings-backend:/data/local.db
docker compose restart backend
```

上传文件同理复制到：

```text
tracing-ancient-buildings-backend:/data/storage
```
