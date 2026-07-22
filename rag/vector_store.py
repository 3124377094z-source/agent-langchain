from langchain_chroma import Chroma
from langchain_core.documents import Document
from utils.config_handler import chroma_conf
from model.factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.path_tool import get_abspath
from utils.file_handler import pdf_loader, txt_loader, listdir_with_allowed_type, get_file_md5_hex
from utils.logger_handler import logger
import os
from datetime import datetime
class VectorStoreService:
    def __init__(self):
        # 向量数据库
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embed_model,
            persist_directory=chroma_conf["persist_directory"],
        )
        # 切块功能
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],
            chunk_overlap=chroma_conf["chunk_overlap"],
            separators=chroma_conf["separators"],
            length_function=len,
        )
    # 实现检索功能
    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf["k"]})
    def load_document(self):
        """
        实现文档切块载入向量数据库，在载入前要先进行md5查重
        :return:
        """
        def check_md5_hex(md5_for_check: str):
            if not os.path.exists(get_abspath(chroma_conf["md5_hex_store"])):
                # 创建文件
                open(get_abspath(chroma_conf["md5_hex_store"]), "w", encoding="utf-8").close()
                return False  # md5 没处理过
            with open(get_abspath(chroma_conf["md5_hex_store"]), "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == md5_for_check:
                        return True  # md5 处理过
                return False  # md5 没处理过
        def save_md5_hex(md5_for_check: str):
            with open(get_abspath(chroma_conf["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_check + "\n")
        # 文档加载函数
        def get_file_documents(read_path: str):
            if read_path.endswith("txt"):
                docs = txt_loader(read_path)
            elif read_path.endswith("pdf"):
                docs = pdf_loader(read_path)
            else:
                return []
            filename = os.path.basename(read_path)
            for doc in docs:
                doc.metadata.update({
                    "filename": filename,
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                })
            return docs
        allowed_files_path: tuple[str] = listdir_with_allowed_type(
            get_abspath(chroma_conf["data_path"]),
            tuple(chroma_conf["allow_knowledge_file_type"]),
        )
        for path in allowed_files_path:
            # 获取文件的MD5
            md5_hex = get_file_md5_hex(path)
            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库]{path}内容已经存在知识库内，跳过")
                continue
            try:
                documents: list[Document] = get_file_documents(path)
                if not documents:
                    logger.warning(f"[加载知识库]{path}内没有有效文本内容，跳过")
                    continue
                split_document: list[Document] = self.spliter.split_documents(documents)
                if not split_document:
                    logger.warning(f"[加载知识库]{path}分片后没有有效文本内容，跳过")
                    continue
                # 将内容存入向量库
                self.vector_store.add_documents(split_document)
                # 记录这个已经处理好的文件的md5，避免下次重复加载
                save_md5_hex(md5_hex)
                logger.info(f"[加载知识库]{path} 内容加载成功")
            except Exception as e:
                # exc_info为True会记录详细的报错堆栈，如果为False仅记录报错信息本身
                logger.error(f"[加载知识库]{path}加载失败：{str(e)}", exc_info=True)
                continue
if __name__ == '__main__':
    vs = VectorStoreService()

    vs.load_document()

    retriever = vs.get_retriever()

    res = retriever.invoke("迷路")
    for r in res:
        print(r.page_content)
        print("-" * 20)
