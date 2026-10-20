"""
RAG (Retrieval-Augmented Generation) service
Handles document indexing and retrieval using Chroma vector database
"""
import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from flask import current_app

# Global Chroma client (lazy loaded)
_chroma_client = None
_collection = None

def get_chroma_client():
    """Get or initialize Chroma client"""
    global _chroma_client

    if _chroma_client is None:
        try:
            # Get vector DB path from config
            vector_db_path = current_app.config['VECTOR_DB_DIR']
            os.makedirs(vector_db_path, exist_ok=True)

            # Initialize Chroma client with persistent storage
            _chroma_client = chromadb.PersistentClient(
                path=vector_db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            print(f"Chroma client initialized at: {vector_db_path}")

        except Exception as e:
            print(f"Error initializing Chroma client: {e}")
            raise

    return _chroma_client


def get_collection(collection_name: str = "documents"):
    """
    Get or create a Chroma collection

    Args:
        collection_name: Name of the collection

    Returns:
        Chroma collection
    """
    try:
        client = get_chroma_client()

        # Get or create collection
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Document chunks for RAG"}
        )

        return collection

    except Exception as e:
        print(f"Error getting collection: {e}")
        raise


def add_documents(
    texts: List[str],
    embeddings: List[List[float]],
    metadatas: List[Dict],
    ids: List[str]
) -> List[str]:
    """
    Add documents to vector database

    Args:
        texts: List of text chunks
        embeddings: List of embedding vectors
        metadatas: List of metadata dictionaries
        ids: List of unique IDs for each chunk

    Returns:
        List of IDs that were added
    """
    try:
        collection = get_collection()

        # Add documents to collection
        collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        print(f"Added {len(texts)} documents to vector database")
        return ids

    except Exception as e:
        print(f"Error adding documents: {e}")
        raise


def search_documents(
    query_text: str,
    query_embedding: List[float],
    n_results: int = 5,
    filter_metadata: Optional[Dict] = None
) -> Dict:
    """
    Search for similar documents

    Args:
        query_text: Query text (for logging)
        query_embedding: Query embedding vector
        n_results: Number of results to return
        filter_metadata: Optional metadata filter (e.g., {"user_id": "123"})

    Returns:
        Dictionary with 'documents', 'metadatas', 'distances', 'ids'
    """
    try:
        collection = get_collection()

        # Search collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata if filter_metadata else None
        )

        # Format results
        return {
            'documents': results['documents'][0] if results['documents'] else [],
            'metadatas': results['metadatas'][0] if results['metadatas'] else [],
            'distances': results['distances'][0] if results['distances'] else [],
            'ids': results['ids'][0] if results['ids'] else []
        }

    except Exception as e:
        print(f"Error searching documents: {e}")
        return {
            'documents': [],
            'metadatas': [],
            'distances': [],
            'ids': []
        }


def delete_documents(ids: List[str]) -> bool:
    """
    Delete documents from vector database

    Args:
        ids: List of document IDs to delete

    Returns:
        True if successful
    """
    try:
        collection = get_collection()

        collection.delete(ids=ids)

        print(f"Deleted {len(ids)} documents from vector database")
        return True

    except Exception as e:
        print(f"Error deleting documents: {e}")
        return False


def delete_documents_by_metadata(filter_metadata: Dict) -> bool:
    """
    Delete documents by metadata filter

    Args:
        filter_metadata: Metadata filter (e.g., {"document_id": "123"})

    Returns:
        True if successful
    """
    try:
        collection = get_collection()

        # Get documents matching filter
        results = collection.get(where=filter_metadata)

        if results['ids']:
            collection.delete(ids=results['ids'])
            print(f"Deleted {len(results['ids'])} documents matching filter")

        return True

    except Exception as e:
        print(f"Error deleting documents by metadata: {e}")
        return False


def get_collection_stats() -> Dict:
    """
    Get statistics about the collection

    Returns:
        Dictionary with collection statistics
    """
    try:
        collection = get_collection()

        count = collection.count()

        return {
            'total_documents': count,
            'collection_name': collection.name
        }

    except Exception as e:
        print(f"Error getting collection stats: {e}")
        return {
            'total_documents': 0,
            'collection_name': 'unknown'
        }
