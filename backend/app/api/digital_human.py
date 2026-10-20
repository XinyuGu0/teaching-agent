"""
数字人模块 API
- 上传半身照、语音、PPT
- 模拟生成演讲稿（Word）
- 模拟生成讲解视频
"""
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import uuid
import time
import threading
from datetime import datetime

bp = Blueprint('digital_human', __name__)
bp.strict_slashes = False

# 任务状态存储（内存中，重启后丢失）
_tasks = {}

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac'}
ALLOWED_PPT_EXTENSIONS = {'pptx', 'ppt'}
ALLOWED_DOC_EXTENSIONS = {'docx', 'doc'}


def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set


def get_upload_dir():
    upload_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', current_app.root_path), 'digital_human')
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


@bp.route('/upload', methods=['POST'])
@bp.route('/upload/', methods=['POST'])
@jwt_required()
def upload_files():
    """上传半身照、语音、PPT文件"""
    try:
        user_id = get_jwt_identity()
        upload_dir = get_upload_dir()
        user_dir = os.path.join(upload_dir, str(user_id))
        os.makedirs(user_dir, exist_ok=True)

        result = {}

        # 半身照
        photo = request.files.get('photo')
        if photo and photo.filename:
            if not allowed_file(photo.filename, ALLOWED_IMAGE_EXTENSIONS):
                return jsonify({'error': '图片格式不支持，请上传 png/jpg/jpeg/gif/webp/bmp'}), 400
            ext = os.path.splitext(photo.filename)[1].lower()
            filename = f"photo_{uuid.uuid4().hex}{ext}"
            path = os.path.join(user_dir, filename)
            photo.save(path)
            result['photo_path'] = path
            result['photo_name'] = photo.filename

        # 语音
        audio = request.files.get('audio')
        if audio and audio.filename:
            if not allowed_file(audio.filename, ALLOWED_AUDIO_EXTENSIONS):
                return jsonify({'error': '音频格式不支持，请上传 mp3/wav/m4a/ogg/flac/aac'}), 400
            ext = os.path.splitext(audio.filename)[1].lower()
            filename = f"audio_{uuid.uuid4().hex}{ext}"
            path = os.path.join(user_dir, filename)
            audio.save(path)
            result['audio_path'] = path
            result['audio_name'] = audio.filename

        # PPT
        ppt = request.files.get('ppt')
        if ppt and ppt.filename:
            if not allowed_file(ppt.filename, ALLOWED_PPT_EXTENSIONS):
                return jsonify({'error': 'PPT格式不支持，请上传 pptx/ppt'}), 400
            ext = os.path.splitext(ppt.filename)[1].lower()
            filename = f"ppt_{uuid.uuid4().hex}{ext}"
            path = os.path.join(user_dir, filename)
            ppt.save(path)
            result['ppt_path'] = path
            result['ppt_name'] = ppt.filename

        return jsonify({'message': '文件上传成功', 'files': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/generate-script', methods=['POST'])
@bp.route('/generate-script/', methods=['POST'])
@jwt_required()
def generate_script():
    """模拟生成演讲稿（Word文档）"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        ppt_name = data.get('ppt_name', '演示文稿')

        task_id = str(uuid.uuid4())

        # 初始化任务状态
        _tasks[task_id] = {
            'status': 'processing',
            'progress': 0,
            'current_step': 0,
            'steps': [
                {'text': '解析PPT内容结构', 'status': 'pending'},
                {'text': '提取关键信息与要点', 'status': 'pending'},
                {'text': '分析语音语调特征', 'status': 'pending'},
                {'text': '生成演讲稿大纲', 'status': 'pending'},
                {'text': '撰写完整演讲稿', 'status': 'pending'},
                {'text': '导出Word文档', 'status': 'pending'},
            ],
            'logs': [],
            'result': None,
            'error': None,
        }

        # 启动后台模拟任务（传入app实例以在线程中使用应用上下文）
        app = current_app._get_current_object()
        thread = threading.Thread(
            target=_simulate_script_generation,
            args=(task_id, user_id, ppt_name, app),
            daemon=True
        )
        thread.start()

        return jsonify({'task_id': task_id}), 202

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _simulate_script_generation(task_id, user_id, ppt_name, app):
    """模拟演讲稿生成过程（在后台线程中运行）"""
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
            _do_script_generation(task_id, user_id, ppt_name, task, steps, log, sleep)
    except Exception as e:
        import traceback
        traceback.print_exc()
        task['status'] = 'failed'
        task['error'] = str(e)
        log(f'生成失败: {e}')


def _do_script_generation(task_id, user_id, ppt_name, task, steps, log, sleep):
    """演讲稿生成的实际步骤"""

    # Step 1: 解析PPT内容结构
    steps[0]['status'] = 'in-progress'
    task['current_step'] = 0
    log('开始解析PPT文件...')
    sleep(800)
    log(f'文件名: {ppt_name}')
    sleep(600)
    log('检测到 12 个幻灯片页面')
    sleep(500)
    log('解析页面布局与文本内容...')
    sleep(1000)
    log('提取标题、正文、图表说明文字')
    sleep(700)
    log('PPT内容结构解析完成')
    steps[0]['status'] = 'completed'
    task['progress'] = 15

    # Step 2: 提取关键信息与要点
    steps[1]['status'] = 'in-progress'
    task['current_step'] = 1
    log('正在提取关键信息...')
    sleep(700)
    log('识别核心论点: 3 个主要观点')
    sleep(600)
    log('提取数据支撑: 5 组关键数据')
    sleep(500)
    log('标注重点段落: 8 处需要详细讲解')
    sleep(800)
    log('关键信息提取完成')
    steps[1]['status'] = 'completed'
    task['progress'] = 30

    # Step 3: 分析语音语调特征
    steps[2]['status'] = 'in-progress'
    task['current_step'] = 2
    log('正在分析语音特征...')
    sleep(600)
    log('语音时长: 约60秒')
    sleep(500)
    log('语速分析: 中等语速 (约200字/分钟)')
    sleep(700)
    log('语调特征: 专业、沉稳')
    sleep(600)
    log('停顿模式: 段落间停顿1.5秒')
    sleep(500)
    log('语音特征分析完成')
    steps[2]['status'] = 'completed'
    task['progress'] = 50

    # Step 4: 生成演讲稿大纲
    steps[3]['status'] = 'in-progress'
    task['current_step'] = 3
    log('正在生成演讲稿大纲...')
    sleep(800)
    log('构建开场白: 自我介绍与主题引入')
    sleep(600)
    log('规划主体结构: 3段式论述')
    sleep(700)
    log('设计过渡语句: 5处自然衔接')
    sleep(500)
    log('编写结尾总结: 呼应主题与展望')
    sleep(600)
    log('演讲稿大纲生成完成')
    steps[3]['status'] = 'completed'
    task['progress'] = 65

    # Step 5: 撰写完整演讲稿
    steps[4]['status'] = 'in-progress'
    task['current_step'] = 4
    log('正在撰写完整演讲稿...')
    sleep(1000)
    log('撰写开场白 (约150字)...')
    sleep(1200)
    log('撰写第一部分: 背景与现状 (约300字)...')
    sleep(1500)
    log('撰写第二部分: 核心方案 (约400字)...')
    sleep(1500)
    log('撰写第三部分: 实施计划 (约350字)...')
    sleep(1200)
    log('撰写结尾总结 (约200字)...')
    sleep(800)
    log('演讲稿撰写完成，总字数约1400字')
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
    log('Word文档导出完成')

    # 使用内置演讲稿文件
    ppt_dir = os.path.join(current_app.config.get('BASE_DIR', os.path.abspath(os.path.join(current_app.root_path, '..'))), 'ppt')
    builtin_doc = os.path.join(ppt_dir, '演讲稿.docx')

    if os.path.isfile(builtin_doc):
        doc_path = builtin_doc
        log(f'使用内置演讲稿: 演讲稿.docx')
    else:
        # 回退：复制到用户目录
        upload_dir = get_upload_dir()
        user_dir = os.path.join(upload_dir, str(user_id))
        os.makedirs(user_dir, exist_ok=True)
        doc_path = os.path.join(user_dir, f'script_{task_id}.docx')
        try:
            from docx import Document
            doc = Document()
            doc.add_heading('演讲稿', level=0)
            doc.add_paragraph(f'基于《{ppt_name}》生成')
            doc.save(doc_path)
        except ImportError:
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(f'演讲稿 - 基于《{ppt_name}》生成')
        log('内置演讲稿不存在，已生成默认文档')

    steps[5]['status'] = 'completed'
    task['progress'] = 100
    task['status'] = 'completed'
    task['result'] = {
        'doc_path': doc_path,
        'doc_name': '演讲稿.docx',
        'word_count': 1400,
        'page_count': 3,
    }
    log('全部完成！演讲稿已生成。')


@bp.route('/generate-video', methods=['POST'])
@bp.route('/generate-video/', methods=['POST'])
@jwt_required()
def generate_video():
    """模拟生成讲解视频"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}

        task_id = str(uuid.uuid4())

        _tasks[task_id] = {
            'status': 'processing',
            'progress': 0,
            'current_step': 0,
            'steps': [
                {'text': '加载半身照与语音', 'status': 'pending'},
                {'text': '人脸关键点检测', 'status': 'pending'},
                {'text': '语音分段与对齐', 'status': 'pending'},
                {'text': '口型驱动模型推理', 'status': 'pending'},
                {'text': '视频帧合成与渲染', 'status': 'pending'},
                {'text': '音频混合与导出', 'status': 'pending'},
                {'text': '视频编码与封装', 'status': 'pending'},
            ],
            'logs': [],
            'result': None,
            'error': None,
        }

        app = current_app._get_current_object()
        thread = threading.Thread(
            target=_simulate_video_generation,
            args=(task_id, user_id, data, app),
            daemon=True
        )
        thread.start()

        return jsonify({'task_id': task_id}), 202

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _simulate_video_generation(task_id, user_id, data, app):
    """模拟视频生成过程（在后台线程中运行）"""
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
            _do_video_generation(task_id, user_id, data, task, steps, log, sleep)
    except Exception as e:
        import traceback
        traceback.print_exc()
        task['status'] = 'failed'
        task['error'] = str(e)
        log(f'生成失败: {e}')


def _do_video_generation(task_id, user_id, data, task, steps, log, sleep):

    # Step 1: 加载半身照与语音
    steps[0]['status'] = 'in-progress'
    task['current_step'] = 0
    log('正在加载素材文件...')
    sleep(700)
    log('加载半身照: 1920×1080 分辨率')
    sleep(500)
    log('加载语音文件: 时长44分56秒, 采样率44100Hz')
    sleep(600)
    log('素材加载完成')
    steps[0]['status'] = 'completed'
    task['progress'] = 10

    # Step 2: 人脸关键点检测
    steps[1]['status'] = 'in-progress'
    task['current_step'] = 1
    log('正在检测人脸关键点...')
    sleep(800)
    log('检测到 1 张人脸')
    sleep(600)
    log('提取 68 个面部关键点')
    sleep(700)
    log('计算面部轮廓与姿态参数')
    sleep(500)
    log('人脸关键点检测完成')
    steps[1]['status'] = 'completed'
    task['progress'] = 25

    # Step 3: 语音分段与对齐
    steps[2]['status'] = 'in-progress'
    task['current_step'] = 2
    log('正在进行语音分段...')
    sleep(600)
    log('语音转文字: 识别出 180 个音素')
    sleep(800)
    log('音素与口型映射: viseme 对齐完成')
    sleep(700)
    log('生成时间轴: 44分56秒 / 30fps = 80880帧')
    sleep(500)
    log('语音分段与对齐完成')
    steps[2]['status'] = 'completed'
    task['progress'] = 40

    # Step 4: 口型驱动模型推理
    steps[3]['status'] = 'in-progress'
    task['current_step'] = 3
    log('正在加载口型驱动模型...')
    sleep(1000)
    log('模型: Wav2Lip v2.0 (已加载)')
    sleep(600)
    log('开始逐帧推理...')
    for i in range(1, 6):
        sleep(800)
        log(f'推理进度: {i * 20}% (帧 {i * 16176}/80880)')
    sleep(600)
    log('口型驱动推理完成')
    steps[3]['status'] = 'completed'
    task['progress'] = 60

    # Step 5: 视频帧合成与渲染
    steps[4]['status'] = 'in-progress'
    task['current_step'] = 4
    log('正在合成视频帧...')
    sleep(700)
    log('合成模式: 半身照 + 口型驱动')
    sleep(800)
    log('背景处理: 智能抠图与背景融合')
    sleep(1000)
    log('渲染进度: 100% (80880帧)')
    sleep(600)
    log('视频帧合成完成')
    steps[4]['status'] = 'completed'
    task['progress'] = 75

    # Step 6: 音频混合与导出
    steps[5]['status'] = 'in-progress'
    task['current_step'] = 5
    log('正在混合音频...')
    sleep(600)
    log('音频降噪处理...')
    sleep(700)
    log('音画同步校准...')
    sleep(500)
    log('音频混合完成')
    steps[5]['status'] = 'completed'
    task['progress'] = 88

    # Step 7: 视频编码与封装
    steps[6]['status'] = 'in-progress'
    task['current_step'] = 6
    log('正在编码视频...')
    sleep(800)
    log('编码器: H.264, 码率 8Mbps')
    sleep(1000)
    log('封装格式: MP4 (H.264 + AAC)')
    sleep(700)
    log('文件大小: 约 48MB')
    sleep(500)

    # 使用指定的数字人视频文件
    base_dir = current_app.config.get('BASE_DIR', os.path.abspath(os.path.join(current_app.root_path, '..')))
    video_path = os.path.join(base_dir, 'ppt', 'sp.mp4')

    if not os.path.exists(video_path):
        log(f'错误: 指定的视频文件不存在: {video_path}')
        task['status'] = 'failed'
        task['error'] = '指定的视频文件不存在'
        return

    # 获取视频文件大小
    file_size_bytes = os.path.getsize(video_path)
    file_size_mb = round(file_size_bytes / (1024 * 1024), 1)

    log('视频编码完成')
    steps[6]['status'] = 'completed'
    task['progress'] = 100
    task['status'] = 'completed'
    task['result'] = {
        'video_path': video_path,
        'video_name': f'讲解视频_{data.get("ppt_name", "演示")}.mp4',
        'video_url': f'/api/digital-human/serve/video/{task_id}',
        'duration': 2696,
        'resolution': '1920x1080',
        'file_size': f'{file_size_mb}MB',
    }
    log('全部完成！讲解视频已生成。')


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
        'logs': task['logs'][-50:],  # 最近50条日志
        'result': task['result'],
    }), 200


