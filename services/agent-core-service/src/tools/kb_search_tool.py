import os
import httpx
from langchain_core.tools import tool

RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://rag-search-service:8010")

@tool
def knowledge_base_search(query: str) -> str:
    """当用户询问关于系统报错、配置疑问、升级故障、技术原理或需要排查生产环境问题时，调用此工具检索内部知识库。
    
    Args:
        query: 抽取的排查关键词或核心问题描述
    """
    try:
        # 内部 RPC/HTTP 跨服务调用 rag-search-service 的精排检索接口
        with httpx.Client(timeout=5.0) as client:
            response = client.post(
                f"{RAG_SERVICE_URL}/api/v1/search",
                json={"query": query, "top_k": 3}
            )
            if response.status_code == 200:
                results = response.json().get("results", [])
                if not results:
                    return "知识库中未找到相关参考技术文档。"
                
                # 拼接召回的 Context 文本块
                formatted_context = []
                for idx, text in enumerate(results):
                    formatted_context.append(f"[参考文档片段 {idx+1}]:\n{text}")
                return "\n\n".join(formatted_context)
            else:
                return f"内部检索服务异常，状态码: {response.status_code}"
    except httpx.RequestError as exc:
        # 优雅降级处理，保证 Agent 链路不崩溃
        return f"无法连接内部检索服务，原因: {exc}。请尝试直接根据已知通用知识回答。"
