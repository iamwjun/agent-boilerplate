import os
from elasticsearch import Elasticsearch

class ESHybridSearcher:
    def __init__(self):
        self.es_host = os.getenv("ES_HOST", "http://elasticsearch:9200")
        self.client = Elasticsearch(
            self.es_host,
            # cloud_id=..., api_key=... # 生产环境鉴权配置
        )
        self.index_name = "tech_support_knowledge"

    def hybrid_search(self, query_text, query_vector, top_k=10):
        """
        执行双路检索：
        1. 关键词检索 (Match): 捕捉错误码、版本号
        2. 向量检索 (k-NN): 捕捉语义意图
        """
        body = {
            "sub_searches": [
                {
                    "query": {
                        "match": {
                            "text_content": {
                                "query": query_text,
                                "boost": 0.1 # 关键词权重辅助
                            }
                        }
                    }
                },
                {
                    "knn": {
                        "field": "text_embedding",
                        "query_vector": query_vector,
                        "k": top_k,
                        "num_candidates": 50
                    }
                }
            ],
            "rank": {
                "rrf": { "window_size": 50 } # RRF 融合算法
            },
            "size": top_k
        }
        
        response = self.client.search(index=self.index_name, body=body)
        return [
            {
                "content": hit["_source"]["text_content"],
                "score": hit["_rank"], # RRF 分数
                "metadata": hit["_source"].get("metadata", {})
            }
            for hit in response["hits"]["hits"]
        ]
