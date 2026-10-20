from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.conversation import Conversation, Message
from app.models.share import ConversationShare

MEMORY_KEYS = ['topic', 'audience', 'purpose', 'slide_count', 'style']


def _get_memory_bank(requirements):
    requirements = requirements or {}
    bank = requirements.get('memory_bank') or {}
    if not isinstance(bank, dict):
        bank = {}
    return bank


def _set_memory_bank(requirements, bank):
    requirements = requirements or {}
    requirements['memory_bank'] = bank
    return requirements

bp = Blueprint('conversation', __name__)

@bp.route('', methods=['GET'])
@jwt_required()
def list_conversations():
    """List user conversations"""
    current_user_id = get_jwt_identity()
    conversations = Conversation.query.filter_by(user_id=current_user_id).order_by(Conversation.updated_at.desc()).all()

    return jsonify({
        'conversations': [conv.to_dict() for conv in conversations]
    }), 200


@bp.route('', methods=['POST'])
@jwt_required()
def create_conversation():
    """Create new conversation with welcome message"""
    current_user_id = get_jwt_identity()
    data = request.get_json() or {}

    conversation = Conversation(
        user_id=current_user_id,
        title=data.get('title', 'New Conversation'),
        state='INITIAL'
    )

    db.session.add(conversation)
    db.session.flush()  # Get conversation ID

    # Add welcome message
    welcome_message = Message(
        conversation_id=conversation.id,
        role='assistant',
        content='您好！我是AI助手，可以帮您生成专业的PPT和教案。\n\n我的能力包括：\n✓ 生成结构清晰的PPT大纲和内容\n✓ 支持多种文档格式（PDF、Word、Excel等）\n✓ 联网搜索最新资料\n✓ 根据您上传的材料定制内容\n\n请告诉我您想制作什么主题的PPT？',
        meta_data={'is_welcome': True}
    )

    db.session.add(welcome_message)
    db.session.commit()

    return jsonify({
        'conversation': conversation.to_dict()
    }), 201


@bp.route('/<conversation_id>', methods=['GET'])
@jwt_required()
def get_conversation(conversation_id):
    """Get conversation with messages"""
    current_user_id = get_jwt_identity()
    conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user_id).first()

    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404

    return jsonify({
        'conversation': conversation.to_dict(include_messages=True)
    }), 200


@bp.route('/<conversation_id>', methods=['DELETE'])
@jwt_required()
def delete_conversation(conversation_id):
    """Delete conversation"""
    current_user_id = get_jwt_identity()
    conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user_id).first()

    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404

    # Delete associated shares first to avoid FK constraint errors
    ConversationShare.query.filter_by(conversation_id=conversation_id).delete()

    db.session.delete(conversation)
    db.session.commit()

    return jsonify({'message': 'Conversation deleted'}), 200


@bp.route('/<conversation_id>/memory', methods=['GET'])
@jwt_required()
def get_conversation_memory(conversation_id):
    """Get extracted memory from conversation requirements"""
    current_user_id = get_jwt_identity()
    conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user_id).first()

    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404

    requirements = conversation.requirements or {}
    memory_bank = _get_memory_bank(requirements)
    memory_items = []

    # 优先返回多条记忆（memory_bank），兼容旧结构
    for key in MEMORY_KEYS:
        values = memory_bank.get(key)
        if isinstance(values, list) and values:
            for idx, val in enumerate(values):
                memory_items.append({'id': f'{key}:{idx}', 'key': key, 'value': val})
            continue

        legacy_value = requirements.get(key)
        if legacy_value is not None and legacy_value != '':
            memory_items.append({'id': f'{key}:0', 'key': key, 'value': legacy_value})

    return jsonify({'memory': memory_items, 'requirements': requirements}), 200


@bp.route('/<conversation_id>/memory/<key>', methods=['PATCH'])
@jwt_required()
def update_memory_item(conversation_id, key):
    """Update one memory item in requirements"""
    current_user_id = get_jwt_identity()
    conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user_id).first()

    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404

    if key not in MEMORY_KEYS:
        return jsonify({'error': 'Invalid memory key'}), 400

    data = request.get_json() or {}
    value = data.get('value')
    memory_id = data.get('id', '')
    if value is None or value == '':
        return jsonify({'error': 'Memory value is required'}), 400

    requirements = conversation.requirements or {}
    memory_bank = _get_memory_bank(requirements)

    if isinstance(memory_id, str) and ':' in memory_id:
        try:
            id_key, id_idx = memory_id.split(':', 1)
            idx = int(id_idx)
            values = memory_bank.get(id_key, [])
            if isinstance(values, list) and 0 <= idx < len(values):
                values[idx] = value
                memory_bank[id_key] = values
            else:
                memory_bank.setdefault(key, []).append(value)
        except Exception:
            memory_bank.setdefault(key, []).append(value)
    else:
        memory_bank.setdefault(key, [])
        if memory_bank[key]:
            memory_bank[key][0] = value
        else:
            memory_bank[key].append(value)

    requirements = _set_memory_bank(requirements, memory_bank)
    conversation.requirements = requirements
    db.session.commit()

    return jsonify({'message': 'Memory item updated', 'requirements': requirements}), 200


