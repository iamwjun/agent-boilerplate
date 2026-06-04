FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY services/data-pipeline-job/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝同步脚本、清洗规则及 Index 结构定义
COPY services/data-pipeline-job/src ./src
COPY services/data-pipeline-job/scripts ./scripts

# 默认执行任务调度器（监听或定时触发文档切片向量化入库）
CMD ["python", "src/job_scheduler.py"]
