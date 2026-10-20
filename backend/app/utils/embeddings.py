"""
Embedding generation utilities using OpenAI-compatible API
支持智谱 Embedding API (https://open.bigmodel.cn/api/paas/v4)
"""
from typing import List
import numpy as np
from flask import current_app
import os
import logging

logger = logging.getLogger(__name__)

# Global embedding client (lazy loaded)
_embedding_client = None
_embedding_base_url = None

def get_embedding_client():
    """Get or initialize OpenAI-compatible client for embeddings"""
    global _embedding_client, _embedding_base_url

    if _embedding_client is None:
        try:
            from openai import OpenAI

            # 智谱 Embedding 使用独立的 API endpoint
            # 优先级: EMBEDDING_* > 智谱官方 > LLM配置
            api_key = os.getenv('EMBEDDING_API_KEY') or os.getenv('GLM_API_KEY') or os.getenv('LLM_API_KEY')
            
            # 智谱 Embedding API 的 base_url
            base_url = os.getenv('EMBEDDING_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')
            
            if not api_key:
                raise ValueError("No API key configured for embeddings (EMBEDDING_API_KEY, GLM_API_KEY or LLM_API_KEY)")

            _embedding_client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            _embedding_base_url = base_url
            print(f"Embedding client initialized (base_url: {base_url})")

        except Exception as e:
            print(f"Error initializing embedding client: {e}")
            raise

    return _embedding_client


# 智谱 Embedding 模型
EMBEDDING_MODEL = "embedding-3"


def generate_embeddings(texts: List[str], batch_size: int = 25) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using 智谱 Embedding API

    Args:
        texts: List of text strings
        batch_size: Number of texts to process per batch

    Returns:
        List of embedding vectors
    """
    if not texts:
        return []

    try:
        client = get_embedding_client()
        embeddings = []
        
        # 使用智谱 embedding-3 模型
        model = os.getenv('EMBEDDING_MODEL', EMBEDDING_MODEL)

        # Process texts in batches for better performance
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}, size: {len(batch)}")

            try:
                response = client.embeddings.create(
                    model=model,
                    input=batch
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                print(f"Successfully used embedding model: {model}")
                
            except Exception as e:
                logger.error(f"Embedding model {model} failed: {e}")
                # 使用零向量作为回退
                for _ in batch:
                    embeddings.append([0.0] * 1024)

        print(f"Generated {len(embeddings)} embeddings")
        return embeddings

    except Exception as e:
        print(f"Error generating embeddings: {e}")
        raise


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single text

    Args:
        text: Text string

    Returns:
        Embedding vector
    """
    embeddings = generate_embeddings([text])
    return embeddings[0] if embeddings else []


def compute_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Compute cosine similarity between two embeddings

    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector

    Returns:
        Similarity score (0-1)
    """
    try:
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Cosine similarity
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

        return float(similarity)

    except Exception as e:
        print(f"Error computing similarity: {e}")
        return 0.0
