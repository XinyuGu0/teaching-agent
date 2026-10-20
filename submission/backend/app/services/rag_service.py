"""
RAG (检索增强生成) 服务模块
基于 ChromaDB 向量数据库实现文档索引与语义检索
"""
import os
import logging
from typing import List, Dict, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings

logger = logging.getLogger(__name__)

# 全局 Chroma 客户端（懒加载）
_chroma_client: Optional[chromadb.PersistentClient] = None


def get_chroma_client() -> chromadb.PersistentClient:
    """
    获取或初始化 ChromaDB 持久化客户端

    Returns:
        ChromaDB PersistentClient 实例
    """
    global _chroma_client
    if _chroma_client is None:
        os.makedirs(settings.VECTOR_DB_DIR, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(
            path=settings.VECTOR_DB_DIR,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )
        logger.info(f"ChromaDB 初始化完成: {settings.VECTOR_DB_DIR}")
    return _chroma_client


def get_collection(collection_name: str = "documents"):
    """获取或创建 ChromaDB 集合"""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"description": "Document chunks for RAG"},
    )


def add_documents(
    texts: List[str],
    embeddings: List[List[float]],
    metadatas: List[Dict],
    ids: List[str],
) -> List[str]:
    """
    将文档分块写入向量数据库

    Args:
        texts: 文本分块列表
        embeddings: 对应的嵌入向量列表
        metadatas: 元数据字典列表
        ids: 唯一标识列表

    Returns:
        成功写入的 ID 列表
    """
    collection = get_collection()
    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )
    logger.info(f"已索引 {len(texts)} 个文档分块")
    return ids


def search_documents(
    query_text: str,
    query_embedding: List[float],
    n_results: int = 5,
    filter_metadata: Optional[Dict] = None,
) -> Dict:
    """
    语义相似度检索

    Args:
        query_text: 查询文本（用于日志）
        query_embedding: 查询文本的嵌入向量
        n_results: 返回结果数量
        filter_metadata: 元数据过滤条件，如 {"user_id": "xxx"}

    Returns:
        包含 documents / metadatas / distances / ids 的字典
    """
    try:
        collection = get_collection()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata if filter_metadata else None,
        )
        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
            "ids": results["ids"][0] if results["ids"] else [],
        }
    except Exception as e:
        logger.error(f"文档检索失败: {e}")
        return {"documents": [], "metadatas": [], "distances": [], "ids": []}


def delete_documents_by_metadata(filter_metadata: Dict) -> bool:
    """按元数据条件删除文档分块"""
    collection = get_collection()
    results = collection.get(where=filter_metadata)
    if results["ids"]:
        collection.delete(ids=results["ids"])
        logger.info(f"已删除 {len(results['ids'])} 个文档分块")
    return True


def get_collection_stats() -> Dict:
    """获取集合统计信息"""
    collection = get_collection()
    return {
        "total_documents": collection.count(),
        "collection_name": collection.name,
    }