@bp.route('/file/<file_type>/<task_id>', methods=['GET'])
@bp.route('/file/<file_type>/<task_id>/', methods=['GET'])
@jwt_required()
def get_generated_file(file_type, task_id):
    """获取生成的文件（演讲稿或视频）- 需要认证，用于下载"""
    task = _tasks.get(task_id)
    if not task:
        return jsonify({'error': '任务不存在'}), 404

    if task['status'] != 'completed' or not task['result']:
        return jsonify({'error': '任务尚未完成'}), 400

    if file_type == 'script':
        file_path = task['result'].get('doc_path')
        download_name = task['result'].get('doc_name', '演讲稿.docx')
    elif file_type == 'video':
        file_path = task['result'].get('video_path')
        download_name = task['result'].get('video_name', '讲解视频.mp4')
    else:
        return jsonify({'error': '不支持的文件类型'}), 400

    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': '文件不存在'}), 404

    return send_file(file_path, as_attachment=True, download_name=download_name)


@bp.route('/serve/<file_type>/<task_id>', methods=['GET'])
@bp.route('/serve/<file_type>/<task_id>/', methods=['GET'])
def serve_file(file_type, task_id):
    """提供文件（无需认证，供视频预览和OnlyOffice下载使用）"""
    task = _tasks.get(task_id)
    if not task:
        return jsonify({'error': '任务不存在'}), 404

    if task['status'] != 'completed' or not task['result']:
        return jsonify({'error': '任务尚未完成'}), 400

    if file_type == 'script':
        file_path = task['result'].get('doc_path')
    elif file_type == 'video':
        file_path = task['result'].get('video_path')
    else:
        return jsonify({'error': '不支持的文件类型'}), 400

    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': '文件不存在'}), 404

    # 针对视频文件，支持 Range 请求（视频在线播放必须）
    if file_type == 'video':
        return _serve_video_with_range(file_path)

    return send_file(file_path, as_attachment=False)


