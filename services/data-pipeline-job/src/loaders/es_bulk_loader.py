import os
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from sentence_transformers import SentenceTransformer

class ESBulkLoader:
    def __init__(self):
        es_host = os.getenv("ES_HOST", "http://elasticsearch:9200")
        self.es = Elasticsearch(es_host)
        self.index_name = "tech_support_knowledge"
        # 向量化模型，保持全链路统一
        self.embed_model = SentenceTransformer('BAAI/bge-large-zh-v1.5')

    def load(self, chunks: list):
        """批量计算向量并写入 Elasticsearch"""
        if not chunks:
            return

        print(f"Starting vectorization for {len(chunks)} chunks...")
        # 提取文本内容进行批量 Embed（利用 Embedding 模型的 batch 能力提高速度）
        texts = [chunk["text_content"] for chunk in chunks]
        embeddings = self.embed_model.encode(texts, batch_size=32, show_progress_bar=True).tolist()

        # 构建 ES 批量操作的 actions
        actions = []
        for idx, chunk in enumerate(chunks):
            action = {
                "_index": self.index_name,
                "_source": {
                    "text_content": chunk["text_content"],
                    "text_embedding": embeddings[idx], # 写入向量
                    "metadata": chunk["metadata"]      # 写入元数据（用于租户隔离/溯源）
                }
            }
            actions.append(action)

        # 执行 Bulk 写入
        success, errors = bulk(self.client=self.es, actions=actions)
        print(f"Successfully indexed {success} documents. Errors: {len(errors) if isinstance(errors, list) else errors}")
