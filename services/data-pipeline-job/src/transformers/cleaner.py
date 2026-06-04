from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

class DocumentTransformer:
    def __init__(self):
        # 1. 第一层：按 Markdown 的一二级标题切分，保证章节段落不被物理斩断
        self.headers_to_split_on = [
            ("#", "Header_1"),
            ("##", "Header_2"),
        ]
        self.md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=self.headers_to_split_on)
        
        # 2. 第二层：如果某章节字数依旧超标，用滑动窗口切分器微调
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,       # 经验值：企业技术文档 500-800 字语义最紧凑
            chunk_overlap=120,     # 重叠 120 字，防止故障描述在切缝处断裂
            length_function=len
        )

    def process_markdown(self, raw_text: str, global_metadata: dict) -> list:
        """输入原始 Markdown 技术文档，输出加工好的 Chunks 列表"""
        # 按照标题切分
        md_header_splits = self.md_splitter.split_text(raw_text)
        
        final_chunks = []
        # 对切分出来的每个部分进行精细化微调
        for doc in md_header_splits:
            sub_chunks = self.text_splitter.split_documents([doc])
            for sub_chunk in sub_chunks:
                # 融合原始元数据与切片元数据
                merged_metadata = global_metadata.copy()
                merged_metadata.update(sub_chunk.metadata)
                
                final_chunks.append({
                    "text_content": sub_chunk.page_content,
                    "metadata": merged_metadata
                })
        return final_chunks
