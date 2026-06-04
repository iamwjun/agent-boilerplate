import torch
from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self):
        # 建议在 Dockerfile 中预下载模型到本地路径
        # BAAI/bge-reranker-large 是目前企业级中文场景的首选
        model_name = 'BAAI/bge-reranker-large'
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CrossEncoder(model_name, device=device)

    def rerank(self, query, documents, top_n=3):
        if not documents:
            return []

        # 构造跨编码器输入：[[问题, 文档1], [问题, 文档2], ...]
        sentence_pairs = [[query, doc['content']] for doc in documents]
        
        # 计算深度相关性得分
        scores = self.model.predict(sentence_pairs)
        
        # 将得分合并并排序
        for i, score in enumerate(scores):
            documents[i]['rerank_score'] = float(score)
            
        # 按重排分数降序排列
        reranked = sorted(documents, key=lambda x: x['rerank_score'], reverse=True)
        return [doc['content'] for doc in reranked[:top_n]]
