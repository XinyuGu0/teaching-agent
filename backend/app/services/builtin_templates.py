"""
内置PPT模板元数据
从 OfficeCLI-main/examples/ppt/templates/styles/ 目录动态加载
只包含有build.sh文件的模板
"""
import os
import logging

logger = logging.getLogger(__name__)

# 动态加载函数
def get_builtin_templates():
    """
    动态获取所有包含build.sh的内置模板
    返回: list of template dicts
    """
    try:
        from app.services.build_sh_generator import get_build_sh_generator
        generator = get_build_sh_generator()
        templates = generator.get_available_templates()
        
        logger.info(f"[BuiltinTemplates] 找到 {len(templates)} 个可用模板")
        return templates
    except Exception as e:
        logger.error(f"[BuiltinTemplates] 加载模板失败: {e}")
        import traceback
        traceback.print_exc()
        return []

# 为了向后兼容，保留旧的硬编码列表（已废弃）
_BUILTIN_TEMPLATES_OLD = [
    {
        'id': 'builtin_science--time-travel',
        'dir_name': 'science--time-travel',
        'name': '时间旅行',
        'name_en': 'Time Travel',
        'category': 'science',
        'tags': ['科幻', '宇宙', '霓虹', '深色'],
        'description': '宇宙霓虹风格，适合未来/科幻主题',
        'slide_count': 5,
        'layout_pattern': 'hero-statement-pillars-evidence-cta',
    },
]

# 使用新的动态加载方式
BUILTIN_TEMPLATES = get_builtin_templates()

# 按分类分组
CATEGORY_GROUPS = {
    'science': {'label': '🔬 科学技术', 'order': 1},
    'brand': {'label': '🏢 品牌产品', 'order': 2},
    'product': {'label': '📦 产品推广', 'order': 3},
    'lifestyle': {'label': '🐱 生活方式', 'order': 4},
    'productivity': {'label': '💡 效率管理', 'order': 5},
    'tech': {'label': '💻 科技公司', 'order': 6},
    'future': {'label': '🚀 未来愿景', 'order': 7},
}

# 模板索引（按id快速查找）
_TEMPLATE_INDEX = {t['id']: t for t in BUILTIN_TEMPLATES}
_DIR_NAME_INDEX = {t['dir_name']: t for t in BUILTIN_TEMPLATES}


def get_all_builtin_templates():
    """获取所有内置模板"""
    return BUILTIN_TEMPLATES


def get_builtin_template(template_id: str):
    """按ID获取内置模板"""
    return _TEMPLATE_INDEX.get(template_id)


def get_builtin_template_by_dir(dir_name: str):
    """按目录名获取内置模板"""
    return _DIR_NAME_INDEX.get(dir_name)


def get_builtin_categories():
    """获取内置模板的分类列表（带模板数量）"""
    cats = {}
    for t in BUILTIN_TEMPLATES:
        cat = t['category']
        if cat not in cats:
            cats[cat] = {'count': 0, **CATEGORY_GROUPS.get(cat, {'label': cat, 'order': 99})}
        cats[cat]['count'] += 1
    return cats
