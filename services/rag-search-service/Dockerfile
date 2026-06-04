# 使用官方集成了 CUDA 和 Python 的轻量底层
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 安装 Python 环境及基础编译工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# 软链接 python 命令
RUN ln -s /usr/bin/python3 /usr/bin/python

# 拷贝并安装机器学习、ES 客户端及深度学习框架依赖
COPY services/rag-search-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 预先创建模型缓存目录（防止容器运行时动态下载导致超时）
RUN mkdir -p /app/models

# 拷贝服务核心源码
COPY services/rag-search-service/src ./src

EXPOSE 8010

# 运行高性能内网检索与精排服务
CMD ["python", "src/main.py"]
