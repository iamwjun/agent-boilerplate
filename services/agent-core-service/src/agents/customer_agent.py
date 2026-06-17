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

def get_strict_rag_prompt() -> ChatPromptTemplate:
    system_instruction = """你是由研发中心闭环打造的【智能售后政务技术支持 Agent】。你当前正在协助资深架构师排查生产环境故障。

==================================================
【核心机密技术知识库（已通过安全隔离审计）】
--------------------------------------------------
{context}
==================================================

【严格工作行为准则（大厂合规红线，请逐条死守）】：
1. 你的回答必须【百分之百严格基于】上方提供的【核心机密技术知识库】。
2. 如果知识库中包含具体的 Shell 命令、SQL 语句或配置参数，请原封不动地输出，并使用标准代码块（如 ```shell）包裹。
3. 如果用户提出的问题（或报错信息）在上方技术知识库中【没有提及】或【无法完全推导】，你必须直接触发兜底指令，原文回答：“抱歉，内部知识库暂未收录该问题的特定修复方案，已自动为您生成追踪工单，请等待值班架构师接入。”，【绝对严禁】根据你的通用常识进行任何二次技术猜测或编写任何没有经过验证的命令。
4. 绝对不要在回答中提及“根据上方知识库描述”、“系统为您检索到”等公网大模型套话，直接向用户输出诊断结论和步骤，保持专业和务实。
5. 涉及敏感数据或路径时，严格配合系统的脱敏引擎进行输出。"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_instruction),
        MessagesPlaceholder(variable_name="chat_history"), # 动态滑动窗口的历史消息
        ("human", "【当前生产环境最新报错/提问】：\n{input}\n\n【请开始执行诊断】：")
    ])
    return prompt
