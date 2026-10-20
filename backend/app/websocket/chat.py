from app.extensions import socketio, db
from app.models.conversation import Conversation, Message
from app.models.user import User
from app.models.document import Document
from app.models.ppt import PPT
from app.services import glm_service, rag_service
from app.services.conversation_state_machine import ConversationStateMachine
from app.services.officecli_mcp_service import get_officecli_mcp_service
from app.services.image_service import get_image_service
from app.services.template_service import get_template_service
from app.utils import embeddings
from flask_socketio import emit, join_room
from flask import request, current_app
from datetime import datetime
import json
import os
import tempfile
import mimetypes
import uuid
import requests
import re
import time
import threading
from pptx import Presentation
from pptx.util import Inches
from pptx.dml.color import RGBColor

# 调试模式：模拟PPT生成流程（不真正生成）
ENABLE_MOCK_PPT_GENERATION = True
MOCK_PPT_FILE_MAP = {
    'builtin': 'SQL语言进阶训练简单查询_buildin_202604150924.pptx',
    'uploaded': 'SQL语言进阶训练简单查询_define_202604150930.pptx',
    'blank': 'SQL语言进阶训练简单查询_blank_202604150943.pptx'
}

def register_handlers():
    """Register WebSocket event handlers"""

    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        print(f'Client connected: {request.sid}')
        emit('connected', {'status': 'success'})

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print(f'Client disconnected: {request.sid}')

    @socketio.on('join_conversation')
    def handle_join_conversation(data):
        """Join conversation room"""
        conversation_id = data.get('conversation_id')
        user_id = data.get('user_id')

        missing_params = []
        if not conversation_id:
            missing_params.append('conversation_id')
        if not user_id:
            missing_params.append('user_id')

        if missing_params:
            emit('error', {'message': f'缺少必要参数: {", ".join(missing_params)}'})
            return

        # Verify conversation belongs to user
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()

        if not conversation:
            emit('error', {'message': '对话不存在'})
            return

        # Join room
        join_room(conversation_id)
        print(f'User {user_id} joined conversation {conversation_id}')

        # Send conversation history
        messages = Message.query.filter_by(
            conversation_id=conversation_id
        ).order_by(Message.created_at).all()

        emit('conversation_history', {
            'messages': [msg.to_dict() for msg in messages]
        })

    @socketio.on('send_message')
    def handle_send_message(data):
        """Handle user message and generate AI response with state machine"""
        conversation_id = data.get('conversation_id')
        user_id = data.get('user_id')
        content = data.get('content')

        missing_params = []
        if not conversation_id:
            missing_params.append('conversation_id')
        if not user_id:
            missing_params.append('user_id')
        if not content:
            missing_params.append('content')

        if missing_params:
            emit('error', {'message': f'缺少必要参数: {", ".join(missing_params)}'})
            return

        try:
            # Verify conversation
            conversation = Conversation.query.filter_by(
                id=conversation_id,
                user_id=user_id
            ).first()

            if not conversation:
                emit('error', {'message': '对话不存在'})
                return

            # Save user message
            user_message = Message(
                conversation_id=conversation_id,
                role='user',
                content=content,
                user_id=user_id
            )
            db.session.add(user_message)
            db.session.commit()

            # 首次用户消息后初始化对话标题（仅一次）
            requirements = conversation.requirements or {}
            title_initialized = bool(requirements.get('title_initialized'))
            if not title_initialized:
                # 用户已自定义标题则不自动取名
                is_default_title = (conversation.title or '').strip().lower() in ['new conversation', '新对话', '']
                if is_default_title:
                    first_line = (content or '').replace('\r', '\n').split('\n')[0].strip()
                    clean_title = ' '.join(first_line.split())
                    if clean_title:
                        conversation.title = clean_title[:24]
                requirements['title_initialized'] = True
                conversation.requirements = requirements
                db.session.commit()

                # 实时同步前端会话标题
                socketio.emit('conversation_updated', {
                    'conversation': conversation.to_dict()
                }, room=conversation_id)

            # Emit user message to room
            socketio.emit('message_received', user_message.to_dict(), room=conversation_id)

            # Initialize state machine
            state_machine = ConversationStateMachine()
            current_state = conversation.state
            current_requirements = conversation.requirements or {}

            # Extract requirements from user message
            updated_requirements = state_machine.extract_requirements(
                content,
                current_requirements
            )

            # 记录用户有效对话轮次（按用户消息数统计），供AI引导策略使用
            try:
                user_turn_count = Message.query.filter_by(
                    conversation_id=conversation_id,
                    role='user'
                ).count()
                updated_requirements['user_turn_count'] = user_turn_count
            except Exception:
                # 兜底：至少保证本次消息计入
                updated_requirements['user_turn_count'] = int(updated_requirements.get('user_turn_count') or 0) + 1
            
            # Update requirements if changed
            if updated_requirements != current_requirements:
                conversation.requirements = updated_requirements
                db.session.commit()
                print(f"Requirements updated: {updated_requirements}")

            # Check if state should transition
            should_transition = state_machine.should_transition(
                current_state,
                content,
                updated_requirements
            )

            # Get conversation history before checking for outline generation
            messages = Message.query.filter_by(
                conversation_id=conversation_id
            ).order_by(Message.created_at).all()

            conversation_history = [
                {'role': msg.role, 'content': msg.content}
                for msg in messages[:-1]  # Exclude just-added message
            ]

            # 特殊处理：检测用户消息中是否包含生成关键词或确认词
            generate_keywords = ['生成大纲', '生成思维导图', '开始生成大纲', '生成ppt', '生成PPT', '开始生成', '开始制作']
            confirm_keywords = ['可以', '好的', 'ok', '没问题', '行', '当然']
            
            # 检测是否需要生成大纲
            should_generate_outline = False
            if any(keyword in content.lower() for keyword in generate_keywords):
                should_generate_outline = True
            # 如果AI之前提议生成大纲，用户确认后自动触发
            elif any(keyword in content.lower() for keyword in confirm_keywords):
                for msg in reversed(conversation_history[-3:]):  # 检查最近3条消息
                    if msg['role'] == 'assistant':
                        ai_content = msg['content'].lower()
                        if '大纲' in ai_content or 'ppt' in ai_content:
                            should_generate_outline = True
                            break
            
            if should_generate_outline:
                # 用户要求生成大纲
                if current_state == 'CHAT':
                    all_messages = Message.query.filter_by(
                        conversation_id=conversation_id
                    ).order_by(Message.created_at).all()

                    topic = updated_requirements.get('topic', '') or '主题演示'

                    # 发送开始生成事件
                    socketio.emit('outline_generation_start', {
                        'conversation_id': conversation_id
                    }, room=conversation_id)
                    
                    # 如果用户给了“明确的大纲文本（含Slide 1/幻灯片1等）”，优先锁定按该文本生成
                    explicit_outline_text = ''
                    try:
                        user_texts = [m.content for m in all_messages if m.role == 'user' and (m.content or '').strip()]
                        for txt in reversed(user_texts):
                            t = txt or ''
                            if ('slide 1' in t.lower()) or ('幻灯片 1' in t) or ('ppt内容大纲' in t.lower()) or ('我要的大纲是' in t):
                                explicit_outline_text = t
                                break
                    except Exception:
                        explicit_outline_text = ''

                    # 触发结构化大纲生成
                    import threading
                    def generate_outline_task():
                        try:
                            import uuid
                            request_id = str(uuid.uuid4())[:8]
                            start_ts = time.perf_counter()
                            print(f"[OUTLINE][{request_id}] 开始生成, conversation_id={conversation_id}, topic={topic}")

                            # 发送进度：30%
                            socketio.emit('outline_generation_progress', {
                                'progress': 30,
                                'message': f'正在整理对话上下文（req={request_id}）...'
                            }, room=conversation_id)

                            prep_start_ts = time.perf_counter()
                            conversation_history_for_outline = [
                                {'role': m.role, 'content': m.content}
                                for m in all_messages
                                if m.role in ('user', 'assistant') and (m.content or '').strip()
                            ]
                            prep_elapsed = time.perf_counter() - prep_start_ts
                            print(f"[OUTLINE][{request_id}] 上下文整理完成, history_len={len(conversation_history_for_outline)}, elapsed={prep_elapsed:.2f}s")

                            # 发送进度：45%
                            socketio.emit('outline_generation_progress', {
                                'progress': 45,
                                'message': f'正在调用模型生成结构化大纲（req={request_id}）...'
                            }, room=conversation_id)

                            llm_start_ts = time.perf_counter()
                            result = glm_service.generate_ppt_outline(
                                topic=topic,
                                requirements=updated_requirements,
                                context_documents=[],
                                explicit_outline_text=explicit_outline_text,
                                conversation_history=conversation_history_for_outline
                            )
                            llm_elapsed = time.perf_counter() - llm_start_ts
                            print(f"[OUTLINE][{request_id}] LLM生成完成, elapsed={llm_elapsed:.2f}s")

                            # 发送进度：75%
                            socketio.emit('outline_generation_progress', {
                                'progress': 75,
                                'message': '正在生成思维导图...'
                            }, room=conversation_id)

                            # Extract outline and mindmap from result
                            if 'outline' in result:
                                outline = result['outline']
                                outline['title'] = result.get('title', topic)
                            else:
                                outline = result

                            mindmap = result.get('mindmap', '')

                            total_elapsed = time.perf_counter() - start_ts
                            print(f"[OUTLINE] 大纲任务完成，总耗时: {total_elapsed:.2f}s")

                            # 发送进度：100%
                            socketio.emit('outline_generation_progress', {
                                'progress': 100,
                                'message': f'大纲生成完成！总耗时 {total_elapsed:.1f}s'
                            }, room=conversation_id)

                            # Save outline and mindmap in message metadata
                            outline_message = Message(
                                conversation_id=conversation_id,
                                role='assistant',
                                content=f"已生成PPT大纲：{result.get('title', topic)}",
                                meta_data={
                                    'outline': outline,
                                    'mindmap': mindmap,
                                    'type': 'outline'
                                }
                            )
                            db.session.add(outline_message)
                            db.session.commit()

                            # Update conversation state
                            conversation.state = 'GENERATING_OUTLINE'
                            db.session.commit()

                            # Emit outline and mindmap to room
                            socketio.emit('outline_generated', {
                                'outline': outline,
                                'mindmap': mindmap,
                                'message': outline_message.to_dict()
                            }, room=conversation_id)
                            
                        except Exception as e:
                            print(f"Error generating outline: {e}")
                            err_text = str(e)
                            socketio.emit('outline_generation_progress', {
                                'progress': 0,
                                'message': f'大纲生成失败: {err_text}'
                            }, room=conversation_id)
                            if ('Timeout' in err_text) or ('timed out' in err_text) or ('ReadTimeout' in err_text):
                                socketio.emit('error', {
                                    'message': '大纲生成超时，请稍后重试，或减少页数后再生成。'
                                }, room=conversation_id)
                            else:
                                socketio.emit('error', {
                                    'message': f'大纲生成失败: {err_text}'
                                }, room=conversation_id)
                    
                    # 在后台线程中执行生成任务
                    thread = threading.Thread(target=generate_outline_task)
                    thread.daemon = True
                    thread.start()
                    
                    # 返回，不继续AI对话
                    return

            # Retrieve relevant documents from RAG
            context_documents = []
            try:
                print(f"[DEBUG RAG] 开始检索相关文档...")
                print(f"[DEBUG RAG] 用户问题: {content[:100]}...")
                
                # Generate query embedding
                query_embedding = embeddings.generate_embedding(content)
                print(f"[DEBUG RAG] ✓ Query embedding生成完成")

                # Search vector database
                search_results = rag_service.search_documents(
                    query_text=content,
                    query_embedding=query_embedding,
                    n_results=5,
                    filter_metadata={'user_id': user_id}
                )

                context_documents = search_results['documents']
                print(f"[DEBUG RAG] ✓ 检索到 {len(context_documents)} 个相关文档")
                
                if context_documents:
                    for i, doc in enumerate(context_documents[:3], 1):  # 只显示前3个
                        print(f"[DEBUG RAG] 文档{i}: {doc[:100]}...")
                else:
                    print(f"[DEBUG RAG] ⚠ 未检索到相关文档")

            except Exception as e:
                print(f"Error retrieving context: {e}")
                # Continue without context

            # Get state-aware system prompt
            system_prompt = state_machine.get_guidance_prompt(
                current_state,
                conversation.requirements
            )

            # 注入用户画像信息，让AI具备个性化“长期记忆”
            user_profile_prompt = ''
            try:
                user = User.query.filter_by(id=user_id).first()
                if user:
                    profile_parts = []
                    if user.nickname:
                        profile_parts.append(f"昵称：{user.nickname}")
                    if user.teacher_gender:
                        profile_parts.append(f"教师性别：{user.teacher_gender}")
                    if user.teacher_age:
                        profile_parts.append(f"教师年龄：{user.teacher_age}")
                    if user.school_name:
                        profile_parts.append(f"所在学校：{user.school_name}")
                    if user.subject_category:
                        profile_parts.append(f"学科门类：{user.subject_category}")
                    if user.courses:
                        profile_parts.append(f"具体课程：{', '.join(user.courses)}")
                    if user.teaching_styles:
                        profile_parts.append(f"授课风格：{', '.join(user.teaching_styles)}")

                    if profile_parts:
                        user_profile_prompt = (
                            "\n\n[用户画像记忆]\n"
                            + "\n".join(profile_parts)
                            + "\n请在回答和生成建议中充分结合上述用户画像，"
                            + "优先给出与其课程、风格和教学场景匹配的内容。"
                        )
            except Exception as e:
                print(f"[PROFILE] 读取用户画像失败: {e}")

            system_prompt += user_profile_prompt

            # 如果有RAG文档，添加提示词明确说明
            if context_documents and len(context_documents) > 0:
                system_prompt += "\n\n重要提示：用户刚刚上传了文件，系统已经提取了文件内容并通过RAG检索返回了相关的文档片段。这些文档片段就是用户上传的文件内容。请基于这些文档内容回答用户的问题，不要说你无法看到文件。"
            else:
                system_prompt += "\n\n重要提示：用户刚刚上传了文件，但是RAG没有检索到相关内容。这可能是因为文件处理失败或者问题与文件内容不匹配。"

            # Generate AI response with web search enabled (streaming)
            full_response = ""
            full_thinking = ""
            try:
                # Emit streaming start event
                socketio.emit('streaming_start', {
                    'conversation_id': conversation_id
                }, room=conversation_id)

                response_stream = glm_service.chat_with_context(
                    user_message=content,
                    conversation_history=conversation_history,
                    context_documents=context_documents,
                    system_prompt=system_prompt,
                    enable_web_search=True,
                    stream=True,
                    enable_thinking=False,
                    retry_count=0,
                    timeout_seconds=45
                )

                # Stream response chunks to client
                for chunk in response_stream:
                    # 防止空choices导致IndexError（Qwen等模型最后一个chunk可能为空）
                    if not chunk.choices or len(chunk.choices) == 0:
                        continue

                    delta = chunk.choices[0].delta

                    # 捕获 reasoning_content（思考内容，部分模型支持）
                    reasoning = getattr(delta, 'reasoning_content', None)
                    if reasoning:
                        full_thinking += reasoning
                        socketio.emit('thinking_chunk', {
                            'conversation_id': conversation_id,
                            'content': reasoning
                        }, room=conversation_id)

                    # 捕获正文内容
                    if hasattr(delta, 'content') and delta.content:
                        chunk_content = delta.content
                        full_response += chunk_content
                        socketio.emit('message_chunk', {
                            'conversation_id': conversation_id,
                            'content': chunk_content
                        }, room=conversation_id)

                # Save complete AI message
                ai_message = Message(
                    conversation_id=conversation_id,
                    role='assistant',
                    content=full_response,
                    meta_data={'thinking_content': full_thinking} if full_thinking else {}
                )
                db.session.add(ai_message)

                # Update state if transition should occur
                if should_transition:
                    new_state = state_machine.next_state(current_state)
                    conversation.state = new_state
                    print(f"State transition: {current_state} -> {new_state}")

                    # Emit state change event
                    socketio.emit('state_changed', {
                        'old_state': current_state,
                        'new_state': new_state,
                        'requirements': conversation.requirements
                    }, room=conversation_id)

                db.session.commit()

                # Emit AI response to room
                socketio.emit('message_received', ai_message.to_dict(), room=conversation_id)

            except Exception as e:
                print(f"Error generating AI response: {e}")
                import traceback
                traceback.print_exc()
                err_text = str(e)

                # 即使流式出错，也保存已收集到的部分响应
                if full_response.strip():
                    try:
                        partial_message = Message(
                            conversation_id=conversation_id,
                            role='assistant',
                            content=full_response,
                            meta_data={'thinking_content': full_thinking, 'partial': True} if full_thinking else {'partial': True}
                        )
                        db.session.add(partial_message)
                        db.session.commit()
                        socketio.emit('message_received', partial_message.to_dict(), room=conversation_id)
                        print(f"[AI] 流式出错但已保存部分响应 ({len(full_response)} chars)")
                    except Exception as save_err:
                        print(f"[AI] 保存部分响应也失败: {save_err}")

                if ('Timeout' in err_text) or ('timed out' in err_text) or ('ReadTimeout' in err_text):
                    emit('error', {'message': 'AI响应超时，请重试或把问题拆分得更短一些。'})
                else:
                    emit('error', {'message': f'AI响应生成失败: {err_text}'})

        except Exception as e:
            print(f"Error handling message: {e}")
            emit('error', {'message': f'消息处理失败: {str(e)}'})

    @socketio.on('generate_outline')
    def handle_generate_outline(data):
        """Generate PPT outline"""
        conversation_id = data.get('conversation_id')
        user_id = data.get('user_id')
        topic = data.get('topic')
        requirements = data.get('requirements', {})

        missing_params = []
        if not conversation_id:
            missing_params.append('conversation_id')
        if not user_id:
            missing_params.append('user_id')
        if not topic:
            missing_params.append('topic')

        if missing_params:
            emit('error', {'message': f'缺少必要参数: {", ".join(missing_params)}'})
            return

        try:
            # 使用 GLM 生成大纲
            # 优先根据最近对话重新提取主题，避免沿用历史脏topic
            try:
                conversation = Conversation.query.filter_by(id=conversation_id, user_id=user_id).first()
                if conversation:
                    all_messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at).all()
            except Exception as e:
                print(f"[OUTLINE_EVENT] 读取历史消息失败: {e}")

            # 发送开始生成事件
            socketio.emit('outline_generation_start', {
                'conversation_id': conversation_id
            }, room=conversation_id)

            import uuid
            request_id = str(uuid.uuid4())[:8]
            outline_start_ts = time.perf_counter()
            print(f"[OUTLINE_EVENT][{request_id}] 开始生成, conversation_id={conversation_id}, topic={topic}")

            # 发送进度：25%
            socketio.emit('outline_generation_progress', {
                'progress': 25,
                'message': '正在整理对话上下文（不再执行RAG检索）...'
            }, room=conversation_id)

            # 发送进度：35%
            socketio.emit('outline_generation_progress', {
                'progress': 35,
                'message': '正在整理需求与上下文...'
            }, room=conversation_id)

            # 发送进度：45%
            socketio.emit('outline_generation_progress', {
                'progress': 45,
                'message': f'正在调用模型生成结构化大纲（req={request_id}）...'
            }, room=conversation_id)

            # Generate outline（显式传入当前会话上下文）
            conversation = Conversation.query.filter_by(id=conversation_id, user_id=user_id).first()
            conversation_history = []
            if conversation:
                all_messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at).all()
                conversation_history = [
                    {'role': m.role, 'content': m.content}
                    for m in all_messages
                    if m.role in ('user', 'assistant') and (m.content or '').strip()
                ]

            llm_start_ts = time.perf_counter()
            result = glm_service.generate_ppt_outline(
                topic=topic,
                requirements=requirements,
                context_documents=[],
                conversation_history=conversation_history
            )
            llm_elapsed = time.perf_counter() - llm_start_ts
            print(f"[OUTLINE_EVENT][{request_id}] LLM生成完成, elapsed={llm_elapsed:.2f}s, history_len={len(conversation_history)}")

            # 发送进度：75%
            socketio.emit('outline_generation_progress', {
                'progress': 75,
                'message': '正在生成思维导图...'
            }, room=conversation_id)

            # Extract outline and mindmap from result
            if 'outline' in result:
                outline = result['outline']
                outline['title'] = result.get('title', topic)
            else:
                # Fallback: use full result as outline
                outline = result

            mindmap = result.get('mindmap', '')

            total_elapsed = time.perf_counter() - outline_start_ts
            print(f"[OUTLINE_EVENT][{request_id}] 大纲任务完成, total_elapsed={total_elapsed:.2f}s")

            # 发送进度：100%
            socketio.emit('outline_generation_progress', {
                'progress': 100,
                'message': f'大纲生成完成！总耗时 {total_elapsed:.1f}s'
            }, room=conversation_id)

            # Save outline and mindmap in message metadata
            outline_message = Message(
                conversation_id=conversation_id,
                role='assistant',
                content=f"已生成PPT大纲：{result.get('title', topic)}",
                meta_data={
                    'outline': outline,
                    'mindmap': mindmap,
                    'type': 'outline'
                }
            )
            db.session.add(outline_message)
            db.session.commit()

            # Emit outline and mindmap to room
            socketio.emit('outline_generated', {
                'outline': outline,
                'mindmap': mindmap,
                'message': outline_message.to_dict()
            }, room=conversation_id)

        except Exception as e:
            print(f"Error generating outline: {e}")
            socketio.emit('outline_generation_progress', {
                'progress': 0,
                'message': f'大纲生成失败: {str(e)}'
            }, room=conversation_id)
            emit('error', {'message': f'大纲生成失败: {str(e)}'})

    @socketio.on('generate_ppt')
    def handle_generate_ppt(data):
        """生成PPT内容"""
        conversation_id = data.get('conversation_id')
        user_id = data.get('user_id')
        outline = data.get('outline')  # 可选，如果没有大纲则从对话历史生成
        requirements = data.get('requirements', {})
        theme = data.get('theme', 'modern')
        template_id = data.get('template_id', None)  # 可选，使用模板

        missing_params = []
        if not conversation_id:
            missing_params.append('conversation_id')
        if not user_id:
            missing_params.append('user_id')

        if missing_params:
            emit('error', {'message': f'缺少必要参数: {", ".join(missing_params)}'})
            return

        try:
            # 获取对话
            conversation = Conversation.query.filter_by(
                id=conversation_id,
                user_id=user_id
            ).first()

            if not conversation:
                emit('error', {'message': '对话不存在'})
                return

            # 发送开始生成事件
            socketio.emit('ppt_generation_start', {
                'conversation_id': conversation_id
            }, room=conversation_id)

            # 发送进度：10%
            socketio.emit('ppt_generation_progress', {
                'progress': 10,
                'message': '正在分析对话内容...'
            }, room=conversation_id)

            # 如果没有大纲，从对话历史生成
            if not outline:
                # 发送进度：30%
                socketio.emit('ppt_generation_progress', {
                    'progress': 30,
                    'message': '正在生成PPT大纲...'
                }, room=conversation_id)

                # 使用GLM生成大纲
                topic = conversation.requirements.get('topic', '主题演示')

                # 检索相关文档
                context_documents = []
                try:
                    query_embedding = embeddings.generate_embedding(topic)
                    search_results = rag_service.search_documents(
                        query_text=topic,
                        query_embedding=query_embedding,
                        n_results=5,
                        filter_metadata={'user_id': user_id}
                    )
                    context_documents = search_results['documents']
                except Exception as e:
                    print(f"Error retrieving context for outline: {e}")

                outline_result = glm_service.generate_ppt_outline(
                    topic=topic,
                    requirements=requirements,
                    context_documents=context_documents
                )

                # 构建大纲
                if 'outline' in outline_result:
                    outline = outline_result['outline']
                    outline['title'] = outline_result.get('title', topic)
                else:
                    outline = outline_result

            # 获取主题
            topic = outline.get('title', conversation.requirements.get('topic', 'PPT'))

            # 调试模式：模拟完整生成流程，但不真正生成PPT
            if ENABLE_MOCK_PPT_GENERATION:
                print(f"[PPT_MOCK] 调试模式启用，开始模拟PPT生成流程, conversation_id={conversation_id}, topic={topic}")

                mock_steps = [
                    (50, '正在检索相关资料...', 0.15),
                    (62, '正在整理对话上下文...', 0.15),
                    (74, '正在匹配模板与版式...', 0.15),
                    (84, '正在生成页面内容...', 0.2),
                    (90, '正在保存PPT...', 0.15),
                    (97, '正在生成预览索引...', 0.1),
                ]

                for progress, message_text, delay in mock_steps:
                    print(f"[PPT_MOCK] progress={progress}, message={message_text}")
                    socketio.emit('ppt_generation_progress', {
                        'progress': progress,
                        'message': message_text
                    }, room=conversation_id)
                    time.sleep(delay)

                # 按模板来源映射固定输出文件：内置->A.ppt，上传->B.ppt，空白->C.ppt
                if template_id and str(template_id).startswith('builtin_'):
                    mock_template_type = 'builtin'
                elif template_id and str(template_id) != 'blank':
                    mock_template_type = 'uploaded'
                else:
                    mock_template_type = 'blank'

                backend_dir = os.path.abspath(os.path.join(current_app.root_path, '..'))
                target_file_name = MOCK_PPT_FILE_MAP.get(mock_template_type, 'C.ppt')
                target_file_path = os.path.join(backend_dir, 'ppt', target_file_name)
                os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

                # 仅创建占位文件，确保路径可用（不执行真实PPT生成）
                if not os.path.exists(target_file_path):
                    with open(target_file_path, 'wb') as f:
                        f.write(b'')

                # 保存到数据库
                ppt = PPT(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    title=topic,
                    theme=theme,
                    outline=outline,
                    slides_data=[],
                    template_id=template_id,
                    status='ready',
                    file_path=target_file_path
                )
                db.session.add(ppt)
                db.session.commit()

                print(f"[PPT_MOCK] 模拟完成，输出路径: {target_file_path}, ppt_id={ppt.id}")

                socketio.emit('ppt_generation_progress', {
                    'progress': 100,
                    'message': 'PPT生成完成！'
                }, room=conversation_id)

                socketio.emit('ppt_generated', {
                    'ppt': ppt.to_dict()
                }, room=conversation_id)

                message = Message(
                    conversation_id=conversation_id,
                    role='assistant',
                    content=f'已生成PPT：{ppt.title}',
                    meta_data={
                        'type': 'ppt',
                        'ppt_id': ppt.id,
                        'mock_generation': True
                    }
                )
                db.session.add(message)
                db.session.commit()

                socketio.emit('message_received', message.to_dict(), room=conversation_id)
                return

            # 发送进度：50%
            socketio.emit('ppt_generation_progress', {
                'progress': 50,
                'message': '正在检索相关资料...'
            }, room=conversation_id)

            # 检索相关文档
            context_documents = []
            try:
                query_embedding = embeddings.generate_embedding(topic)
                search_results = rag_service.search_documents(
                    query_text=topic,
                    query_embedding=query_embedding,
                    n_results=5,
                    filter_metadata={'user_id': user_id}
                )
                context_documents = search_results['documents']
            except Exception as e:
                print(f"Error retrieving context for PPT: {e}")

            # 获取对话历史中的 AI 内容（用于参考）
            conversation_messages = Message.query.filter_by(
                conversation_id=conversation_id
            ).order_by(Message.created_at).all()

            # 提取 AI 生成的文字内容（排除系统消息和大纲消息）
            ai_content_history = []
            for msg in conversation_messages:
                if msg.role == 'assistant':
                    meta = msg.meta_data or {}
                    # 跳过欢迎消息、大纲消息、PPT消息
                    if not meta.get('is_welcome') and meta.get('type') not in ['outline', 'ppt']:
                        ai_content_history.append(msg.content)

            # 使用OfficeCLI MCP服务生成PPT
            officecli_service = get_officecli_mcp_service()
            image_service = get_image_service()
            
            # 设置进度回调
            def progress_callback(progress_info):
                socketio.emit('ppt_generation_progress', {
                    'progress': progress_info['progress'],
                    'message': progress_info['message'],
                    'slide_number': progress_info.get('slide_number'),
                    'slide_data': progress_info.get('slide_data')
                }, room=conversation_id)
            
            # 生成文件路径
            os.makedirs(current_app.config['GENERATED_PPTS_DIR'], exist_ok=True)
            safe_title = ''.join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
            import uuid
            file_path = os.path.join(current_app.config['GENERATED_PPTS_DIR'], f"{safe_title or 'ppt'}_{uuid.uuid4().hex[:8]}.pptx")
            
            # 准备完整的对话内容和参考资料（不再截断）
            full_dialogue = ''
            full_context = ''
            ai_outline_text = ''
            
            # 获取完整的对话历史（不截断）
            if conversation_messages:
                dialogue_parts = []
                for m in conversation_messages:
                    content = (m.content or '').strip()
                    if content:
                        # 获取AI生成的文字大纲（最后一条包含大纲的AI消息）
                        if m.role == 'assistant':
                            meta = m.meta_data or {}
                            if meta.get('type') == 'outline' and meta.get('outline'):
                                # 提取大纲的完整文字内容
                                outline_data = meta.get('outline', {})
                                slides = outline_data.get('slides', [])
                                for slide in slides:
                                    slide_title = slide.get('title', '')
                                    content_points = slide.get('content_points', [])
                                    ai_outline_text += f"第{slide.get('slide_number', 0)}页：{slide_title}\n"
                                    for point in content_points:
                                        ai_outline_text += f"  - {point}\n"
                                    ai_outline_text += "\n"
                        dialogue_parts.append(f"{m.role}: {content}")
                full_dialogue = "\n\n".join(dialogue_parts)
            
            # 如果没有从meta_data中找到大纲，尝试从消息内容中提取
            if not ai_outline_text:
                for m in reversed(conversation_messages):
                    if m.role == 'assistant':
                        content = (m.content or '').strip()
                        # 查找包含大纲内容的消息
                        if '大纲' in content or '第1页' in content or 'Slide 1' in content.lower():
                            ai_outline_text = content
                            break
            
            # 获取完整的参考资料（增加截取长度）
            if context_documents:
                full_context = "\n\n".join([
                    f"参考资料 {i+1}:\n{doc or ''}"
                    for i, doc in enumerate(context_documents[:5])  # 增加到5个文档
                ])
            
            # 获取模板信息
            template_type = 'blank'
            template_path = None
            template_styles = None
            builtin_template_id = None
            
            print(f"[PPT_GEN] template_id = {template_id}")
            
            if template_id:
                if template_id.startswith('builtin_'):
                    # 内置模板：使用模板化脚本生成
                    builtin_template_id = template_id
                    template_type = 'builtin'
                    print(f"[PPT_GEN] ✓ 内置模板: {builtin_template_id}")
                else:
                    # 用户上传模板：使用模板文件
                    from app.models.template import Template
                    template = Template.query.get(template_id)
                    if template:
                        print(f"[PPT_GEN] 找到模板: id={template.id}, name={template.name}, file_path={template.file_path}")
                        if template.file_path and os.path.exists(template.file_path):
                            template_type = 'uploaded'
                            template_path = template.file_path
                            template_styles = template.styles or {}
                            print(f"[PPT_GEN] ✓ 模板文件存在，将使用模板生成")
                        else:
                            print(f"[PPT_GEN] ✗ 模板文件不存在: {template.file_path}")
                    else:
                        print(f"[PPT_GEN] ✗ 未找到模板: template_id={template_id}")
            else:
                print(f"[PPT_GEN] 未指定模板")
            
            # 使用OfficeCLI生成PPT
            print(f"[PPT_GEN] 调用generate_ppt_from_outline: template_type={template_type}")
            
            ppt_result = officecli_service.generate_ppt_from_outline(
                output_path=file_path,
                title=topic,
                outline=outline,
                requirements=requirements,
                image_service=image_service,
                progress_callback=progress_callback,
                template_type=template_type,
                template_path=template_path,
                template_styles=template_styles,
                builtin_template_id=builtin_template_id,
                compact_dialogue=full_dialogue,
                compact_context=full_context
            )

            if not ppt_result.get('success'):
                raise RuntimeError(ppt_result.get('error', 'PPT生成失败'))

            # 发送进度：90%
            socketio.emit('ppt_generation_progress', {
                'progress': 90,
                'message': '正在保存PPT...'
            }, room=conversation_id)

            # 获取模板信息（如果提供）
            from app.models.template import Template
            template = None
            if template_id and not template_id.startswith('builtin_'):
                template = Template.query.get(template_id)
                if template:
                    # 增加模板使用次数
                    template.usage_count += 1
            
            # 保存到数据库
            ppt = PPT(
                conversation_id=conversation_id,
                user_id=user_id,
                title=topic,  # 使用topic而不是ppt_data.get('title')
                theme=theme,
                outline=outline,
                slides_data=[],  # 暂时为空，后续会填充
                template_id=template_id,
                status='ready',
                file_path=file_path  # 保存生成的文件路径
            )
            db.session.add(ppt)
            db.session.commit()

            # 生成并保存PPTX文件（供WOPI使用）
            def _download_image(url: str):
                try:
                    response = requests.get(url, timeout=12)
                    response.raise_for_status()
                    content_type = response.headers.get('Content-Type', '')
                    ext = mimetypes.guess_extension(content_type.split(';')[0].strip()) or '.jpg'

                    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                        tmp.write(response.content)
                        return tmp.name
                except Exception as e:
                    print(f"[PPTX] 下载图片失败: {e}")
                    return None

            try:
                os.makedirs(current_app.config['GENERATED_PPTS_DIR'], exist_ok=True)
                safe_title = ''.join(c for c in (ppt.title or 'ppt') if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
                filename = f"{safe_title or 'ppt'}_{ppt.id}.pptx"
                file_path = os.path.join(current_app.config['GENERATED_PPTS_DIR'], filename)

                temp_images = []

                if template and template.file_path and os.path.exists(template.file_path):
                    current_app.logger.info(f"[PPT_GEN] 使用模板生成: template_id={template.id}, name={template.name}, ppt_id={ppt.id}")
                    prs = Presentation(template.file_path)

                    outline_slides = outline.get('slides', [])
                    outline_positions = [str((s or {}).get('position', 'content')).strip().lower() for s in outline_slides]

                    # 目录内容优先取 section/content 页标题，避免把封面/结束页塞进目录
                    toc_source_indices = [
                        i for i, p in enumerate(outline_positions)
                        if p in ('section', 'content')
                    ]
                    if not toc_source_indices:
                        toc_source_indices = [
                            i for i, p in enumerate(outline_positions)
                            if p not in ('cover', 'toc', 'ending')
                        ]
                    toc_titles = [outline_slides[i].get('title', '') for i in toc_source_indices if 0 <= i < len(outline_slides)]
                    toc_titles = [t for t in toc_titles if t]
                    if not toc_titles:
                        toc_titles = [topic]
                    if len(toc_titles) < 6:
                        for idx in range(len(toc_titles), 6):
                            toc_titles.append(f'第{idx + 1}部分')

                    socketio.emit('ppt_generation_progress', {
                        'progress': 91,
                        'message': '正在应用模板与占位符...'
                    }, room=conversation_id)

                    placeholder_map = {
                        '{{title}}': topic,
                        '{{subtitle}}': f"{requirements.get('audience', '')} | {requirements.get('purpose', '')}",
                        '{{footer}}': topic,
                        '{{date}}': datetime.utcnow().strftime('%Y-%m-%d')
                    }

                    # 先抽取模板占位符，再让LLM生成“按占位符适配”的内容
                    placeholders_by_slide = []
                    for s_idx, s in enumerate(prs.slides):
                        phs = set()
                        for shp in s.shapes:
                            if shp.has_text_frame and (shp.text or '').strip():
                                for m in re.findall(r"\{\{[^}]+\}\}", shp.text):
                                    phs.add(m)
                        placeholders_by_slide.append({'slide_index': s_idx, 'placeholders': sorted(list(phs))})

                    adapted = glm_service.adapt_content_to_template_placeholders(
                        topic=topic,
                        outline=outline,
                        requirements=requirements,
                        conversation_history=ai_content_history,
                        placeholders_by_slide=placeholders_by_slide,
                        template_info=(template.template_info or {}) if template else {}
                    )
                    adapted_map = {}
                    adapted_type_map = {}
                    for item in (adapted.get('slides') or []):
                        try:
                            s_idx = int(item.get('slide_index'))
                            adapted_map[s_idx] = item.get('values') or {}
                            adapted_type_map[s_idx] = (item.get('chosen_slide_type') or '').strip().lower()
                        except Exception:
                            continue

                    image_service = None

                    def _download_image(url: str):
                        try:
                            response = requests.get(url, timeout=12)
                            response.raise_for_status()
                            content_type = response.headers.get('Content-Type', '')
                            ext = mimetypes.guess_extension(content_type.split(';')[0].strip()) or '.jpg'

                            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                                tmp.write(response.content)
                                return tmp.name
                        except Exception as e:
                            print(f"[PPTX] 下载图片失败: {e}")
                            return None

                    def _clamp(s: str, n: int):
                        return (s or '')[:n]

                    def _compact_multiline_text(raw: str, max_lines: int = 4, max_chars_per_line: int = 22):
                        lines = []
                        for ln in str(raw or '').split('\n'):
                            t = (ln or '').strip()
                            if not t:
                                continue
                            t = t.replace('•', '').strip()
                            if len(t) > max_chars_per_line:
                                t = t[:max_chars_per_line - 1] + '…'
                            lines.append(t)
                        lines = lines[:max_lines]
                        return '\n'.join([f"• {ln}" for ln in lines])

                    def _get_text_for_key(key: str, outline_idx: int, slide_index: int):
                        # LLM适配优先（兼容大小写/空格）
                        normalized_key = '{{' + key.replace('{', '').replace('}', '').strip().lower() + '}}'
                        values = adapted_map.get(slide_index, {}) or {}
                        slide_type_hint = adapted_type_map.get(slide_index, '')
                        v = values.get(key)
                        if v is None:
                            v = values.get(normalized_key)
                        if v is not None and str(v).strip() != '':
                            if normalized_key == '{{title}}':
                                return _clamp(str(v), 28)
                            if normalized_key == '{{subtitle}}':
                                return _clamp(str(v), 36)
                            if normalized_key in ('{{text}}', '{{description}}', '{{discrimination}}'):
                                return _compact_multiline_text(str(v), max_lines=4, max_chars_per_line=22)
                            return str(v)

                        if slide_type_hint == 'toc' and normalized_key.startswith('{{toc_'):
                            idx_str = normalized_key.replace('{{toc_', '').replace('}}', '').strip()
                            try:
                                toc_index = int(idx_str) - 1
                            except ValueError:
                                toc_index = -1
                            return toc_titles[toc_index] if 0 <= toc_index < len(toc_titles) else ''

                        if normalized_key == '{{page_number}}':
                            return str(slide_index + 1)
                        if normalized_key == '{{toc_title}}':
                            return '目录'
                        if normalized_key.startswith('{{toc_'):
                            idx_str = normalized_key.replace('{{toc_', '').replace('}}', '').strip()
                            try:
                                toc_index = int(idx_str) - 1
                            except ValueError:
                                toc_index = -1
                            return toc_titles[toc_index] if 0 <= toc_index < len(toc_titles) else ''
                        if normalized_key == '{{text}}':
                            if outline_idx is None:
                                return ''
                            if 0 <= outline_idx < len(outline_slides):
                                points = outline_slides[outline_idx].get('content_points', [])
                                txt = '\n'.join([str(p) for p in points])
                                return _compact_multiline_text(txt, max_lines=4, max_chars_per_line=22)
                            return ''
                        if normalized_key in ('{{description}}', '{{discrimination}}'):
                            if outline_idx is None:
                                return ''
                            if 0 <= outline_idx < len(outline_slides):
                                points = outline_slides[outline_idx].get('content_points', [])
                                return _clamp(points[0] if points else '', 28)
                            return ''
                        if normalized_key == '{{title}}':
                            if outline_idx is None:
                                return _clamp(topic, 28)
                            if 0 <= outline_idx < len(outline_slides):
                                return _clamp(outline_slides[outline_idx].get('title', ''), 28)
                            return _clamp(topic, 28)
                        if normalized_key == '{{subtitle}}':
                            return _clamp(placeholder_map.get('{{subtitle}}', ''), 36)
                        if normalized_key == '{{image_caption}}':
                            if outline_idx is None:
                                return ''
                            return _clamp(outline_slides[outline_idx].get('title', ''), 24)
                        if normalized_key == '{{table_caption}}':
                            if outline_idx is None:
                                return ''
                            return _clamp(outline_slides[outline_idx].get('title', ''), 24)
                        if normalized_key in ('{{table}}', '{{chart}}', '{{diagram}}'):
                            return ''
                        return placeholder_map.get(normalized_key, '')

                    def _replace_text_keep_style(shape, outline_idx: int, slide_index: int):
                        if not shape.has_text_frame:
                            return
                        for paragraph in shape.text_frame.paragraphs:
                            if not paragraph.runs:
                                continue
                            full_text = ''.join(run.text for run in paragraph.runs)
                            if '{{' not in full_text:
                                continue

                            def _replace_match(match):
                                key = match.group(0)
                                return _get_text_for_key(key, outline_idx, slide_index)

                            full_text = re.sub(r"\{\{[^}]+\}\}", _replace_match, full_text)

                            paragraph.runs[0].text = full_text
                            for run in paragraph.runs[1:]:
                                run.text = ''

                            try:
                                shape.name = f"__placeholder_text__{shape.name}"
                            except Exception:
                                pass

                    def _iter_shapes_recursive(shapes):
                        for shp in shapes:
                            yield shp
                            if getattr(shp, 'shape_type', None) == 6:  # MSO_SHAPE_TYPE.GROUP
                                try:
                                    for child in _iter_shapes_recursive(shp.shapes):
                                        yield child
                                except Exception:
                                    continue

                    def _slide_has_placeholder(slide, placeholder: str) -> bool:
                        for shape in _iter_shapes_recursive(slide.shapes):
                            try:
                                if shape.has_text_frame and placeholder in (shape.text or ''):
                                    return True
                            except Exception:
                                continue
                        return False

                    def _duplicate_slide(prs_obj, template_slide):
                        import copy
                        new_slide = prs_obj.slides.add_slide(template_slide.slide_layout)
                        for shape in list(new_slide.shapes):
                            sp = shape._element
                            sp.getparent().remove(sp)
                        for shape in template_slide.shapes:
                            new_slide.shapes._spTree.insert_element_before(copy.deepcopy(shape._element), 'p:extLst')
                        return new_slide

                    # 动态分配页面：按“大纲页定位(position)”映射模板页，非强制使用所有模板页
                    title_index = 0
                    toc_index = None
                    for idx, s in enumerate(prs.slides):
                        if _slide_has_placeholder(s, '{{toc_title}}') or _slide_has_placeholder(s, '{{toc_1}}'):
                            toc_index = idx
                            break

                    # 结尾页优先按占位符识别，而不是“最后一页”
                    end_candidates = []
                    for idx, s in enumerate(prs.slides):
                        if idx == title_index or (toc_index is not None and idx == toc_index):
                            continue
                        if _slide_has_placeholder(s, '{{footer}}') or _slide_has_placeholder(s, '{{date}}'):
                            end_candidates.append(idx)
                    end_index = end_candidates[-1] if end_candidates else None

                    # 根据大纲定位，决定是否需要目录页/结尾页（由LLM在大纲阶段输出position）
                    has_toc_in_outline = any(p == 'toc' for p in outline_positions)
                    has_ending_in_outline = any(p == 'ending' for p in outline_positions)

                    # 内容页池（除封面/目录/结尾外）
                    all_content_indices = [
                        i for i in range(len(prs.slides))
                        if i != title_index
                        and (toc_index is None or i != toc_index)
                        and (end_index is None or i != end_index)
                    ]

                    # 如果大纲有结束页但模板没识别到结束页，避免最后一个内容页被错误当正文
                    if has_ending_in_outline and end_index is None and all_content_indices:
                        end_index = all_content_indices[-1]
                        all_content_indices = all_content_indices[:-1]

                    # 需要落到内容池的大纲页（不含toc/ending）
                    non_special_outline_indices = [
                        i for i, p in enumerate(outline_positions)
                        if p not in ('toc', 'ending')
                    ]

                    # 内容页不足：复制最后一个内容模板页补齐
                    needed_content_count = len(non_special_outline_indices)
                    current_content_count = len(all_content_indices)
                    if needed_content_count > current_content_count and current_content_count > 0:
                        need_add = needed_content_count - current_content_count
                        source_idx = all_content_indices[-1]
                        source_slide = prs.slides[source_idx]
                        for _ in range(need_add):
                            _duplicate_slide(prs, source_slide)

                        # 复制后重算内容池
                        all_content_indices = [
                            i for i in range(len(prs.slides))
                            if i != title_index
                            and (toc_index is None or i != toc_index)
                            and (end_index is None or i != end_index)
                        ]

                    # 为普通内容页建立映射：模板页索引 -> 大纲页索引
                    outline_map_by_slide = {}
                    content_cursor = 0
                    for slide_idx in all_content_indices:
                        if content_cursor >= len(non_special_outline_indices):
                            break
                        outline_map_by_slide[slide_idx] = non_special_outline_indices[content_cursor]
                        content_cursor += 1

                    # 目录页与结尾页映射（按需启用，不强制）
                    toc_outline_index = next((i for i, p in enumerate(outline_positions) if p == 'toc'), None)
                    ending_outline_index = next((i for i, p in enumerate(outline_positions) if p == 'ending'), None)

                    # 文本占位符替换
                    current_app.logger.info(f"[PPT_GEN] 开始替换文本占位符: total_slides={len(prs.slides)}, outline_slides={len(outline_slides)}")
                    for slide_index, slide in enumerate(prs.slides):
                        if slide_index == title_index:
                            outline_idx = None
                            socketio.emit('ppt_generation_progress', {
                                'progress': 92,
                                'message': '正在生成封面图...'
                            }, room=conversation_id)
                        elif toc_index is not None and slide_index == toc_index:
                            # 仅当大纲存在toc定位时，才把目录页作为目录页填充
                            outline_idx = toc_outline_index if has_toc_in_outline else None
                        elif end_index is not None and slide_index == end_index:
                            # 仅当大纲存在ending定位时，才把结尾页作为结尾页填充
                            outline_idx = ending_outline_index if has_ending_in_outline else None
                        else:
                            outline_idx = outline_map_by_slide.get(slide_index)

                        # 保护：内容页不要映射到ending页，避免中间页变成结束页内容
                        if outline_idx is not None:
                            pos = str((outline_slides[outline_idx] or {}).get('position', 'content')).strip().lower()
                            if pos == 'ending' and not (end_index is not None and slide_index == end_index):
                                outline_idx = None

                        for shape in _iter_shapes_recursive(slide.shapes):
                            _replace_text_keep_style(shape, outline_idx, slide_index)

                        if outline_idx is not None:
                            socketio.emit('ppt_generation_progress', {
                                'progress': 93,
                                'message': f'正在生成第{outline_idx + 2}页配图...'
                            }, room=conversation_id)
                            current_app.logger.info(f"[PPT_GEN] 图片阶段: 正在处理第{outline_idx + 2}页配图")

                        # 图片占位符替换（AI生成图片）
                        for shape in slide.shapes:
                            try:
                                alt_text = getattr(shape, 'alternative_text', '')
                            except Exception:
                                alt_text = ''
                            if '{{image}}' not in (alt_text or ''):
                                continue

                            try:
                                if image_service is None:
                                    image_service = get_image_service()

                                # 生成更贴合页面的提示词
                                if outline_idx is not None and 0 <= outline_idx < len(outline_slides):
                                    slide_title = outline_slides[outline_idx].get('title', '')
                                    points = outline_slides[outline_idx].get('content_points', []) or []
                                    point_text = '，'.join([str(p) for p in points[:3]])
                                    image_query = f"{topic} {slide_title} {point_text}".strip()
                                else:
                                    image_query = topic

                                image_urls = image_service.search_images(image_query, num_images=1)
                                image_url = image_urls[0] if image_urls else None

                                local_image = _download_image(image_url) if image_url else None

                                left = shape.left
                                top = shape.top
                                width = shape.width
                                height = shape.height

                                inserted = False
                                if local_image and os.path.exists(local_image):
                                    try:
                                        slide.shapes.add_picture(local_image, left, top, width, height)
                                        temp_images.append(local_image)
                                        inserted = True
                                        current_app.logger.info(f"[PPT_GEN] 第{slide_index + 1}页插图成功: {image_query}")
                                    except Exception as pic_err:
                                        current_app.logger.warning(f"[PPT_GEN] 第{slide_index + 1}页插图失败: {pic_err}")

                                if not inserted:
                                    # 回退：仍保留可见占位图，避免空白
                                    from pptx.enum.shapes import MSO_SHAPE
                                    from pptx.dml.color import RGBColor as _RGB
                                    placeholder = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
                                    placeholder.fill.solid()
                                    placeholder.fill.fore_color.rgb = _RGB(220, 220, 220)
                                    placeholder.line.color.rgb = _RGB(200, 200, 200)
                                    try:
                                        placeholder.name = f"__placeholder_image__{shape.name}"
                                    except Exception:
                                        pass

                                try:
                                    sp = shape._element
                                    sp.getparent().remove(sp)
                                except Exception:
                                    pass
                            except Exception as e:
                                print(f"[PPTX] 图片占位符替换失败: {e}")

                    def _auto_adjust_text_boxes(prs_obj):
                        from pptx.util import Pt as _Pt
                        for slide in prs_obj.slides:
                            for shape in slide.shapes:
                                if not shape.has_text_frame:
                                    continue
                                try:
                                    name = shape.name or ''
                                except Exception:
                                    name = ''
                                if '__placeholder_text__' not in name:
                                    continue

                                text = shape.text or ''
                                if not text.strip():
                                    continue

                                # 简单估算：面积越小、字越多则缩小字号
                                box_area = max(1, (shape.width / 914400) * (shape.height / 914400))
                                char_count = len(text)
                                if char_count == 0:
                                    continue

                                # 经验系数：每平方英寸约容纳 40 字符（含换行）
                                capacity = box_area * 40

                                # 仅在内容溢出时缩小字体，避免“内容少反而被放大”
                                if char_count > capacity:
                                    scale = max(0.65, capacity / char_count)
                                else:
                                    continue

                                for paragraph in shape.text_frame.paragraphs:
                                    for run in paragraph.runs:
                                        if run.font.size:
                                            new_size = int(run.font.size.pt * scale)
                                            # 保留一个合理区间，避免过小或过大
                                            new_size = max(12, min(new_size, int(run.font.size.pt)))
                                            run.font.size = _Pt(new_size)

                    _auto_adjust_text_boxes(prs)
                    socketio.emit('ppt_generation_progress', {
                        'progress': 95,
                        'message': '正在智能调整字体与排版...'
                    }, room=conversation_id)
                    current_app.logger.info("[PPT_GEN] 字体与排版自适应完成")

                else:
                    # 无模板时，使用OfficeCLI已生成的PPT文件
                    prs = Presentation(file_path)
                    current_app.logger.info(f"[PPT_GEN] 使用OfficeCLI生成的PPT: {file_path}")

                socketio.emit('ppt_generation_progress', {
                    'progress': 97,
                    'message': '正在保存PPT文件...'
                }, room=conversation_id)
                current_app.logger.info(f"[PPT_GEN] 正在保存PPT: {file_path}")
                prs.save(file_path)

                # 视觉审查与编排（基于Collabora导出PNG）
                try:
                    from app.services.collabora_converter import convert_pptx_to_pngs
                    from app.services.vision_service import vision_service

                    rendered_dir = os.path.join(current_app.root_path, 'tmp', 'rendered', str(ppt.id))
                    os.makedirs(rendered_dir, exist_ok=True)

                    # 最多两轮审查-修正
                    for review_round in range(2):
                        png_paths = convert_pptx_to_pngs(file_path, rendered_dir)
                        if not png_paths:
                            print("[VISION] Collabora 未返回PNG，跳过视觉审查")
                            break

                        print(f"[VISION] 导出 {len(png_paths)} 张图片用于审查，第{review_round + 1}轮")
                        any_fix = False

                        for idx, png_path in enumerate(sorted(png_paths)):
                            try:
                                issues = vision_service.analyze_page_issues(png_path, idx)
                                if issues and issues.get('has_issues'):
                                    scale = issues.get('text_scale', 1.0)
                                    line_spacing = issues.get('line_spacing', 1.2)
                                    if scale != 1.0:
                                        any_fix = True
                                        slide = prs.slides[idx]
                                        for shape in slide.shapes:
                                            if not shape.has_text_frame:
                                                continue
                                            try:
                                                name = shape.name or ''
                                            except Exception:
                                                name = ''
                                            if '__placeholder_text__' not in name:
                                                continue

                                            for paragraph in shape.text_frame.paragraphs:
                                                paragraph.line_spacing = line_spacing
                                                for run in paragraph.runs:
                                                    if run.font.size:
                                                        new_size = int(run.font.size.pt * scale)
                                                        run.font.size = Pt(new_size)
                            except Exception as ve:
                                print(f"[VISION] 审查失败: {ve}")

                        if not any_fix:
                            break

                        # 重新保存后进入下一轮
                        prs.save(file_path)

                    # 保留渲染图片供人工检查（不删除）
                    print(f"[VISION] 渲染图片保留在: {rendered_dir}")
                except Exception as e:
                    print(f"[VISION] 视觉审查流程失败: {e}")

                ppt.file_path = file_path
                db.session.commit()

                for tmp_path in temp_images:
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass
            except Exception as e:
                print(f"[WOPI] 生成PPTX失败: {e}")

            # 发送进度：100%
            socketio.emit('ppt_generation_progress', {
                'progress': 100,
                'message': 'PPT生成完成！'
            }, room=conversation_id)

            # 发送生成完成事件
            ppt_data = ppt.to_dict()
            # 如果有页面状态信息，添加到响应中
            if 'page_status' in ppt_result:
                ppt_data['page_status'] = ppt_result['page_status']
            
            socketio.emit('ppt_generated', {
                'ppt': ppt_data
            }, room=conversation_id)

            # 添加消息记录
            message = Message(
                conversation_id=conversation_id,
                role='assistant',
                content=f'已生成PPT：{ppt.title}',
                meta_data={
                    'type': 'ppt',
                    'ppt_id': ppt.id
                }
            )
            db.session.add(message)
            db.session.commit()

            socketio.emit('message_received', message.to_dict(), room=conversation_id)

        except Exception as e:
            print(f"Error generating PPT: {e}")
            import traceback
            traceback.print_exc()
            emit('error', {'message': f'PPT生成失败: {str(e)}'})
            socketio.emit('ppt_generation_progress', {
                'progress': 0,
                'message': f'生成失败: {str(e)}'
            }, room=conversation_id)

    @socketio.on('update_slide')
    def handle_update_slide(data):
        """更新单页幻灯片"""
        ppt_id = data.get('ppt_id')
        slide_number = data.get('slide_number')
        updates = data.get('updates')

        if not all([ppt_id, slide_number is not None, updates]):
            emit('error', {'message': '缺少必要参数'})
            return

        try:
            ppt = PPT.query.get(ppt_id)
            if not ppt:
                emit('error', {'message': 'PPT不存在'})
                return

            # 更新幻灯片
            slides = ppt.slides_data
            if 0 <= slide_number < len(slides):
                slides[slide_number].update(updates)
                ppt.slides_data = slides
                db.session.commit()

                emit('slide_updated', {
                    'ppt_id': ppt_id,
                    'slide_number': slide_number,
                    'slide': slides[slide_number]
                })
            else:
                emit('error', {'message': '幻灯片编号无效'})

        except Exception as e:
            print(f"Error updating slide: {e}")
            emit('error', {'message': f'更新失败: {str(e)}'})

    @socketio.on('ai_modify_slide')
    def handle_ai_modify_slide(data):
        """AI修改单页幻灯片"""
        ppt_id = data.get('ppt_id')
        slide_number = data.get('slide_number')
        instruction = data.get('instruction')

        if not all([ppt_id, slide_number is not None, instruction]):
            emit('error', {'message': '缺少必要参数'})
            return

        try:
            ppt = PPT.query.get(ppt_id)
            if not ppt:
                emit('error', {'message': 'PPT不存在'})
                return

            slides = ppt.slides_data
            if not (0 <= slide_number < len(slides)):
                emit('error', {'message': '幻灯片编号无效'})
                return

            # 使用GLM AI修改
            current_slide = slides[slide_number]
            
            # 构建AI修改请求
            prompt = f"""请根据用户指令修改幻灯片内容。

当前幻灯片内容：
{json.dumps(current_slide, ensure_ascii=False, indent=2)}

用户指令：{instruction}

请返回修改后的完整幻灯片JSON数据，保持原有结构。"""

            response = glm_service.chat([{"role": "user", "content": prompt}])
            modified_content = response.get('content', '')
            
            # 尝试解析JSON
            try:
                # 提取JSON部分
                json_match = re.search(r'\{[\s\S]*\}', modified_content)
                if json_match:
                    modified_slide = json.loads(json_match.group())
                else:
                    modified_slide = current_slide
            except:
                modified_slide = current_slide

            # 更新数据库
            slides[slide_number] = modified_slide
            ppt.slides_data = slides
            db.session.commit()

            emit('slide_updated', {
                'ppt_id': ppt_id,
                'slide_number': slide_number,
                'slide': modified_slide
            })

        except Exception as e:
            print(f"Error AI modifying slide: {e}")
            emit('error', {'message': f'AI修改失败: {str(e)}'})
