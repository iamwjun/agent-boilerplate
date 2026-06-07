import re

class DataMasker:
    """企业级全链路数据脱敏引擎"""
    
    def __init__(self):
        # 预编译常用高密资产的正则表达式
        self.patterns = {
            "phone": (re.compile(r"1[3-9]\d{9}"), lambda m: m.group()[:3] + "****" + m.group()[7:]),
            "id_card": (re.compile(r"\d{15}|\d{18}"), lambda m: m.group()[:4] + "************" + m.group()[-2:]),
            "secret_key": (re.compile(r"(?i)(secret_key|passwd|password|access_key|token)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{16,})['\"]?"), 
                           lambda m: f"{m.group(1)}: ******")
        }

    def mask_text(self, text: str) -> str:
        """对文本进行全量合规脱敏"""
        if not text:
            return text
            
        masked_text = text
        for _, (pattern, repl_func) in self.patterns.items():
            masked_text = pattern.sub(repl_func, masked_text)
            
        return masked_text