def _serve_video_with_range(file_path):
    """支持 Range 请求的视频流式响应，确保浏览器 <video> 可以在线播放"""
    from flask import Response

    file_size = os.path.getsize(file_path)
    range_header = request.headers.get('Range', None)

    # 根据 MIME 类型确定 content type
    import mimetypes
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = 'video/mp4'

    if not range_header:
        # 无 Range 请求，返回完整文件（支持普通 GET）
        response = send_file(file_path, mimetype=content_type, as_attachment=False)
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Content-Length'] = file_size
        return response

    # 解析 Range 头，如 "bytes=0-1023"
    range_match = None
    try:
        range_match = range_header.replace('bytes=', '').split('-')
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if range_match[1] else file_size - 1
    except (ValueError, IndexError):
        start = 0
        end = file_size - 1

    # 限制范围
    if start >= file_size:
        return Response(status=416, headers={'Content-Range': f'bytes */{file_size}'})

    end = min(end, file_size - 1)
    chunk_size = end - start + 1

    with open(file_path, 'rb') as f:
        f.seek(start)
        data = f.read(chunk_size)

    response = Response(
        data,
        status=206,
        mimetype=content_type,
    )
    response.headers['Content-Range'] = f'bytes {start}-{end}/{file_size}'
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Content-Length'] = chunk_size
    response.headers['Cache-Control'] = 'no-cache'
    return response


@bp.route('/preview/<task_id>', methods=['GET'])
@bp.route('/preview/<task_id>/', methods=['GET'])
@jwt_required()
def get_preview_config(task_id):
    """获取OnlyOffice预览配置（用于预览演讲稿）"""
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

    file_url = f"{public_base_url}/api/digital-human/serve/script/{task_id}"

    import hashlib
    stat = os.stat(doc_path)
    key_base = f"digital_human_{task_id}_{stat.st_mtime}_{stat.st_size}"
    doc_key = hashlib.md5(key_base.encode()).hexdigest()

    doc_config = {
        'fileType': 'docx',
        'key': doc_key,
        'title': task['result'].get('doc_name', '演讲稿.docx'),
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
