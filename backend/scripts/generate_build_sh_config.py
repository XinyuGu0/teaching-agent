"""
自动生成build_sh_templates.py配置文件
读取所有build.sh文件并生成Python配置代码
"""
import os
import json
import re

def read_build_sh_file(build_sh_path):
    """读取build.sh文件内容"""
    with open(build_sh_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_metadata(build_sh_content, dir_name):
    """从build.sh内容中提取元数据"""
    metadata = {
        'dir_name': dir_name,
        'name': '',
        'category': '',
        'tags': [],
        'description': '',
        'background_color': 'FFFFFF',
        'font': '思源黑体'
    }
    
    # 提取背景色
    bg_match = re.search(r'background[=:\s]+["\']?([A-Fa-f0-9]{6})', build_sh_content)
    if bg_match:
        metadata['background_color'] = bg_match.group(1)
    
    # 提取字体
    font_match = re.search(r'font["\']?\s*[:=]\s*["\']([^"\']+)["\']', build_sh_content)
    if font_match:
        metadata['font'] = font_match.group(1)
    
    # 生成显示名称
    parts = dir_name.split('--')
    if len(parts) == 2:
        category, style = parts
        
        # 分类映射
        category_map = {
            'science': '科学',
            'brand': '品牌',
            'product': '产品',
            'lifestyle': '生活',
            'productivity': '效率',
            'tech': '科技',
            'future': '未来'
        }
        metadata['category'] = category_map.get(category, category)
        
        # 风格名称映射
        style_names = {
            'time-travel': '时间旅行',
            'alien-guide': '外星指南',
            'space-exploration': '太空探索',
            'aura-coffee': '咖啡美学',
            'aura-coffee-dark': '咖啡美学（深色）',
            'cat-philosophy': '猫咪哲学',
            'cat-secret-life': '猫咪秘密',
            'geminicli-timetravel': '时光穿梭',
            'attention-budget': '注意力预算',
            'wildlife-company': '野生动物',
            '2050-vision': '2050愿景'
        }
        
        style_name = style_names.get(style, style.replace('-', ' ').title())
        metadata['name'] = f"{metadata['category']} - {style_name}"
        
        # 生成标签
        tags = []
        if category == 'science':
            tags.extend(['科幻', '深色'])
            if 'time' in style:
                tags.append('时间')
            elif 'space' in style:
                tags.extend(['太空', '宇宙'])
            elif 'alien' in style:
                tags.extend(['外星', '霓虹'])
        elif category == 'brand':
            tags.extend(['品牌', '极简'])
            if 'coffee' in style:
                tags.append('咖啡')
            if 'dark' in style:
                tags.append('深色')
            else:
                tags.append('浅色')
        elif category == 'lifestyle':
            tags.extend(['生活', '趣味'])
            if 'cat' in style:
                tags.append('猫咪')
        elif category == 'product':
            tags.extend(['产品', '科技'])
        elif category == 'productivity':
            tags.extend(['效率', '专注'])
        elif category == 'tech':
            tags.extend(['科技', '自然'])
        elif category == 'future':
            tags.extend(['未来', '科技'])
        
        metadata['tags'] = tags
        
        # 生成描述
        descriptions = {
            'science--time-travel': '宇宙霓虹风格，适合未来/科幻主题',
            'science--alien-guide': '深色科幻风格，适合地外生命/未来主题',
            'science--space-exploration': '太空探索旅程演示风格',
            'brand--aura-coffee': '极简品牌展示风格，适合咖啡/轻食品牌',
            'brand--aura-coffee-dark': '奢华极简深色主题，适合高端品牌展示',
            'lifestyle--cat-philosophy': '趣味生活哲学风格，适合轻松话题',
            'lifestyle--cat-secret-life': '温馨生活记录风格，适合日常分享',
            'product--geminicli-timetravel': '科技产品推广风格，适合AI/工具产品',
            'productivity--attention-budget': '专注力管理风格，适合效率/时间管理',
            'tech--wildlife-company': '自然科技公司风格，适合环保/科技结合',
            'future--2050-vision': '未来愿景展示风格，适合前瞻性话题'
        }
        metadata['description'] = descriptions.get(dir_name, f'{metadata["category"]}主题演示')
    
    return metadata

def generate_config():
    """生成配置文件"""
    styles_dir = os.path.join(
        os.path.dirname(__file__), '..',
        'OfficeCLI-main', 'examples', 'ppt', 'templates', 'styles'
    )
    
    if not os.path.exists(styles_dir):
        print(f"错误: 目录不存在 {styles_dir}")
        return
    
    # 收集所有包含build.sh的模板
    templates = []
    for dir_name in sorted(os.listdir(styles_dir)):
        build_sh_path = os.path.join(styles_dir, dir_name, 'build.sh')
        
        if os.path.exists(build_sh_path):
            print(f"处理模板: {dir_name}")
            
            # 读取build.sh内容
            build_sh_content = read_build_sh_file(build_sh_path)
            
            # 提取元数据
            metadata = extract_metadata(build_sh_content, dir_name)
            
            templates.append({
                'dir_name': dir_name,
                'metadata': metadata,
                'build_sh': build_sh_content
            })
    
    # 生成Python配置代码
    output_file = os.path.join(
        os.path.dirname(__file__), '..',
        'app', 'services', 'build_sh_templates.py'
    )
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('"""\n')
        f.write('内置PPT模板的build.sh内容硬编码\n')
        f.write('此文件由脚本自动生成，请勿手动修改\n')
        f.write('"""\n\n')
        
        # 写入BUILD_SH_CONTENT
        f.write('BUILD_SH_CONTENT = {\n')
        for template in templates:
            dir_name = template['dir_name']
            build_sh = template['build_sh']
            
            # 转义三引号
            escaped_build_sh = build_sh.replace("'''", "\\'\\'\\'")
            
            f.write(f"    '{dir_name}': '''\n")
            f.write(escaped_build_sh)
            f.write("''',\n\n")
        f.write('}\n\n')
        
        # 写入TEMPLATE_METADATA
        f.write('TEMPLATE_METADATA = {\n')
        for template in templates:
            dir_name = template['dir_name']
            metadata = template['metadata']
            
            f.write(f"    '{dir_name}': {{\n")
            f.write(f"        'id': 'builtin_{dir_name}',\n")
            f.write(f"        'dir_name': '{dir_name}',\n")
            f.write(f"        'name': '{metadata['name']}',\n")
            f.write(f"        'category': '{metadata['category']}',\n")
            f.write(f"        'tags': {json.dumps(metadata['tags'], ensure_ascii=False)},\n")
            f.write(f"        'description': '{metadata['description']}',\n")
            f.write(f"        'background_color': '{metadata['background_color']}',\n")
            f.write(f"        'font': '{metadata['font']}',\n")
            f.write(f"        'template_type': 'builtin'\n")
            f.write('    },\n')
        f.write('}\n\n')
        
        # 写入辅助函数
        f.write('def get_build_sh_content(template_id: str) -> str:\n')
        f.write('    """获取指定模板的build.sh内容"""\n')
        f.write('    dir_name = template_id.replace(\'builtin_\', \'\')\n')
        f.write('    return BUILD_SH_CONTENT.get(dir_name, \'\')\n\n')
        f.write('def get_template_metadata(template_id: str) -> dict:\n')
        f.write('    """获取指定模板的元数据"""\n')
        f.write('    dir_name = template_id.replace(\'builtin_\', \'\')\n')
        f.write('    return TEMPLATE_METADATA.get(dir_name, {})\n\n')
        f.write('def get_all_template_ids() -> list:\n')
        f.write('    """获取所有可用模板ID列表"""\n')
        f.write('    return [f\'builtin_{dir_name}\' for dir_name in BUILD_SH_CONTENT.keys()]\n')
    
    print(f"\n✅ 配置文件已生成: {output_file}")
    print(f"✅ 共处理 {len(templates)} 个模板")
    
    # 打印模板列表
    print("\n模板列表:")
    for template in templates:
        metadata = template['metadata']
        print(f"  - {metadata['name']} ({template['dir_name']})")

if __name__ == '__main__':
    generate_config()
