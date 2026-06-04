├── .github/                     # CI/CD 自动化流水线（Github Actions / GitLab CI）
│   └── workflows/               # 包含各个微服务的编译、镜像打包(Docker)与K8s部署脚本
├── .images/                     # 项目架构图或静态资源
├── charts/                      # Helm Charts 用于 Kubernetes 编排部署
│   ├── agent-core/
│   └── rag-search/
├── config/                      # 全局环境配置中心（支持 Dev、Staging、Prod）
│   ├── base.yaml
│   ├── production.yaml
│   └── security-policy.json     # 安全脱敏、敏感词过滤规则定义
│
# ======================== 核心服务源码区 ========================
├── services/
│   │
│   ├── agent-core-service/      # 1. Agent 核心智能编排服务（Python/FastAPI 或 Java/Spring）
│   │   ├── src/
│   │   │   ├── agents/          # Agent 决策中心
│   │   │   │   ├── __init__.py
│   │   │   │   ├── customer_agent.py # 技术支持 Agent 定义
│   │   │   │   └── router.py    # 意图路由逻辑
│   │   │   ├── chains/          # 复杂的 LangChain 链式结构
│   │   │   ├── tools/           # Agent 可调用的工具集（RPC/HTTP 调用其他微服务）
│   │   │   │   ├── kb_search_tool.py  # 调用 rag-search-service 的工具
│   │   │   │   └── ops_api_tool.py   # 调用内部运维系统的工具
│   │   │   ├── memory/          # 基于 Redis 的会话持久化层
│   │   │   ├── api/             # HTTP/gRPC 接口层（提供 SSE 流式输出接口）
│   │   │   │   └── v1/
│   │   │   └── main.py          # 服务启动入口
│   │   ├── tests/               # 单元测试与 Prompt 效果测试
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── rag-search-service/     # 2. RAG 检索与重排服务（高性能 Python 服务，对接 GPU）
│   │   ├── src/
│   │   │   ├── search/          # ES 检索核心逻辑
│   │   │   │   ├── es_client.py # ES 8.x 连接池管理
│   │   │   │   └── hybrid_q.py  # BM25 + KNN 混合查询语句组装
│   │   │   ├── rerank/          # Reranker 模型加载与推理
│   │   │   │   └── model_loader.py
│   │   │   ├── api/             # 仅供内网 RPC/gRPC 调用的高性能接口
│   │   │   └── main.py
│   │   ├── model_weights/       # 离线精排模型权重暂存区（生产中通常挂载 NAS/S3）
│   │   ├── Dockerfile (CUDA)     # 支持 GPU 加速的 Docker 镜像配置
│   │   └── requirements.txt
│   │
│   └── data-pipeline-job/       # 3. 离线/增量数据同步与清洗任务
│       ├── src/
│       │   ├── extractors/      # 数据源抽取器（Jira, Confluence, Gitlab API）
│       │   ├── transformers/    # LangChain 切片、清洗、文本加工
│       │   ├── loaders/         # ES 批量 Bulk 写入器
│       │   └── job_scheduler.py # 任务调度器（或对接 Airflow/XXL-JOB）
│       ├── scripts/             # 初始化 ES Index Mapping 的一次性脚本
│       │   └── init_es_schema.json
│       └── requirements.txt
│
# ======================== 共享组件与公共库 ========================
├── libs/                        # 内部共享的二方库（防止代码重复）
│   ├── agent-common-proto/      # gRPC 定义文件（ProtoBuf），统一全链路契约
│   └── agent-security-sdk/      # 企业级安全SDK（包含数据脱敏、Token校验、审计日志）
│
# ======================== 前端与多端接入层 ========================
├── web/                         # 前端 Web 交付台（React / Vue 3）
│   ├── src/
│   │   ├── components/          # 聊天窗口、流式文本渲染、Markdown/代码块高亮组件
│   │   └── hooks/               # useSSE.ts 专门处理服务器发送事件流
│   └── package.json
│
├── README.md
└── docker-compose.yml           # 本地一键拉起 ES, Redis, Web 的开发测试环境
