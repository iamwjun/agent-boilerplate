import time
from src.transformers.cleaner import DocumentTransformer
from src.loaders.es_bulk_loader import ESBulkLoader

def run_sync_pipeline():
    print("🚀 Starting Data Pipeline Job...")
    
    # 模拟从企业内部存储中抽取的经典历史技术问答数据
    mock_raw_data = [
        {
            "content": "# 常见内核 OOM 故障排查\n## 错误码 ERR_0921 的紧急处理\n当系统由于连接数暴满引发内存溢出时，控制台会抛出 ERR_0921 错误。此时应当立刻登录高密节点，执行 `SET GLOBAL force_release_conn = 1;` 来强制释放长连接。此操作可瞬间降低 40% 的内存水位。",
            "metadata": {"source": "Jira_Ticket_10293", "tenant_id": "tenant_A"}
        },
        {
            "content": "# 数据库升级指南\n## 连接池变更公告\n自 v3.2.0 版本起，数据库底层的 `max_connections` 参数在未重启实例前不会动态生效。如果在升级过程中遭遇连接数耗尽，请优先检查基础设施的存活指标。",
            "metadata": {"source": "Confluence_Doc_772", "tenant_id": "tenant_A"}
        }
    ]

    transformer = DocumentTransformer()
    loader = ESBulkLoader()

    all_processed_chunks = []
    
    for item in mock_raw_data:
        # 经历数据清洗与自适应切片
        chunks = transformer.process_markdown(item["content"], item["metadata"])
        all_processed_chunks.extend(chunks)

    # 批量入库
    loader.load(all_processed_chunks)
    print("🏁 Data Pipeline Job finished successfully.")

if __name__ == "__main__":
    # 生产环境中，通常这里会结合 Kafka 监听、Flink 增量变更或定时轮询逻辑
    run_sync_pipeline()
