"""
内置PPT模板的build.sh内容硬编码
此文件由脚本自动生成，请勿手动修改
"""

BUILD_SH_CONTENT = {
    'brand--aura-coffee': '''
#!/bin/bash
set -e

FILE="aura_coffee.pptx"

echo "Creating PPT..."
officecli create "$FILE"
officecli add "$FILE" '/' --type slide --prop layout=blank --prop background=F9F6F0

echo "Building Slide 1..."
cat << 'JSON_EOF' > s1.json
[
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!bg-main","preset":"ellipse","fill":"F3EFE6","x":"15cm","y":"0cm","width":"25cm","height":"25cm","line":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!circle-accent","preset":"ellipse","fill":"C2A878","x":"5cm","y":"14cm","width":"2cm","height":"2cm","line":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!line-top","preset":"rect","fill":"2B2624","x":"0cm","y":"2cm","width":"10cm","height":"0.2cm","line":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!slash-accent","preset":"rect","fill":"8B6F47","x":"25cm","y":"10cm","width":"0.2cm","height":"5cm","rotation":"45","line":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!card-1","preset":"roundRect","fill":"FFFFFF","opacity":"0.9","x":"36cm","y":"7cm","width":"8.5cm","height":"10cm","line":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!card-2","preset":"roundRect","fill":"FFFFFF","opacity":"0.9","x":"36cm","y":"7cm","width":"8.5cm","height":"10cm","line":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!card-3","preset":"roundRect","fill":"FFFFFF","opacity":"0.9","x":"36cm","y":"7cm","width":"8.5cm","height":"10cm","line":"none"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!hero-title","text":"AURA COFFEE","font":"Montserrat","bold":"true","size":"64","color":"2B2624","x":"4cm","y":"7cm","width":"24cm","height":"4cm","align":"left","valign":"middle","line":"none","fill":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!hero-sub","text":"极简主义咖啡美学 / MINIMALIST COFFEE AESTHETICS","font":"思源黑体","size":"18","color":"8B6F47","x":"4cm","y":"11cm","width":"24cm","height":"2cm","align":"left","valign":"top","line":"none","fill":"none"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!statement-title","text":"我们只做一件事：还原咖啡豆本真的风味","font":"思源黑体","bold":"true","size":"36","color":"2B2624","x":"36cm","y":"7cm","width":"24cm","height":"3cm","align":"left","line":"none","fill":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!statement-desc","text":"在纷繁复杂的时代，我们拒绝过度包装与冗余添加。\n以最克制的方式，呈现大自然赋予的纯粹果香与醇厚。","font":"思源黑体","size":"20","color":"8B6F47","x":"36cm","y":"11cm","width":"20cm","height":"4cm","align":"left","line":"none","fill":"none"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!pillars-title","text":"三大核心坚持","font":"思源黑体","bold":"true","size":"36","color":"2B2624","x":"36cm","y":"2cm","width":"15cm","height":"2cm","align":"left","line":"none","fill":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!p1-title","text":"甄选微批次","font":"思源黑体","bold":"true","size":"24","color":"2B2624","x":"36cm","y":"8cm","width":"6.5cm","height":"1.5cm","align":"center","line":"none","fill":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!p1-sub","text":"Micro-Lot Selection","font":"Montserrat","size":"14","color":"C2A878","x":"36cm","y":"9.5cm","width":"6.5cm","height":"1cm","align":"center","line":"none","fill":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!p1-desc","text":"深入原产地，仅挑选SCA评分85+以上的单一产区微批次咖啡豆。","font":"思源黑体","size":"16","color":"8B6F47","x":"36cm","y":"11cm","width":"6.5cm","height":"5cm","align":"center","valign":"top","line":"none","fill":"none"}},
  
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!p2-title","text":"极简烘焙","font":"思源黑体","bold":"true","size":"24","color":"2B2624","x":"36cm","y":"8cm","width":"6.5cm","height":"1.5cm","align":"center","line":"none","fill":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!p2-sub","text":"Minimalist Roasting","font":"Montserrat","size":"14","color":"C2A878","x":"36cm","y":"9.5cm","width":"6.5cm","height":"1cm","align":"center","line":"none","fill":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!p2-desc","text":"摒弃重度烘焙，采用精准的浅中烘焙曲线，保留地域风味特色。","font":"思源黑体","size":"16","color":"8B6F47","x":"36cm","y":"11cm","width":"6.5cm","height":"5cm","align":"center","valign":"top","line":"none","fill":"none"}},
  
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!p3-title","text":"大师手冲","font":"思源黑体","bold":"true","size":"24","color":"2B2624","x":"36cm","y":"8cm","width":"6.5cm","height":"1.5cm","align":"center","line":"none","fill":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!p3-sub","text":"Master Brewing","font":"Montserrat","size":"14","color":"C2A878","x":"36cm","y":"9.5cm","width":"6.5cm","height":"1cm","align":"center","line":"none","fill":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!p3-desc","text":"严控水温、水粉比与冲煮时间，确保每一杯出品的极致稳定与干净。","font":"思源黑体","size":"16","color":"8B6F47","x":"36cm","y":"11cm","width":"6.5cm","height":"5cm","align":"center","valign":"top","line":"none","fill":"none"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!evi-title","text":"经得起挑剔的品质标准","font":"思源黑体","bold":"true","size":"36","color":"2B2624","x":"36cm","y":"2cm","width":"20cm","height":"2cm","align":"left","line":"none","fill":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!evi-num1","text":"15","font":"Montserrat","bold":"true","size":"80","color":"2B2624","x":"36cm","y":"6cm","width":"12cm","height":"4cm","align":"center","line":"none","fill":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!evi-t1","text":"天最佳赏味期限制","font":"思源黑体","size":"20","color":"8B6F47","x":"36cm","y":"11cm","width":"12cm","height":"2cm","align":"center","line":"none","fill":"none"}},
  
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!evi-num2","text":"0","font":"Montserrat","bold":"true","size":"48","color":"2B2624","x":"36cm","y":"6cm","width":"5cm","height":"3cm","align":"center","line":"none","fill":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!evi-t2","text":"添加人工香精","font":"思源黑体","size":"18","color":"8B6F47","x":"36cm","y":"9cm","width":"7cm","height":"2cm","align":"left","valign":"middle","line":"none","fill":"none"}},
  
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!evi-num3","text":"100%","font":"Montserrat","bold":"true","size":"48","color":"2B2624","x":"36cm","y":"6cm","width":"5cm","height":"3cm","align":"center","line":"none","fill":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!evi-t3","text":"可降解环保包装","font":"思源黑体","size":"18","color":"8B6F47","x":"36cm","y":"9cm","width":"7cm","height":"2cm","align":"left","valign":"middle","line":"none","fill":"none"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!cta-title","text":"回归纯粹，期待与你相遇","font":"思源黑体","bold":"true","size":"48","color":"2B2624","x":"36cm","y":"7cm","width":"26cm","height":"3cm","align":"center","line":"none","fill":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!cta-web","text":"www.auracoffee.com","font":"Montserrat","size":"20","color":"8B6F47","x":"36cm","y":"11cm","width":"26cm","height":"1.5cm","align":"center","line":"none","fill":"none"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!cta-email","text":"partner@auracoffee.com","font":"Montserrat","size":"20","color":"8B6F47","x":"36cm","y":"12cm","width":"26cm","height":"1.5cm","align":"center","line":"none","fill":"none"}}
]
JSON_EOF
officecli batch "$FILE" < s1.json

echo "Building Slide 2..."
officecli add "$FILE" '/' --from '/slide[1]'
cat << 'JSON_EOF' > s2.json
[
  {"command":"set","path":"/slide[2]","props":{"transition":"morph"}},
  {"command":"set","path":"/slide[2]/shape[1]","props":{"x":"0cm","y":"2cm","width":"15cm","height":"15cm"}},
  {"command":"set","path":"/slide[2]/shape[2]","props":{"x":"30cm","y":"5cm","width":"4cm","height":"4cm"}},
  {"command":"set","path":"/slide[2]/shape[3]","props":{"x":"5cm","y":"4cm","width":"5cm"}},
  {"command":"set","path":"/slide[2]/shape[4]","props":{"x":"25cm","y":"15cm","height":"8cm","rotation":"90"}},
  {"command":"set","path":"/slide[2]/shape[8]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[2]/shape[9]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[2]/shape[10]","props":{"x":"5cm","y":"7cm"}},
  {"command":"set","path":"/slide[2]/shape[11]","props":{"x":"5cm","y":"11cm"}}
]
JSON_EOF
officecli batch "$FILE" < s2.json

echo "Building Slide 3..."
officecli add "$FILE" '/' --from '/slide[1]'
cat << 'JSON_EOF' > s3.json
[
  {"command":"set","path":"/slide[3]","props":{"transition":"morph"}},
  {"command":"set","path":"/slide[3]/shape[1]","props":{"x":"20cm","y":"0cm","width":"15cm","height":"25cm","fill":"EAE3D5"}},
  {"command":"set","path":"/slide[3]/shape[2]","props":{"x":"2cm","y":"2cm","width":"3cm","height":"3cm"}},
  {"command":"set","path":"/slide[3]/shape[3]","props":{"x":"3cm","y":"3.5cm","width":"28cm","height":"0.1cm"}},
  {"command":"set","path":"/slide[3]/shape[4]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[3]/shape[5]","props":{"x":"3cm","y":"6cm"}},
  {"command":"set","path":"/slide[3]/shape[6]","props":{"x":"12.5cm","y":"6cm"}},
  {"command":"set","path":"/slide[3]/shape[7]","props":{"x":"22cm","y":"6cm"}},
  {"command":"set","path":"/slide[3]/shape[8]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[3]/shape[9]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[3]/shape[12]","props":{"x":"3cm","y":"1.5cm"}},
  
  {"command":"set","path":"/slide[3]/shape[13]","props":{"x":"4cm","y":"7.5cm"}},
  {"command":"set","path":"/slide[3]/shape[14]","props":{"x":"4cm","y":"9cm"}},
  {"command":"set","path":"/slide[3]/shape[15]","props":{"x":"4cm","y":"11cm"}},
  {"command":"set","path":"/slide[3]/shape[16]","props":{"x":"13.5cm","y":"7.5cm"}},
  {"command":"set","path":"/slide[3]/shape[17]","props":{"x":"13.5cm","y":"9cm"}},
  {"command":"set","path":"/slide[3]/shape[18]","props":{"x":"13.5cm","y":"11cm"}},
  {"command":"set","path":"/slide[3]/shape[19]","props":{"x":"23cm","y":"7.5cm"}},
  {"command":"set","path":"/slide[3]/shape[20]","props":{"x":"23cm","y":"9cm"}},
  {"command":"set","path":"/slide[3]/shape[21]","props":{"x":"23cm","y":"11cm"}}
]
JSON_EOF
officecli batch "$FILE" < s3.json

echo "Building Slide 4..."
officecli add "$FILE" '/' --from '/slide[1]'
cat << 'JSON_EOF' > s4.json
[
  {"command":"set","path":"/slide[4]","props":{"transition":"morph"}},
  {"command":"set","path":"/slide[4]/shape[1]","props":{"x":"28cm","y":"14cm","width":"8cm","height":"8cm"}},
  {"command":"set","path":"/slide[4]/shape[2]","props":{"x":"1cm","y":"1cm","width":"1.5cm","height":"1.5cm"}},
  {"command":"set","path":"/slide[4]/shape[3]","props":{"x":"2cm","y":"3cm","width":"30cm"}},
  {"command":"set","path":"/slide[4]/shape[4]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[5]","props":{"x":"2cm","y":"5cm","width":"14cm","height":"12cm"}},
  {"command":"set","path":"/slide[4]/shape[6]","props":{"x":"17cm","y":"5cm","width":"14cm","height":"5.5cm"}},
  {"command":"set","path":"/slide[4]/shape[7]","props":{"x":"17cm","y":"11.5cm","width":"14cm","height":"5.5cm"}},
  {"command":"set","path":"/slide[4]/shape[8]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[9]","props":{"x":"36cm"}},
  
  {"command":"set","path":"/slide[4]/shape[22]","props":{"x":"2cm","y":"1.5cm"}},
  {"command":"set","path":"/slide[4]/shape[23]","props":{"x":"3cm","y":"7cm"}},
  {"command":"set","path":"/slide[4]/shape[24]","props":{"x":"3cm","y":"12cm"}},
  {"command":"set","path":"/slide[4]/shape[25]","props":{"x":"18cm","y":"6.2cm"}},
  {"command":"set","path":"/slide[4]/shape[26]","props":{"x":"23cm","y":"6.7cm"}},
  {"command":"set","path":"/slide[4]/shape[27]","props":{"x":"18cm","y":"12.7cm"}},
  {"command":"set","path":"/slide[4]/shape[28]","props":{"x":"23cm","y":"13.2cm"}}
]
JSON_EOF
officecli batch "$FILE" < s4.json

echo "Building Slide 5..."
officecli add "$FILE" '/' --from '/slide[1]'
cat << 'JSON_EOF' > s5.json
[
  {"command":"set","path":"/slide[5]","props":{"transition":"morph"}},
  {"command":"set","path":"/slide[5]/shape[1]","props":{"x":"10cm","y":"0cm","width":"30cm","height":"30cm"}},
  {"command":"set","path":"/slide[5]/shape[2]","props":{"x":"5cm","y":"12cm","width":"2cm","height":"2cm"}},
  {"command":"set","path":"/slide[5]/shape[3]","props":{"x":"14cm","y":"13cm","width":"6cm"}},
  {"command":"set","path":"/slide[5]/shape[4]","props":{"x":"28cm","y":"4cm","height":"4cm","rotation":"45"}},
  {"command":"set","path":"/slide[5]/shape[8]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[9]","props":{"x":"36cm"}},
  
  {"command":"set","path":"/slide[5]/shape[29]","props":{"x":"4cm","y":"8cm"}},
  {"command":"set","path":"/slide[5]/shape[30]","props":{"x":"4cm","y":"13.5cm"}},
  {"command":"set","path":"/slide[5]/shape[31]","props":{"x":"4cm","y":"15cm"}}
]
JSON_EOF
officecli batch "$FILE" < s5.json

echo "Validating PPT..."
officecli validate "$FILE"
officecli view outline "$FILE"
''',

    'brand--aura-coffee-dark': '''
#!/bin/bash

# AURA COFFEE - Morph PPT Builder

# 1. Initialize PPT
rm -f "AURA_COFFEE.pptx"
officecli create "AURA_COFFEE.pptx"

# 2. Generate JSON using Python
python3 - << 'PYEOF'
import json
import sys

commands = []

def add_slide(idx, transition="none"):
    commands.append({
        "command": "add",
        "parent": "/",
        "type": "slide",
        "props": {
            "background": "111111",
            "transition": transition
        }
    })

def add_shape(slide_idx, name, props):
    base_props = {"name": name, "preset": "rect", "fill": "none", "line": "none", "font": "Helvetica"}
    base_props.update(props)
    commands.append({
        "command": "add",
        "parent": f"/slide[{slide_idx}]",
        "type": "shape",
        "props": base_props
    })

# --- Actor Data Registry (to keep text consistent for ghosting) ---
ACTOR_TEXTS = {
    "!!brand-title": "AURA COFFEE",
    "!!brand-sub": "纯 粹 之 境 | 极简高级精品咖啡",
    "!!statement-main": "少即是多，剥离繁杂，只为一杯纯粹好咖啡。",
    "!!statement-sub": "在喧嚣的都市中，我们坚持做减法。\n拒绝过度包装与人工添加，让咖啡回归最本真的风味，\n这是 AURA 的美学，也是对品质的极致专注。",
    "!!pillar-title": "三大核心原则",
    "!!box1-title": "01. 严苛寻豆",
    "!!box1-desc": "深入埃塞俄比亚、哥伦比亚等原产地，仅甄选海拔 1500 米以上的 SCA 85+ 级精品生豆。",
    "!!box2-title": "02. 精准烘焙",
    "!!box2-desc": "采用德国 Probat 烘焙机，结合气象数据微调曲线，激发每一支豆子的风土之味。",
    "!!box3-title": "03. 科学萃取",
    "!!box3-desc": "精准控制 93°C 水温与 9 Bar 压力，金杯法则护航，确保每一杯出品的稳定与完美。",
    "!!ev-number": "1%",
    "!!ev-title": "全球前 1% 极微批次特选",
    "!!ev-desc1": "• 年度限量供应 500kg 庄园级瑰夏",
    "!!ev-desc2": "• 100% 环保可降解极简材质包装",
    "!!ev-desc3": "• 多位 Q-Grader 国际品鉴师严格把控",
    "!!cta-title": "品味纯粹，即刻启程",
    "!!cta-web": "www.auracoffee.com",
    "!!cta-email": "partner@auracoffee.com"
}

# Default ghost properties
def ghost(name):
    return {
        "x": "36cm", "y": "0cm", "width": "1cm", "height": "1cm",
        "text": ACTOR_TEXTS.get(name, ""),
        "color": "000000", "size": "10",
        "fill": "none" if "line" not in name else "000000",
        "opacity": "0"
    }

# All actors list
ALL_ACTORS = [
    "!!deco-line", "!!brand-title", "!!brand-sub",
    "!!statement-main", "!!statement-sub",
    "!!pillar-title", 
    "!!box1-line", "!!box1-title", "!!box1-desc",
    "!!box2-line", "!!box2-title", "!!box2-desc",
    "!!box3-line", "!!box3-title", "!!box3-desc",
    "!!ev-number", "!!ev-title", "!!ev-desc1", "!!ev-desc2", "!!ev-desc3",
    "!!cta-title", "!!cta-web", "!!cta-email"
]

# Slide 1: Hero
s1_active = {
    "!!deco-line": {"x": "4cm", "y": "8.5cm", "width": "2cm", "height": "0.1cm", "fill": "D4AF37"},
    "!!brand-title": {"x": "4cm", "y": "9cm", "width": "25cm", "height": "3cm", "text": ACTOR_TEXTS["!!brand-title"], "size": "60", "color": "FFFFFF", "bold": "true"},
    "!!brand-sub": {"x": "4.2cm", "y": "12cm", "width": "25cm", "height": "1cm", "text": ACTOR_TEXTS["!!brand-sub"], "size": "16", "color": "888888", "lineSpacing": "1.5"}
}

# Slide 2: Statement
s2_active = {
    "!!brand-title": {"x": "4cm", "y": "2cm", "width": "10cm", "height": "1cm", "text": ACTOR_TEXTS["!!brand-title"], "size": "14", "color": "555555", "bold": "true"},
    "!!deco-line": {"x": "4cm", "y": "7cm", "width": "1cm", "height": "0.1cm", "fill": "D4AF37"},
    "!!statement-main": {"x": "4cm", "y": "8cm", "width": "25cm", "height": "2cm", "text": ACTOR_TEXTS["!!statement-main"], "size": "36", "color": "FFFFFF"},
    "!!statement-sub": {"x": "4cm", "y": "11cm", "width": "20cm", "height": "4cm", "text": ACTOR_TEXTS["!!statement-sub"], "size": "16", "color": "888888", "lineSpacing": "1.8", "valign": "top"}
}

# Slide 3: Pillars
s3_active = {
    "!!brand-title": {"x": "4cm", "y": "2cm", "width": "10cm", "height": "1cm", "text": ACTOR_TEXTS["!!brand-title"], "size": "14", "color": "555555", "bold": "true"},
    "!!deco-line": {"x": "4cm", "y": "4.5cm", "width": "5cm", "height": "0.1cm", "fill": "D4AF37"},
    "!!pillar-title": {"x": "4cm", "y": "3cm", "width": "25cm", "height": "1.5cm", "text": ACTOR_TEXTS["!!pillar-title"], "size": "24", "color": "FFFFFF"},
    "!!box1-line": {"x": "4cm", "y": "7cm", "width": "0.1cm", "height": "7cm", "fill": "333333"},
    "!!box1-title": {"x": "4.5cm", "y": "7cm", "width": "8cm", "height": "1cm", "text": ACTOR_TEXTS["!!box1-title"], "size": "16", "color": "FFFFFF"},
    "!!box1-desc": {"x": "4.5cm", "y": "8.5cm", "width": "7.5cm", "height": "5cm", "text": ACTOR_TEXTS["!!box1-desc"], "size": "14", "color": "888888", "lineSpacing": "1.6", "valign": "top"},
    "!!box2-line": {"x": "13.5cm", "y": "7cm", "width": "0.1cm", "height": "7cm", "fill": "333333"},
    "!!box2-title": {"x": "14cm", "y": "7cm", "width": "8cm", "height": "1cm", "text": ACTOR_TEXTS["!!box2-title"], "size": "16", "color": "FFFFFF"},
    "!!box2-desc": {"x": "14cm", "y": "8.5cm", "width": "7.5cm", "height": "5cm", "text": ACTOR_TEXTS["!!box2-desc"], "size": "14", "color": "888888", "lineSpacing": "1.6", "valign": "top"},
    "!!box3-line": {"x": "23cm", "y": "7cm", "width": "0.1cm", "height": "7cm", "fill": "333333"},
    "!!box3-title": {"x": "23.5cm", "y": "7cm", "width": "8cm", "height": "1cm", "text": ACTOR_TEXTS["!!box3-title"], "size": "16", "color": "FFFFFF"},
    "!!box3-desc": {"x": "23.5cm", "y": "8.5cm", "width": "7.5cm", "height": "5cm", "text": ACTOR_TEXTS["!!box3-desc"], "size": "14", "color": "888888", "lineSpacing": "1.6", "valign": "top"}
}

# Slide 4: Evidence
s4_active = {
    "!!brand-title": {"x": "4cm", "y": "2cm", "width": "10cm", "height": "1cm", "text": ACTOR_TEXTS["!!brand-title"], "size": "14", "color": "555555", "bold": "true"},
    "!!deco-line": {"x": "15cm", "y": "10.5cm", "width": "3cm", "height": "0.1cm", "fill": "D4AF37"},
    "!!ev-number": {"x": "4cm", "y": "7cm", "width": "10cm", "height": "5cm", "text": ACTOR_TEXTS["!!ev-number"], "size": "110", "color": "D4AF37", "bold": "true", "font": "Arial"},
    "!!ev-title": {"x": "4cm", "y": "12cm", "width": "12cm", "height": "2cm", "text": ACTOR_TEXTS["!!ev-title"], "size": "20", "color": "FFFFFF"},
    "!!ev-desc1": {"x": "15cm", "y": "7cm", "width": "15cm", "height": "1.5cm", "text": ACTOR_TEXTS["!!ev-desc1"], "size": "16", "color": "CCCCCC"},
    "!!ev-desc2": {"x": "15cm", "y": "8.5cm", "width": "15cm", "height": "1.5cm", "text": ACTOR_TEXTS["!!ev-desc2"], "size": "16", "color": "CCCCCC"},
    "!!ev-desc3": {"x": "15cm", "y": "12cm", "width": "15cm", "height": "1.5cm", "text": ACTOR_TEXTS["!!ev-desc3"], "size": "16", "color": "CCCCCC"}
}

# Slide 5: CTA
s5_active = {
    "!!deco-line": {"x": "4cm", "y": "7cm", "width": "2cm", "height": "0.1cm", "fill": "D4AF37"},
    "!!cta-title": {"x": "4cm", "y": "8cm", "width": "25cm", "height": "3cm", "text": ACTOR_TEXTS["!!cta-title"], "size": "44", "color": "FFFFFF"},
    "!!brand-title": {"x": "4cm", "y": "12cm", "width": "15cm", "height": "1.5cm", "text": ACTOR_TEXTS["!!brand-title"], "size": "20", "color": "888888", "bold": "true"},
    "!!cta-web": {"x": "4cm", "y": "14cm", "width": "10cm", "height": "1cm", "text": ACTOR_TEXTS["!!cta-web"], "size": "14", "color": "555555"},
    "!!cta-email": {"x": "10cm", "y": "14cm", "width": "10cm", "height": "1cm", "text": ACTOR_TEXTS["!!cta-email"], "size": "14", "color": "555555"}
}

slides_data = [
    ("none", s1_active),
    ("morph", s2_active),
    ("morph", s3_active),
    ("morph", s4_active),
    ("morph", s5_active)
]

for i, (transition, active_dict) in enumerate(slides_data):
    slide_idx = i + 1
    add_slide(slide_idx, transition)
    for actor in ALL_ACTORS:
        if actor in active_dict:
            add_shape(slide_idx, actor, active_dict[actor])
        else:
            add_shape(slide_idx, actor, ghost(actor))

with open('commands.json', 'w') as f:
    json.dump(commands, f)

PYEOF

# 3. Execute batch commands
echo "Executing batch commands..."
cat commands.json | officecli batch "AURA_COFFEE.pptx"

# 4. Clean up
rm commands.json
echo "Build complete."

''',

    'future--2050-vision': '''
#!/bin/bash
set -e

FILE="未来已来_2050.pptx"
echo "Creating PPT: $FILE"
officecli create "$FILE"

echo "Setting up Slide 1..."
officecli add "$FILE" '/' --type slide --prop layout=blank --prop background=0B0C10

# -- Scene Actors (1-6) --
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!bg-orb" --prop preset=ellipse --prop fill=66FCF1 --prop opacity=0.08 --prop x=0cm --prop y=0cm --prop width=20cm --prop height=20cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!bg-box" --prop preset=rect --prop fill=1F2833 --prop opacity=0.3 --prop x=2cm --prop y=2cm --prop width=8cm --prop height=15cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!accent-line" --prop preset=rect --prop fill=66FCF1 --prop x=1cm --prop y=4cm --prop width=0.2cm --prop height=5cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!frame" --prop preset=rect --prop fill=none --prop line=1F2833 --prop lineWidth=2 --prop x=1.2cm --prop y=0.8cm --prop width=31.47cm --prop height=17.45cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!dot-1" --prop preset=ellipse --prop fill=45A29E --prop x=5cm --prop y=10cm --prop width=0.5cm --prop height=0.5cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!dot-2" --prop preset=ellipse --prop fill=66FCF1 --prop x=30cm --prop y=15cm --prop width=1cm --prop height=1cm

# -- Slide 1 Headline Actors (7-9) --
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!hero-title" --prop text="未来已来：2050" --prop font="思源黑体" --prop size=64 --prop bold=true --prop color=FFFFFF --prop x=4cm --prop y=6cm --prop width=25cm --prop height=4cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!hero-sub" --prop text="全息时代的一天" --prop font="思源黑体" --prop size=36 --prop color=C5C6C7 --prop x=4.2cm --prop y=10.5cm --prop width=15cm --prop height=2cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!hero-tag" --prop text="THE BOUNDARY DISSOLVES" --prop font="Montserrat" --prop size=16 --prop color=66FCF1 --prop x=4.2cm --prop y=13cm --prop width=15cm --prop height=1.5cm --prop bold=true

# -- Slide 2 Headline Actors (10-11) --
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!stmt-text" --prop text="物理与数字的边界彻底消融" --prop font="思源黑体" --prop size=54 --prop bold=true --prop color=FFFFFF --prop align=center --prop x=36cm --prop y=7cm --prop width=28cm --prop height=4cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!stmt-sub" --prop text="智能代理、脑机接口与空间计算重塑了我们的每一秒" --prop font="思源黑体" --prop size=24 --prop color=45A29E --prop align=center --prop x=36cm --prop y=12cm --prop width=28cm --prop height=2cm

# -- Slide 3 Content Actors (12-23) --
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!p1-bg" --prop preset=roundRect --prop fill=1F2833 --prop opacity=0.4 --prop x=36cm --prop y=4.5cm --prop width=9cm --prop height=11cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!p1-time" --prop text="07:00" --prop font="Montserrat" --prop size=28 --prop bold=true --prop color=66FCF1 --prop x=36cm --prop y=5.5cm --prop width=7cm --prop height=1.5cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!p1-title" --prop text="基因营养与唤醒" --prop font="思源黑体" --prop size=24 --prop bold=true --prop color=FFFFFF --prop x=36cm --prop y=7.5cm --prop width=7.5cm --prop height=1.5cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!p1-desc" --prop text="AI管家实时读取体征，合成专属营养早餐，温和唤醒意识。" --prop font="思源黑体" --prop size=16 --prop color=C5C6C7 --prop x=36cm --prop y=10cm --prop width=7cm --prop height=4cm

officecli add "$FILE" '/slide[1]' --type shape --prop name="!!p2-bg" --prop preset=roundRect --prop fill=1F2833 --prop opacity=0.4 --prop x=36cm --prop y=4.5cm --prop width=9cm --prop height=11cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!p2-time" --prop text="14:00" --prop font="Montserrat" --prop size=28 --prop bold=true --prop color=66FCF1 --prop x=36cm --prop y=5.5cm --prop width=7cm --prop height=1.5cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!p2-title" --prop text="全息远程协同" --prop font="思源黑体" --prop size=24 --prop bold=true --prop color=FFFFFF --prop x=36cm --prop y=7.5cm --prop width=7.5cm --prop height=1.5cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!p2-desc" --prop text="在虚拟火星基地与全球团队开启三维会议，数据触手可及。" --prop font="思源黑体" --prop size=16 --prop color=C5C6C7 --prop x=36cm --prop y=10cm --prop width=7cm --prop height=4cm

officecli add "$FILE" '/slide[1]' --type shape --prop name="!!p3-bg" --prop preset=roundRect --prop fill=1F2833 --prop opacity=0.4 --prop x=36cm --prop y=4.5cm --prop width=9cm --prop height=11cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!p3-time" --prop text="21:00" --prop font="Montserrat" --prop size=28 --prop bold=true --prop color=66FCF1 --prop x=36cm --prop y=5.5cm --prop width=7cm --prop height=1.5cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!p3-title" --prop text="沉浸式潜意识休眠" --prop font="思源黑体" --prop size=24 --prop bold=true --prop color=FFFFFF --prop x=36cm --prop y=7.5cm --prop width=8cm --prop height=1.5cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!p3-desc" --prop text="脑机接口连接潜意识网络，在深睡中完成知识载入与精神放松。" --prop font="思源黑体" --prop size=16 --prop color=C5C6C7 --prop x=36cm --prop y=10cm --prop width=7cm --prop height=4cm

# -- Slide 4 Content Actors (24-29) --
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!ev-bg" --prop preset=rect --prop fill=45A29E --prop opacity=0.3 --prop x=36cm --prop y=3cm --prop width=15cm --prop height=13cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!ev-num" --prop text="98.5%" --prop font="Montserrat" --prop size=96 --prop bold=true --prop color=66FCF1 --prop x=36cm --prop y=5cm --prop width=15cm --prop height=5cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!ev-label" --prop text="全球人口脑机接口接入率" --prop font="思源黑体" --prop size=24 --prop color=FFFFFF --prop x=36cm --prop y=11cm --prop width=13cm --prop height=2cm

officecli add "$FILE" '/slide[1]' --type shape --prop name="!!ev2-bg" --prop preset=rect --prop fill=1F2833 --prop opacity=0.5 --prop x=36cm --prop y=8cm --prop width=12cm --prop height=8cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!ev2-num" --prop text="12.4 hrs" --prop font="Montserrat" --prop size=64 --prop bold=true --prop color=FFFFFF --prop x=36cm --prop y=9.5cm --prop width=10cm --prop height=3cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!ev2-label" --prop text="平均每日混合现实驻留时长" --prop font="思源黑体" --prop size=18 --prop color=C5C6C7 --prop x=36cm --prop y=13.5cm --prop width=10cm --prop height=2cm

# -- Slide 5 Headline Actors (30-31) --
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!cta-title" --prop text="准备好迎接你的未来了吗？" --prop font="思源黑体" --prop size=48 --prop bold=true --prop color=FFFFFF --prop align=center --prop x=36cm --prop y=7cm --prop width=26cm --prop height=3cm
officecli add "$FILE" '/slide[1]' --type shape --prop name="!!cta-btn" --prop text="EXPLORE 2050" --prop preset=roundRect --prop font="Montserrat" --prop size=18 --prop bold=true --prop color=0B0C10 --prop fill=66FCF1 --prop align=center --prop x=36cm --prop y=11.5cm --prop width=6cm --prop height=1.5cm

# ==============================================================================
# Slide 2: Statement
# ==============================================================================
echo "Setting up Slide 2..."
officecli add "$FILE" '/' --from '/slide[1]'
cat << 'JSON_EOF' | officecli batch "$FILE"
[
  {"command":"set","path":"/slide[2]","props":{"transition":"morph"}},
  
  {"command":"set","path":"/slide[2]/shape[1]","props":{"x":"20cm","y":"8cm","opacity":"0.05","fill":"45A29E"}},
  {"command":"set","path":"/slide[2]/shape[2]","props":{"x":"14cm","y":"2cm","width":"18cm","opacity":"0.1"}},
  {"command":"set","path":"/slide[2]/shape[3]","props":{"x":"2cm","y":"2cm","width":"30cm","height":"0.2cm"}},
  {"command":"set","path":"/slide[2]/shape[5]","props":{"x":"31cm","y":"4cm"}},
  {"command":"set","path":"/slide[2]/shape[6]","props":{"x":"3cm","y":"16cm"}},

  {"command":"set","path":"/slide[2]/shape[7]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[2]/shape[8]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[2]/shape[9]","props":{"x":"36cm","y":"0cm"}},

  {"command":"set","path":"/slide[2]/shape[10]","props":{"x":"2.9cm","y":"7cm"}},
  {"command":"set","path":"/slide[2]/shape[11]","props":{"x":"2.9cm","y":"12cm"}}
]
JSON_EOF

# ==============================================================================
# Slide 3: Pillars
# ==============================================================================
echo "Setting up Slide 3..."
officecli add "$FILE" '/' --from '/slide[2]'
cat << 'JSON_EOF' | officecli batch "$FILE"
[
  {"command":"set","path":"/slide[3]","props":{"transition":"morph"}},
  
  {"command":"set","path":"/slide[3]/shape[1]","props":{"x":"10cm","y":"0cm","opacity":"0.08","fill":"66FCF1"}},
  {"command":"set","path":"/slide[3]/shape[2]","props":{"x":"2cm","y":"2cm","width":"30cm","height":"2cm","opacity":"0.1"}},
  {"command":"set","path":"/slide[3]/shape[3]","props":{"x":"31cm","y":"4cm","width":"0.2cm","height":"5cm"}},
  
  {"command":"set","path":"/slide[3]/shape[10]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[3]/shape[11]","props":{"x":"36cm","y":"0cm"}},

  {"command":"set","path":"/slide[3]/shape[12]","props":{"x":"2.5cm","y":"4.5cm"}},
  {"command":"set","path":"/slide[3]/shape[13]","props":{"x":"3.5cm","y":"5.5cm","animation":"fade-entrance-400-with"}},
  {"command":"set","path":"/slide[3]/shape[14]","props":{"x":"3.5cm","y":"7.5cm","animation":"fade-entrance-400-with"}},
  {"command":"set","path":"/slide[3]/shape[15]","props":{"x":"3.5cm","y":"10cm","animation":"fade-entrance-400-with"}},

  {"command":"set","path":"/slide[3]/shape[16]","props":{"x":"12.5cm","y":"4.5cm"}},
  {"command":"set","path":"/slide[3]/shape[17]","props":{"x":"13.5cm","y":"5.5cm","animation":"fade-entrance-400-with"}},
  {"command":"set","path":"/slide[3]/shape[18]","props":{"x":"13.5cm","y":"7.5cm","animation":"fade-entrance-400-with"}},
  {"command":"set","path":"/slide[3]/shape[19]","props":{"x":"13.5cm","y":"10cm","animation":"fade-entrance-400-with"}},

  {"command":"set","path":"/slide[3]/shape[20]","props":{"x":"22.5cm","y":"4.5cm"}},
  {"command":"set","path":"/slide[3]/shape[21]","props":{"x":"23.5cm","y":"5.5cm","animation":"fade-entrance-400-with"}},
  {"command":"set","path":"/slide[3]/shape[22]","props":{"x":"23.5cm","y":"7.5cm","animation":"fade-entrance-400-with"}},
  {"command":"set","path":"/slide[3]/shape[23]","props":{"x":"23.5cm","y":"10cm","animation":"fade-entrance-400-with"}}
]
JSON_EOF

# ==============================================================================
# Slide 4: Evidence
# ==============================================================================
echo "Setting up Slide 4..."
officecli add "$FILE" '/' --from '/slide[3]'
cat << 'JSON_EOF' | officecli batch "$FILE"
[
  {"command":"set","path":"/slide[4]","props":{"transition":"morph"}},
  
  {"command":"set","path":"/slide[4]/shape[1]","props":{"x":"15cm","y":"10cm","opacity":"0.05"}},
  {"command":"set","path":"/slide[4]/shape[2]","props":{"x":"2cm","y":"4cm","width":"4cm","height":"11cm"}},
  {"command":"set","path":"/slide[4]/shape[3]","props":{"x":"2cm","y":"15.5cm","width":"12cm","height":"0.2cm"}},

  {"command":"set","path":"/slide[4]/shape[12]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[4]/shape[13]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[4]/shape[14]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[4]/shape[15]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[4]/shape[16]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[4]/shape[17]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[4]/shape[18]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[4]/shape[19]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[4]/shape[20]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[4]/shape[21]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[4]/shape[22]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[4]/shape[23]","props":{"x":"36cm","y":"0cm"}},

  {"command":"set","path":"/slide[4]/shape[24]","props":{"x":"4cm","y":"3cm"}},
  {"command":"set","path":"/slide[4]/shape[25]","props":{"x":"5cm","y":"5cm"}},
  {"command":"set","path":"/slide[4]/shape[26]","props":{"x":"5cm","y":"12cm"}},

  {"command":"set","path":"/slide[4]/shape[27]","props":{"x":"20cm","y":"8cm"}},
  {"command":"set","path":"/slide[4]/shape[28]","props":{"x":"21cm","y":"9.5cm"}},
  {"command":"set","path":"/slide[4]/shape[29]","props":{"x":"21cm","y":"13.5cm"}}
]
JSON_EOF

# ==============================================================================
# Slide 5: CTA
# ==============================================================================
echo "Setting up Slide 5..."
officecli add "$FILE" '/' --from '/slide[4]'
cat << 'JSON_EOF' | officecli batch "$FILE"
[
  {"command":"set","path":"/slide[5]","props":{"transition":"morph"}},

  {"command":"set","path":"/slide[5]/shape[1]","props":{"x":"8cm","y":"0cm","width":"15cm","height":"15cm","opacity":"0.08"}},
  {"command":"set","path":"/slide[5]/shape[2]","props":{"x":"12cm","y":"10cm","width":"10cm","height":"6cm"}},
  {"command":"set","path":"/slide[5]/shape[3]","props":{"x":"16.5cm","y":"16cm","width":"0.8cm","height":"0.2cm"}},

  {"command":"set","path":"/slide[5]/shape[24]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[5]/shape[25]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[5]/shape[26]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[5]/shape[27]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[5]/shape[28]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[5]/shape[29]","props":{"x":"36cm","y":"0cm"}},

  {"command":"set","path":"/slide[5]/shape[30]","props":{"x":"3.9cm","y":"7cm"}},
  {"command":"set","path":"/slide[5]/shape[31]","props":{"x":"13.9cm","y":"11.5cm"}}
]
JSON_EOF

echo "Done building. Validating PPT..."
officecli validate "$FILE"
officecli view "$FILE" outline
''',

    'lifestyle--cat-philosophy': '''
#!/bin/bash
set -e

FILE="cat_philosophy.pptx"
echo "Creating PPTX: $FILE"
officecli create "$FILE"

echo "Adding Slide 1 (hero)..."
officecli add "$FILE" '/' --type slide --prop layout=blank --prop background=FFF9E6
echo '[
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"circle-main","preset":"ellipse","fill":"FF8A4C","x":"18cm","y":"3cm","width":"18cm","height":"18cm","opacity":"1.0"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"circle-sub","preset":"ellipse","fill":"FFC533","x":"26cm","y":"12cm","width":"10cm","height":"10cm","opacity":"1.0"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"round-box","preset":"roundRect","fill":"FFC533","x":"5cm","y":"12cm","width":"12cm","height":"6cm","rotation":"-10","opacity":"0.3"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"line-top","preset":"roundRect","fill":"4A3B32","x":"3cm","y":"2cm","width":"6cm","height":"0.4cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"dot-small","preset":"ellipse","fill":"4A3B32","x":"28cm","y":"3cm","width":"1.5cm","height":"1.5cm"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"s1-title","text":"猫咪的统治哲学","font":"Source Han Sans","size":"64","bold":"true","color":"2A201A","x":"3cm","y":"4cm","width":"22cm","height":"4cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"s1-sub","text":"为什么地球人自愿成为“铲屎官”？","font":"Source Han Sans","size":"36","color":"4A3B32","x":"3cm","y":"8.5cm","width":"24cm","height":"2cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"s1-tag","text":"一场长达一万年的双向奔赴","font":"Source Han Sans","size":"20","color":"FF8A4C","bold":"true","x":"3cm","y":"11.5cm","width":"15cm","height":"1.5cm"}}
]' | officecli batch "$FILE"


echo "Adding Slide 2 (statement)..."
officecli add "$FILE" '/' --from '/slide[1]'
echo '[
  {"command":"set","path":"/slide[2]","props":{"transition":"morph"}},
  {"command":"set","path":"/slide[2]/shape[1]","props":{"x":"5cm","y":"0cm","width":"26cm","height":"26cm","opacity":"0.1"}},
  {"command":"set","path":"/slide[2]/shape[2]","props":{"x":"10cm","y":"10cm","width":"18cm","height":"18cm","opacity":"0.1"}},
  {"command":"set","path":"/slide[2]/shape[3]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[2]/shape[4]","props":{"x":"14cm","y":"4cm","width":"8cm"}},
  {"command":"set","path":"/slide[2]/shape[5]","props":{"x":"6cm","y":"14cm","width":"2cm","height":"2cm"}},
  {"command":"set","path":"/slide[2]/shape[6]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[2]/shape[7]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[2]/shape[8]","props":{"x":"36cm"}},

  {"command":"add","parent":"/slide[2]","type":"shape","props":{"name":"s2-title","text":"这不是你养了宠物，\\n这是一场完美的跨物种PUA。","font":"Source Han Sans","size":"54","bold":"true","color":"2A201A","align":"center","x":"4cm","y":"6cm","width":"26cm","height":"5cm"}},
  {"command":"add","parent":"/slide[2]","type":"shape","props":{"name":"s2-sub","text":"狗被驯化用来工作，而猫走进人类生活，只因为这里有免费的食物和暖炉。","font":"Source Han Sans","size":"24","color":"4A3B32","align":"right","x":"12cm","y":"13cm","width":"18cm","height":"3cm"}}
]' | officecli batch "$FILE"


echo "Adding Slide 3 (pillars)..."
officecli add "$FILE" '/' --from '/slide[2]'
echo '[
  {"command":"set","path":"/slide[3]","props":{"transition":"morph"}},
  {"command":"set","path":"/slide[3]/shape[1]","props":{"x":"0cm","y":"12cm","width":"12cm","height":"12cm","opacity":"0.2"}},
  {"command":"set","path":"/slide[3]/shape[2]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[3]/shape[3]","props":{"x":"2cm","y":"2cm","width":"8cm","height":"8cm","opacity":"0.1","rotation":"0"}},
  {"command":"set","path":"/slide[3]/shape[4]","props":{"x":"2cm","y":"2cm","width":"8cm"}},
  {"command":"set","path":"/slide[3]/shape[5]","props":{"x":"30cm","y":"2cm","width":"3cm","height":"3cm"}},
  {"command":"set","path":"/slide[3]/shape[9]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[3]/shape[10]","props":{"x":"36cm"}},

  {"command":"add","parent":"/slide[3]","type":"shape","props":{"name":"s3-title","text":"统治地球的三大核心武器","font":"Source Han Sans","size":"44","bold":"true","color":"2A201A","x":"2cm","y":"3cm","width":"24cm","height":"2.5cm"}},

  {"command":"add","parent":"/slide[3]","type":"shape","props":{"name":"p1-bg","preset":"roundRect","fill":"FFFFFF","x":"2cm","y":"6.5cm","width":"9cm","height":"10.5cm","opacity":"0.8","animation":"fade-entrance-400-with"}},
  {"command":"add","parent":"/slide[3]","type":"shape","props":{"name":"p2-bg","preset":"roundRect","fill":"FFFFFF","x":"12.5cm","y":"6.5cm","width":"9cm","height":"10.5cm","opacity":"0.8","animation":"fade-entrance-400-with-delay=100"}},
  {"command":"add","parent":"/slide[3]","type":"shape","props":{"name":"p3-bg","preset":"roundRect","fill":"FFFFFF","x":"23cm","y":"6.5cm","width":"9cm","height":"10.5cm","opacity":"0.8","animation":"fade-entrance-400-with-delay=200"}},

  {"command":"add","parent":"/slide[3]","type":"shape","props":{"name":"p1-title","text":"① 幼态延续","font":"Source Han Sans","size":"26","bold":"true","color":"FF8A4C","x":"3cm","y":"7.5cm","width":"7cm","height":"1.5cm","animation":"fade-entrance-400-with"}},
  {"command":"add","parent":"/slide[3]","type":"shape","props":{"name":"p1-desc","text":"大眼睛、小鼻子，触发人类的本能抚育冲动。Baby Schema 让人类无法抗拒。","font":"Source Han Sans","size":"18","color":"4A3B32","x":"3cm","y":"9.5cm","width":"7cm","height":"5cm","animation":"fade-entrance-400-with"}},

  {"command":"add","parent":"/slide[3]","type":"shape","props":{"name":"p2-title","text":"② 专属夹子音","font":"Source Han Sans","size":"26","bold":"true","color":"FF8A4C","x":"13.5cm","y":"7.5cm","width":"7cm","height":"1.5cm","animation":"fade-entrance-400-with-delay=100"}},
  {"command":"add","parent":"/slide[3]","type":"shape","props":{"name":"p2-desc","text":"成年猫之间不喵喵叫。这种特定频率专门用来模拟婴儿啼哭，精准操控人类神经。","font":"Source Han Sans","size":"18","color":"4A3B32","x":"13.5cm","y":"9.5cm","width":"7cm","height":"5cm","animation":"fade-entrance-400-with-delay=100"}},

  {"command":"add","parent":"/slide[3]","type":"shape","props":{"name":"p3-title","text":"③ 间歇性强化","font":"Source Han Sans","size":"26","bold":"true","color":"FF8A4C","x":"24cm","y":"7.5cm","width":"7cm","height":"1.5cm","animation":"fade-entrance-400-with-delay=200"}},
  {"command":"add","parent":"/slide[3]","type":"shape","props":{"name":"p3-desc","text":"时而高冷，时而粘人。在心理学上，这是最容易让人上瘾的反馈机制。","font":"Source Han Sans","size":"18","color":"4A3B32","x":"24cm","y":"9.5cm","width":"7cm","height":"5cm","animation":"fade-entrance-400-with-delay=200"}}
]' | officecli batch "$FILE"


echo "Adding Slide 4 (evidence)..."
officecli add "$FILE" '/' --from '/slide[3]'
echo '[
  {"command":"set","path":"/slide[4]","props":{"transition":"morph"}},
  {"command":"set","path":"/slide[4]/shape[1]","props":{"x":"15cm","y":"0cm","width":"26cm","height":"26cm","opacity":"1.0"}},
  {"command":"set","path":"/slide[4]/shape[2]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[4]/shape[3]","props":{"x":"24cm","y":"8cm","width":"12cm","height":"12cm","opacity":"1.0","rotation":"15"}},
  {"command":"set","path":"/slide[4]/shape[4]","props":{"x":"2cm","y":"3cm","width":"5cm"}},
  {"command":"set","path":"/slide[4]/shape[5]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[4]/shape[11]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[12]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[13]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[14]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[15]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[16]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[17]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[18]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[19]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[20]","props":{"x":"36cm"}},

  {"command":"add","parent":"/slide[4]","type":"shape","props":{"name":"s4-title","text":"不仅控制心，还控制多巴胺","font":"Source Han Sans","size":"40","bold":"true","color":"2A201A","x":"2cm","y":"4cm","width":"15cm","height":"2.5cm"}},
  {"command":"add","parent":"/slide[4]","type":"shape","props":{"name":"s4-data1-val","text":"25-150","font":"Montserrat","size":"80","bold":"true","color":"FFFFFF","align":"right","x":"15cm","y":"5cm","width":"13cm","height":"4cm"}},
  {"command":"add","parent":"/slide[4]","type":"shape","props":{"name":"s4-data1-unit","text":"Hz","font":"Montserrat","size":"40","bold":"true","color":"FFFFFF","x":"28cm","y":"7.5cm","width":"4cm","height":"2cm"}},
  {"command":"add","parent":"/slide[4]","type":"shape","props":{"name":"s4-data1-desc","text":"猫咪呼噜声频率，医学证明能促进骨骼愈合","font":"Source Han Sans","size":"20","color":"FFFFFF","align":"right","x":"18cm","y":"10.5cm","width":"14cm","height":"2cm"}},
  
  {"command":"add","parent":"/slide[4]","type":"shape","props":{"name":"s4-data2-title","text":"降低皮质醇","font":"Source Han Sans","size":"28","bold":"true","color":"FF8A4C","x":"2cm","y":"8cm","width":"12cm","height":"1.5cm"}},
  {"command":"add","parent":"/slide[4]","type":"shape","props":{"name":"s4-data2-desc","text":"看猫咪视频能瞬间降低压力荷尔蒙，提升多巴胺。","font":"Source Han Sans","size":"18","color":"4A3B32","x":"2cm","y":"9.5cm","width":"12cm","height":"3cm"}},

  {"command":"add","parent":"/slide[4]","type":"shape","props":{"name":"s4-data3-title","text":"弓形虫假说","font":"Source Han Sans","size":"28","bold":"true","color":"FF8A4C","x":"2cm","y":"13cm","width":"12cm","height":"1.5cm"}},
  {"command":"add","parent":"/slide[4]","type":"shape","props":{"name":"s4-data3-desc","text":"猫咪体内的寄生虫可能悄悄改变了人类的冒险神经。","font":"Source Han Sans","size":"18","color":"4A3B32","x":"2cm","y":"14.5cm","width":"12cm","height":"3cm"}}
]' | officecli batch "$FILE"


echo "Adding Slide 5 (cta)..."
officecli add "$FILE" '/' --from '/slide[4]'
echo '[
  {"command":"set","path":"/slide[5]","props":{"transition":"morph"}},
  {"command":"set","path":"/slide[5]/shape[1]","props":{"x":"12cm","y":"4cm","width":"10cm","height":"10cm","opacity":"0.8"}},
  {"command":"set","path":"/slide[5]/shape[2]","props":{"x":"8cm","y":"3cm","width":"6cm","height":"6cm","opacity":"1.0"}},
  {"command":"set","path":"/slide[5]/shape[3]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[5]/shape[4]","props":{"x":"14cm","y":"15cm","width":"6cm"}},
  {"command":"set","path":"/slide[5]/shape[5]","props":{"x":"16cm","y":"5cm","width":"2cm","height":"2cm"}},
  {"command":"set","path":"/slide[5]/shape[21]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[22]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[23]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[24]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[25]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[26]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[27]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[28]","props":{"x":"36cm"}},

  {"command":"add","parent":"/slide[5]","type":"shape","props":{"name":"s5-title","text":"接受现实吧","font":"Source Han Sans","size":"64","bold":"true","color":"2A201A","align":"center","x":"4cm","y":"6cm","width":"26cm","height":"4cm"}},
  {"command":"add","parent":"/slide[5]","type":"shape","props":{"name":"s5-sub","text":"今天你给主子开罐头了吗？","font":"Source Han Sans","size":"32","color":"4A3B32","align":"center","x":"4cm","y":"11cm","width":"26cm","height":"2cm"}}
]' | officecli batch "$FILE"

echo "Done."''',

    'lifestyle--cat-secret-life': '''
#!/bin/bash
set -e

# Configuration
PPT_FILE="Cat-Secret-Life.pptx"
FONT_MAIN="思源黑体"
FONT_TITLE="Montserrat"
BG_COLOR="FFF8E7"
TEXT_DARK="3D3B3C"
TEXT_LIGHT="FFFFFF"
C_ORANGE="FF8A65"
C_YELLOW="FFD54F"
C_TEAL="4DB6AC"
C_DARK="3D3B3C"

# 1. Create file and Slide 1 (Hero)
echo "Creating PPT and Slide 1..."
officecli create "$PPT_FILE"
officecli add "$PPT_FILE" '/' --type slide --prop layout=blank --prop background="$BG_COLOR"

# ----- Define Scene Actors (Create on Slide 1) -----
# !!blob-main (Large background blob)
officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="blob-main" --prop preset=roundRect --prop fill="$C_ORANGE" --prop opacity=0.15 --prop x=18cm --prop y=5cm --prop width=20cm --prop height=15cm --prop rotation=15

# !!dot-orange (Large orange circle)
officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="dot-orange" --prop preset=ellipse --prop fill="$C_ORANGE" --prop x=0cm --prop y=12cm --prop width=12cm --prop height=12cm

# !!dot-yellow (Medium yellow circle)
officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="dot-yellow" --prop preset=ellipse --prop fill="$C_YELLOW" --prop x=26cm --prop y=0cm --prop width=8cm --prop height=8cm

# !!line-teal (Teal accent pill)
officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="line-teal" --prop preset=roundRect --prop fill="$C_TEAL" --prop x=6cm --prop y=4cm --prop width=3cm --prop height=0.6cm --prop rotation=-20

# !!tri-dark (Dark triangle)
officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="tri-dark" --prop preset=triangle --prop fill="$C_DARK" --prop opacity=0.8 --prop x=30cm --prop y=15cm --prop width=3cm --prop height=3cm --prop rotation=45

# !!accent-star (Star)
officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="accent-star" --prop preset=star5 --prop fill="$C_YELLOW" --prop x=10cm --prop y=16cm --prop width=2cm --prop height=2cm --prop rotation=10


# ----- Slide 1 Content Actors -----
# Hero Title
officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="hero-title" --prop text="猫的秘密生活" --prop font="$FONT_MAIN" --prop size=72 --prop bold=true --prop color="$TEXT_DARK" --prop align=center --prop valign=middle --prop x=4.4cm --prop y=7cm --prop width=25cm --prop height=3.5cm

# Hero Subtitle
officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="hero-sub" --prop text="人类观察报告（代号：喵星卧底）" --prop font="$FONT_MAIN" --prop size=32 --prop color="$TEXT_DARK" --prop opacity=0.8 --prop align=center --prop valign=middle --prop x=4.4cm --prop y=10.5cm --prop width=25cm --prop height=2cm

# ----- Define other slides' content actors (Ghosted on Slide 1) -----
# S2 Statement text
officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="statement-main" --prop text="你以为你在养猫？
其实是猫在观察你。" --prop font="$FONT_MAIN" --prop size=54 --prop bold=true --prop color="$TEXT_LIGHT" --prop align=center --prop valign=middle --prop x=36cm --prop y=6cm --prop width=26cm --prop height=6cm

# S3 Pillars content
for i in {1..3}; do
  officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="pillar-bg-$i" --prop preset=roundRect --prop fill="$C_DARK" --prop opacity=0.05 --prop x=36cm --prop y=8cm --prop width=8cm --prop height=8cm
  officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="pillar-num-$i" --prop text="0$i" --prop font="$FONT_TITLE" --prop size=48 --prop bold=true --prop color="$C_ORANGE" --prop align=left --prop x=36cm --prop y=8cm --prop width=6cm --prop height=2cm
  officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="pillar-title-$i" --prop font="$FONT_MAIN" --prop size=28 --prop bold=true --prop color="$TEXT_DARK" --prop align=left --prop x=36cm --prop y=10cm --prop width=6cm --prop height=1.5cm
  officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="pillar-desc-$i" --prop font="$FONT_MAIN" --prop size=16 --prop color="$TEXT_DARK" --prop align=left --prop x=36cm --prop y=11.5cm --prop width=6.5cm --prop height=4cm
done
officecli set "$PPT_FILE" '/slide[1]/shape[12]' --prop text="日常充电"
officecli set "$PPT_FILE" '/slide[1]/shape[13]' --prop text="寻找阳光最充足的位置，进入深度休眠模式，补充能量。"
officecli set "$PPT_FILE" '/slide[1]/shape[16]' --prop text="幻觉狩猎"
officecli set "$PPT_FILE" '/slide[1]/shape[17]' --prop text="在夜深人静时，捕捉人类看不见的“空气猎物”。"
officecli set "$PPT_FILE" '/slide[1]/shape[20]' --prop text="高冷监视"
officecli set "$PPT_FILE" '/slide[1]/shape[21]' --prop text="居高临下，用充满智慧的眼神审视人类的愚蠢行为。"

# S4 Evidence content
officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="evi-num" --prop text="70%" --prop font="$FONT_TITLE" --prop size=120 --prop bold=true --prop color="$TEXT_LIGHT" --prop align=right --prop x=36cm --prop y=5cm --prop width=15cm --prop height=6cm
officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="evi-desc" --prop text="猫咪一生中睡觉的时间占比。剩余时间里，一半在舔毛，一半在夜间跑酷。" --prop font="$FONT_MAIN" --prop size=24 --prop color="$TEXT_LIGHT" --prop align=left --prop x=36cm --prop y=11cm --prop width=12cm --prop height=5cm

# S5 Comparison content
officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="comp-title-l" --prop text="狗" --prop font="$FONT_MAIN" --prop size=64 --prop bold=true --prop color="$TEXT_LIGHT" --prop align=center --prop x=36cm --prop y=4cm --prop width=10cm --prop height=3cm
officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="comp-desc-l" --prop text="“你是神！
你给我吃的！”" --prop font="$FONT_MAIN" --prop size=32 --prop color="$TEXT_LIGHT" --prop align=center --prop x=36cm --prop y=8cm --prop width=12cm --prop height=5cm
officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="comp-title-r" --prop text="猫" --prop font="$FONT_MAIN" --prop size=64 --prop bold=true --prop color="$TEXT_LIGHT" --prop align=center --prop x=36cm --prop y=4cm --prop width=10cm --prop height=3cm
officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="comp-desc-r" --prop text="“我是神！
你给我吃的！”" --prop font="$FONT_MAIN" --prop size=32 --prop color="$TEXT_LIGHT" --prop align=center --prop x=36cm --prop y=8cm --prop width=12cm --prop height=5cm

# S6 CTA content
officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="cta-title" --prop text="观察结束，去开罐头吧！" --prop font="$FONT_MAIN" --prop size=54 --prop bold=true --prop color="$TEXT_DARK" --prop align=center --prop x=36cm --prop y=6cm --prop width=26cm --prop height=3cm
officecli add "$PPT_FILE" '/slide[1]' --type shape --prop name="cta-sub" --prop text="毕竟，主子已经等急了。" --prop font="$FONT_MAIN" --prop size=28 --prop color="$TEXT_DARK" --prop opacity=0.8 --prop align=center --prop x=36cm --prop y=10cm --prop width=26cm --prop height=2cm

echo "Slide 1 built."


# =================================================================================
# 2. Slide 2: Statement (The core realization)
# =================================================================================
echo "Building Slide 2..."
officecli add "$PPT_FILE" '/' --from '/slide[1]'
officecli set "$PPT_FILE" '/slide[2]' --prop transition=morph

# Move Hero content off-screen
officecli set "$PPT_FILE" '/slide[2]/shape[7]' --prop x=36cm --prop y=0cm # hero-title
officecli set "$PPT_FILE" '/slide[2]/shape[8]' --prop x=36cm --prop y=5cm # hero-sub

# Bring Statement content on-screen
officecli set "$PPT_FILE" '/slide[2]/shape[9]' --prop x=3.9cm --prop y=6cm

# Morph Scene Actors for Statement (Dark background via huge dark tri)
# Make !!tri-dark huge and cover the screen to create a dark background
officecli set "$PPT_FILE" '/slide[2]/shape[5]' --prop preset=rect --prop x=0cm --prop y=0cm --prop width=45cm --prop height=30cm --prop rotation=0 --prop opacity=1

# Adjust other scene actors
officecli set "$PPT_FILE" '/slide[2]/shape[1]' --prop x=0cm --prop y=12cm --prop width=10cm --prop height=10cm --prop rotation=45 --prop opacity=0.3 # blob
officecli set "$PPT_FILE" '/slide[2]/shape[2]' --prop x=28cm --prop y=2cm --prop width=8cm --prop height=8cm --prop opacity=0.5 # dot-orange
officecli set "$PPT_FILE" '/slide[2]/shape[3]' --prop x=5cm --prop y=0cm --prop width=12cm --prop height=12cm --prop opacity=0.2 # dot-yellow
officecli set "$PPT_FILE" '/slide[2]/shape[4]' --prop x=16cm --prop y=15cm --prop width=4cm --prop height=0.6cm --prop rotation=0 # line-teal
officecli set "$PPT_FILE" '/slide[2]/shape[6]' --prop x=25cm --prop y=14cm --prop rotation=90 # accent-star


# =================================================================================
# 3. Slide 3: Pillars (Three core behaviors)
# =================================================================================
echo "Building Slide 3..."
officecli add "$PPT_FILE" '/' --from '/slide[2]'
officecli set "$PPT_FILE" '/slide[3]' --prop transition=morph

# Ghost previous content
officecli set "$PPT_FILE" '/slide[3]/shape[9]' --prop x=36cm --prop y=0cm # statement-main

# Scene Actors Morph: Revert dark bg, structure nicely
officecli set "$PPT_FILE" '/slide[3]/shape[5]' --prop preset=triangle --prop x=28cm --prop y=0cm --prop width=8cm --prop height=8cm --prop rotation=180 --prop opacity=0.1 # tri-dark returns to normal
officecli set "$PPT_FILE" '/slide[3]/shape[1]' --prop x=2cm --prop y=2cm --prop width=30cm --prop height=15cm --prop rotation=0 --prop opacity=0.05 # blob-main
officecli set "$PPT_FILE" '/slide[3]/shape[2]' --prop x=0cm --prop y=0cm --prop width=15cm --prop height=15cm --prop opacity=0.1 # dot-orange
officecli set "$PPT_FILE" '/slide[3]/shape[3]' --prop x=25cm --prop y=14cm --prop width=12cm --prop height=12cm --prop opacity=0.1 # dot-yellow
officecli set "$PPT_FILE" '/slide[3]/shape[4]' --prop x=1.5cm --prop y=1.5cm --prop width=30cm --prop height=0.2cm --prop rotation=0 # line-teal spans top
officecli set "$PPT_FILE" '/slide[3]/shape[6]' --prop x=2cm --prop y=16cm --prop rotation=180 # accent-star

# Bring Pillars on-screen
# Col 1: x=2.5cm
officecli set "$PPT_FILE" '/slide[3]/shape[10]' --prop x=2.5cm --prop y=4cm --prop width=8cm --prop height=12cm
officecli set "$PPT_FILE" '/slide[3]/shape[11]' --prop x=3.5cm --prop y=5cm --prop animation=fade-entrance-400-with
officecli set "$PPT_FILE" '/slide[3]/shape[12]' --prop x=3.5cm --prop y=7cm --prop animation=fade-entrance-400-with
officecli set "$PPT_FILE" '/slide[3]/shape[13]' --prop x=3.5cm --prop y=8.5cm --prop width=6cm --prop height=6cm --prop animation=fade-entrance-400-with

# Col 2: x=12.5cm
officecli set "$PPT_FILE" '/slide[3]/shape[14]' --prop x=12.9cm --prop y=4cm --prop width=8cm --prop height=12cm
officecli set "$PPT_FILE" '/slide[3]/shape[15]' --prop x=13.9cm --prop y=5cm --prop animation=fade-entrance-400-with-delay=100
officecli set "$PPT_FILE" '/slide[3]/shape[16]' --prop x=13.9cm --prop y=7cm --prop animation=fade-entrance-400-with-delay=100
officecli set "$PPT_FILE" '/slide[3]/shape[17]' --prop x=13.9cm --prop y=8.5cm --prop width=6cm --prop height=6cm --prop animation=fade-entrance-400-with-delay=100

# Col 3: x=22.5cm
officecli set "$PPT_FILE" '/slide[3]/shape[18]' --prop x=23.3cm --prop y=4cm --prop width=8cm --prop height=12cm
officecli set "$PPT_FILE" '/slide[3]/shape[19]' --prop x=24.3cm --prop y=5cm --prop animation=fade-entrance-400-with-delay=200
officecli set "$PPT_FILE" '/slide[3]/shape[20]' --prop x=24.3cm --prop y=7cm --prop animation=fade-entrance-400-with-delay=200
officecli set "$PPT_FILE" '/slide[3]/shape[21]' --prop x=24.3cm --prop y=8.5cm --prop width=6cm --prop height=6cm --prop animation=fade-entrance-400-with-delay=200


# =================================================================================
# 4. Slide 4: Evidence (Data Reveal)
# =================================================================================
echo "Building Slide 4..."
officecli add "$PPT_FILE" '/' --from '/slide[3]'
officecli set "$PPT_FILE" '/slide[4]' --prop transition=morph

# Ghost Pillars
for i in {10..21}; do
  officecli set "$PPT_FILE" "/slide[4]/shape[$i]" --prop x=36cm
done

# Scene Actors Morph: Asymmetric data highlight
# Use !!blob-main as dark background on the left
officecli set "$PPT_FILE" '/slide[4]/shape[1]' --prop fill="$C_TEAL" --prop x=0cm --prop y=0cm --prop width=25cm --prop height=30cm --prop rotation=0 --prop opacity=1

# Other actors
officecli set "$PPT_FILE" '/slide[4]/shape[2]' --prop x=24cm --prop y=10cm --prop width=8cm --prop height=8cm --prop opacity=1 # dot-orange
officecli set "$PPT_FILE" '/slide[4]/shape[3]' --prop x=28cm --prop y=2cm --prop width=4cm --prop height=4cm --prop opacity=1 # dot-yellow
officecli set "$PPT_FILE" '/slide[4]/shape[4]' --prop x=18cm --prop y=4cm --prop width=6cm --prop height=0.6cm --prop rotation=45 # line-teal
officecli set "$PPT_FILE" '/slide[4]/shape[5]' --prop x=20cm --prop y=14cm --prop width=4cm --prop height=4cm --prop rotation=90 # tri-dark
officecli set "$PPT_FILE" '/slide[4]/shape[6]' --prop x=30cm --prop y=16cm --prop rotation=30 # accent-star

# Bring Evidence on-screen
officecli set "$PPT_FILE" '/slide[4]/shape[22]' --prop x=1cm --prop y=4cm --prop align=center # evi-num (over teal background)
officecli set "$PPT_FILE" '/slide[4]/shape[23]' --prop x=1cm --prop y=12cm --prop width=13cm --prop align=center # evi-desc (over teal background)


# =================================================================================
# 5. Slide 5: Comparison (Dog vs. Cat)
# =================================================================================
echo "Building Slide 5..."
officecli add "$PPT_FILE" '/' --from '/slide[4]'
officecli set "$PPT_FILE" '/slide[5]' --prop transition=morph

# Ghost Evidence
officecli set "$PPT_FILE" '/slide[5]/shape[22]' --prop x=36cm
officecli set "$PPT_FILE" '/slide[5]/shape[23]' --prop x=36cm

# Scene Actors Morph: Split 50/50
# !!blob-main (Teal) goes left
officecli set "$PPT_FILE" '/slide[5]/shape[1]' --prop preset=rect --prop fill="$C_TEAL" --prop x=0cm --prop y=0cm --prop width=16.9cm --prop height=19.05cm --prop opacity=1

# !!dot-orange morphs into huge right background
officecli set "$PPT_FILE" '/slide[5]/shape[2]' --prop preset=rect --prop x=16.9cm --prop y=0cm --prop width=17cm --prop height=19.05cm --prop rotation=0 --prop opacity=1

# Other actors small/scattered
officecli set "$PPT_FILE" '/slide[5]/shape[3]' --prop x=14cm --prop y=16cm --prop width=6cm --prop height=6cm --prop opacity=0.3 # dot-yellow
officecli set "$PPT_FILE" '/slide[5]/shape[4]' --prop x=16.9cm --prop y=0cm --prop width=0.4cm --prop height=19cm --prop rotation=0 --prop fill="$TEXT_LIGHT" # line-teal becomes divider
officecli set "$PPT_FILE" '/slide[5]/shape[5]' --prop x=2cm --prop y=2cm --prop width=3cm --prop height=3cm --prop rotation=180 --prop opacity=0.3 # tri-dark
officecli set "$PPT_FILE" '/slide[5]/shape[6]' --prop x=30cm --prop y=2cm --prop opacity=0.3 # accent-star

# Bring Comparison on-screen
# Left (Dog)
officecli set "$PPT_FILE" '/slide[5]/shape[24]' --prop x=3.5cm --prop y=4cm # comp-title-l
officecli set "$PPT_FILE" '/slide[5]/shape[25]' --prop x=2.5cm --prop y=9cm # comp-desc-l
# Right (Cat)
officecli set "$PPT_FILE" '/slide[5]/shape[26]' --prop x=20cm --prop y=4cm # comp-title-r
officecli set "$PPT_FILE" '/slide[5]/shape[27]' --prop x=19cm --prop y=9cm # comp-desc-r


# =================================================================================
# 6. Slide 6: CTA (Conclusion)
# =================================================================================
echo "Building Slide 6..."
officecli add "$PPT_FILE" '/' --from '/slide[5]'
officecli set "$PPT_FILE" '/slide[6]' --prop transition=morph

# Ghost Comparison
officecli set "$PPT_FILE" '/slide[6]/shape[24]' --prop x=36cm
officecli set "$PPT_FILE" '/slide[6]/shape[25]' --prop x=36cm
officecli set "$PPT_FILE" '/slide[6]/shape[26]' --prop x=36cm
officecli set "$PPT_FILE" '/slide[6]/shape[27]' --prop x=36cm

# Scene Actors Morph: Back to Hero-like but warmer/inviting
officecli set "$PPT_FILE" '/slide[6]/shape[1]' --prop preset=roundRect --prop fill="$C_YELLOW" --prop x=6.9cm --prop y=4cm --prop width=20cm --prop height=11cm --prop rotation=0 --prop opacity=0.2 # blob-main
officecli set "$PPT_FILE" '/slide[6]/shape[2]' --prop preset=ellipse --prop fill="$C_ORANGE" --prop x=28cm --prop y=12cm --prop width=10cm --prop height=10cm --prop rotation=0 --prop opacity=0.8 # dot-orange
officecli set "$PPT_FILE" '/slide[6]/shape[3]' --prop x=0cm --prop y=0cm --prop width=8cm --prop height=8cm --prop opacity=0.8 # dot-yellow
officecli set "$PPT_FILE" '/slide[6]/shape[4]' --prop x=20cm --prop y=15cm --prop width=6cm --prop height=0.6cm --prop fill="$C_TEAL" --prop rotation=-10 # line-teal
officecli set "$PPT_FILE" '/slide[6]/shape[5]' --prop preset=triangle --prop x=5cm --prop y=15cm --prop width=4cm --prop height=4cm --prop rotation=45 --prop opacity=0.5 # tri-dark
officecli set "$PPT_FILE" '/slide[6]/shape[6]' --prop x=16cm --prop y=3cm --prop width=3cm --prop height=3cm --prop rotation=45 --prop opacity=1 # accent-star

# Bring CTA on-screen
officecli set "$PPT_FILE" '/slide[6]/shape[28]' --prop x=3.9cm --prop y=6.5cm
officecli set "$PPT_FILE" '/slide[6]/shape[29]' --prop x=3.9cm --prop y=9.5cm

echo "Validating PPT..."
officecli validate "$PPT_FILE"
officecli view "$PPT_FILE" outline

echo "Done! Presentation is ready: $PPT_FILE"
''',

    'product--geminicli-timetravel': '''
#!/bin/bash
set -e
OUTPUT="TimeTravel.pptx"
echo "Creating $OUTPUT ..."
officecli create "$OUTPUT"

# Create 6 slides
for i in 1 2 3 4 5 6; do
  officecli add "$OUTPUT" '/' --type slide --prop layout=blank --prop background=0B0F19
done

# Font settings
FONT_EN="Montserrat"
FONT_CN="Microsoft YaHei"
COLOR_TEXT="FFFFFF"
COLOR_SUB="8B949E"
COLOR_ACCENT="58A6FF"
COLOR_ACCENT2="7C3AED"
COLOR_DARK="161B22"

# --- SLIDE 1 (Hero) ---
# Create scene actors
officecli add "$OUTPUT" '/slide[1]' --type shape --name="scene-circle" --prop preset=ellipse \
  --prop fill=$COLOR_ACCENT2 --prop opacity=0.15 --prop softEdge=60 \
  --prop x=18cm --prop y=4cm --prop width=15cm --prop height=15cm

officecli add "$OUTPUT" '/slide[1]' --type shape --name="scene-slash" --prop preset=diamond \
  --prop fill=$COLOR_ACCENT --prop opacity=0.1 --prop \
  --prop x=4cm --prop y=10cm --prop width=8cm --prop height=8cm --prop rotation=15

officecli add "$OUTPUT" '/slide[1]' --type shape --name="scene-line-top" --prop preset=rect \
  --prop fill=$COLOR_ACCENT --prop opacity=0.8 \
  --prop x=2cm --prop y=2cm --prop width=10cm --prop height=0.1cm

officecli add "$OUTPUT" '/slide[1]' --type shape --name="scene-box" --prop preset=rect \
  --prop fill=none --prop line=$COLOR_ACCENT --prop lineWidth=2pt --prop opacity=0.3 \
  --prop x=22cm --prop y=10cm --prop width=6cm --prop height=6cm --prop rotation=45

# Content Actors S1
officecli add "$OUTPUT" '/slide[1]' --type shape --name="s1-title" \
  --prop text="时空旅行指南" --prop font="$FONT_CN" --prop size=56 --prop color=$COLOR_TEXT \
  --prop align=left --prop x=2cm --prop y=6cm --prop width=25cm --prop height=2cm --prop fill=none

officecli add "$OUTPUT" '/slide[1]' --type shape --name="s1-subtitle" \
  --prop text="从 理 论 到 实 践" --prop font="$FONT_CN" --prop size=28 --prop color=$COLOR_ACCENT \
  --prop align=left --prop x=2cm --prop y=8.5cm --prop width=25cm --prop height=1.5cm --prop fill=none

officecli add "$OUTPUT" '/slide[1]' --type shape --name="s1-desc" \
  --prop text="开启你的第四维之旅，了解关于时间的终极奥秘" --prop font="$FONT_CN" --prop size=16 --prop color=$COLOR_SUB \
  --prop align=left --prop x=2cm --prop y=10.5cm --prop width=25cm --prop height=1cm --prop fill=none

# Pre-create Content Actors for later slides (Ghosted)
# S2
officecli add "$OUTPUT" '/slide[1]' --type shape --name="s2-statement" \
  --prop text="“时间不是一条单行道，而是一片可以航行的海洋。”" --prop font="$FONT_CN" --prop size=40 --prop color=$COLOR_TEXT \
  --prop align=center --prop x=36cm --prop y=6cm --prop width=28cm --prop height=3cm --prop fill=none
officecli add "$OUTPUT" '/slide[1]' --type shape --name="s2-desc" \
  --prop text="爱因斯坦的相对论打破了绝对时空观" --prop font="$FONT_CN" --prop size=20 --prop color=$COLOR_ACCENT \
  --prop align=center --prop x=36cm --prop y=10cm --prop width=20cm --prop height=1cm --prop fill=none

# S3
for j in 1 2 3; do
  officecli add "$OUTPUT" '/slide[1]' --type shape --name="s3-card-$j" --prop preset=roundRect \
    --prop fill=$COLOR_DARK --prop opacity=0 --prop x=36cm --prop y=6cm --prop width=9cm --prop height=10cm
  officecli add "$OUTPUT" '/slide[1]' --type shape --name="s3-title-$j" \
    --prop text="理论" --prop font="$FONT_CN" --prop size=24 --prop color=$COLOR_TEXT --prop align=left \
    --prop x=36cm --prop y=7cm --prop width=8cm --prop height=1cm --prop fill=none --prop opacity=0
  officecli add "$OUTPUT" '/slide[1]' --type shape --name="s3-desc-$j" \
    --prop text="描述" --prop font="$FONT_CN" --prop size=16 --prop color=$COLOR_SUB --prop align=left \
    --prop x=36cm --prop y=9cm --prop width=8cm --prop height=5cm --prop fill=none --prop opacity=0
done
officecli add "$OUTPUT" '/slide[1]' --type shape --name="s3-header" \
  --prop text="三大理论基石" --prop font="$FONT_CN" --prop size=36 --prop color=$COLOR_TEXT \
  --prop align=left --prop x=36cm --prop y=2cm --prop width=15cm --prop height=1.5cm --prop fill=none

# S4
officecli add "$OUTPUT" '/slide[1]' --type shape --name="s4-data-bg" --prop preset=roundRect \
  --prop fill=$COLOR_ACCENT2 --prop opacity=0 \
  --prop x=36cm --prop y=4cm --prop width=15cm --prop height=10cm
officecli add "$OUTPUT" '/slide[1]' --type shape --name="s4-data-num" \
  --prop text="38微秒" --prop font="$FONT_CN" --prop size=60 --prop color=$COLOR_TEXT \
  --prop align=center --prop x=36cm --prop y=6cm --prop width=15cm --prop height=2cm --prop fill=none --prop opacity=0
officecli add "$OUTPUT" '/slide[1]' --type shape --name="s4-data-desc" \
  --prop text="GPS 卫星每天比地面快的时间\n必须修正否则定位失效" --prop font="$FONT_CN" --prop size=18 --prop color=$COLOR_TEXT \
  --prop align=center --prop x=36cm --prop y=9cm --prop width=15cm --prop height=2cm --prop fill=none --prop opacity=0

# S5 Timeline
for j in 1 2 3 4; do
  officecli add "$OUTPUT" '/slide[1]' --type shape --name="s5-dot-$j" --prop preset=ellipse \
    --prop fill=$COLOR_ACCENT --prop x=36cm --prop y=8cm --prop width=1cm --prop height=1cm --prop opacity=0
  officecli add "$OUTPUT" '/slide[1]' --type shape --name="s5-year-$j" \
    --prop text="20世纪" --prop font="$FONT_CN" --prop size=24 --prop color=$COLOR_TEXT --prop align=center \
    --prop x=36cm --prop y=6cm --prop width=6cm --prop height=1.5cm --prop fill=none --prop opacity=0
  officecli add "$OUTPUT" '/slide[1]' --type shape --name="s5-desc-$j" \
    --prop text="理论奠基" --prop font="$FONT_CN" --prop size=14 --prop color=$COLOR_SUB --prop align=center \
    --prop x=36cm --prop y=9.5cm --prop width=6cm --prop height=3cm --prop fill=none --prop opacity=0
done

# S6 CTA
officecli add "$OUTPUT" '/slide[1]' --type shape --name="s6-cta-title" \
  --prop text="保持好奇，探索未知" --prop font="$FONT_CN" --prop size=48 --prop color=$COLOR_TEXT \
  --prop align=center --prop x=36cm --prop y=7cm --prop width=25cm --prop height=2cm --prop fill=none
officecli add "$OUTPUT" '/slide[1]' --type shape --name="s6-cta-desc" \
  --prop text="属于人类的时空时代终将到来" --prop font="$FONT_CN" --prop size=20 --prop color=$COLOR_ACCENT \
  --prop align=center --prop x=36cm --prop y=10cm --prop width=25cm --prop height=1cm --prop fill=none

# --- SLIDE 2 (Statement) ---
officecli add "$OUTPUT" '/' --from '/slide[1]'
officecli set "$OUTPUT" '/slide[2]' --prop transition=morph

# Move S1 content out
officecli set "$OUTPUT" '/slide[2]' --name="s1-title" --prop x=36cm --prop y=0cm
officecli set "$OUTPUT" '/slide[2]' --name="s1-subtitle" --prop x=36cm --prop y=2cm
officecli set "$OUTPUT" '/slide[2]' --name="s1-desc" --prop x=36cm --prop y=4cm

# Move Scene actors around
officecli set "$OUTPUT" '/slide[2]' --name="scene-circle" 
  --prop x=4cm --prop y=2cm --prop width=25cm --prop height=25cm --prop opacity=0.08
officecli set "$OUTPUT" '/slide[2]' --name="scene-slash" 
  --prop x=24cm --prop y=2cm --prop rotation=45
officecli set "$OUTPUT" '/slide[2]' --name="scene-line-top" 
  --prop x=11cm --prop y=4cm --prop width=12cm
officecli set "$OUTPUT" '/slide[2]' --name="scene-box" 
  --prop x=4cm --prop y=14cm --prop rotation=15

# Bring S2 content in
officecli set "$OUTPUT" '/slide[2]' --name="s2-statement" 
  --prop x=3cm --prop y=6cm
officecli set "$OUTPUT" '/slide[2]' --name="s2-desc" 
  --prop x=7cm --prop y=11cm

# --- SLIDE 3 (Pillars) ---
officecli add "$OUTPUT" '/' --from '/slide[2]'
officecli set "$OUTPUT" '/slide[3]' --prop transition=morph

# Move S2 out
officecli set "$OUTPUT" '/slide[3]' --name="s2-statement" --prop x=36cm --prop y=1cm
officecli set "$OUTPUT" '/slide[3]' --name="s2-desc" --prop x=36cm --prop y=4cm

# Scene actors change
officecli set "$OUTPUT" '/slide[3]' --name="scene-circle" 
  --prop x=2cm --prop y=-5cm --prop width=30cm --prop height=30cm --prop opacity=0.05
officecli set "$OUTPUT" '/slide[3]' --name="scene-slash" 
  --prop x=2cm --prop y=2cm --prop rotation=90
officecli set "$OUTPUT" '/slide[3]' --name="scene-box" 
  --prop x=28cm --prop y=2cm --prop rotation=90

# Bring S3 header
officecli set "$OUTPUT" '/slide[3]' --name="s3-header" 
  --prop x=2cm --prop y=1.5cm

# Bring S3 Pillars in
officecli set "$OUTPUT" '/slide[3]' --name="s3-card-1" 
  --prop x=2cm --prop y=5cm --prop opacity=0.12 --prop animation=fade-entrance-300-with
officecli set "$OUTPUT" '/slide[3]' --name="s3-title-1" 
  --prop text="① 狭义相对论" --prop x=2.5cm --prop y=6cm --prop opacity=1 --prop animation=fade-entrance-400-with
officecli set "$OUTPUT" '/slide[3]' --name="s3-desc-1" 
  --prop text="速度越快，时间越慢。
光速旅行是通往未来的单程票。" 
  --prop x=2.5cm --prop y=8cm --prop opacity=1 --prop animation=fade-entrance-500-with

officecli set "$OUTPUT" '/slide[3]' --name="s3-card-2" 
  --prop x=12.5cm --prop y=5cm --prop opacity=0.12 --prop animation=fade-entrance-300-with
officecli set "$OUTPUT" '/slide[3]' --name="s3-title-2" 
  --prop text="② 广义相对论" --prop x=13cm --prop y=6cm --prop opacity=1 --prop animation=fade-entrance-400-with
officecli set "$OUTPUT" '/slide[3]' --name="s3-desc-2" 
  --prop text="引力扭曲时空。
黑洞边缘或虫洞可能是穿越时空的捷径。" 
  --prop x=13cm --prop y=8cm --prop opacity=1 --prop animation=fade-entrance-500-with

officecli set "$OUTPUT" '/slide[3]' --name="s3-card-3" 
  --prop x=23cm --prop y=5cm --prop opacity=0.12 --prop animation=fade-entrance-300-with
officecli set "$OUTPUT" '/slide[3]' --name="s3-title-3" 
  --prop text="③ 量子纠缠" --prop x=23.5cm --prop y=6cm --prop opacity=1 --prop animation=fade-entrance-400-with
officecli set "$OUTPUT" '/slide[3]' --name="s3-desc-3" 
  --prop text="微观层面的超距作用，
为超越光速的信息传输提供遐想。" 
  --prop x=23.5cm --prop y=8cm --prop opacity=1 --prop animation=fade-entrance-500-with

# --- SLIDE 4 (Evidence) ---
officecli add "$OUTPUT" '/' --from '/slide[3]'
officecli set "$OUTPUT" '/slide[4]' --prop transition=morph

# Move S3 out
officecli set "$OUTPUT" '/slide[4]' --name="s3-header" --prop x=36cm --prop y=2cm
officecli set "$OUTPUT" '/slide[4]' --name="s3-card-1" --prop x=36cm --prop opacity=0
officecli set "$OUTPUT" '/slide[4]' --name="s3-title-1" --prop x=36cm --prop opacity=0
officecli set "$OUTPUT" '/slide[4]' --name="s3-desc-1" --prop x=36cm --prop opacity=0
officecli set "$OUTPUT" '/slide[4]' --name="s3-card-2" --prop x=36cm --prop opacity=0
officecli set "$OUTPUT" '/slide[4]' --name="s3-title-2" --prop x=36cm --prop opacity=0
officecli set "$OUTPUT" '/slide[4]' --name="s3-desc-2" --prop x=36cm --prop opacity=0
officecli set "$OUTPUT" '/slide[4]' --name="s3-card-3" --prop x=36cm --prop opacity=0
officecli set "$OUTPUT" '/slide[4]' --name="s3-title-3" --prop x=36cm --prop opacity=0
officecli set "$OUTPUT" '/slide[4]' --name="s3-desc-3" --prop x=36cm --prop opacity=0

# Scene actors change
officecli set "$OUTPUT" '/slide[4]' --name="scene-circle" 
  --prop x=18cm --prop y=0cm --prop width=20cm --prop height=20cm --prop opacity=0.1
officecli set "$OUTPUT" '/slide[4]' --name="scene-slash" 
  --prop x=5cm --prop y=12cm --prop rotation=135
officecli set "$OUTPUT" '/slide[4]' --name="scene-box" 
  --prop x=2cm --prop y=5cm --prop rotation=180

# Bring S4 evidence in
officecli set "$OUTPUT" '/slide[4]' --name="s4-data-bg" 
  --prop x=2cm --prop y=4cm --prop opacity=0.2
officecli set "$OUTPUT" '/slide[4]' --name="s4-data-num" 
  --prop x=2cm --prop y=6cm --prop opacity=1
officecli set "$OUTPUT" '/slide[4]' --name="s4-data-desc" 
  --prop x=2cm --prop y=9cm --prop opacity=1

# --- SLIDE 5 (Timeline) ---
officecli add "$OUTPUT" '/' --from '/slide[4]'
officecli set "$OUTPUT" '/slide[5]' --prop transition=morph

# Move S4 out
officecli set "$OUTPUT" '/slide[5]' --name="s4-data-bg" --prop x=36cm --prop opacity=0
officecli set "$OUTPUT" '/slide[5]' --name="s4-data-num" --prop x=36cm --prop opacity=0
officecli set "$OUTPUT" '/slide[5]' --name="s4-data-desc" --prop x=36cm --prop opacity=0

# Scene actors change
officecli set "$OUTPUT" '/slide[5]' --name="scene-circle" 
  --prop x=0cm --prop y=0cm --prop width=10cm --prop height=10cm --prop opacity=0.15
officecli set "$OUTPUT" '/slide[5]' --name="scene-line-top" 
  --prop x=4cm --prop y=8.5cm --prop width=26cm --prop height=0.2cm --prop opacity=0.3
officecli set "$OUTPUT" '/slide[5]' --name="scene-box" 
  --prop x=15cm --prop y=6cm --prop width=4cm --prop height=4cm --prop rotation=0

# Bring S5 timeline in
officecli set "$OUTPUT" '/slide[5]' --name="s5-dot-1" 
  --prop x=5cm --prop y=8cm --prop opacity=1
officecli set "$OUTPUT" '/slide[5]' --name="s5-year-1" 
  --prop text="20世纪" --prop x=2.5cm --prop y=6cm --prop opacity=1
officecli set "$OUTPUT" '/slide[5]' --name="s5-desc-1" 
  --prop text="理论奠基
相对论与量子力学" --prop x=2.5cm --prop y=9.5cm --prop opacity=1

officecli set "$OUTPUT" '/slide[5]' --name="s5-dot-2" 
  --prop x=12cm --prop y=8cm --prop opacity=1
officecli set "$OUTPUT" '/slide[5]' --name="s5-year-2" 
  --prop text="21世纪" --prop x=9.5cm --prop y=6cm --prop opacity=1
officecli set "$OUTPUT" '/slide[5]' --name="s5-desc-2" 
  --prop text="实证阶段
微观粒子验证
时间膨胀" --prop x=9.5cm --prop y=9.5cm --prop opacity=1

officecli set "$OUTPUT" '/slide[5]' --name="s5-dot-3" 
  --prop x=19cm --prop y=8cm --prop opacity=1
officecli set "$OUTPUT" '/slide[5]' --name="s5-year-3" 
  --prop text="22世纪" --prop x=16.5cm --prop y=6cm --prop opacity=1
officecli set "$OUTPUT" '/slide[5]' --name="s5-desc-3" 
  --prop text="初步探索
光帆飞行器达到
20%光速" --prop x=16.5cm --prop y=9.5cm --prop opacity=1

officecli set "$OUTPUT" '/slide[5]' --name="s5-dot-4" 
  --prop x=26cm --prop y=8cm --prop opacity=1
officecli set "$OUTPUT" '/slide[5]' --name="s5-year-4" 
  --prop text="23世纪" --prop x=23.5cm --prop y=6cm --prop opacity=1
officecli set "$OUTPUT" '/slide[5]' --name="s5-desc-4" 
  --prop text="深空航行
搭乘亚光速飞船
跨越星际" --prop x=23.5cm --prop y=9.5cm --prop opacity=1

# --- SLIDE 6 (CTA) ---
officecli add "$OUTPUT" '/' --from '/slide[5]'
officecli set "$OUTPUT" '/slide[6]' --prop transition=morph

# Move S5 out
for j in 1 2 3 4; do
  officecli set "$OUTPUT" '/slide[6]' --name="s5-dot-$j" --prop x=36cm --prop opacity=0
  officecli set "$OUTPUT" '/slide[6]' --name="s5-year-$j" --prop x=36cm --prop opacity=0
  officecli set "$OUTPUT" '/slide[6]' --name="s5-desc-$j" --prop x=36cm --prop opacity=0
done

# Scene actors change
officecli set "$OUTPUT" '/slide[6]' --name="scene-circle" 
  --prop x=9.5cm --prop y=2cm --prop width=15cm --prop height=15cm --prop opacity=0.2
officecli set "$OUTPUT" '/slide[6]' --name="scene-slash" 
  --prop x=28cm --prop y=12cm --prop rotation=180
officecli set "$OUTPUT" '/slide[6]' --name="scene-line-top" 
  --prop x=12cm --prop y=14cm --prop width=10cm

# Bring CTA in
officecli set "$OUTPUT" '/slide[6]' --name="s6-cta-title" 
  --prop x=4.5cm --prop y=7cm
officecli set "$OUTPUT" '/slide[6]' --name="s6-cta-desc" 
  --prop x=4.5cm --prop y=10cm

echo "Validation..."
officecli validate "$OUTPUT"
officecli view outline "$OUTPUT"
''',

    'productivity--attention-budget': '''
#!/usr/bin/env bash
set -euo pipefail

OUT="注意力预算-把手机时间变成创造时间.pptx"

rm -f "$OUT"

officecli create "$OUT"
officecli add "$OUT" '/' --type slide --prop layout=blank --prop background=0B0F1A --prop transition=morph

cat <<'JSON' | officecli batch "$OUT"
[
  {"command":"set","path":"/slide[1]","props":{"transition":"morph","background":"0B0F1A"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"bg-blob-1","preset":"ellipse","fill":"2BE4A8","opacity":"0.10","x":"0cm","y":"0cm","width":"14cm","height":"14cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"bg-blob-2","preset":"ellipse","fill":"FFB020","opacity":"0.08","x":"22cm","y":"9.8cm","width":"12cm","height":"12cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"bg-slab","preset":"roundRect","fill":"5B6CFF","opacity":"0.07","x":"28cm","y":"2cm","width":"6cm","height":"12cm","rotation":"10"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"bg-line-1","preset":"rect","fill":"FFFFFF","opacity":"0.06","x":"1.2cm","y":"1.0cm","width":"31.47cm","height":"0.2cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"bg-line-2","preset":"rect","fill":"2BE4A8","opacity":"0.08","x":"5cm","y":"15.2cm","width":"25cm","height":"0.2cm","rotation":"-12"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"bg-dot","preset":"ellipse","fill":"FF4D6D","opacity":"0.18","x":"30cm","y":"3cm","width":"1.4cm","height":"1.4cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"bg-ring","preset":"ellipse","fill":"000000","opacity":"0.01","line":"2BE4A8","lineWidth":"2","lineOpacity":"0.22","x":"24cm","y":"0.8cm","width":"8cm","height":"8cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"bg-chip","preset":"roundRect","fill":"FFB020","opacity":"0.10","x":"1.2cm","y":"16.2cm","width":"5.6cm","height":"2.2cm","rotation":"0"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"hero-title","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"注意力预算","font":"PingFang SC","size":"72","bold":"true","color":"FFFFFF","align":"center","valign":"middle","x":"4cm","y":"6.2cm","width":"25.9cm","height":"2.6cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"hero-subtitle","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"把手机时间变成创造时间","font":"PingFang SC","size":"36","bold":"false","color":"B9C6D6","align":"center","valign":"middle","x":"4cm","y":"9.6cm","width":"25.9cm","height":"1.6cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"hero-tagline","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"7 天可执行练习 · 无需任何 App","font":"PingFang SC","size":"18","bold":"false","color":"7F93AA","align":"center","valign":"middle","x":"4cm","y":"12.0cm","width":"25.9cm","height":"1.0cm"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"statement-main","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"你不是没时间，你是被碎片买走了","font":"PingFang SC","size":"56","bold":"true","color":"FFFFFF","align":"center","valign":"middle","x":"36cm","y":"7.2cm","width":"27.4cm","height":"2.4cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"statement-sub","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"每一次下意识打开，都在付一笔“重启成本”","font":"PingFang SC","size":"24","bold":"false","color":"B9C6D6","align":"center","valign":"middle","x":"36cm","y":"11.8cm","width":"23.8cm","height":"1.2cm"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillars-title","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"三件事，立刻把注意力收回来","font":"PingFang SC","size":"40","bold":"true","color":"FFFFFF","align":"left","valign":"middle","x":"36cm","y":"1.2cm","width":"31.47cm","height":"1.4cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar1-bg","preset":"roundRect","fill":"FFFFFF","opacity":"0.06","line":"2BE4A8","lineWidth":"2","lineOpacity":"0.18","x":"36cm","y":"5.0cm","width":"9.6cm","height":"12.6cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar1-title","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"① 识别触发器","font":"PingFang SC","size":"28","bold":"true","color":"FFFFFF","align":"left","valign":"middle","x":"36cm","y":"6.0cm","width":"8.4cm","height":"1.2cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar1-desc","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"把“无聊/压力/等待/社交”写成清单；每次打开前问：我现在要解决什么？","font":"PingFang SC","size":"16","bold":"false","color":"B9C6D6","align":"left","valign":"top","x":"36cm","y":"7.6cm","width":"8.4cm","height":"6.0cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar2-bg","preset":"roundRect","fill":"FFFFFF","opacity":"0.06","line":"2BE4A8","lineWidth":"2","lineOpacity":"0.18","x":"36cm","y":"5.0cm","width":"9.6cm","height":"12.6cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar2-title","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"② 设定预算","font":"PingFang SC","size":"28","bold":"true","color":"FFFFFF","align":"left","valign":"middle","x":"36cm","y":"6.0cm","width":"8.4cm","height":"1.2cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar2-desc","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"给娱乐/社交一个固定额度（示例：30 分钟）；用完就停，把想刷的内容写到明天清单。","font":"PingFang SC","size":"16","bold":"false","color":"B9C6D6","align":"left","valign":"top","x":"36cm","y":"7.6cm","width":"8.4cm","height":"6.0cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar3-bg","preset":"roundRect","fill":"FFFFFF","opacity":"0.06","line":"2BE4A8","lineWidth":"2","lineOpacity":"0.18","x":"36cm","y":"5.0cm","width":"9.6cm","height":"12.6cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar3-title","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"③ 保护深度区","font":"PingFang SC","size":"28","bold":"true","color":"FFFFFF","align":"left","valign":"middle","x":"36cm","y":"6.0cm","width":"8.4cm","height":"1.2cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar3-desc","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"每天至少留 1 个 90 分钟无打扰区块；手机离身，通知改成预约（集中 2 次处理）。","font":"PingFang SC","size":"16","bold":"false","color":"B9C6D6","align":"left","valign":"top","x":"36cm","y":"7.6cm","width":"8.4cm","height":"6.0cm"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"timeline-title","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"一天 4 步流程：把预算花在对的地方","font":"PingFang SC","size":"36","bold":"true","color":"FFFFFF","align":"left","valign":"middle","x":"36cm","y":"1.2cm","width":"31.47cm","height":"1.4cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"timeline-line","preset":"rect","fill":"FFFFFF","opacity":"0.08","x":"36cm","y":"6.1cm","width":"31.47cm","height":"0.2cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"step1-num","preset":"ellipse","fill":"2BE4A8","opacity":"1","text":"1","font":"PingFang SC","size":"20","bold":"true","color":"0B0F1A","align":"center","valign":"middle","x":"36cm","y":"5.3cm","width":"1.6cm","height":"1.6cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"step1-title","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"启动（2 分钟）","font":"PingFang SC","size":"22","bold":"true","color":"FFFFFF","align":"left","valign":"middle","x":"36cm","y":"7.4cm","width":"6.2cm","height":"1.0cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"step1-desc","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"写下今天 1 件最重要的事；设定预算：30 分钟。","font":"PingFang SC","size":"16","bold":"false","color":"B9C6D6","align":"left","valign":"top","x":"36cm","y":"8.8cm","width":"6.2cm","height":"3.0cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"step2-num","preset":"ellipse","fill":"FFB020","opacity":"1","text":"2","font":"PingFang SC","size":"20","bold":"true","color":"0B0F1A","align":"center","valign":"middle","x":"36cm","y":"5.3cm","width":"1.6cm","height":"1.6cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"step2-title","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"深潜（×2）","font":"PingFang SC","size":"22","bold":"true","color":"FFFFFF","align":"left","valign":"middle","x":"36cm","y":"7.4cm","width":"6.2cm","height":"1.0cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"step2-desc","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"计时 25–45 分钟；手机离身；想刷→写到稍后清单。","font":"PingFang SC","size":"16","bold":"false","color":"B9C6D6","align":"left","valign":"top","x":"36cm","y":"8.8cm","width":"6.2cm","height":"3.0cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"step3-num","preset":"ellipse","fill":"5B6CFF","opacity":"1","text":"3","font":"PingFang SC","size":"20","bold":"true","color":"FFFFFF","align":"center","valign":"middle","x":"36cm","y":"5.3cm","width":"1.6cm","height":"1.6cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"step3-title","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"缓冲（5 分钟）","font":"PingFang SC","size":"22","bold":"true","color":"FFFFFF","align":"left","valign":"middle","x":"36cm","y":"7.4cm","width":"6.2cm","height":"1.0cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"step3-desc","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"统一处理消息：删/回/记录三选一，避免无底洞。","font":"PingFang SC","size":"16","bold":"false","color":"B9C6D6","align":"left","valign":"top","x":"36cm","y":"8.8cm","width":"6.2cm","height":"3.0cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"step4-num","preset":"ellipse","fill":"FF4D6D","opacity":"1","text":"4","font":"PingFang SC","size":"20","bold":"true","color":"FFFFFF","align":"center","valign":"middle","x":"36cm","y":"5.3cm","width":"1.6cm","height":"1.6cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"step4-title","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"复盘（1 分钟）","font":"PingFang SC","size":"22","bold":"true","color":"FFFFFF","align":"left","valign":"middle","x":"36cm","y":"7.4cm","width":"6.2cm","height":"1.0cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"step4-desc","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"写 1 行：预算花在哪？明天只调整一处。","font":"PingFang SC","size":"16","bold":"false","color":"B9C6D6","align":"left","valign":"top","x":"36cm","y":"8.8cm","width":"6.2cm","height":"3.0cm"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"evidence-title","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"三个指标，让注意力“看得见”","font":"PingFang SC","size":"36","bold":"true","color":"FFFFFF","align":"left","valign":"middle","x":"36cm","y":"1.2cm","width":"31.47cm","height":"1.4cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"evidence-caption","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"建议目标值（从你当前水平的 80% 开始）","font":"PingFang SC","size":"16","bold":"false","color":"7F93AA","align":"left","valign":"middle","x":"36cm","y":"2.8cm","width":"31.47cm","height":"0.9cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"evidence-note","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"只要记录 3 天，你就能看到趋势","font":"PingFang SC","size":"14","bold":"false","color":"7F93AA","align":"left","valign":"middle","x":"36cm","y":"3.7cm","width":"31.47cm","height":"0.8cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"eviA-bg","preset":"roundRect","fill":"102A2C","opacity":"1","line":"2BE4A8","lineWidth":"2","lineOpacity":"0.80","x":"36cm","y":"5.0cm","width":"19.2cm","height":"12.6cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"eviA-num","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"≤20 次/天","font":"PingFang SC","size":"64","bold":"true","color":"FFFFFF","align":"left","valign":"middle","x":"36cm","y":"7.2cm","width":"17.6cm","height":"2.6cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"eviA-label","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"无意识打开手机","font":"PingFang SC","size":"20","bold":"false","color":"B9C6D6","align":"left","valign":"middle","x":"36cm","y":"10.3cm","width":"17.6cm","height":"1.0cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"eviB-bg","preset":"roundRect","fill":"2C2310","opacity":"1","line":"FFB020","lineWidth":"2","lineOpacity":"0.80","x":"36cm","y":"5.0cm","width":"11.1cm","height":"5.9cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"eviB-num","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"≥90 分钟","font":"PingFang SC","size":"44","bold":"true","color":"FFFFFF","align":"left","valign":"middle","x":"36cm","y":"6.2cm","width":"9.6cm","height":"1.8cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"eviB-label","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"深度工作总时长","font":"PingFang SC","size":"18","bold":"false","color":"B9C6D6","align":"left","valign":"middle","x":"36cm","y":"8.3cm","width":"9.6cm","height":"1.0cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"eviC-bg","preset":"roundRect","fill":"2C1020","opacity":"1","line":"FF4D6D","lineWidth":"2","lineOpacity":"0.80","x":"36cm","y":"11.7cm","width":"11.1cm","height":"5.9cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"eviC-num","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"≤8 次","font":"PingFang SC","size":"44","bold":"true","color":"FFFFFF","align":"left","valign":"middle","x":"36cm","y":"12.9cm","width":"9.6cm","height":"1.8cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"eviC-label","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"任务切换次数","font":"PingFang SC","size":"18","bold":"false","color":"B9C6D6","align":"left","valign":"middle","x":"36cm","y":"15.0cm","width":"9.6cm","height":"1.0cm"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"quote-main","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"注意力流向哪里，你就长成哪里。","font":"PingFang SC","size":"48","bold":"true","color":"FFFFFF","align":"center","valign":"middle","x":"36cm","y":"6.8cm","width":"27.4cm","height":"3.2cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"quote-attrib","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"— 给未来的自己","font":"PingFang SC","size":"18","bold":"false","color":"7F93AA","align":"center","valign":"middle","x":"36cm","y":"11.0cm","width":"27.4cm","height":"1.0cm"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"cta-title","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"7 天挑战：让注意力回到你手上","font":"PingFang SC","size":"48","bold":"true","color":"FFFFFF","align":"center","valign":"middle","x":"36cm","y":"2.0cm","width":"27.9cm","height":"1.8cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"cta-item1","preset":"roundRect","fill":"FFFFFF","opacity":"0.06","line":"2BE4A8","lineWidth":"2","lineOpacity":"0.35","text":"1 记录：每天 1 次，记下无意识打开次数","font":"PingFang SC","size":"24","bold":"true","color":"FFFFFF","align":"left","valign":"middle","x":"36cm","y":"6.0cm","width":"25.9cm","height":"2.6cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"cta-item2","preset":"roundRect","fill":"FFFFFF","opacity":"0.06","line":"FFB020","lineWidth":"2","lineOpacity":"0.35","text":"2 预算：每天 1 个额度（示例：30 分钟）","font":"PingFang SC","size":"24","bold":"true","color":"FFFFFF","align":"left","valign":"middle","x":"36cm","y":"9.4cm","width":"25.9cm","height":"2.6cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"cta-item3","preset":"roundRect","fill":"FFFFFF","opacity":"0.06","line":"FF4D6D","lineWidth":"2","lineOpacity":"0.35","text":"3 深度区：每天 1 个 90 分钟手机离身区块","font":"PingFang SC","size":"24","bold":"true","color":"FFFFFF","align":"left","valign":"middle","x":"36cm","y":"12.8cm","width":"25.9cm","height":"2.6cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"cta-footer","preset":"rect","fill":"000000","opacity":"0","lineOpacity":"0","text":"现在就做：写下你今天的第一笔预算","font":"PingFang SC","size":"16","bold":"false","color":"7F93AA","align":"center","valign":"middle","x":"36cm","y":"16.6cm","width":"27.4cm","height":"0.9cm"}}
]
JSON

officecli add "$OUT" '/' --from '/slide[1]'
cat <<'JSON' | officecli batch "$OUT"
[
  {"command":"set","path":"/slide[2]","props":{"transition":"morph","background":"0B0F1A"}},

  {"command":"set","path":"/slide[2]/shape[1]","props":{"x":"0cm","y":"8cm","width":"16cm","height":"16cm","fill":"5B6CFF","opacity":"0.08"}},
  {"command":"set","path":"/slide[2]/shape[2]","props":{"x":"18cm","y":"0cm","width":"16cm","height":"16cm","fill":"2BE4A8","opacity":"0.06"}},
  {"command":"set","path":"/slide[2]/shape[3]","props":{"x":"0cm","y":"0cm","width":"10cm","height":"6cm","fill":"FFB020","opacity":"0.05","rotation":"-8"}},
  {"command":"set","path":"/slide[2]/shape[4]","props":{"x":"32.2cm","y":"1.0cm","width":"0.2cm","height":"17cm","fill":"FFFFFF","opacity":"0.06"}},
  {"command":"set","path":"/slide[2]/shape[5]","props":{"x":"2cm","y":"2cm","width":"30cm","height":"0.2cm","rotation":"18","fill":"2BE4A8","opacity":"0.05"}},
  {"command":"set","path":"/slide[2]/shape[6]","props":{"x":"3cm","y":"3cm","width":"1.8cm","height":"1.8cm","fill":"FFB020","opacity":"0.22"}},
  {"command":"set","path":"/slide[2]/shape[7]","props":{"x":"1.2cm","y":"0.8cm","width":"10cm","height":"10cm","line":"FF4D6D","lineOpacity":"0.18"}},
  {"command":"set","path":"/slide[2]/shape[8]","props":{"x":"27cm","y":"15.8cm","width":"6.4cm","height":"2.6cm","fill":"2BE4A8","opacity":"0.10","rotation":"12"}},

  {"command":"set","path":"/slide[2]/shape[9]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[2]/shape[10]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[2]/shape[11]","props":{"x":"36cm"}},

  {"command":"set","path":"/slide[2]/shape[12]","props":{"x":"3.2cm","y":"7.2cm","width":"27.4cm","height":"2.4cm"}},
  {"command":"set","path":"/slide[2]/shape[13]","props":{"x":"5.0cm","y":"11.8cm","width":"23.8cm","height":"1.2cm"}}
]
JSON

officecli add "$OUT" '/' --from '/slide[2]'
cat <<'JSON' | officecli batch "$OUT"
[
  {"command":"set","path":"/slide[3]","props":{"transition":"morph","background":"0B0F1A"}},

  {"command":"set","path":"/slide[3]/shape[1]","props":{"x":"0cm","y":"0cm","width":"12cm","height":"12cm","fill":"2BE4A8","opacity":"0.06"}},
  {"command":"set","path":"/slide[3]/shape[2]","props":{"x":"21cm","y":"10.5cm","width":"13cm","height":"13cm","fill":"FF4D6D","opacity":"0.06"}},
  {"command":"set","path":"/slide[3]/shape[3]","props":{"x":"26.4cm","y":"2.8cm","width":"7.2cm","height":"14cm","fill":"5B6CFF","opacity":"0.05","rotation":"6"}},
  {"command":"set","path":"/slide[3]/shape[4]","props":{"x":"1.2cm","y":"17.6cm","width":"31.47cm","height":"0.2cm","fill":"FFFFFF","opacity":"0.05"}},
  {"command":"set","path":"/slide[3]/shape[5]","props":{"x":"6cm","y":"3.0cm","width":"24cm","height":"0.2cm","rotation":"6","fill":"FFB020","opacity":"0.06"}},
  {"command":"set","path":"/slide[3]/shape[6]","props":{"x":"2.0cm","y":"3.2cm","width":"1.2cm","height":"1.2cm","fill":"2BE4A8","opacity":"0.18"}},
  {"command":"set","path":"/slide[3]/shape[7]","props":{"x":"25.2cm","y":"0.6cm","width":"7.6cm","height":"7.6cm","line":"2BE4A8","lineOpacity":"0.16"}},
  {"command":"set","path":"/slide[3]/shape[8]","props":{"x":"1.2cm","y":"2.2cm","width":"6.2cm","height":"2.0cm","fill":"FFB020","opacity":"0.08","rotation":"-8"}},

  {"command":"set","path":"/slide[3]/shape[12]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[3]/shape[13]","props":{"x":"36cm"}},

  {"command":"set","path":"/slide[3]/shape[14]","props":{"x":"1.2cm","y":"1.2cm"}},
  {"command":"set","path":"/slide[3]/shape[15]","props":{"x":"1.2cm","y":"5.0cm"}},
  {"command":"set","path":"/slide[3]/shape[16]","props":{"x":"1.8cm","y":"6.0cm"}},
  {"command":"set","path":"/slide[3]/shape[17]","props":{"x":"1.8cm","y":"7.6cm"}},
  {"command":"set","path":"/slide[3]/shape[18]","props":{"x":"12.0cm","y":"5.0cm"}},
  {"command":"set","path":"/slide[3]/shape[19]","props":{"x":"12.6cm","y":"6.0cm"}},
  {"command":"set","path":"/slide[3]/shape[20]","props":{"x":"12.6cm","y":"7.6cm"}},
  {"command":"set","path":"/slide[3]/shape[21]","props":{"x":"22.8cm","y":"5.0cm"}},
  {"command":"set","path":"/slide[3]/shape[22]","props":{"x":"23.4cm","y":"6.0cm"}},
  {"command":"set","path":"/slide[3]/shape[23]","props":{"x":"23.4cm","y":"7.6cm"}}
]
JSON

officecli add "$OUT" '/' --from '/slide[3]'
cat <<'JSON' | officecli batch "$OUT"
[
  {"command":"set","path":"/slide[4]","props":{"transition":"morph","background":"0B0F1A"}},

  {"command":"set","path":"/slide[4]/shape[1]","props":{"x":"0cm","y":"10cm","width":"15cm","height":"15cm","fill":"FFB020","opacity":"0.06"}},
  {"command":"set","path":"/slide[4]/shape[2]","props":{"x":"20cm","y":"0cm","width":"14cm","height":"14cm","fill":"2BE4A8","opacity":"0.05"}},
  {"command":"set","path":"/slide[4]/shape[3]","props":{"x":"0cm","y":"0cm","width":"9cm","height":"8cm","fill":"5B6CFF","opacity":"0.05","rotation":"-12"}},
  {"command":"set","path":"/slide[4]/shape[4]","props":{"x":"1.2cm","y":"4.6cm","width":"31.47cm","height":"0.2cm","fill":"FFFFFF","opacity":"0.05"}},
  {"command":"set","path":"/slide[4]/shape[5]","props":{"x":"3cm","y":"17.4cm","width":"28cm","height":"0.2cm","rotation":"0","fill":"FF4D6D","opacity":"0.06"}},
  {"command":"set","path":"/slide[4]/shape[6]","props":{"x":"31.2cm","y":"2.6cm","width":"1.2cm","height":"1.2cm","fill":"FF4D6D","opacity":"0.18"}},
  {"command":"set","path":"/slide[4]/shape[7]","props":{"x":"1.2cm","y":"0.8cm","width":"9.0cm","height":"9.0cm","line":"2BE4A8","lineOpacity":"0.12"}},
  {"command":"set","path":"/slide[4]/shape[8]","props":{"x":"26.8cm","y":"15.6cm","width":"6.6cm","height":"2.4cm","fill":"FFB020","opacity":"0.08","rotation":"8"}},

  {"command":"set","path":"/slide[4]/shape[14]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[15]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[16]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[17]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[18]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[19]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[20]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[21]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[22]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[4]/shape[23]","props":{"x":"36cm"}},

  {"command":"set","path":"/slide[4]/shape[24]","props":{"x":"1.2cm","y":"1.2cm"}},
  {"command":"set","path":"/slide[4]/shape[25]","props":{"x":"1.2cm","y":"6.1cm"}},

  {"command":"set","path":"/slide[4]/shape[26]","props":{"x":"3.9cm","y":"5.3cm"}},
  {"command":"set","path":"/slide[4]/shape[27]","props":{"x":"1.6cm","y":"7.4cm"}},
  {"command":"set","path":"/slide[4]/shape[28]","props":{"x":"1.6cm","y":"8.8cm"}},

  {"command":"set","path":"/slide[4]/shape[29]","props":{"x":"12.1cm","y":"5.3cm"}},
  {"command":"set","path":"/slide[4]/shape[30]","props":{"x":"9.8cm","y":"7.4cm"}},
  {"command":"set","path":"/slide[4]/shape[31]","props":{"x":"9.8cm","y":"8.8cm"}},

  {"command":"set","path":"/slide[4]/shape[32]","props":{"x":"20.3cm","y":"5.3cm"}},
  {"command":"set","path":"/slide[4]/shape[33]","props":{"x":"18.0cm","y":"7.4cm"}},
  {"command":"set","path":"/slide[4]/shape[34]","props":{"x":"18.0cm","y":"8.8cm"}},

  {"command":"set","path":"/slide[4]/shape[35]","props":{"x":"28.5cm","y":"5.3cm"}},
  {"command":"set","path":"/slide[4]/shape[36]","props":{"x":"26.2cm","y":"7.4cm"}},
  {"command":"set","path":"/slide[4]/shape[37]","props":{"x":"26.2cm","y":"8.8cm"}}
]
JSON

officecli add "$OUT" '/' --from '/slide[4]'
cat <<'JSON' | officecli batch "$OUT"
[
  {"command":"set","path":"/slide[5]","props":{"transition":"morph","background":"0B0F1A"}},

  {"command":"set","path":"/slide[5]/shape[1]","props":{"x":"0cm","y":"0cm","width":"18cm","height":"18cm","fill":"2BE4A8","opacity":"0.05"}},
  {"command":"set","path":"/slide[5]/shape[2]","props":{"x":"23cm","y":"9.6cm","width":"11cm","height":"11cm","fill":"FFB020","opacity":"0.06"}},
  {"command":"set","path":"/slide[5]/shape[3]","props":{"x":"26.2cm","y":"0.8cm","width":"7.2cm","height":"9.6cm","fill":"5B6CFF","opacity":"0.05","rotation":"14"}},
  {"command":"set","path":"/slide[5]/shape[4]","props":{"x":"1.2cm","y":"1.0cm","width":"31.47cm","height":"0.2cm","fill":"FFFFFF","opacity":"0.05"}},
  {"command":"set","path":"/slide[5]/shape[5]","props":{"x":"6cm","y":"17.6cm","width":"24cm","height":"0.2cm","rotation":"0","fill":"2BE4A8","opacity":"0.05"}},
  {"command":"set","path":"/slide[5]/shape[6]","props":{"x":"2.0cm","y":"16.0cm","width":"1.2cm","height":"1.2cm","fill":"FF4D6D","opacity":"0.16"}},
  {"command":"set","path":"/slide[5]/shape[7]","props":{"x":"24.2cm","y":"1.0cm","width":"8.6cm","height":"8.6cm","line":"2BE4A8","lineOpacity":"0.14"}},
  {"command":"set","path":"/slide[5]/shape[8]","props":{"x":"1.2cm","y":"2.2cm","width":"6.2cm","height":"2.0cm","fill":"FFB020","opacity":"0.07","rotation":"0"}},

  {"command":"set","path":"/slide[5]/shape[24]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[25]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[26]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[27]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[28]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[29]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[30]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[31]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[32]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[33]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[34]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[35]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[36]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[5]/shape[37]","props":{"x":"36cm"}},

  {"command":"set","path":"/slide[5]/shape[38]","props":{"x":"1.2cm","y":"1.2cm"}},
  {"command":"set","path":"/slide[5]/shape[39]","props":{"x":"1.2cm","y":"2.8cm"}},
  {"command":"set","path":"/slide[5]/shape[40]","props":{"x":"1.2cm","y":"3.7cm"}},

  {"command":"set","path":"/slide[5]/shape[41]","props":{"x":"1.2cm","y":"5.0cm"}},
  {"command":"set","path":"/slide[5]/shape[42]","props":{"x":"2.4cm","y":"7.2cm"}},
  {"command":"set","path":"/slide[5]/shape[43]","props":{"x":"2.4cm","y":"10.3cm"}},

  {"command":"set","path":"/slide[5]/shape[44]","props":{"x":"21.6cm","y":"5.0cm"}},
  {"command":"set","path":"/slide[5]/shape[45]","props":{"x":"22.4cm","y":"6.2cm"}},
  {"command":"set","path":"/slide[5]/shape[46]","props":{"x":"22.4cm","y":"8.3cm"}},

  {"command":"set","path":"/slide[5]/shape[47]","props":{"x":"21.6cm","y":"11.7cm"}},
  {"command":"set","path":"/slide[5]/shape[48]","props":{"x":"22.4cm","y":"12.9cm"}},
  {"command":"set","path":"/slide[5]/shape[49]","props":{"x":"22.4cm","y":"15.0cm"}}
]
JSON

officecli add "$OUT" '/' --from '/slide[5]'
cat <<'JSON' | officecli batch "$OUT"
[
  {"command":"set","path":"/slide[6]","props":{"transition":"morph","background":"0B0F1A"}},

  {"command":"set","path":"/slide[6]/shape[1]","props":{"x":"0cm","y":"0cm","width":"12cm","height":"12cm","fill":"2BE4A8","opacity":"0.03"}},
  {"command":"set","path":"/slide[6]/shape[2]","props":{"x":"22cm","y":"10.2cm","width":"12cm","height":"12cm","fill":"FFB020","opacity":"0.03"}},
  {"command":"set","path":"/slide[6]/shape[3]","props":{"x":"27.4cm","y":"2.0cm","width":"6.2cm","height":"14.2cm","fill":"5B6CFF","opacity":"0.02","rotation":"0"}},
  {"command":"set","path":"/slide[6]/shape[4]","props":{"x":"1.2cm","y":"18.0cm","width":"31.47cm","height":"0.2cm","fill":"FFFFFF","opacity":"0.03"}},
  {"command":"set","path":"/slide[6]/shape[5]","props":{"x":"36cm","y":"0cm","opacity":"0.03"}},
  {"command":"set","path":"/slide[6]/shape[6]","props":{"x":"31.0cm","y":"3.0cm","width":"1.0cm","height":"1.0cm","fill":"FF4D6D","opacity":"0.10"}},
  {"command":"set","path":"/slide[6]/shape[7]","props":{"x":"24.8cm","y":"0.8cm","width":"8.2cm","height":"8.2cm","lineOpacity":"0.10"}},
  {"command":"set","path":"/slide[6]/shape[8]","props":{"x":"36cm","opacity":"0.04"}},

  {"command":"set","path":"/slide[6]/shape[38]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[6]/shape[39]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[6]/shape[40]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[6]/shape[41]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[6]/shape[42]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[6]/shape[43]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[6]/shape[44]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[6]/shape[45]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[6]/shape[46]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[6]/shape[47]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[6]/shape[48]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[6]/shape[49]","props":{"x":"36cm"}},

  {"command":"set","path":"/slide[6]/shape[50]","props":{"x":"3.2cm","y":"6.8cm"}},
  {"command":"set","path":"/slide[6]/shape[51]","props":{"x":"3.2cm","y":"11.0cm"}}
]
JSON

officecli add "$OUT" '/' --from '/slide[6]'
cat <<'JSON' | officecli batch "$OUT"
[
  {"command":"set","path":"/slide[7]","props":{"transition":"morph","background":"0B0F1A"}},

  {"command":"set","path":"/slide[7]/shape[1]","props":{"x":"0cm","y":"0cm","width":"14cm","height":"14cm","fill":"2BE4A8","opacity":"0.06"}},
  {"command":"set","path":"/slide[7]/shape[2]","props":{"x":"20.5cm","y":"10.0cm","width":"13.5cm","height":"13.5cm","fill":"FFB020","opacity":"0.06"}},
  {"command":"set","path":"/slide[7]/shape[3]","props":{"x":"27.6cm","y":"1.6cm","width":"6.2cm","height":"13.8cm","fill":"5B6CFF","opacity":"0.05","rotation":"10"}},
  {"command":"set","path":"/slide[7]/shape[4]","props":{"x":"1.2cm","y":"1.0cm","width":"31.47cm","height":"0.2cm","opacity":"0.05"}},
  {"command":"set","path":"/slide[7]/shape[5]","props":{"x":"4cm","y":"17.4cm","width":"26cm","height":"0.2cm","rotation":"-8","fill":"FF4D6D","opacity":"0.06"}},
  {"command":"set","path":"/slide[7]/shape[6]","props":{"x":"2.6cm","y":"3.0cm","width":"1.2cm","height":"1.2cm","fill":"2BE4A8","opacity":"0.16"}},
  {"command":"set","path":"/slide[7]/shape[7]","props":{"x":"1.2cm","y":"9.8cm","width":"9.4cm","height":"9.4cm","line":"2BE4A8","lineOpacity":"0.14"}},
  {"command":"set","path":"/slide[7]/shape[8]","props":{"x":"26.8cm","y":"14.8cm","width":"6.6cm","height":"2.4cm","fill":"FFB020","opacity":"0.08","rotation":"0"}},

  {"command":"set","path":"/slide[7]/shape[50]","props":{"x":"36cm"}},
  {"command":"set","path":"/slide[7]/shape[51]","props":{"x":"36cm"}},

  {"command":"set","path":"/slide[7]/shape[52]","props":{"x":"3.0cm","y":"2.0cm"}},
  {"command":"set","path":"/slide[7]/shape[53]","props":{"x":"4.0cm","y":"6.0cm"}},
  {"command":"set","path":"/slide[7]/shape[54]","props":{"x":"4.0cm","y":"9.4cm"}},
  {"command":"set","path":"/slide[7]/shape[55]","props":{"x":"4.0cm","y":"12.8cm"}},
  {"command":"set","path":"/slide[7]/shape[56]","props":{"x":"3.2cm","y":"16.6cm"}}
]
JSON
''',

    'science--alien-guide': '''
#!/bin/bash
set +H
set -e

F="Alien_Guide.pptx"
echo "Building $F..."
rm -f "$F"
officecli create "$F"

BG="0B0C10"
CYAN="66FCF1"
TEAL="45A29E"
WHITE="FFFFFF"
GRAY="C5C6C7"
DARK="1F2833"

a() { officecli add "$F" "$1" --type shape "${@:2}"; }
sl() { officecli add "$F" / --type slide "$@"; }

# Helper for scene actors to maintain consistency across slides for Morph animation
scene_actors() {
  local s="$1"
  local c_x="$2" c_y="$3" c_w="$4" c_o="$5"
  local r_x="$6" r_y="$7" r_w="$8" r_h="$9" r_o="${10}"
  local a1_x="${11}" a1_y="${12}"
  local a2_x="${13}" a2_y="${14}"
  local lt_x="${15}" lt_y="${16}" lt_w="${17}"
  local lb_x="${18}" lb_y="${19}" lb_w="${20}"

  a "$s" --prop name="!!bg-circ" --prop preset=ellipse --prop x="${c_x}cm" --prop y="${c_y}cm" --prop width="${c_w}cm" --prop height="${c_w}cm" --prop fill=$DARK --prop line=none --prop opacity="${c_o}"
  a "$s" --prop name="!!bg-rect" --prop preset=roundRect --prop x="${r_x}cm" --prop y="${r_y}cm" --prop width="${r_w}cm" --prop height="${r_h}cm" --prop fill=$TEAL --prop line=none --prop opacity="${r_o}"
  a "$s" --prop name="!!accent-1" --prop preset=ellipse --prop x="${a1_x}cm" --prop y="${a1_y}cm" --prop width=0.8cm --prop height=0.8cm --prop fill=$CYAN --prop line=none
  a "$s" --prop name="!!accent-2" --prop preset=ellipse --prop x="${a2_x}cm" --prop y="${a2_y}cm" --prop width=1.2cm --prop height=1.2cm --prop fill=$CYAN --prop line=none
  a "$s" --prop name="!!line-top" --prop preset=rect --prop x="${lt_x}cm" --prop y="${lt_y}cm" --prop width="${lt_w}cm" --prop height=0.2cm --prop fill=$CYAN --prop line=none
  a "$s" --prop name="!!line-bot" --prop preset=rect --prop x="${lb_x}cm" --prop y="${lb_y}cm" --prop width="${lb_w}cm" --prop height=0.2cm --prop fill=$TEAL --prop line=none
}

# Slide 1: Hero
echo "  S1..."
sl --prop background=$BG
scene_actors '/slide[1]' 20 4 15 0.5   1 2 12 12 0.1   5 15   30 2   2 1 8   24 18 8

a '/slide[1]' --prop text="外星人地球" --prop x=2cm --prop y=4cm --prop width=18cm --prop height=3cm --prop size=64 --prop bold=true --prop color=$WHITE --prop fill=none --prop line=none
a '/slide[1]' --prop text="生存指南" --prop x=2cm --prop y=7.5cm --prop width=18cm --prop height=3cm --prop size=64 --prop bold=true --prop color=$CYAN --prop fill=none --prop line=none

a '/slide[1]' --prop text="从伪装到精通 (An Alien's Guide to Earth)" --prop x=2.2cm --prop y=11.5cm --prop width=20cm --prop height=1.5cm --prop size=24 --prop color=$GRAY --prop fill=none --prop line=none
a '/slide[1]' --prop text="本安全手册专为刚抵达银河系猎户旋臂第三行星的访客编写，
帮助你完美融入人类社会。" --prop x=2.2cm --prop y=13.5cm --prop width=18cm --prop height=3cm --prop size=16 --prop color=$GRAY --prop fill=none --prop line=none --prop lineSpacing=1.5

# Slide 2: Statement
echo "  S2..."
sl --prop background=$BG --prop transition=morph
scene_actors '/slide[2]' 2 2 18 0.3   22 5 8 14 0.1   15 3   2 16   10 1 4   2 18 12

a '/slide[2]' --prop text="RULE NO.1" --prop x=18cm --prop y=4cm --prop width=12cm --prop height=1.5cm --prop size=20 --prop bold=true --prop color=$CYAN --prop fill=none --prop line=none
a '/slide[2]' --prop text="第一法则" --prop x=18cm --prop y=5.5cm --prop width=12cm --prop height=2cm --prop size=48 --prop bold=true --prop color=$WHITE --prop fill=none --prop line=none

a '/slide[2]' --prop text="永远不要试图与猫讲道理。" --prop x=6cm --prop y=9cm --prop width=24cm --prop height=4cm --prop size=54 --prop bold=true --prop color=$CYAN --prop fill=none --prop line=none --prop align=center

a '/slide[2]' --prop text="数据表明，它们才是这颗星球真正的统治者，
人类只是它们的“铲屎官”。" --prop x=6cm --prop y=14cm --prop width=24cm --prop height=3cm --prop size=18 --prop color=$GRAY --prop fill=none --prop line=none --prop lineSpacing=1.5 --prop align=center

# Slide 3: Pillars
echo "  S3..."
sl --prop background=$BG --prop transition=morph
scene_actors '/slide[3]' 10 8 14 0.6   2 2 30 6 0.05   2 2   31 16   14 1 6   14 18 6

a '/slide[3]' --prop text="人类三大迷惑行为" --prop x=2cm --prop y=2.5cm --prop width=20cm --prop height=2cm --prop size=40 --prop bold=true --prop color=$WHITE --prop fill=none --prop line=none

# Pillar 1
a '/slide[3]' --prop preset=roundRect --prop x=2cm --prop y=6cm --prop width=8cm --prop height=10cm --prop fill=$DARK --prop line=none
a '/slide[3]' --prop text="01" --prop x=3cm --prop y=7cm --prop width=3cm --prop height=1.5cm --prop size=28 --prop bold=true --prop color=$CYAN --prop fill=none --prop line=none
a '/slide[3]' --prop text="排队 (Queueing)" --prop x=3cm --prop y=9cm --prop width=6cm --prop height=1.5cm --prop size=20 --prop bold=true --prop color=$WHITE --prop fill=none --prop line=none
a '/slide[3]' --prop text="人类极其喜欢排成一条直线，这种奇特的几何排列会给他们带来莫名的安全感。" --prop x=3cm --prop y=11.5cm --prop width=6cm --prop height=4cm --prop size=14 --prop color=$GRAY --prop fill=none --prop line=none --prop lineSpacing=1.5

# Pillar 2
a '/slide[3]' --prop preset=roundRect --prop x=12.5cm --prop y=6cm --prop width=8cm --prop height=10cm --prop fill=$DARK --prop line=none
a '/slide[3]' --prop text="02" --prop x=13.5cm --prop y=7cm --prop width=3cm --prop height=1.5cm --prop size=28 --prop bold=true --prop color=$CYAN --prop fill=none --prop line=none
a '/slide[3]' --prop text="密码 (Passwords)" --prop x=13.5cm --prop y=9cm --prop width=6cm --prop height=1.5cm --prop size=20 --prop bold=true --prop color=$WHITE --prop fill=none --prop line=none
a '/slide[3]' --prop text="他们总是忘记自己设置的安全验证码，然后被迫重置成一模一样的。" --prop x=13.5cm --prop y=11.5cm --prop width=6cm --prop height=4cm --prop size=14 --prop color=$GRAY --prop fill=none --prop line=none --prop lineSpacing=1.5

# Pillar 3
a '/slide[3]' --prop preset=roundRect --prop x=23cm --prop y=6cm --prop width=8cm --prop height=10cm --prop fill=$DARK --prop line=none
a '/slide[3]' --prop text="03" --prop x=24cm --prop y=7cm --prop width=3cm --prop height=1.5cm --prop size=28 --prop bold=true --prop color=$CYAN --prop fill=none --prop line=none
a '/slide[3]' --prop text="“好的收到”" --prop x=24cm --prop y=9cm --prop width=6cm --prop height=1.5cm --prop size=20 --prop bold=true --prop color=$WHITE --prop fill=none --prop line=none
a '/slide[3]' --prop text="人类常用此短语结束在线对话，但实际上有 80% 的概率并未接收任何实质信息。" --prop x=24cm --prop y=11.5cm --prop width=6cm --prop height=4cm --prop size=14 --prop color=$GRAY --prop fill=none --prop line=none --prop lineSpacing=1.5

# Slide 4: Evidence
echo "  S4..."
sl --prop background=$BG --prop transition=morph
scene_actors '/slide[4]' 4 4 12 0.8   18 4 12 12 0.1   16 10   8 16   2 4 2   18 16 12

a '/slide[4]' --prop text="99.9%" --prop x=4cm --prop y=7cm --prop width=12cm --prop height=5cm --prop size=80 --prop bold=true --prop color=$CYAN --prop fill=none --prop line=none --prop align=center

a '/slide[4]' --prop text="能量来源分析" --prop x=18cm --prop y=5cm --prop width=12cm --prop height=2cm --prop size=36 --prop bold=true --prop color=$WHITE --prop fill=none --prop line=none
a '/slide[4]' --prop text="早晨系统启动所需咖啡因比例" --prop x=18cm --prop y=8.5cm --prop width=12cm --prop height=1.5cm --prop size=18 --prop color=$CYAN --prop fill=none --prop line=none
a '/slide[4]' --prop text="警告！如果没有摄入这种被称为“咖啡”的黑色苦味液体，地球人的核心系统在早晨极易发生崩溃。" --prop x=18cm --prop y=11cm --prop width=12cm --prop height=4cm --prop size=16 --prop color=$GRAY --prop fill=none --prop line=none --prop lineSpacing=1.5

# Slide 5: CTA
echo "  S5..."
sl --prop background=$BG --prop transition=morph
scene_actors '/slide[5]' 14 5 20 0.4   8 6 18 8 0.1   10 5   24 14   13 4 8   13 16 8

a '/slide[5]' --prop text="祝你在地球好运！" --prop x=6cm --prop y=7cm --prop width=22cm --prop height=3cm --prop size=54 --prop bold=true --prop color=$WHITE --prop fill=none --prop line=none --prop align=center

a '/slide[5]' --prop text="切记收好你的触角，保持双足行走，并随时保持尴尬又不失礼貌的微笑。" --prop x=6cm --prop y=11cm --prop width=22cm --prop height=2cm --prop size=16 --prop color=$GRAY --prop fill=none --prop line=none --prop align=center

a '/slide[5]' --prop preset=roundRect --prop x=12.5cm --prop y=14cm --prop width=9cm --prop height=1.5cm --prop fill=$CYAN --prop line=none
a '/slide[5]' --prop text="启动伪装程序 [ ENGAGE ]" --prop x=12.5cm --prop y=14cm --prop width=9cm --prop height=1.5cm --prop size=14 --prop bold=true --prop color=$DARK --prop fill=none --prop line=none --prop align=center --prop valign=center

echo "Done!"
''',

    'science--space-exploration': '''
#!/bin/bash
set -e

FILENAME="太空探索历程.pptx"

echo "Building $FILENAME..."

# Remove existing file if present
[ -f "$FILENAME" ] && rm "$FILENAME"

# Create new presentation
officecli create "$FILENAME"

# ===== Slide 1: Hero - 封面页 =====
echo "Creating Slide 1: Hero..."
cat << 'BATCH_EOF' | officecli batch "$FILENAME"
[
  {"command":"add","parent":"/","type":"slide","props":{"layout":"blank","background":"0A0E27"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"planet-main","preset":"ellipse","fill":"1E3A5F","opacity":"0.3","width":"12cm","height":"12cm","x":"24cm","y":"8cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"glow-accent","preset":"ellipse","fill":"4A5FFF","opacity":"0.08","width":"18cm","height":"18cm","x":"21cm","y":"5cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"star-1","preset":"star5","fill":"FFD700","opacity":"0.6","width":"0.8cm","height":"0.8cm","x":"5cm","y":"3cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"star-2","preset":"star5","fill":"FFFFFF","opacity":"0.5","width":"0.6cm","height":"0.6cm","x":"8cm","y":"7cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"star-3","preset":"star5","fill":"FFD700","opacity":"0.7","width":"0.7cm","height":"0.7cm","x":"28cm","y":"4cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"line-orbit","preset":"ellipse","line":"4A90E2","lineWidth":"0.15cm","fill":"none","opacity":"0.3","width":"20cm","height":"20cm","x":"18cm","y":"4cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"dot-small","preset":"ellipse","fill":"00D9FF","opacity":"0.8","width":"0.4cm","height":"0.4cm","x":"3cm","y":"15cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"hero-title","text":"太空探索历程","font":"苹方-简","size":"68","bold":"true","color":"FFFFFF","align":"center","valign":"middle","width":"26cm","height":"4cm","x":"4cm","y":"6cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"hero-subtitle","text":"从地球到星辰大海的伟大征程","font":"苹方-简","size":"24","color":"B8C5D6","align":"center","valign":"middle","width":"26cm","height":"2cm","x":"4cm","y":"10.5cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"statement-text","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"0cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"statement-subtitle","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"5cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar-title","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"10cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar-1-num","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"15cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar-1-title","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"0cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar-1-desc","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"5cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar-2-num","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"10cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar-2-title","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"15cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar-2-desc","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"0cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar-3-num","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"5cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar-3-title","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"10cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"pillar-3-desc","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"15cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"showcase-title","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"0cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"showcase-quote","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"5cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"showcase-data1","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"10cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"showcase-data2","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"15cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"evidence-title","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"0cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"evidence-main","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"5cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"evidence-point1","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"10cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"evidence-point2","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"15cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"evidence-point3","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"0cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"cta-title","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"5cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"cta-text","text":"","font":"苹方-简","size":"18","color":"FFFFFF","width":"1cm","height":"1cm","x":"36cm","y":"10cm"}}
]
BATCH_EOF

# ===== Slide 2: Statement - 仰望星空 =====
echo "Creating Slide 2: Statement..."
officecli add "$FILENAME" '/' --from '/slide[1]'
cat << 'BATCH_EOF' | officecli batch "$FILENAME"
[
  {"command":"set","path":"/slide[2]","props":{"transition":"morph"}},
  {"command":"set","path":"/slide[2]/shape[1]","props":{"x":"2cm","y":"2cm","width":"8cm","height":"8cm"}},
  {"command":"set","path":"/slide[2]/shape[2]","props":{"x":"0cm","y":"0cm","width":"15cm","height":"15cm","opacity":"0.1"}},
  {"command":"set","path":"/slide[2]/shape[3]","props":{"x":"26cm","y":"5cm"}},
  {"command":"set","path":"/slide[2]/shape[4]","props":{"x":"29cm","y":"14cm"}},
  {"command":"set","path":"/slide[2]/shape[5]","props":{"x":"10cm","y":"2cm"}},
  {"command":"set","path":"/slide[2]/shape[6]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[2]/shape[7]","props":{"x":"28cm","y":"17cm"}},
  {"command":"set","path":"/slide[2]/shape[8]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[2]/shape[9]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[2]/shape[10]","props":{"text":"仰望星空，是人类与生俱来的本能","font":"苹方-简","size":"42","bold":"true","color":"FFFFFF","align":"center","valign":"middle","width":"28cm","height":"3cm","x":"3cm","y":"4cm"}},
  {"command":"set","path":"/slide[2]/shape[11]","props":{"text":"从古代天文学家绘制星图，到伽利略用望远镜观测木星卫星，再到现代火箭技术的诞生，人类从未停止探索宇宙的脚步。20世纪中叶，太空时代的大门终于被推开。","font":"苹方-简","size":"18","color":"D0D8E5","align":"center","valign":"middle","width":"26cm","height":"6cm","x":"4cm","y":"8.5cm"}}
]
BATCH_EOF

# ===== Slide 3: Pillars - 突破大气层 =====
echo "Creating Slide 3: Pillars..."
officecli add "$FILENAME" '/' --from '/slide[1]'
cat << 'BATCH_EOF' | officecli batch "$FILENAME"
[
  {"command":"set","path":"/slide[3]","props":{"transition":"morph"}},
  {"command":"set","path":"/slide[3]/shape[1]","props":{"preset":"roundRect","fill":"2A4A6F","opacity":"0.12","width":"8cm","height":"11cm","x":"2.5cm","y":"5cm"}},
  {"command":"set","path":"/slide[3]/shape[2]","props":{"preset":"roundRect","fill":"2A4A6F","opacity":"0.12","width":"8cm","height":"11cm","x":"13cm","y":"5cm"}},
  {"command":"set","path":"/slide[3]/shape[3]","props":{"x":"24cm","y":"12cm","width":"0.6cm","height":"0.6cm"}},
  {"command":"set","path":"/slide[3]/shape[4]","props":{"x":"18cm","y":"3cm","width":"0.5cm","height":"0.5cm"}},
  {"command":"set","path":"/slide[3]/shape[5]","props":{"x":"30cm","y":"8cm","width":"0.7cm","height":"0.7cm"}},
  {"command":"set","path":"/slide[3]/shape[6]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[3]/shape[7]","props":{"preset":"roundRect","fill":"2A4A6F","opacity":"0.12","width":"8cm","height":"11cm","x":"23.5cm","y":"5cm"}},
  {"command":"set","path":"/slide[3]/shape[8]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[3]/shape[9]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[3]/shape[10]","props":{"x":"36cm","y":"10cm"}},
  {"command":"set","path":"/slide[3]/shape[11]","props":{"x":"36cm","y":"15cm"}},
  {"command":"set","path":"/slide[3]/shape[12]","props":{"text":"突破大气层：太空时代的黎明","font":"苹方-简","size":"32","bold":"true","color":"FFFFFF","align":"left","valign":"top","width":"28cm","height":"2cm","x":"2.5cm","y":"2cm"}},
  {"command":"set","path":"/slide[3]/shape[13]","props":{"text":"1957","font":"苹方-简","size":"56","bold":"true","color":"FFD700","align":"center","valign":"top","width":"8cm","height":"3cm","x":"2.5cm","y":"5.5cm"}},
  {"command":"set","path":"/slide[3]/shape[14]","props":{"text":"人造卫星","font":"苹方-简","size":"28","bold":"true","color":"FFFFFF","align":"center","valign":"top","width":"8cm","height":"2cm","x":"2.5cm","y":"9cm"}},
  {"command":"set","path":"/slide[3]/shape[15]","props":{"text":"苏联发射斯普特尼克1号，人类第一颗人造卫星进入轨道，标志着太空时代开启","font":"苹方-简","size":"16","color":"C0CAD9","align":"left","valign":"top","width":"7cm","height":"4cm","x":"3cm","y":"11.5cm"}},
  {"command":"set","path":"/slide[3]/shape[16]","props":{"text":"1961","font":"苹方-简","size":"56","bold":"true","color":"FFD700","align":"center","valign":"top","width":"8cm","height":"3cm","x":"13cm","y":"5.5cm"}},
  {"command":"set","path":"/slide[3]/shape[17]","props":{"text":"载人飞行","font":"苹方-简","size":"28","bold":"true","color":"FFFFFF","align":"center","valign":"top","width":"8cm","height":"2cm","x":"13cm","y":"9cm"}},
  {"command":"set","path":"/slide[3]/shape[18]","props":{"text":"尤里·加加林乘坐东方1号完成108分钟环绕地球飞行，成为第一个进入太空的人类","font":"苹方-简","size":"16","color":"C0CAD9","align":"left","valign":"top","width":"7cm","height":"4cm","x":"13.5cm","y":"11.5cm"}},
  {"command":"set","path":"/slide[3]/shape[19]","props":{"text":"1965","font":"苹方-简","size":"56","bold":"true","color":"FFD700","align":"center","valign":"top","width":"8cm","height":"3cm","x":"23.5cm","y":"5.5cm"}},
  {"command":"set","path":"/slide[3]/shape[20]","props":{"text":"太空行走","font":"苹方-简","size":"28","bold":"true","color":"FFFFFF","align":"center","valign":"top","width":"8cm","height":"2cm","x":"23.5cm","y":"9cm"}},
  {"command":"set","path":"/slide[3]/shape[21]","props":{"text":"列昂诺夫完成人类首次舱外活动，在太空中漂浮12分钟","font":"苹方-简","size":"16","color":"C0CAD9","align":"left","valign":"top","width":"7cm","height":"4cm","x":"24cm","y":"11.5cm"}}
]
BATCH_EOF

# ===== Slide 4: Showcase - 月球征程 =====
echo "Creating Slide 4: Showcase..."
officecli add "$FILENAME" '/' --from '/slide[1]'
cat << 'BATCH_EOF' | officecli batch "$FILENAME"
[
  {"command":"set","path":"/slide[4]","props":{"transition":"morph"}},
  {"command":"set","path":"/slide[4]/shape[1]","props":{"preset":"ellipse","fill":"F5A623","opacity":"0.15","width":"14cm","height":"14cm","x":"20cm","y":"6cm"}},
  {"command":"set","path":"/slide[4]/shape[2]","props":{"preset":"ellipse","fill":"FFD700","opacity":"0.05","width":"10cm","height":"10cm","x":"23cm","y":"8cm"}},
  {"command":"set","path":"/slide[4]/shape[3]","props":{"x":"2cm","y":"15cm"}},
  {"command":"set","path":"/slide[4]/shape[4]","props":{"x":"31cm","y":"3cm"}},
  {"command":"set","path":"/slide[4]/shape[5]","props":{"x":"5cm","y":"4cm"}},
  {"command":"set","path":"/slide[4]/shape[6]","props":{"x":"36cm","y":"10cm"}},
  {"command":"set","path":"/slide[4]/shape[7]","props":{"preset":"ellipse","fill":"F5A623","opacity":"0.4","width":"1.2cm","height":"1.2cm","x":"2cm","y":"2cm"}},
  {"command":"set","path":"/slide[4]/shape[8]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[4]/shape[9]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[4]/shape[10]","props":{"x":"36cm","y":"10cm"}},
  {"command":"set","path":"/slide[4]/shape[11]","props":{"x":"36cm","y":"15cm"}},
  {"command":"set","path":"/slide[4]/shape[12]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[4]/shape[13]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[4]/shape[14]","props":{"x":"36cm","y":"10cm"}},
  {"command":"set","path":"/slide[4]/shape[15]","props":{"x":"36cm","y":"15cm"}},
  {"command":"set","path":"/slide[4]/shape[16]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[4]/shape[17]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[4]/shape[18]","props":{"x":"36cm","y":"10cm"}},
  {"command":"set","path":"/slide[4]/shape[19]","props":{"x":"36cm","y":"15cm"}},
  {"command":"set","path":"/slide[4]/shape[20]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[4]/shape[21]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[4]/shape[22]","props":{"text":"月球征程","font":"苹方-简","size":"48","bold":"true","color":"FFFFFF","align":"left","valign":"top","width":"20cm","height":"3cm","x":"2.5cm","y":"2.5cm"}},
  {"command":"set","path":"/slide[4]/shape[23]","props":{"text":"这是一个人的一小步，却是人类的一大步","font":"苹方-简","size":"32","bold":"true","color":"FFD700","align":"left","valign":"middle","width":"18cm","height":"4cm","x":"2.5cm","y":"6.5cm"}},
  {"command":"set","path":"/slide[4]/shape[24]","props":{"text":"1969年7月20日，阿波罗11号成功登月，38万公里的旅程","font":"苹方-简","size":"20","color":"E5EAF3","align":"left","valign":"top","width":"18cm","height":"3cm","x":"2.5cm","y":"11cm"}},
  {"command":"set","path":"/slide[4]/shape[25]","props":{"text":"6次成功登月任务（1969-1972）","font":"苹方-简","size":"18","color":"B8C5D6","align":"left","valign":"top","width":"18cm","height":"2cm","x":"2.5cm","y":"14.5cm"}}
]
BATCH_EOF

# ===== Slide 5: Pillars - 空间站时代 =====
echo "Creating Slide 5: Pillars..."
officecli add "$FILENAME" '/' --from '/slide[1]'
cat << 'BATCH_EOF' | officecli batch "$FILENAME"
[
  {"command":"set","path":"/slide[5]","props":{"transition":"morph"}},
  {"command":"set","path":"/slide[5]/shape[1]","props":{"preset":"rect","fill":"00D9FF","opacity":"0.08","width":"9cm","height":"10cm","x":"2cm","y":"5.5cm"}},
  {"command":"set","path":"/slide[5]/shape[2]","props":{"preset":"rect","fill":"4A90E2","opacity":"0.08","width":"9cm","height":"10cm","x":"12.5cm","y":"5.5cm"}},
  {"command":"set","path":"/slide[5]/shape[3]","props":{"x":"6cm","y":"3cm"}},
  {"command":"set","path":"/slide[5]/shape[4]","props":{"x":"15cm","y":"17cm"}},
  {"command":"set","path":"/slide[5]/shape[5]","props":{"x":"25cm","y":"5cm"}},
  {"command":"set","path":"/slide[5]/shape[6]","props":{"preset":"ellipse","fill":"00D9FF","opacity":"0.08","line":"none","width":"8cm","height":"8cm","x":"14cm","y":"6cm"}},
  {"command":"set","path":"/slide[5]/shape[7]","props":{"preset":"rect","fill":"5865F2","opacity":"0.08","width":"9cm","height":"10cm","x":"23cm","y":"5.5cm"}},
  {"command":"set","path":"/slide[5]/shape[8]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[5]/shape[9]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[5]/shape[10]","props":{"x":"36cm","y":"10cm"}},
  {"command":"set","path":"/slide[5]/shape[11]","props":{"x":"36cm","y":"15cm"}},
  {"command":"set","path":"/slide[5]/shape[12]","props":{"text":"空间站时代：在轨道上生活","font":"苹方-简","size":"32","bold":"true","color":"FFFFFF","align":"left","valign":"top","width":"28cm","height":"2cm","x":"2cm","y":"2.5cm"}},
  {"command":"set","path":"/slide[5]/shape[13]","props":{"text":"和平号空间站","font":"苹方-简","size":"24","bold":"true","color":"FFFFFF","align":"center","valign":"top","width":"8cm","height":"2cm","x":"2.5cm","y":"6cm"}},
  {"command":"set","path":"/slide[5]/shape[14]","props":{"text":"1986-2001","font":"苹方-简","size":"20","color":"00D9FF","align":"center","valign":"top","width":"8cm","height":"1.5cm","x":"2.5cm","y":"8.5cm"}},
  {"command":"set","path":"/slide[5]/shape[15]","props":{"text":"运行15年，累计接待137名宇航员，证明人类可以在太空长期生活","font":"苹方-简","size":"16","color":"C0CAD9","align":"left","valign":"top","width":"7.5cm","height":"4cm","x":"2.8cm","y":"10.5cm"}},
  {"command":"set","path":"/slide[5]/shape[16]","props":{"text":"国际空间站","font":"苹方-简","size":"24","bold":"true","color":"FFFFFF","align":"center","valign":"top","width":"8cm","height":"2cm","x":"13cm","y":"6cm"}},
  {"command":"set","path":"/slide[5]/shape[17]","props":{"text":"1998-至今","font":"苹方-简","size":"20","color":"4A90E2","align":"center","valign":"top","width":"8cm","height":"1.5cm","x":"13cm","y":"8.5cm"}},
  {"command":"set","path":"/slide[5]/shape[18]","props":{"text":"16国合作，400km轨道高度，持续有人驻守超过23年","font":"苹方-简","size":"16","color":"C0CAD9","align":"left","valign":"top","width":"7.5cm","height":"4cm","x":"13.3cm","y":"10.5cm"}},
  {"command":"set","path":"/slide[5]/shape[19]","props":{"text":"中国空间站","font":"苹方-简","size":"24","bold":"true","color":"FFFFFF","align":"center","valign":"top","width":"8cm","height":"2cm","x":"23.5cm","y":"6cm"}},
  {"command":"set","path":"/slide[5]/shape[20]","props":{"text":"2021-至今","font":"苹方-简","size":"20","color":"5865F2","align":"center","valign":"top","width":"8cm","height":"1.5cm","x":"23.5cm","y":"8.5cm"}},
  {"command":"set","path":"/slide[5]/shape[21]","props":{"text":"自主研发，T字构型，可容纳3-6名航天员长期工作","font":"苹方-简","size":"16","color":"C0CAD9","align":"left","valign":"top","width":"7.5cm","height":"4cm","x":"23.8cm","y":"10.5cm"}}
]
BATCH_EOF

# ===== Slide 6: Evidence - 火星梦想 =====
echo "Creating Slide 6: Evidence..."
officecli add "$FILENAME" '/' --from '/slide[1]'
cat << 'BATCH_EOF' | officecli batch "$FILENAME"
[
  {"command":"set","path":"/slide[6]","props":{"transition":"morph"}},
  {"command":"set","path":"/slide[6]/shape[1]","props":{"preset":"ellipse","fill":"D84315","opacity":"0.5","width":"18cm","height":"18cm","x":"18cm","y":"2cm"}},
  {"command":"set","path":"/slide[6]/shape[2]","props":{"preset":"ellipse","fill":"FF5722","opacity":"0.2","width":"12cm","height":"12cm","x":"21cm","y":"5cm"}},
  {"command":"set","path":"/slide[6]/shape[3]","props":{"fill":"FFB74D","x":"4cm","y":"3cm","width":"0.5cm","height":"0.5cm"}},
  {"command":"set","path":"/slide[6]/shape[4]","props":{"fill":"FFFFFF","x":"8cm","y":"16cm","width":"0.4cm","height":"0.4cm"}},
  {"command":"set","path":"/slide[6]/shape[5]","props":{"fill":"FF6B35","x":"12cm","y":"2cm","width":"0.6cm","height":"0.6cm"}},
  {"command":"set","path":"/slide[6]/shape[6]","props":{"x":"36cm","y":"10cm"}},
  {"command":"set","path":"/slide[6]/shape[7]","props":{"preset":"ellipse","fill":"FF6B35","opacity":"0.15","width":"3cm","height":"3cm","x":"2cm","y":"15cm"}},
  {"command":"set","path":"/slide[6]/shape[8]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[6]/shape[9]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[6]/shape[10]","props":{"x":"36cm","y":"10cm"}},
  {"command":"set","path":"/slide[6]/shape[11]","props":{"x":"36cm","y":"15cm"}},
  {"command":"set","path":"/slide[6]/shape[12]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[6]/shape[13]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[6]/shape[14]","props":{"x":"36cm","y":"10cm"}},
  {"command":"set","path":"/slide[6]/shape[15]","props":{"x":"36cm","y":"15cm"}},
  {"command":"set","path":"/slide[6]/shape[16]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[6]/shape[17]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[6]/shape[18]","props":{"x":"36cm","y":"10cm"}},
  {"command":"set","path":"/slide[6]/shape[19]","props":{"x":"36cm","y":"15cm"}},
  {"command":"set","path":"/slide[6]/shape[20]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[6]/shape[21]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[6]/shape[22]","props":{"x":"36cm","y":"10cm"}},
  {"command":"set","path":"/slide[6]/shape[23]","props":{"x":"36cm","y":"15cm"}},
  {"command":"set","path":"/slide[6]/shape[24]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[6]/shape[25]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[6]/shape[26]","props":{"text":"火星梦想","font":"苹方-简","size":"48","bold":"true","color":"FFFFFF","align":"left","valign":"top","width":"15cm","height":"3cm","x":"2cm","y":"2.5cm"}},
  {"command":"set","path":"/slide[6]/shape[27]","props":{"text":"下一个人类的家园","font":"苹方-简","size":"36","bold":"true","color":"FF8A65","align":"left","valign":"top","width":"15cm","height":"2.5cm","x":"2cm","y":"6cm"}},
  {"command":"set","path":"/slide[6]/shape[28]","props":{"text":"探测器先行","font":"苹方-简","size":"22","bold":"true","color":"FFFFFF","align":"left","valign":"top","width":"14cm","height":"1.5cm","x":"2cm","y":"9.5cm"}},
  {"command":"set","path":"/slide[6]/shape[29]","props":{"text":"已有10+个火星探测器成功着陆，毅力号、祝融号正在工作","font":"苹方-简","size":"16","color":"D0D8E5","align":"left","valign":"top","width":"14cm","height":"2.5cm","x":"2cm","y":"11cm"}},
  {"command":"set","path":"/slide[6]/shape[30]","props":{"text":"技术突破 | SpaceX星舰可重复使用，NASA Artemis重返月球为火星铺路","font":"苹方-简","size":"16","color":"D0D8E5","align":"left","valign":"top","width":"14cm","height":"2.5cm","x":"2cm","y":"13.5cm"}},
  {"command":"set","path":"/slide[6]/shape[31]","props":{"text":"2030年代","font":"苹方-简","size":"28","bold":"true","color":"FFD700","align":"right","valign":"middle","width":"10cm","height":"2cm","x":"21cm","y":"8cm"}},
  {"command":"set","path":"/slide[6]/shape[32]","props":{"text":"NASA计划实现载人登陆火星","font":"苹方-简","size":"18","color":"FFFFFF","align":"right","valign":"middle","width":"10cm","height":"2cm","x":"21cm","y":"10.5cm"}}
]
BATCH_EOF

# ===== Slide 7: CTA - 征途未完 =====
echo "Creating Slide 7: CTA..."
officecli add "$FILENAME" '/' --from '/slide[1]'
cat << 'BATCH_EOF' | officecli batch "$FILENAME"
[
  {"command":"set","path":"/slide[7]","props":{"transition":"morph"}},
  {"command":"set","path":"/slide[7]/shape[1]","props":{"preset":"ellipse","fill":"1E3A5F","opacity":"0.2","width":"16cm","height":"16cm","x":"10cm","y":"3cm"}},
  {"command":"set","path":"/slide[7]/shape[2]","props":{"preset":"ellipse","fill":"9B59B6","opacity":"0.12","width":"20cm","height":"20cm","x":"8cm","y":"1cm"}},
  {"command":"set","path":"/slide[7]/shape[3]","props":{"x":"30cm","y":"2cm","width":"0.9cm","height":"0.9cm"}},
  {"command":"set","path":"/slide[7]/shape[4]","props":{"x":"3cm","y":"5cm","width":"0.7cm","height":"0.7cm"}},
  {"command":"set","path":"/slide[7]/shape[5]","props":{"x":"26cm","y":"16cm","width":"0.8cm","height":"0.8cm"}},
  {"command":"set","path":"/slide[7]/shape[6]","props":{"preset":"ellipse","fill":"8E44AD","opacity":"0.08","line":"none","width":"24cm","height":"24cm","x":"6cm","y":"0cm"}},
  {"command":"set","path":"/slide[7]/shape[7]","props":{"preset":"ellipse","fill":"3498DB","opacity":"0.7","width":"0.5cm","height":"0.5cm","x":"16cm","y":"9cm"}},
  {"command":"set","path":"/slide[7]/shape[8]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[7]/shape[9]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[7]/shape[10]","props":{"x":"36cm","y":"10cm"}},
  {"command":"set","path":"/slide[7]/shape[11]","props":{"x":"36cm","y":"15cm"}},
  {"command":"set","path":"/slide[7]/shape[12]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[7]/shape[13]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[7]/shape[14]","props":{"x":"36cm","y":"10cm"}},
  {"command":"set","path":"/slide[7]/shape[15]","props":{"x":"36cm","y":"15cm"}},
  {"command":"set","path":"/slide[7]/shape[16]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[7]/shape[17]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[7]/shape[18]","props":{"x":"36cm","y":"10cm"}},
  {"command":"set","path":"/slide[7]/shape[19]","props":{"x":"36cm","y":"15cm"}},
  {"command":"set","path":"/slide[7]/shape[20]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[7]/shape[21]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[7]/shape[22]","props":{"x":"36cm","y":"10cm"}},
  {"command":"set","path":"/slide[7]/shape[23]","props":{"x":"36cm","y":"15cm"}},
  {"command":"set","path":"/slide[7]/shape[24]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[7]/shape[25]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[7]/shape[26]","props":{"x":"36cm","y":"10cm"}},
  {"command":"set","path":"/slide[7]/shape[27]","props":{"x":"36cm","y":"15cm"}},
  {"command":"set","path":"/slide[7]/shape[28]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[7]/shape[29]","props":{"x":"36cm","y":"5cm"}},
  {"command":"set","path":"/slide[7]/shape[30]","props":{"x":"36cm","y":"10cm"}},
  {"command":"set","path":"/slide[7]/shape[31]","props":{"text":"征途未完","font":"苹方-简","size":"64","bold":"true","color":"FFFFFF","align":"center","valign":"middle","width":"26cm","height":"3.5cm","x":"4cm","y":"5.5cm"}},
  {"command":"set","path":"/slide[7]/shape[32]","props":{"text":"从第一颗卫星到空间站，从月球漫步到火星梦想，人类的探索永不止步。星辰大海，就在前方。","font":"苹方-简","size":"20","color":"B8C5D6","align":"center","valign":"middle","width":"26cm","height":"5cm","x":"4cm","y":"10cm"}}
]
BATCH_EOF

# ===== Validate =====
echo "Validating..."
officecli validate "$FILENAME"

echo "Build complete: $FILENAME"
echo "Total slides: 7"
''',

    'science--time-travel': '''
#!/bin/bash
set -e

# Generate Python script
cat << 'PYEOF' > build_internal.py
import json
import os
import subprocess

file_name = "Time_Travel.pptx"

def run_batch(name, batch_data):
    with open(f"{name}.json", "w", encoding="utf-8") as f:
        json.dump(batch_data, f)
    subprocess.run(f"cat {name}.json | officecli batch {file_name}", shell=True, check=True)

subprocess.run(["officecli", "create", file_name], check=True)
subprocess.run(["officecli", "add", file_name, "/", "--type", "slide", "--prop", "layout=blank", "--prop", "background=050510"], check=True)

slide1 = [
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!bg-glow1","preset":"ellipse","fill":"8A2BE2","opacity":"0.15","x":"0cm","y":"0cm","width":"15cm","height":"15cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!bg-glow2","preset":"ellipse","fill":"00FFFF","opacity":"0.15","x":"18cm","y":"4cm","width":"15cm","height":"15cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!ring","preset":"donut","fill":"none","line":"00FFFF","lineWidth":"2","x":"25cm","y":"2cm","width":"5cm","height":"5cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!line-top","preset":"rect","fill":"8A2BE2","x":"4cm","y":"2cm","width":"8cm","height":"0.1cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!star1","preset":"star5","fill":"00FFFF","opacity":"0.5","x":"3cm","y":"15cm","width":"1cm","height":"1cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!star2","preset":"star5","fill":"8A2BE2","opacity":"0.5","x":"30cm","y":"12cm","width":"1.5cm","height":"1.5cm"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!hero-title","text":"穿越时空：科学还是幻想？","x":"4cm","y":"7cm","width":"26cm","height":"3cm","font":"思源黑体","size":"56","color":"FFFFFF","bold":"true","align":"center"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!hero-sub","text":"从爱因斯坦的相对论到现代量子物理的探索之旅","x":"4cm","y":"10.5cm","width":"26cm","height":"2cm","font":"思源黑体","size":"24","color":"AAAAAA","align":"center"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!statement-text","text":"时间并非绝对的流逝，\n而是一种可以被弯曲的维度。","x":"36cm","y":"0cm","width":"30cm","height":"6cm","font":"思源黑体","size":"44","color":"FFFFFF","bold":"true","align":"center","lineSpacing":"1.5"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!statement-sub","text":"根据广义相对论，引力越强，时间流逝越慢。我们每个人都已经是时间旅行者，只不过只能以每秒一秒的速度走向未来。","x":"36cm","y":"1cm","width":"26cm","height":"4cm","font":"思源黑体","size":"20","color":"AAAAAA","align":"center"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!pillar-title","text":"物理学中的三种时间旅行可能","x":"36cm","y":"2cm","width":"20cm","height":"2cm","font":"思源黑体","size":"36","color":"FFFFFF","bold":"true"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!pillar-1-bg","preset":"roundRect","fill":"111122","opacity":"0.6","x":"36cm","y":"3cm","width":"9cm","height":"11cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!pillar-1-title","text":"虫洞理论","x":"36cm","y":"4cm","width":"7cm","height":"1.5cm","font":"思源黑体","size":"28","color":"00FFFF","bold":"true"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!pillar-1-desc","text":"连接宇宙中两个遥远时空点的捷径，理论上可以实现瞬间跨越，如爱因斯坦-罗森桥。","x":"36cm","y":"5cm","width":"7cm","height":"6cm","font":"思源黑体","size":"18","color":"CCCCCC","lineSpacing":"1.3"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!pillar-2-bg","preset":"roundRect","fill":"111122","opacity":"0.6","x":"36cm","y":"6cm","width":"9cm","height":"11cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!pillar-2-title","text":"光速飞行","x":"36cm","y":"7cm","width":"7cm","height":"1.5cm","font":"思源黑体","size":"28","color":"00FFFF","bold":"true"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!pillar-2-desc","text":"当物体运动速度接近光速时，自身时间会显著变慢，从而穿越到相对的未来（双生子佯谬）。","x":"36cm","y":"8cm","width":"7cm","height":"6cm","font":"思源黑体","size":"18","color":"CCCCCC","lineSpacing":"1.3"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!pillar-3-bg","preset":"roundRect","fill":"111122","opacity":"0.6","x":"36cm","y":"9cm","width":"9cm","height":"11cm"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!pillar-3-title","text":"宇宙弦","x":"36cm","y":"10cm","width":"7cm","height":"1.5cm","font":"思源黑体","size":"28","color":"00FFFF","bold":"true"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!pillar-3-desc","text":"假设存在的高密度能量细丝，其强大的引力场可能导致时空闭合，形成时间循环。","x":"36cm","y":"11cm","width":"7cm","height":"6cm","font":"思源黑体","size":"18","color":"CCCCCC","lineSpacing":"1.3"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!evi-title","text":"时间膨胀的真实观测数据","x":"36cm","y":"12cm","width":"20cm","height":"2cm","font":"思源黑体","size":"36","color":"FFFFFF","bold":"true"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!evi-data","text":"38 微秒","x":"36cm","y":"13cm","width":"12cm","height":"4cm","font":"Montserrat","size":"80","color":"00FFFF","bold":"true"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!evi-desc","text":"GPS卫星每天必须调整38微秒的时钟误差。由于卫星在太空中受到的引力较小且运动速度快，其时间流逝速度与地面不同。如果不修正，GPS定位每天会产生10公里的误差。","x":"36cm","y":"14cm","width":"15cm","height":"8cm","font":"思源黑体","size":"22","color":"CCCCCC","lineSpacing":"1.5"}},

  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!cta-title","text":"未来，我们会在过去相遇吗？","x":"36cm","y":"15cm","width":"26cm","height":"3cm","font":"思源黑体","size":"52","color":"FFFFFF","bold":"true","align":"center"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"name":"!!cta-sub","text":"保持对宇宙的敬畏与好奇","x":"36cm","y":"16cm","width":"26cm","height":"2cm","font":"思源黑体","size":"24","color":"00FFFF","align":"center"}}
]
run_batch("slide1", slide1)

slide2 = [
  {"command":"add","parent":"/","from":"/slide[1]","type":"slide"},
  {"command":"set","path":"/slide[2]","props":{"transition":"morph"}},
  {"command":"set","path":"/slide[2]/shape[1]","props":{"x":"10cm","y":"2cm","width":"14cm","height":"14cm"}},
  {"command":"set","path":"/slide[2]/shape[2]","props":{"x":"5cm","y":"5cm","width":"10cm","height":"10cm"}},
  {"command":"set","path":"/slide[2]/shape[3]","props":{"x":"15cm","y":"10cm","width":"8cm","height":"8cm"}},
  {"command":"set","path":"/slide[2]/shape[4]","props":{"x":"12cm","y":"15cm","width":"10cm","height":"0.1cm"}},
  {"command":"set","path":"/slide[2]/shape[5]","props":{"x":"28cm","y":"4cm"}},
  {"command":"set","path":"/slide[2]/shape[6]","props":{"x":"5cm","y":"10cm"}},
  {"command":"set","path":"/slide[2]/shape[7]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[2]/shape[8]","props":{"x":"36cm","y":"1cm"}},
  {"command":"set","path":"/slide[2]/shape[9]","props":{"x":"2cm","y":"6cm"}},
  {"command":"set","path":"/slide[2]/shape[10]","props":{"x":"4cm","y":"13cm"}}
]
run_batch("slide2", slide2)

slide3 = [
  {"command":"add","parent":"/","from":"/slide[1]","type":"slide"},
  {"command":"set","path":"/slide[3]","props":{"transition":"morph"}},
  {"command":"set","path":"/slide[3]/shape[1]","props":{"x":"0cm","y":"12cm","width":"10cm","height":"10cm"}},
  {"command":"set","path":"/slide[3]/shape[2]","props":{"x":"23cm","y":"0cm","width":"12cm","height":"12cm"}},
  {"command":"set","path":"/slide[3]/shape[3]","props":{"x":"30cm","y":"15cm","width":"3cm","height":"3cm"}},
  {"command":"set","path":"/slide[3]/shape[4]","props":{"x":"2cm","y":"2cm","width":"5cm","height":"0.1cm"}},
  {"command":"set","path":"/slide[3]/shape[5]","props":{"x":"20cm","y":"2cm"}},
  {"command":"set","path":"/slide[3]/shape[6]","props":{"x":"10cm","y":"17cm"}},
  {"command":"set","path":"/slide[3]/shape[7]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[3]/shape[8]","props":{"x":"36cm","y":"1cm"}},
  {"command":"set","path":"/slide[3]/shape[9]","props":{"x":"36cm","y":"2cm"}},
  {"command":"set","path":"/slide[3]/shape[10]","props":{"x":"36cm","y":"3cm"}},
  {"command":"set","path":"/slide[3]/shape[11]","props":{"x":"2cm","y":"1.5cm"}},
  {"command":"set","path":"/slide[3]/shape[12]","props":{"x":"2cm","y":"5cm"}},
  {"command":"set","path":"/slide[3]/shape[13]","props":{"x":"3cm","y":"6cm"}},
  {"command":"set","path":"/slide[3]/shape[14]","props":{"x":"3cm","y":"8cm"}},
  {"command":"set","path":"/slide[3]/shape[15]","props":{"x":"12.5cm","y":"5cm"}},
  {"command":"set","path":"/slide[3]/shape[16]","props":{"x":"13.5cm","y":"6cm"}},
  {"command":"set","path":"/slide[3]/shape[17]","props":{"x":"13.5cm","y":"8cm"}},
  {"command":"set","path":"/slide[3]/shape[18]","props":{"x":"23cm","y":"5cm"}},
  {"command":"set","path":"/slide[3]/shape[19]","props":{"x":"24cm","y":"6cm"}},
  {"command":"set","path":"/slide[3]/shape[20]","props":{"x":"24cm","y":"8cm"}}
]
run_batch("slide3", slide3)

slide4 = [
  {"command":"add","parent":"/","from":"/slide[1]","type":"slide"},
  {"command":"set","path":"/slide[4]","props":{"transition":"morph"}},
  {"command":"set","path":"/slide[4]/shape[1]","props":{"x":"2cm","y":"4cm","width":"12cm","height":"12cm","fill":"111122","opacity":"0.6"}},
  {"command":"set","path":"/slide[4]/shape[2]","props":{"x":"16cm","y":"5cm","width":"16cm","height":"10cm","opacity":"0.1"}},
  {"command":"set","path":"/slide[4]/shape[3]","props":{"x":"5cm","y":"5cm","width":"6cm","height":"6cm"}},
  {"command":"set","path":"/slide[4]/shape[4]","props":{"x":"15cm","y":"8cm","width":"15cm","height":"0.1cm"}},
  {"command":"set","path":"/slide[4]/shape[5]","props":{"x":"30cm","y":"3cm"}},
  {"command":"set","path":"/slide[4]/shape[6]","props":{"x":"8cm","y":"16cm"}},
  {"command":"set","path":"/slide[4]/shape[7]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[4]/shape[8]","props":{"x":"36cm","y":"1cm"}},
  {"command":"set","path":"/slide[4]/shape[21]","props":{"x":"2cm","y":"1.5cm"}},
  {"command":"set","path":"/slide[4]/shape[22]","props":{"x":"4cm","y":"8cm"}},
  {"command":"set","path":"/slide[4]/shape[23]","props":{"x":"16cm","y":"7cm"}}
]
run_batch("slide4", slide4)

slide5 = [
  {"command":"add","parent":"/","from":"/slide[1]","type":"slide"},
  {"command":"set","path":"/slide[5]","props":{"transition":"morph"}},
  {"command":"set","path":"/slide[5]/shape[1]","props":{"x":"0cm","y":"0cm","width":"15cm","height":"15cm","fill":"8A2BE2","opacity":"0.15"}},
  {"command":"set","path":"/slide[5]/shape[2]","props":{"x":"18cm","y":"4cm","width":"15cm","height":"15cm"}},
  {"command":"set","path":"/slide[5]/shape[3]","props":{"x":"25cm","y":"2cm","width":"5cm","height":"5cm"}},
  {"command":"set","path":"/slide[5]/shape[4]","props":{"x":"13cm","y":"16cm","width":"8cm","height":"0.1cm"}},
  {"command":"set","path":"/slide[5]/shape[5]","props":{"x":"6cm","y":"5cm"}},
  {"command":"set","path":"/slide[5]/shape[6]","props":{"x":"28cm","y":"15cm"}},
  {"command":"set","path":"/slide[5]/shape[7]","props":{"x":"36cm","y":"0cm"}},
  {"command":"set","path":"/slide[5]/shape[8]","props":{"x":"36cm","y":"1cm"}},
  {"command":"set","path":"/slide[5]/shape[24]","props":{"x":"4cm","y":"7cm"}},
  {"command":"set","path":"/slide[5]/shape[25]","props":{"x":"4cm","y":"11cm"}}
]
run_batch("slide5", slide5)
PYEOF

python3 build_internal.py
rm build_internal.py slide1.json slide2.json slide3.json slide4.json slide5.json
''',

    'tech--wildlife-company': '''
#!/bin/bash
set -e

FILENAME="野生动物科技公司.pptx"

echo "Creating PPT: $FILENAME"

# Create PPT file
officecli create "$FILENAME"

# Add slide 1 with background
officecli add "$FILENAME" '/' --type slide --prop layout=blank --prop background=FFF8F0

# Add all actors to slide 1 using batch
cat << 'EOF' | officecli batch "$FILENAME"
[
  {
    "command": "add",
    "parent": "/slide[1]",
    "type": "shape",
    "props": {
      "name": "dot-accent1",
      "preset": "ellipse",
      "fill": "FF8C42",
      "opacity": "0.12",
      "x": "28cm",
      "y": "2cm",
      "width": "7cm",
      "height": "7cm"
    }
  },
  {
    "command": "add",
    "parent": "/slide[1]",
    "type": "shape",
    "props": {
      "name": "dot-accent2",
      "preset": "ellipse",
      "fill": "FFD166",
      "opacity": "0.15",
      "x": "2cm",
      "y": "13cm",
      "width": "5cm",
      "height": "5cm"
    }
  },
  {
    "command": "add",
    "parent": "/slide[1]",
    "type": "shape",
    "props": {
      "name": "rect-bg",
      "preset": "roundRect",
      "fill": "6AB547",
      "opacity": "0.1",
      "x": "0cm",
      "y": "7cm",
      "width": "8cm",
      "height": "10cm"
    }
  },
  {
    "command": "add",
    "parent": "/slide[1]",
    "type": "shape",
    "props": {
      "name": "triangle-corner",
      "preset": "triangle",
      "fill": "FF8C42",
      "opacity": "0.12",
      "x": "1cm",
      "y": "1cm",
      "width": "3cm",
      "height": "3cm",
      "rotation": "30"
    }
  },
  {
    "command": "add",
    "parent": "/slide[1]",
    "type": "shape",
    "props": {
      "name": "leaf-shape",
      "preset": "ellipse",
      "fill": "6AB547",
      "opacity": "0.12",
      "x": "25cm",
      "y": "12cm",
      "width": "4cm",
      "height": "6cm",
      "rotation": "45"
    }
  },
  {
    "command": "add",
    "parent": "/slide[1]",
    "type": "shape",
    "props": {
      "name": "circle-small",
      "preset": "ellipse",
      "fill": "FFD166",
      "opacity": "0.15",
      "x": "30cm",
      "y": "15cm",
      "width": "2.5cm",
      "height": "2.5cm"
    }
  },
  {
    "command": "add",
    "parent": "/slide[1]",
    "type": "shape",
    "props": {
      "name": "roundrect-float",
      "preset": "roundRect",
      "fill": "FF8C42",
      "opacity": "0.08",
      "x": "15cm",
      "y": "1cm",
      "width": "5cm",
      "height": "3cm",
      "rotation": "15"
    }
  },
  {
    "command": "add",
    "parent": "/slide[1]",
    "type": "shape",
    "props": {
      "name": "ellipse-glow",
      "preset": "ellipse",
      "fill": "6AB547",
      "opacity": "0.1",
      "x": "24cm",
      "y": "8cm",
      "width": "6cm",
      "height": "4cm"
    }
  },
  {
    "command": "add",
    "parent": "/slide[1]",
    "type": "shape",
    "props": {
      "name": "hero-title",
      "text": "野生动物科技公司",
      "font": "PingFang SC",
      "size": "68",
      "bold": "true",
      "color": "4A4A4A",
      "align": "center",
      "valign": "middle",
      "x": "6cm",
      "y": "6cm",
      "width": "22cm",
      "height": "3cm"
    }
  },
  {
    "command": "add",
    "parent": "/slide[1]",
    "type": "shape",
    "props": {
      "name": "hero-subtitle",
      "text": "WildTech Inc. — 让天性驱动创新",
      "font": "PingFang SC",
      "size": "32",
      "color": "FF8C42",
      "align": "center",
      "valign": "middle",
      "x": "8cm",
      "y": "9.5cm",
      "width": "18cm",
      "height": "1.5cm"
    }
  },
  {
    "command": "add",
    "parent": "/slide[1]",
    "type": "shape",
    "props": {
      "name": "hero-tagline",
      "text": "当动物王国遇见硅谷",
      "font": "PingFang SC",
      "size": "20",
      "color": "6AB547",
      "align": "center",
      "valign": "middle",
      "x": "11cm",
      "y": "11.5cm",
      "width": "12cm",
      "height": "1cm"
    }
  },
  {
    "command": "add",
    "parent": "/slide[1]",
    "type": "shape",
    "props": {
      "name": "section-title",
      "text": "",
      "font": "PingFang SC",
      "size": "40",
      "bold": "true",
      "color": "4A4A4A",
      "x": "36cm",
      "y": "0cm",
      "width": "20cm",
      "height": "2cm"
    }
  },
  {
    "command": "add",
    "parent": "/slide[1]",
    "type": "shape",
    "props": {
      "name": "statement-text",
      "text": "",
      "font": "PingFang SC",
      "size": "52",
      "bold": "true",
      "color": "4A4A4A",
      "align": "center",
      "valign": "middle",
      "x": "36cm",
      "y": "5cm",
      "width": "26cm",
      "height": "3cm"
    }
  },
  {
    "command": "add",
    "parent": "/slide[1]",
    "type": "shape",
    "props": {
      "name": "statement-sub",
      "text": "",
      "font": "PingFang SC",
      "size": "24",
      "color": "6AB547",
      "align": "center",
      "valign": "middle",
      "x": "36cm",
      "y": "10cm",
      "width": "28cm",
      "height": "4cm"
    }
  }
]
EOF

echo "Slide 1 complete (hero)"

# Clone and adjust for slide 2
officecli add "$FILENAME" '/' --from '/slide[1]'
cat slide2.json | officecli batch "$FILENAME"
echo "Slide 2 complete (statement)"

# Clone and adjust for slide 3
officecli add "$FILENAME" '/' --from '/slide[1]'
cat slide3.json | officecli batch "$FILENAME"
echo "Slide 3 complete (pillars)"

# Clone and adjust for slide 4
officecli add "$FILENAME" '/' --from '/slide[1]'
cat slide4.json | officecli batch "$FILENAME"
echo "Slide 4 complete (evidence)"

# Clone and adjust for slide 5
officecli add "$FILENAME" '/' --from '/slide[1]'
cat slide5.json | officecli batch "$FILENAME"
echo "Slide 5 complete (showcase)"

# Clone and adjust for slide 6
officecli add "$FILENAME" '/' --from '/slide[1]'
cat slide6.json | officecli batch "$FILENAME"
echo "Slide 6 complete (quote)"

# Clone and adjust for slide 7
officecli add "$FILENAME" '/' --from '/slide[1]'
cat slide7.json | officecli batch "$FILENAME"
echo "Slide 7 complete (cta)"

# Validate
echo "Validating PPT..."
officecli validate "$FILENAME"

echo "✅ PPT generation complete: $FILENAME"
echo "View outline:"
officecli view "$FILENAME" outline
''',

}