@bp.route('/<conversation_id>/memory/<key>', methods=['DELETE'])
@jwt_required()
def delete_memory_item(conversation_id, key):
    """Delete one memory item from requirements"""
    current_user_id = get_jwt_identity()
    conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user_id).first()

    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404

    if key not in MEMORY_KEYS:
        return jsonify({'error': 'Invalid memory key'}), 400

    memory_id = request.args.get('id', '')
    requirements = conversation.requirements or {}
    memory_bank = _get_memory_bank(requirements)

    if isinstance(memory_id, str) and ':' in memory_id:
        try:
            id_key, id_idx = memory_id.split(':', 1)
            idx = int(id_idx)
            values = memory_bank.get(id_key, [])
            if isinstance(values, list) and 0 <= idx < len(values):
                values.pop(idx)
                if values:
                    memory_bank[id_key] = values
                else:
                    memory_bank.pop(id_key, None)
        except Exception:
            pass
    else:
        # 兼容旧逻辑：删除整类
        memory_bank.pop(key, None)
        if key in requirements:
            requirements.pop(key)

    requirements = _set_memory_bank(requirements, memory_bank)
    conversation.requirements = requirements
    db.session.commit()

    return jsonify({'message': 'Memory item deleted', 'requirements': requirements}), 200


@bp.route('/<conversation_id>/memory', methods=['DELETE'])
@jwt_required()
def clear_conversation_memory(conversation_id):
    """Clear all memory items in one conversation"""
    current_user_id = get_jwt_identity()
    conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user_id).first()

    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404

    requirements = conversation.requirements or {}
    for k in MEMORY_KEYS:
        requirements.pop(k, None)
    requirements['memory_bank'] = {}

    conversation.requirements = requirements
    db.session.commit()

    return jsonify({'message': 'Conversation memory cleared', 'requirements': requirements}), 200


@bp.route('/<conversation_id>', methods=['PATCH', 'PUT'])
@jwt_required()
def update_conversation(conversation_id):
    """Update conversation"""
    current_user_id = get_jwt_identity()
    conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user_id).first()

    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404

    data = request.get_json()
    if 'title' in data:
        conversation.title = data['title']
    if 'status' in data:
        conversation.status = data['status']
    if 'state' in data:
        conversation.state = data['state']
    if 'requirements' in data:
        conversation.requirements = data['requirements']

    db.session.commit()

    return jsonify({
        'conversation': conversation.to_dict()
    }), 200


