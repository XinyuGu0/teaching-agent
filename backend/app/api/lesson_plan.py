"""
教案生成模块 API
- 模拟生成教案（Word文档）
"""
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import uuid
import time
import threading
from datetime import datetime

bp = Blueprint('lesson_plan', __name__)
bp.strict_slashes = False

# 任务状态存储（内存中，重启后丢失）
_tasks = {}


@bp.route('/generate', methods=['POST'])
@bp.route('/generate/', methods=['POST'])
@jwt_required()
def generate_lesson_plan():
    """模拟生成教案"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        ppt_name = data.get('ppt_name', '演示文稿')
        ppt_id = data.get('ppt_id')

        task_id = str(uuid.uuid4())

        _tasks[task_id] = {
            'status': 'processing',
            'progress': 0,
            'current_step': 0,
            'steps': [
                {'text': '分析PPT内容结构', 'status': 'pending'},
                {'text': '提取教学目标与重点', 'status': 'pending'},
                {'text': '设计教学流程', 'status': 'pending'},
                {'text': '编写教案正文', 'status': 'pending'},
                {'text': '生成配套练习题', 'status': 'pending'},
                {'text': '导出Word文档', 'status': 'pending'},
            ],
            'logs': [],
            'result': None,
            'error': None,
        }

        app = current_app._get_current_object()
        thread = threading.Thread(
            target=_simulate_lesson_plan_generation,
            args=(task_id, user_id, ppt_name, ppt_id, app),
            daemon=True
        )
        thread.start()

        return jsonify({'task_id': task_id}), 202

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _simulate_lesson_plan_generation(task_id, user_id, ppt_name, ppt_id, app):
    """模拟教案生成过程（在后台线程中运行）"""
    task = _tasks.get(task_id)
    if not task:
        return

    def log(msg):
        task['logs'].append({'time': datetime.now().strftime('%H:%M:%S'), 'msg': msg})

    def sleep(ms):
        time.sleep(ms / 1000)

    steps = task['steps']

    try:
        with app.app_context():
            _do_lesson_plan_generation(task_id, user_id, ppt_name, ppt_id, task, steps, log, sleep)
    except Exception as e:
        import traceback
        traceback.print_exc()
        task['status'] = 'failed'
        task['error'] = str(e)
        log(f'生成失败: {e}')


def _do_lesson_plan_generation(task_id, user_id, ppt_name, ppt_id, task, steps, log, sleep):
    """教案生成的实际步骤"""

    # Step 1: 分析PPT内容结构
    steps[0]['status'] = 'in-progress'
    task['current_step'] = 0
    log('开始分析PPT内容...')
    sleep(800)
    log(f'文件名: {ppt_name}')
    sleep(600)
    log('检测到 12 个幻灯片页面')
    sleep(500)
    log('解析页面布局与文本内容...')
    sleep(1000)
    log('提取标题、正文、图表说明文字')
    sleep(700)
    log('PPT内容结构分析完成')
    steps[0]['status'] = 'completed'
    task['progress'] = 15

    # Step 2: 提取教学目标与重点
    steps[1]['status'] = 'in-progress'
    task['current_step'] = 1
    log('正在提取教学目标...')
    sleep(700)
    log('识别知识目标: 3 个核心知识点')
    sleep(600)
    log('识别能力目标: 2 项技能培养')
    sleep(500)
    log('标注教学重点: 4 处关键内容')
    sleep(800)
    log('标注教学难点: 2 处难点突破')
    sleep(500)
    log('教学目标提取完成')
    steps[1]['status'] = 'completed'
    task['progress'] = 30

    # Step 3: 设计教学流程
    steps[2]['status'] = 'in-progress'
    task['current_step'] = 2
    log('正在设计教学流程...')
    sleep(800)
    log('规划导入环节: 情境引入 (5分钟)')
    sleep(600)
    log('规划讲授环节: 知识讲解 (20分钟)')
    sleep(700)
    log('规划互动环节: 讨论与练习 (10分钟)')
    sleep(500)
    log('规划总结环节: 归纳与拓展 (5分钟)')
    sleep(600)
    log('教学流程设计完成')
    steps[2]['status'] = 'completed'
    task['progress'] = 50

    # Step 4: 编写教案正文
    steps[3]['status'] = 'in-progress'
    task['current_step'] = 3
    log('正在编写教案正文...')
    sleep(1000)
    log('编写教学目标与重难点分析...')
    sleep(1200)
    log('编写教学准备与学情分析...')
    sleep(1000)
    log('编写教学过程详细步骤...')
    sleep(1500)
    log('编写板书设计与教学反思...')
    sleep(800)
    log('教案正文编写完成')
    steps[3]['status'] = 'completed'
    task['progress'] = 70

    # Step 5: 生成配套练习题
    steps[4]['status'] = 'in-progress'
    task['current_step'] = 4
    log('正在生成配套练习题...')
    sleep(800)
    log('生成基础练习: 5 道选择题')
    sleep(700)
    log('生成进阶练习: 3 道简答题')
    sleep(600)
    log('生成拓展练习: 2 道论述题')
    sleep(500)
    log('配套练习题生成完成')
    steps[4]['status'] = 'completed'
    task['progress'] = 85

    # Step 6: 导出Word文档
    steps[5]['status'] = 'in-progress'
    task['current_step'] = 5
    log('正在导出Word文档...')
    sleep(800)
    log('设置文档格式: A4纸张、宋体小四...')
    sleep(600)
    log('添加页眉页脚...')
    sleep(500)
    log('生成目录...')
    sleep(700)

    # 使用内置教案文件
    base_dir = current_app.config.get('BASE_DIR', os.path.abspath(os.path.join(current_app.root_path, '..')))
    ppt_dir = os.path.join(base_dir, 'ppt')
    builtin_doc = os.path.join(ppt_dir, '教案.docx')

    if os.path.isfile(builtin_doc):
        doc_path = builtin_doc
        log(f'使用内置教案: 教案.docx')
    else:
        log(f'错误: 内置教案文件不存在: {builtin_doc}')
        task['status'] = 'failed'
        task['error'] = '教案文件不存在'
        return

    file_size_bytes = os.path.getsize(doc_path)
    file_size_mb = round(file_size_bytes / (1024 * 1024), 1)

    log('Word文档导出完成')
    steps[5]['status'] = 'completed'
    task['progress'] = 100
    task['status'] = 'completed'
    task['result'] = {
        'doc_path': doc_path,
        'doc_name': f'教案_{ppt_name}.docx',
        'doc_url': f'/api/lesson-plans/serve/{task_id}',
        'word_count': 3200,
        'page_count': 6,
        'file_size': f'{file_size_mb}MB',
    }
    log('全部完成！教案已生成。')


@bp.route('/task/<task_id>', methods=['GET'])
@bp.route('/task/<task_id>/', methods=['GET'])
@jwt_required()
def get_task_status(task_id):
    """获取任务状态"""
    task = _tasks.get(task_id)
    if not task:
        return jsonify({'error': '任务不存在'}), 404

    return jsonify({
        'task_id': task_id,
        'status': task['status'],
        'progress': task['progress'],
        'current_step': task['current_step'],
        'steps': task['steps'],
        'logs': task['logs'],
        'result': task['result'],
        'error': task['error'],
    }), 200


@bp.route('/file/<task_id>', methods=['GET'])
@bp.route('/file/<task_id>/', methods=['GET'])
@jwt_required()
def download_lesson_plan(task_id):
    """下载教案文件"""
    task = _tasks.get(task_id)
    if not task:
        return jsonify({'error': '任务不存在'}), 404

    if task['status'] != 'completed' or not task['result']:
        return jsonify({'error': '任务尚未完成'}), 400

    file_path = task['result'].get('doc_path')
    download_name = task['result'].get('doc_name', '教案.docx')

    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': '文件不存在'}), 404

    return send_file(file_path, as_attachment=True, download_name=download_name)


@bp.route('/serve/<task_id>', methods=['GET'])
@bp.route('/serve/<task_id>/', methods=['GET'])
def serve_lesson_plan(task_id):
    """提供教案文件（无需认证，供OnlyOffice下载使用）"""
    task = _tasks.get(task_id)
    if not task:
        return jsonify({'error': '任务不存在'}), 404

    if task['status'] != 'completed' or not task['result']:
        return jsonify({'error': '任务尚未完成'}), 400

    file_path = task['result'].get('doc_path')

    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': '文件不存在'}), 404

    return send_file(file_path, as_attachment=False)


@bp.route('/preview/<task_id>', methods=['GET'])
@bp.route('/preview/<task_id>/', methods=['GET'])
@jwt_required()
def get_preview_config(task_id):
    """获取OnlyOffice预览配置（用于预览教案）"""
    task = _tasks.get(task_id)
    if not task:
        return jsonify({'error': '任务不存在'}), 404

    if task['status'] != 'completed' or not task['result']:
        return jsonify({'error': '任务尚未完成'}), 400

    doc_path = task['result'].get('doc_path')
    if not doc_path or not os.path.exists(doc_path):
        return jsonify({'error': '文件不存在'}), 404

    onlyoffice_url = current_app.config.get('ONLYOFFICE_URL', 'http://localhost:80')
    jwt_secret = current_app.config.get('ONLYOFFICE_JWT_SECRET', '')

    public_base_url = current_app.config.get('PUBLIC_BASE_URL', '').strip()
    if not public_base_url:
        public_base_url = request.host_url.rstrip('/')
    public_base_url = public_base_url.replace('localhost', '127.0.0.1')

    file_url = f"{public_base_url}/api/lesson-plans/serve/{task_id}"

    import hashlib
    stat = os.stat(doc_path)
    key_base = f"lesson_plan_{task_id}_{stat.st_mtime}_{stat.st_size}"
    doc_key = hashlib.md5(key_base.encode()).hexdigest()

    doc_config = {
        'fileType': 'docx',
        'key': doc_key,
        'title': task['result'].get('doc_name', '教案.docx'),
        'url': file_url,
        'permissions': {
            'edit': True,
            'download': True,
            'print': True
        }
    }

    editor_cfg = {
        'lang': 'zh-CN',
        'mode': 'edit',
        'user': {
            'id': str(get_jwt_identity()),
            'name': 'User'
        },
        'customization': {
            'autosave': True,
        }
    }

    token = ''
    if jwt_secret:
        import jwt as pyjwt
        import time as time_mod
        payload = {
            'document': doc_config,
            'documentType': 'word',
            'editorConfig': editor_cfg,
            'iat': int(time_mod.time()),
            'exp': int(time_mod.time()) + 3600
        }
        try:
            token = pyjwt.encode(payload, jwt_secret, algorithm='HS256')
            if isinstance(token, bytes):
                token = token.decode('utf-8')
        except Exception:
            token = ''

    return jsonify({
        'file_name': doc_config['title'],
        'file_url': file_url,
        'key': doc_key,
        'onlyoffice_url': onlyoffice_url,
        'token': token,
        'document': doc_config,
        'editor_config': editor_cfg,
    }), 200
