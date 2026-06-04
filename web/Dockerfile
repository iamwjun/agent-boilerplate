# Stage 1: 编译前端静态资源
FROM node:20-alpine AS builder

WORKDIR /app

# 优先拷贝 package.json 利用 Docker 缓存层优化构建速度
COPY web/package.json web/package-lock.json ./
RUN npm ci

COPY web/ .
# 执行打包生成 dist 目录
RUN npm run build

# Stage 2: 使用 Nginx 静态托管
FROM nginx:1.25-alpine

# 拷贝打包好的静态文件到 Nginx 默认托管路径
COPY --from=builder /app/dist /usr/share/nginx/html

# 覆盖默认的 Nginx 配置，以支持单页应用(SPA)的路由跳转及 SSE 代理
COPY web/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