TEMPLATE_METADATA = {
    'brand--aura-coffee': {
        'id': 'builtin_brand--aura-coffee',
        'dir_name': 'brand--aura-coffee',
        'name': '品牌 - 咖啡美学',
        'category': '品牌',
        'tags': ["品牌", "极简", "咖啡", "浅色"],
        'description': '极简品牌展示风格，适合咖啡/轻食品牌',
        'background_color': 'F9F6F0',
        'font': 'Montserrat',
        'template_type': 'builtin'
    },
    'brand--aura-coffee-dark': {
        'id': 'builtin_brand--aura-coffee-dark',
        'dir_name': 'brand--aura-coffee-dark',
        'name': '品牌 - 咖啡美学（深色）',
        'category': '品牌',
        'tags': ["品牌", "极简", "咖啡", "深色"],
        'description': '奢华极简深色主题，适合高端品牌展示',
        'background_color': 'FFFFFF',
        'font': 'Helvetica',
        'template_type': 'builtin'
    },
    'future--2050-vision': {
        'id': 'builtin_future--2050-vision',
        'dir_name': 'future--2050-vision',
        'name': '未来 - 2050愿景',
        'category': '未来',
        'tags': ["未来", "科技"],
        'description': '未来愿景展示风格，适合前瞻性话题',
        'background_color': '0B0C10',
        'font': '思源黑体',
        'template_type': 'builtin'
    },
    'lifestyle--cat-philosophy': {
        'id': 'builtin_lifestyle--cat-philosophy',
        'dir_name': 'lifestyle--cat-philosophy',
        'name': '生活 - 猫咪哲学',
        'category': '生活',
        'tags': ["生活", "趣味", "猫咪"],
        'description': '趣味生活哲学风格，适合轻松话题',
        'background_color': 'FFF9E6',
        'font': 'Source Han Sans',
        'template_type': 'builtin'
    },
    'lifestyle--cat-secret-life': {
        'id': 'builtin_lifestyle--cat-secret-life',
        'dir_name': 'lifestyle--cat-secret-life',
        'name': '生活 - 猫咪秘密',
        'category': '生活',
        'tags': ["生活", "趣味", "猫咪"],
        'description': '温馨生活记录风格，适合日常分享',
        'background_color': 'FFFFFF',
        'font': '$FONT_MAIN',
        'template_type': 'builtin'
    },
    'product--geminicli-timetravel': {
        'id': 'builtin_product--geminicli-timetravel',
        'dir_name': 'product--geminicli-timetravel',
        'name': '产品 - 时光穿梭',
        'category': '产品',
        'tags': ["产品", "科技"],
        'description': '科技产品推广风格，适合AI/工具产品',
        'background_color': '0B0F19',
        'font': '$FONT_CN',
        'template_type': 'builtin'
    },
    'productivity--attention-budget': {
        'id': 'builtin_productivity--attention-budget',
        'dir_name': 'productivity--attention-budget',
        'name': '效率 - 注意力预算',
        'category': '效率',
        'tags': ["效率", "专注"],
        'description': '专注力管理风格，适合效率/时间管理',
        'background_color': '0B0F1A',
        'font': 'PingFang SC',
        'template_type': 'builtin'
    },
    'science--alien-guide': {
        'id': 'builtin_science--alien-guide',
        'dir_name': 'science--alien-guide',
        'name': '科学 - 外星指南',
        'category': '科学',
        'tags': ["科幻", "深色", "外星", "霓虹"],
        'description': '深色科幻风格，适合地外生命/未来主题',
        'background_color': 'FFFFFF',
        'font': '思源黑体',
        'template_type': 'builtin'
    },
    'science--space-exploration': {
        'id': 'builtin_science--space-exploration',
        'dir_name': 'science--space-exploration',
        'name': '科学 - 太空探索',
        'category': '科学',
        'tags': ["科幻", "深色", "太空", "宇宙"],
        'description': '太空探索旅程演示风格',
        'background_color': 'FFFFFF',
        'font': '苹方-简',
        'template_type': 'builtin'
    },
    'science--time-travel': {
        'id': 'builtin_science--time-travel',
        'dir_name': 'science--time-travel',
        'name': '科学 - 时间旅行',
        'category': '科学',
        'tags': ["科幻", "深色", "时间"],
        'description': '宇宙霓虹风格，适合未来/科幻主题',
        'background_color': '050510',
        'font': '思源黑体',
        'template_type': 'builtin'
    },
    'tech--wildlife-company': {
        'id': 'builtin_tech--wildlife-company',
        'dir_name': 'tech--wildlife-company',
        'name': '科技 - 野生动物',
        'category': '科技',
        'tags': ["科技", "自然"],
        'description': '自然科技公司风格，适合环保/科技结合',
        'background_color': 'FFF8F0',
        'font': 'PingFang SC',
        'template_type': 'builtin'
    },
}

def get_build_sh_content(template_id: str) -> str:
    """获取指定模板的build.sh内容"""
    dir_name = template_id.replace('builtin_', '')
    return BUILD_SH_CONTENT.get(dir_name, '')

def get_template_metadata(template_id: str) -> dict:
    """获取指定模板的元数据"""
    dir_name = template_id.replace('builtin_', '')
    return TEMPLATE_METADATA.get(dir_name, {})

def get_all_template_ids() -> list:
    """获取所有可用模板ID列表"""
    return [f'builtin_{dir_name}' for dir_name in BUILD_SH_CONTENT.keys()]