@bp.route('/<conversation_id>/generate-outline', methods=['POST'])
@jwt_required()
def generate_outline_from_dialogue(conversation_id):
    """根据对话记录和选择的模板生成PPT大纲 - SSE流式响应"""
    import json
    import re
    from flask import Response, stream_with_context
    
    current_user_id = get_jwt_identity()
    
    # 获取对话
    conversation = Conversation.query.filter_by(
        id=conversation_id,
        user_id=current_user_id
    ).first()
    
    if not conversation:
        return jsonify({'error': '对话不存在'}), 404
    
    # 获取请求数据
    data = request.get_json() or {}
    dialogue = data.get('dialogue', '')
    template_id = data.get('template_id', '')
    
    if not dialogue:
        return jsonify({'error': '对话内容不能为空'}), 400
    
    if not template_id:
        return jsonify({'error': '请先选择模板'}), 400
    
    def _extract_json_text(text):
        cleaned_text = text.strip()
        if '```json' in cleaned_text:
            cleaned_text = cleaned_text.split('```json', 1)[1]
            if '```' in cleaned_text:
                cleaned_text = cleaned_text.split('```', 1)[0]
        elif '```' in cleaned_text:
            parts = cleaned_text.split('```')
            if len(parts) >= 3:
                cleaned_text = parts[1]
                if cleaned_text.startswith('json'):
                    cleaned_text = cleaned_text[4:]

        return cleaned_text.strip()

    def _parse_json_from_text(text):
        cleaned_text = _extract_json_text(text)
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as ex:
            # 尝试提取第一个平衡的大括号对象
            for start_index in range(len(cleaned_text)):
                if cleaned_text[start_index] != '{':
                    continue
                depth = 0
                for end_index in range(start_index, len(cleaned_text)):
                    if cleaned_text[end_index] == '{':
                        depth += 1
                    elif cleaned_text[end_index] == '}':
                        depth -= 1
                        if depth == 0:
                            candidate = cleaned_text[start_index:end_index + 1]
                            try:
                                return json.loads(candidate)
                            except json.JSONDecodeError:
                                break
            raise ex

    def generate():
        try:
            # 阶段1: 准备中
            yield f"data: {json.dumps({'stage': 'preparing', 'progress': 5, 'message': '正在准备生成大纲...'})}\n\n"
            
            # 获取模板信息
            slide_count = 5
            layout_pattern = 'hero-statement-pillars-evidence-cta'
            
            if template_id and template_id.startswith('builtin_'):
                from app.services.builtin_templates import get_builtin_template
                template_info = get_builtin_template(template_id)
                if template_info:
                    slide_count = template_info.get('slide_count', 5)
                    layout_pattern = template_info.get('layout_pattern', 'hero-statement-pillars-evidence-cta')
                    print(f"[Generate Outline] 使用内置模板: {template_id}, 页数: {slide_count}, 布局: {layout_pattern}")
            
            # 阶段2: 构建提示词
            yield f"data: {json.dumps({'stage': 'building_prompt', 'progress': 10, 'message': '正在构建提示词...'})}\n\n"
            
            from app.services.glm_service import chat as llm_chat
            
            prompt = f"""你是一个专业的PPT内容策划师。请根据以下对话记录，生成一个结构清晰的PPT大纲。

对话记录:
{dialogue}

模板要求:
1. 生成{slide_count}页的PPT大纲
2. 布局模式: {layout_pattern}
3. 每页包含标题和2-3个要点
4. 大纲应该简洁、专业、易于理解
5. 所有字符串中的换行必须使用 \\n  转义
6. 必须只返回一个合法的JSON对象，不要包含任何解释或额外文字

返回格式示例:
{{
  "title": "主题标题",
  "slides": [
    {{
      "slide_number": 1,
      "title": "第一页标题",
      "content_points": ["要点1", "要点2", "要点3"]
    }},
    {{
      "slide_number": 2,
      "title": "第二页标题",
      "content_points": ["要点1", "要点2"]
    }}
  ]
}}

请直接返回JSON格式的大纲，不要包含任何解释或额外文字。"""
            
            # 阶段3: 调用LLM（流式）
            yield f"data: {json.dumps({'stage': 'calling_llm', 'progress': 20, 'message': '正在调用AI生成大纲...'})}\n\n"
            
            response = llm_chat(
                messages=[
                    {"role": "system", "content": "你是一个专业的PPT内容策划师，擅长根据对话内容生成结构清晰的PPT大纲。"},
                    {"role": "user", "content": prompt}
                ],
                model="qwen3.5-plus-2026-02-15",
                temperature=0.7,
                max_tokens=2000,
                stream=True,
                timeout_seconds=600
            )
            
            # 阶段4: 流式接收内容
            full_content = ""
            chunk_count = 0
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        full_content += delta.content
                        chunk_count += 1
                        # 根据接收到的内容量估算进度 (20-80)
                        progress = min(80, 20 + int(chunk_count * 0.5))
                        yield f"data: {json.dumps({'stage': 'receiving', 'progress': progress, 'message': f'正在接收AI响应...'})}\n\n"
            
            # 阶段5: 解析JSON
            yield f"data: {json.dumps({'stage': 'parsing', 'progress': 85, 'message': '正在解析大纲内容...'})}\n\n"
            
            if not full_content:
                yield f"data: {json.dumps({'stage': 'error', 'progress': 0, 'message': 'AI未返回内容'})}\n\n"
                return
            
            print(f"[Generate Outline] LLM响应: {full_content[:500]}")
            
            # 尝试解析JSON
            outline_json = _parse_json_from_text(full_content)
            
            print(f"[Generate Outline] 解析成功: {outline_json}")
            
            # 阶段6: 完成
            yield f"data: {json.dumps({'stage': 'done', 'progress': 100, 'message': '大纲生成完成！', 'outline': outline_json})}\n\n"
            
        except json.JSONDecodeError as e:
            print(f"[Generate Outline] JSON解析失败: {e}")
            yield f"data: {json.dumps({'stage': 'error', 'progress': 0, 'message': f'解析大纲失败: {str(e)}'})}\n\n"
        except Exception as e:
            print(f"[Generate Outline] 异常: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'stage': 'error', 'progress': 0, 'message': f'生成大纲失败: {str(e)}'})}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )
