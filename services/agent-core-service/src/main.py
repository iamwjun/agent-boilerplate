import os
import json
import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# 导入内部封装的 Agent 执行器引擎
from src.agents.customer_agent import create_agent_executor

# 导入企业级安全 SDK 二方库组件 (已由 libs/agent-security-sdk 提供)
from agent_security_sdk.guardrails import InputOutputGuardrails
from agent_security_sdk.masking import DataMasker

# 初始化 FastAPI 异步应用
app = FastAPI(
    title="Enterprise Agent Core Service",
    description="大企业级智能客服/技术支持 Agent 核心编排微服务",
    version="1.0.0"
)

# 配置企业级跨域资源共享 (CORS) 策略
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议替换为具体的企业内部域名白名单，如 ["*.yourcompany.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 在微服务启动时，全局初始化唯一的 LangChain Agent 决策引擎
agent_engine = create_agent_executor()

# 初始化安全SDK组件
security_guard = InputOutputGuardrails()
data_masker = DataMasker()


class ChatRequest(BaseModel):
    session_id: str  # 会话唯一标识，用于 Redis 路由历史聊天记录
    message: str     # 用户输入的技术报错或提问内容


@app.post("/api/v1/chat")
async def chat_stream_endpoint(request: ChatRequest, raw_req: Request):
    """
    智能 Agent 技术问答核心接口
    采用 Server-Sent Events (SSE) 协议，实现多轮对话、RAG检索状态变更提示以及 LLM 极致流畅的流式吐字。
    """
    
    async def event_generator():
        # 核心监控：捕获当前的微服务链路追踪 Trace ID (大企业全链路排查必备)
        trace_id = raw_req.headers.get("X-Trace-Id", "internal-dev-trace")
        
        # ==========================================
        # 步骤 1：全链路安全护栏 - 输入侧合规性检查
        # ==========================================
        input_check = security_guard.check_input(request.message)
        if not input_check.is_safe:
            # 发现高危攻击（如提示词注入攻击），直接熔断阻断并安全降级回复
            payload = {
                "type": "answer",
                "content": input_check.patched_text,
                "trace_id": trace_id
            }
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            return

        # ==========================================
        # 步骤 2：驱动 LangChain 引擎并监听全生命周期事件
        # ==========================================
        try:
            # astream_events(version="v2") 是 LangChain 专门用于大厂复杂 Agent 场景设计的异步事件流
            # 它能把“LLM正在思考”、“开始查工具”、“工具查完、开始生成”等细粒度状态实时吐出来
            async for event in agent_engine.astream_events(
                {"input": input_check.patched_text},
                config={
                    "configurable": {"session_id": request.session_id},
                    "callbacks": [] # 可在此处绑定企业自建的 OpenTelemetry 或 Prometheus 监控回调
                },
                version="v2"
            ):
                event_type = event["event"]
                event_name = event["name"]

                # 事件 A：Agent 决策中心判定需要开始调用某项工具 (如 RAG 检索库)
                if event_type == "on_tool_start":
                    if event_name == "knowledge_base_search":
                        status_payload = {
                            "type": "status",
                            "content": "🔍 正在调用 Elasticsearch 运行混合检索与重排提纯...",
                            "trace_id": trace_id
                        }
                        yield f"data: {json.dumps(status_payload, ensure_ascii=False)}\n\n"
                
                # 事件 B：工具执行结束，将召回进度广播给前端 UI
                elif event_type == "on_tool_end":
                    if event_name == "knowledge_base_search":
                        status_payload = {
                            "type": "status",
                            "content": "✅ 专属知识抽取完毕，正在组装一键修复方案...",
                            "trace_id": trace_id
                        }
                        yield f"data: {json.dumps(status_payload, ensure_ascii=False)}\n\n"

                # 事件 C：大模型基座正在以秒级/毫秒级流式吐出答案的单个 Token
                elif event_type == "on_chat_model_stream":
                    raw_token = event["data"]["chunk"].content
                    if raw_token:
                        # ==========================================
                        # 步骤 3：全链路安全护栏 - 输出侧内容脱敏与审计
                        # ==========================================
                        # A. 敏感词实时护栏过滤
                        output_check = security_guard.check_output(raw_token)
                        # B. 个人隐私/高密资产（手机号、密码、AccessKey）正则硬脱敏
                        clean_token = data_masker.mask_text(output_check.patched_text)

                        # 组装标准企业级网关响应体，发送 SSE 数据块
                        answer_payload = {
                            "type": "answer",
                            "content": clean_token,
                            "trace_id": trace_id
                        }
                        yield f"data: {json.dumps(answer_payload, ensure_ascii=False)}\n\n"

        except Exception as e:
            # 异常防线：在异步流生成过程中如遇大模型超时、网络断开等，捕获异常防止服务僵死
            error_payload = {
                "type": "error",
                "content": f"🚨 [系统网关提示]: 服务处理发生异常，请稍后重试或联系人工支持。错误追踪码: {trace_id}",
                "trace_id": trace_id
            }
            yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"

    # 返回高性能支持流式长链接的 StreamingResponse
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/health")
async def health_check():
    """
    服务健康检查接口 (大企业 K8s 存活探针 Liveness/Readiness Probe 必备)
    """
    return {
        "status": "UP",
        "service": "agent-core-service",
        "dependencies": {
            "redis": "connected_mock"  # 实际企业级中会引入真正的 ping 检查
        }
    }


if __name__ == "__main__":
    import uvicorn
    # 本地启动测试代码：运行命令 python src/main.py
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
