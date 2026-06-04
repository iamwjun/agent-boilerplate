# Stage 1: 构建依赖环境
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY services/agent-core-service/requirements.txt .

# 将依赖安装到局部目录，避免污染系统全局环境
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: 最终生产镜像
FROM python:3.11-slim AS runner

WORKDIR /app

# 从编译阶段拷贝安装好的 Python 依赖库
COPY --from=builder /root/.local /root/.local
COPY services/agent-core-service/src ./src

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# 启动 FastAPI 服务，并开启标准流式传输支持
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop"]
