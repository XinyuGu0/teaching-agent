"""
Background tasks for document processing using Celery
"""
from app.extensions import celery, db
from app.models.document import Document
from app.utils import file_processor, chunking, embeddings
from app.services import rag_service
from datetime import datetime, timezone
import uuid

@celery.task
def process_document_task(document_id, conversation_id=None):
    """
    Process document in background with full RAG pipeline
    1. Extract text from document
    2. Chunk text into smaller pieces
    3. Generate embeddings for each chunk
    4. Store in vector database
    
    Args:
        document_id: Document ID
        conversation_id: Optional conversation ID for WebSocket notifications
    """
    try:
        document = Document.query.get(document_id)
        if not document:
            print(f"Document {document_id} not found")
            return

        import time
        start_time = time.time()
        print(f"[DEBUG] ========== 开始处理文档 ==========")
        print(f"[DEBUG] 文档: {document.original_filename} (ID: {document.id})")
        print(f"[DEBUG] Conversation ID: {conversation_id}")

        # Step 1: Extract text
        print(f"[DEBUG] [1/4] 开始提取文本...")
        try:
            text = file_processor.extract_text(document.file_path, document.file_type)
            print(f"[DEBUG] ✓ 文本提取完成: {len(text)} 字符")
        except Exception as e:
            print(f"[ERROR] 文本提取失败: {e}")
            import traceback
            traceback.print_exc()
            document.status = 'failed'
            db.session.commit()
            return

        if not text or len(text.strip()) < 10:
            print(f"[DEBUG] ⚠ 提取的文本太少，跳过处理")
            document.status = 'ready'  # Mark as ready even if no text
            document.processed_at = datetime.now(timezone.utc)
            db.session.commit()
            return

        # Step 2: Chunk text (优化：增大chunk_size减少chunks数量)
        print(f"[DEBUG] [2/4] 开始文本分块...")
        chunk_start = time.time()
        try:
            chunks = chunking.chunk_text(
                text,
                chunk_size=2000,  # 从800增加到2000，减少chunks数量
                overlap=200       # 从100增加到200，保持上下文连续性
            )
            chunk_time = time.time() - chunk_start
            print(f"[DEBUG] ✓ 文本分块完成: {len(chunks)} 个chunks, 耗时: {chunk_time:.2f}秒")

            # 如果chunks太多（超过20个），重新chunk更大的size
            if len(chunks) > 20:
                print(f"[DEBUG] ⚠ Chunks数量过多 ({len(chunks)}), 重新分块...")
                rechunk_start = time.time()
                chunks = chunking.chunk_text(
                    text,
                    chunk_size=4000,
                    overlap=400
                )
                rechunk_time = time.time() - rechunk_start
                print(f"[DEBUG] ✓ 重新分块完成: {len(chunks)} 个chunks, 耗时: {rechunk_time:.2f}秒")

        except Exception as e:
            print(f"[ERROR] 文本分块失败: {e}")
            import traceback
            traceback.print_exc()
            document.status = 'failed'
            db.session.commit()
            return

        if not chunks:
            print(f"[DEBUG] ⚠ 没有生成chunks")
            document.status = 'ready'
            document.processed_at = datetime.now(timezone.utc)
            db.session.commit()
            return

        # Step 3: Generate embeddings
        print(f"[DEBUG] [3/4] 开始生成embeddings (batch_size=25)...")
        embed_start = time.time()
        try:
            chunk_embeddings = embeddings.generate_embeddings(chunks)
            embed_time = time.time() - embed_start
            print(f"[DEBUG] ✓ Embeddings生成完成: {len(chunk_embeddings)} 个, 耗时: {embed_time:.2f}秒")
        except Exception as e:
            print(f"[ERROR] Embeddings生成失败: {e}")
            import traceback
            traceback.print_exc()
            document.status = 'failed'
            db.session.commit()
            return

        # Step 4: Store in vector database
        print(f"[DEBUG] [4/4] 开始存储到向量数据库...")
        store_start = time.time()
        try:
            # Create unique IDs for each chunk
            chunk_ids = [f"{document.id}_chunk_{i}" for i in range(len(chunks))]

            # Create metadata for each chunk
            metadatas = [
                {
                    'document_id': document.id,
                    'user_id': document.user_id,
                    'filename': document.original_filename,
                    'file_type': document.file_type,
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
                for i in range(len(chunks))
            ]

            # Add to vector database
            vector_ids = rag_service.add_documents(
                texts=chunks,
                embeddings=chunk_embeddings,
                metadatas=metadatas,
                ids=chunk_ids
            )

            # Store vector IDs in document record
            document.vector_ids = vector_ids
            store_time = time.time() - store_start
            print(f"[DEBUG] ✓ 向量数据库存储完成: {len(vector_ids)} 个chunks, 耗时: {store_time:.2f}秒")

        except Exception as e:
            print(f"[ERROR] 向量数据库存储失败: {e}")
            import traceback
            traceback.print_exc()
            document.status = 'failed'
            db.session.commit()
            return

        # Mark as ready
        print(f"[DEBUG] 更新文档状态为 'ready'...")
        document.status = 'ready'
        document.processed_at = datetime.utcnow()
        db.session.commit()

        total_time = time.time() - start_time
        print(f"[DEBUG] ========== 文档处理完成 ==========")
        print(f"[DEBUG] 文档: {document.original_filename}")
        print(f"[DEBUG] 总耗时: {total_time:.2f}秒")
        print(f"[DEBUG] 统计: 提取文本 → 分块({len(chunks)}) → embeddings → 存储")
        print(f"[DEBUG] =======================================")

        # 发送WebSocket通知（如果提供了conversation_id）
        if conversation_id:
            try:
                from flask import current_app
                from app.extensions import socketio
                
                # 检查是否有应用上下文
                if not current_app:
                    print(f"No Flask app context, skipping WebSocket notification")
                else:
                    # 在应用上下文中发送通知
                    with current_app.app_context():
                        socketio.emit('document_processed', {
                            'document_id': document.id,
                            'original_filename': document.original_filename,
                            'file_type': document.file_type,
                            'status': 'ready',
                            'chunks_count': len(chunks)
                        }, room=conversation_id)
                        print(f"Sent document processed notification to conversation {conversation_id}")
            except Exception as e:
                print(f"Error sending WebSocket notification: {e}")
        else:
            print(f"No conversation_id provided, skipping WebSocket notification")

    except Exception as e:
        print(f"Error processing document: {e}")
        if document:
            document.status = 'failed'
            db.session.commit()
            
            # 发送失败通知
            if conversation_id:
                try:
                    from flask import current_app
                    from app.extensions import socketio
                    
                    with current_app.app_context():
                        socketio.emit('document_processed', {
                            'document_id': document.id,
                            'original_filename': document.original_filename,
                            'status': 'failed',
                            'error': str(e)
                        }, room=conversation_id)
                except Exception as notify_error:
                    print(f"Error sending failure notification: {notify_error}")
        
        raise
