from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app
import httpx
import xml.etree.ElementTree as ET
from urllib.parse import urlparse


def _get_serializer():
    secret = current_app.config.get('WOPI_SECRET_KEY')
    return URLSafeTimedSerializer(secret, salt='wopi')


def generate_wopi_token(file_id: str, user_id: str, file_type: str = 'ppt') -> str:
    serializer = _get_serializer()
    return serializer.dumps({
        'file_id': file_id,
        'file_type': file_type,
        'user_id': user_id
    })


def verify_wopi_token(token: str, max_age: int = None):
    serializer = _get_serializer()
    ttl = max_age or current_app.config.get('WOPI_TOKEN_TTL', 3600)
    try:
        data = serializer.loads(token, max_age=ttl)
        return data
    except (BadSignature, SignatureExpired):
        return None


def fetch_collabora_discovery(collabora_url):
    if not collabora_url:
        return None
    url = collabora_url.rstrip('/') + '/hosting/discovery'
    try:
        response = httpx.get(url, timeout=8)
        response.raise_for_status()
        return response.text
    except Exception:
        return None


def get_collabora_ppt_app_path(collabora_url):
    return get_collabora_app_path(collabora_url, 'pptx')


def get_collabora_app_path(collabora_url, file_ext: str):
    discovery_xml = fetch_collabora_discovery(collabora_url)
    if not discovery_xml:
        return '/browser/dist/loleaflet.html'

    try:
        root = ET.fromstring(discovery_xml)
    except Exception:
        return '/browser/dist/loleaflet.html'

    ext_list = {file_ext.lower()} if file_ext else set()
    # 兼容常见Office扩展
    if file_ext and file_ext.lower() == 'ppt':
        ext_list.add('pptx')
    if file_ext and file_ext.lower() == 'doc':
        ext_list.add('docx')
    if file_ext and file_ext.lower() == 'xls':
        ext_list.add('xlsx')

    for action in root.findall('.//action'):
        ext = action.attrib.get('ext')
        if ext and ext.lower() in ext_list:
            urlsrc = action.attrib.get('urlsrc')
            if not urlsrc:
                continue

            url_part = urlsrc.split('?')[0]
            if url_part.startswith('http'):
                parsed = urlparse(url_part)
                return parsed.path

            return url_part

    return '/browser/dist/loleaflet.html'
