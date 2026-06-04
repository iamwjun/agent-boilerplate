from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory

from src.tools.kb_search_tool import knowledge_base_search
from src.memory.redis_manager import get_redis_chat_history

def create_agent_executor() -> RunnableWithMessageHistory:
    # 1. 初始化支持 Function Calling 的基座大模型
    llm = ChatOpenAI(
        model="deepseek-chat", # 生产中可灵活替换为 qwen, gpt-4o 等
        temperature=0.1,       # 降低创造力，提升技术排查的严谨度
        streaming=True
    )
    
    # 2. 注入企业 Agent 工具箱
    tools = [knowledge_base_search]
    
    # 3. 组装具备强约束的企业级 Prompt 资产
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是公司自主研发的云原生数据库资深售后架构师。你拥有调用内部历史工单和技术文档库的权限。\n"
                   "【工作行为准则】:\n"
                   "1. 面对用户反馈的线上报错、代码 OOM 或配置疑问，必须优先调用 `knowledge_base_search` 工具。\n"
                   "2. 严格基于工具返回的参考文档提供故障排查步骤、避坑指南和修复命令。\n"
                   "3. 如果参考文档中没有提供相关方案，请诚实告知用户：'抱歉，内部知识库暂未收录此问题的特定解法，已为您通知值班工程师介入'，绝对严禁凭空捏造技术命令或错误码。\n"
                   "4. 回复请保持逻辑清晰，代码块需要标注具体的语言或 Shell 语法。"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # 4. 构建原生工具 Agent 实例
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    # 5. 包装为高层级的 Executor 执行器
    executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        handle_tool_errors=True # 捕获工具错误，允许 Agent 自行反思兜底
    )
    
    # 6. 整合 Redis 会话记忆链
    agent_with_history = RunnableWithMessageHistory(
        executor,
        get_session_history=get_redis_chat_history,
        input_messages_key="input",
        history_messages_key="chat_history"
    )
    
    return agent_with_history
