from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sentence_transformers import SentenceTransformer
from src.search.es_client import ESHybridSearcher
from src.rerank.model_wrapper import Reranker

app = FastAPI(title="RAG Search & Rerank Service")

# 初始化组件
# 向量化模型建议与 Ingestion 阶段保持一致
embed_model = SentenceTransformer('BAAI/bge-large-zh-v1.5')
es_searcher = ESHybridSearcher()
reranker = Reranker()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    rerank_top_n: int = 3

@app.post("/api/v1/search")
async def search_endpoint(request: SearchRequest):
    try:
        # 1. 文本向量化
        query_vec = embed_model.encode(request.query).tolist()
        
        # 2. ES 混合检索 (召回阶段)
        raw_hits = es_searcher.hybrid_search(
            query_text=request.query, 
            query_vector=query_vec, 
            top_k=request.top_k
        )
        
        if not raw_hits:
            return {"results": []}
            
        # 3. 交叉编码器重排 (精排阶段)
        final_texts = reranker.rerank(
            query=request.query, 
            documents=raw_hits, 
            top_n=request.rerank_top_n
        )
        
        return {"results": final_texts}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
