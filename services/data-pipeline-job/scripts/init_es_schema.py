import os
from elasticsearch import Elasticsearch

def init_index():
    es_host = os.getenv("ES_HOST", "http://elasticsearch:9200")
    es = Elasticsearch(es_host)
    index_name = "tech_support_knowledge"

    # 如果索引已存在，则不重复创建
    if es.indices.exists(index=index_name):
        print(f"Index {index_name} already exists.")
        return

    # 定义企业级混合检索映射
    mapping = {
        "mappings": {
            "properties": {
                "text_content": { 
                    "type": "text", 
                    "analyzer": "ik_max_word",       # 生产环境建议安装并配置 IK 中文分词器
                    "search_analyzer": "ik_smart"
                }, 
                "text_embedding": {
                    "type": "dense_vector",
                    "dims": 1024,                     # bge-large-zh-v1.5 的标准输出维度
                    "index": True,
                    "similarity": "cosine"            # 使用余弦相似度
                },
                "metadata": {
                    "properties": {
                        "source": { "type": "keyword" },
                        "tenant_id": { "type": "keyword" },
                        "created_at": { "type": "date" }
                    }
                }
            }
        }
    }

    es.indices.create(index=index_name, body=mapping)
    print(f"Successfully created index: {index_name}")

if __name__ == "__main__":
    init_index()
