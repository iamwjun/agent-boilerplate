import os
from pydantic import BaseModel
from typing import List, Tuple

class GuardrailsResult(BaseModel):
    is_safe: bool
    risk_level: str  # NONE, LOW, HIGH
    reason: str
    patched_text: str

class InputOutputGuardrails:
    """大模型输入输出双向安全护栏"""
    
    def __init__(self):
        # 实际企业中这些敏感词会从远程安全中心(如布谷鸟、网易易盾)异步加载和热更新
        self.banned_words = ["删库跑路", "解密算法", "提权漏洞", "内网渗透", "系统后门"]
        # 提示词注入防御的关键字
        self.injection_keywords = ["ignore previous instructions", "忽略上述所有指令", "你现在是系统管理员"]

    def check_input(self, user_input: str) -> GuardrailsResult:
        """检查用户提问是否存在恶意注入或违规攻击"""
        lowered_input = user_input.lower()
        
        # 1. 提示词注入攻击防御
        for kw in self.injection_keywords:
            if kw in lowered_input:
                return GuardrailsResult(
                    is_safe=False,
                    risk_level="HIGH",
                    reason="检测到非法的提示词注入攻击拦截。",
                    patched_text="提示：您的请求由于触发安全策略已被系统拒绝。"
                )
        
        return GuardrailsResult(is_safe=True, risk_level="NONE", reason="", patched_text=user_input)

    def check_output(self, agent_output: str) -> GuardrailsResult:
        """检查大模型输出是否包含企业禁止吐出的敏感词"""
        for word in self.banned_words:
            if word in agent_output:
                # 发现高危词汇，立刻触发强制降级熔断，拒绝把回答给到用户
                return GuardrailsResult(
                    is_safe=False,
                    risk_level="HIGH",
                    reason=f"大模型响应命中企业高危敏感词: [{word}]",
                    patched_text="抱歉，当前的回答由于涉及安全敏感信息已被系统拦截，请尝试换种方式提问。"
                )
                
        return GuardrailsResult(is_safe=True, risk_level="NONE", reason="", patched_text=agent_output)
