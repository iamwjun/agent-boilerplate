import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.agents.customer_agent import create_agent_executor

app = FastAPI(title="Enterprise Agent Core Service", version="1.0.0")

# 开启跨域，便于前端 Web 联调
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化全局 Agent 骨架
agent_engine = create_agent_executor()

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/api/v1/chat")
async def chat_stream_endpoint(request: ChatRequest):
    """接收用户请求，利用 Server-Sent Events (SSE) 协议异步吐出 Agent 思考和生成流"""
    
    async def event_generator():
        # astream_events v2 可以捕获 LangChain 内部每一个原子事件（Tool调用开始、LLM吐字等）
        async for event in agent_engine.astream_events(
            {"input": request.message},
            config={"configurable": {"session_id": request.session_id}},
            version="v2"
        ):
            event_type = event["event"]
            
            # 事件A：大模型正在实时吐出流式回答的 Token
            if event_type == "on_chat_model_stream":
                token = event["data"]["chunk"].content
                if token:
                    yield f"data: {json.dumps({'type': 'answer', 'content': token}, ensure_ascii=False)}\n\n"
            
            # 事件B：Agent 决策中心决定开始调用知识库检索工具
            elif event_type == "on_tool_start":
                tool_name = event["name"]
                if tool_name == "knowledge_base_search":
                    yield f"data: {json.dumps({'type': 'status', 'content': '🔍 正在检索内部知识库并运行重排提纯...'}, ensure_ascii=False)}\n\n"
            
            # 事件C：工具执行完毕，可以在此向前端发送信号（或选择在后台保持静默）
            elif event_type == "on_tool_end":
                yield f"data: {json.dumps({'type': 'status', 'content': '✅ 知识提取完毕，正在组织修复方案...'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/health")
def health_check():
    return {"status": "healthy"}
