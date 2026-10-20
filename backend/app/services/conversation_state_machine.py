"""
Conversation State Machine Service
Manages conversation state transitions and generates guidance prompts
"""

class ConversationStateMachine:
    """State machine for managing conversation flow"""

    # State definitions - 简化状态，去掉固定需求收集
    STATES = {
        'INITIAL': '初始化',
        'CHAT': '对话中',
        'GENERATING_OUTLINE': '生成大纲',
        'GENERATING_PPT': '生成PPT',
        'PPT_READY': 'PPT已就绪',
        'COMPLETED': '已完成'
    }

    # State transitions - 简化转换逻辑
    STATE_TRANSITIONS = {
        'INITIAL': 'CHAT',
        'CHAT': 'GENERATING_OUTLINE',  # 从对话直接进入生成大纲
        'GENERATING_OUTLINE': 'GENERATING_PPT',  # 大纲生成完成后直接进入生成PPT
        'GENERATING_PPT': 'PPT_READY'
        # 'PPT_READY': 'COMPLETED'  # 注释掉，防止PPT生成完成后自动跳转
    }

    # 不再使用固定的必需字段，改为AI智能判断
    REQUIRED_FIELDS = {}

    def get_guidance_prompt(self, state, requirements):
        """
        Generate guidance prompt based on current state
        采用AI自主引导方式，不使用固定的需求字段

        Args:
            state: Current conversation state
            requirements: Dict of collected information

        Returns:
            System prompt string for GLM
        """
        if state == 'INITIAL':
            return self._get_initial_prompt()
        elif state == 'CHAT':
            return self._get_chat_prompt(requirements)
        elif state == 'OUTLINE_GENERATED':
            return self._get_outline_generated_prompt()
        else:
            return self._get_default_prompt()

    def _get_initial_prompt(self):
        """Initial greeting prompt"""
        return """你是一个专业的AI教学助手，帮助用户生成高质量的PPT和教案。

当前阶段：初始化

你的任务：
1. 热情地欢迎用户
2. 简要介绍你的能力（生成PPT、教案、支持多种格式文档、联网搜索）
3. 引导用户告诉你想制作什么主题的PPT

回复要求：
- 语气友好、专业
- 简洁明了，不要过于冗长
- 主动询问用户的PPT主题"""

    def _get_chat_prompt(self, requirements):
        """
        Chat prompt with AI-guided conversation
        让AI自主判断信息是否足够，主动引导或提议生成

        Args:
            requirements: 已收集的信息（字典）

        Returns:
            System prompt for GLM
        """
        # 构建已收集信息摘要
        collected_info = []
        if requirements.get('topic'):
            collected_info.append(f"主题：{requirements['topic']}")
        if requirements.get('audience'):
            collected_info.append(f"受众：{requirements['audience']}")
        if requirements.get('purpose'):
            collected_info.append(f"用途：{requirements['purpose']}")
        if requirements.get('slide_count'):
            collected_info.append(f"页数：{requirements['slide_count']}页")
        if requirements.get('style'):
            collected_info.append(f"风格：{requirements['style']}")
        if requirements.get('teaching_goal'):
            collected_info.append(f"教学目标：{requirements['teaching_goal']}")
        if requirements.get('key_points'):
            collected_info.append(f"知识要点：{requirements['key_points']}")
        if requirements.get('duration'):
            collected_info.append(f"课时/时长：{requirements['duration']}")
        if requirements.get('output_style'):
            collected_info.append(f"产出风格：{requirements['output_style']}")

        user_turn_count = int(requirements.get('user_turn_count') or 0)

        collected_summary = "已收集信息：\\n" + "\\n".join(collected_info) if collected_info else "暂无具体信息"

        prompt = f"""你是一个专业的AI教学助手，正在通过对话帮助用户准备PPT制作。

{collected_summary}
    当前用户有效对话轮次：{user_turn_count}（按用户发送消息次数统计）

你的任务：
1. 根据对话内容判断是否已经收集了足够的信息来生成PPT
    2. 如果信息不足，自然地询问缺失的关键信息（主题、受众、用途、教学目标、知识要点、时长、页数、产出风格等）
3. 如果信息基本完整（至少有明确的主题），主动提议开始生成PPT大纲
4. 不要过度收集信息，只关注生成PPT的必要内容

判断标准：
- 必须有：明确的主题
- 建议有：目标受众、使用场景
    - 可选：页数（默认10-15页）、风格（默认简约商务）
    - 教学场景优先补充：教学目标、知识要点、时长、产出风格

对话策略：
- 每次只问一个问题，不要一次问多个
- 根据用户的回答灵活调整
- 如果用户提供了多个信息，确认后继续
- 当核心信息（主题、用途、受众）都有时，主动提议生成大纲
    - 当用户需求表述模糊时，优先追问教学目标、知识要点、时长、产出风格
    - 当用户轮次 < 3 时，不要引导用户点击右上角生成按钮（可先继续澄清）
    - 当用户轮次 >= 3 且已有主题，并且至少补充了2项关键信息（受众/用途/教学目标/知识要点/时长/风格）时，在回复结尾追加这句原文：
      “基本信息已确认，若满意可点击右上角生成按钮进行ppt和大纲的生成”
- 当用户说"生成大纲"、"生成思维导图"、"生成PPT"时，表示同意生成

回复示例：
1. "好的！请问这个PPT的目标受众是谁？比如是给小学生、大学生还是企业员工？"
2. "了解了，这个PPT大概需要多少页呢？我建议10-15页比较合适。"
    3. "好的，我已经了解到：主题是人工智能，受众是大学生，用途是教学。我们可以开始生成PPT大纲了，您看可以吗？"
    4. "为了让内容更贴合课堂，请问本节课最核心的教学目标是什么？"
    5. "方便补充下预计时长吗？例如15分钟导入、40分钟完整授课，或90分钟专题课。"
    6. "您希望最终产出的风格偏学术严谨，还是更可视化、互动化？"
4. "好的，我现在就为您生成PPT大纲和思维导图，请稍候..."（当用户说"可以"或"好的"时）
5. "收到！我现在为您生成PPT大纲和思维导图..."（当用户直接说"生成大纲"时）

回复要求：
- 语气自然、友好，不要像机器人一样按顺序提问
- 根据上下文智能判断还需要什么信息
- 避免重复询问已经明确的信息
- 当信息足够时，主动提议下一步行动
- 如果用户主动提出生成要求（如"生成大纲"、"生成PPT"），直接说"好的，我现在为您生成..."，不要再说你需要先收集信息
- 当用户同意生成时，说"好的，我现在为您生成PPT大纲和思维导图，请稍候..."
"""

        return prompt

    def _get_gathering_prompt(self, requirements):
        """Requirements gathering prompt"""
        missing_fields = self._get_missing_fields(requirements)

        prompt = """你是一个专业的AI教学助手，正在帮助用户收集PPT制作需求。

当前阶段：收集需求

已收集的信息：
"""
        for key, value in requirements.items():
            prompt += f"- {self._field_name_cn(key)}: {value}\n"

        prompt += f"\n还需要收集的信息：\n"
        for field in missing_fields:
            prompt += f"- {self._field_name_cn(field)}\n"

        prompt += """
你的任务：
1. 根据已收集的信息，自然地询问下一个缺失的信息
2. 每次只问一个问题，不要一次问多个
3. 提供具体的示例帮助用户理解
4. 如果用户的回答不够明确，礼貌地要求澄清

询问顺序和示例：
- 主题(topic): "请告诉我您想制作什么主题的PPT？"
- 受众(audience): "这个PPT的目标受众是谁？例如：小学生、高中生、大学生、企业员工等"
- 用途(purpose): "PPT的主要用途是什么？例如：课堂教学、会议演示、培训材料、学术报告等"
- 页数(slide_count): "您希望PPT有多少页？建议10-30页"
- 风格(style): "您希望什么样的风格？例如：简约、商务、活泼、学术、科技感等"

回复要求：
- 语气友好、耐心
- 一次只问一个问题
- 提供具体示例
- 如果用户提供了多个信息，要确认并继续询问缺失的"""

        return prompt

    def _get_requirements_complete_prompt(self, requirements):
        """Requirements complete confirmation prompt"""
        return f"""你是一个专业的AI教学助手，已经收集完用户的PPT制作需求。

当前阶段：需求收集完成

收集到的完整需求：
- 主题: {requirements.get('topic', '未知')}
- 受众: {requirements.get('audience', '未知')}
- 用途: {requirements.get('purpose', '未知')}
- 页数: {requirements.get('slide_count', '未知')}
- 风格: {requirements.get('style', '未知')}

你的任务：
1. 总结用户的需求，让用户确认
2. 询问用户是否需要补充或修改
3. 如果用户确认无误，告知即将生成PPT大纲
4. 如果用户需要修改，记录修改内容

回复要求：
- 清晰地总结所有需求
- 给用户确认或修改的机会
- 语气专业、确认性"""

    def _get_outline_generated_prompt(self):
        """Outline generated prompt"""
        return """你是一个专业的AI教学助手，已经为用户生成了PPT大纲。

当前阶段：大纲已生成

你的任务：
1. 解释大纲的结构和内容
2. 询问用户是否满意
3. 如果用户想修改，询问具体要修改哪些部分
4. 如果用户确认，告知即将开始生成完整的PPT

回复要求：
- 简要说明大纲的特点
- 主动询问用户意见
- 对修改请求给出具体建议"""

    def _get_outline_approved_prompt(self):
        """Outline approved prompt"""
        return """你是一个专业的AI教学助手，用户已确认PPT大纲。

当前阶段：大纲已确认

你的任务：
1. 告知用户即将开始生成完整的PPT
2. 说明生成过程可能需要一些时间
3. 询问用户是否需要选择模板

回复要求：
- 简洁明了
- 给用户合理的时间预期"""

    def _get_default_prompt(self):
        """Default prompt for other states"""
        return """你是一个专业的AI教学助手，帮助用户生成高质量的PPT和教案。

请根据用户的问题和当前对话上下文，提供专业、有帮助的回复。

回复要求：
- 语气友好、专业
- 回答准确、有针对性
- 必要时提供具体建议"""

    def should_transition(self, state, user_message, requirements):
        """
        Determine if state should transition
        简化逻辑：INITIAL -> CHAT，CHAT由AI自主判断是否进入生成大纲

        Args:
            state: Current state
            user_message: User's message
            requirements: Current requirements dict

        Returns:
            Boolean indicating if transition should occur
        """
        if state == 'INITIAL':
            # 只要有对话内容就从INITIAL进入CHAT
            return len(user_message.strip()) > 3

        elif state == 'CHAT':
            # 在CHAT状态下，不自动转换
            # AI会在对话中主动提议生成大纲
            # 只有用户明确要求生成时才转换（通过特殊指令）
            generate_keywords = ['开始生成', '生成大纲', '生成ppt', '生成ppt']
            return any(keyword in user_message.lower() for keyword in generate_keywords)

        elif state == 'OUTLINE_GENERATED':
            # 用户确认大纲后生成PPT
            approval_keywords = ['确认', '可以', '没问题', '好的', '满意', '不错', '开始生成', '生成ppt']
            return any(keyword in user_message.lower() for keyword in approval_keywords)

        return False

    def next_state(self, current_state):
        """Get next state in the flow"""
        return self.STATE_TRANSITIONS.get(current_state, current_state)

    def extract_requirements(self, user_message, current_requirements):
        """
        Extract requirement information from user message
        Uses keyword matching and pattern recognition

        Args:
            user_message: User's message
            current_requirements: Current requirements dict

        Returns:
            Updated requirements dict
        """
        import re
        requirements = current_requirements.copy()

        # Extract slide count from anywhere in the message (优先提取页数)
        if 'slide_count' not in requirements or not requirements['slide_count']:
            # 匹配各种页数表达方式
            slide_patterns = [
                r'(\d+)\s*页',
                r'(\d+)\s*张',
                r'(\d+)\s*个幻灯片',
                r'(\d+)\s*slides?',
                r'大概\s*(\d+)',
                r'约\s*(\d+)',
            ]
            for pattern in slide_patterns:
                match = re.search(pattern, user_message)
                if match:
                    requirements['slide_count'] = match.group(1)
                    break

        # Extract teaching duration / class time
        if 'duration' not in requirements or not requirements['duration']:
            duration_patterns = [
                r'(\d+\s*(分钟|小时|课时))',
                r'(一节课|两节课|半节课|整节课)',
                r'(短课|长课|微课)'
            ]
            for pattern in duration_patterns:
                match = re.search(pattern, user_message)
                if match:
                    requirements['duration'] = match.group(1)
                    break

        # Extract teaching goal / objective
        if 'teaching_goal' not in requirements or not requirements['teaching_goal']:
            if any(k in user_message for k in ['教学目标', '目标是', '学习目标', '达成', '掌握', '理解', '会']) and len(user_message.strip()) <= 120:
                requirements['teaching_goal'] = user_message.strip()

        # Extract key points / knowledge points
        if 'key_points' not in requirements or not requirements['key_points']:
            if any(k in user_message for k in ['知识要点', '重点', '难点', '关键点', '核心点', '主要内容']) and len(user_message.strip()) <= 120:
                requirements['key_points'] = user_message.strip()

        # Extract audience keywords
        if 'audience' not in requirements or not requirements['audience']:
            audience_keywords = {
                '小学生': '小学生', '中学生': '中学生', '高中生': '高中生',
                '大学生': '大学生', '研究生': '研究生',
                '企业': '企业员工', '员工': '企业员工',
                '老师': '教师', '教师': '教师',
                '家长': '家长', '儿童': '儿童'
            }
            for keyword, value in audience_keywords.items():
                if keyword in user_message:
                    requirements['audience'] = value
                    break

        # Extract purpose keywords
        if 'purpose' not in requirements or not requirements['purpose']:
            purpose_keywords = {
                '教学': '课堂教学', '课堂': '课堂教学', '上课': '课堂教学',
                '教育': '教育培训', '培训': '培训材料',
                '会议': '会议演示', '演示': '会议演示',
                '报告': '学术报告', '学术': '学术报告',
                '汇报': '工作汇报', '工作': '工作汇报'
            }
            for keyword, value in purpose_keywords.items():
                if keyword in user_message:
                    requirements['purpose'] = value
                    break

        # Extract style keywords
        if 'style' not in requirements or not requirements['style']:
            style_keywords = {
                '简约': '简约', '简洁': '简约', '简单': '简约',
                '商务': '商务', '专业': '商务', '正式': '商务',
                '活泼': '活泼', '可爱': '活泼', '卡通': '活泼',
                '学术': '学术', '科技': '科技感', '现代': '现代',
                '时尚': '时尚', '极简': '简约', '扁平': '简约'
            }
            for keyword, value in style_keywords.items():
                if keyword in user_message:
                    requirements['style'] = value
                    break

            # 支持"XX风格"、"XX感"等变体
            if 'style' not in requirements or not requirements['style']:
                import re
                style_pattern = r'(简约|商务|活泼|学术|科技|现代|时尚|极简|扁平)(风格|感)?'
                match = re.search(style_pattern, user_message)
                if match:
                    base_style = match.group(1)
                    requirements['style'] = style_keywords.get(base_style, base_style)

        # Extract output style preference (教学产出风格)
        if 'output_style' not in requirements or not requirements['output_style']:
            output_style_keywords = {
                '严谨': '学术严谨',
                '学术': '学术严谨',
                '可视化': '可视化表达',
                '互动': '互动引导',
                '故事化': '故事化表达',
                '案例': '案例驱动',
                '项目式': '项目式学习',
                '启发式': '启发式教学'
            }
            for keyword, value in output_style_keywords.items():
                if keyword in user_message:
                    requirements['output_style'] = value
                    break

        # Extract topic (if not already set)
        # 仅在文本像“课程/技术主题”时提取，过滤“我是谁”等闲聊问句
        if 'topic' not in requirements or not requirements['topic']:
            topic_candidate = user_message.strip()
            bad_starters = ['我是谁', '你是谁', '你叫什么', '在吗', '你好', 'hi', 'hello']
            has_bad_starter = any(topic_candidate.lower().startswith(s) for s in bad_starters)
            has_question_mark = ('?' in topic_candidate) or ('？' in topic_candidate)
            has_topic_signal = any(k in topic_candidate for k in [
                '课程', '开发', '编程', '算法', '数据库', '数据存储', '移动应用',
                '教学', '培训', '网络', '架构', '设计', '产品', '运营', '管理'
            ])

            if (
                topic_candidate
                and len(topic_candidate) <= 48
                and not has_bad_starter
                and (has_topic_signal or not has_question_mark)
                and not any(k in topic_candidate for k in ['受众', '用途', '风格', '页', '张', '生成', '大纲'])
            ):
                requirements['topic'] = topic_candidate

        # 注意：不再将整句用户输入直接回填到 audience/purpose/style，
        # 仅保留关键词/规则抽取，避免“记忆=用户原话”

        return requirements

    def _get_missing_fields(self, requirements):
        """Get list of missing required fields (已废弃，保留兼容性）"""
        # 不再使用固定字段，返回空列表
        return []

    def _all_requirements_collected(self, requirements):
        """Check if all required fields are collected (已废弃，保留兼容性）"""
        # 不再使用固定字段，AI自主判断
        return True

    def _field_name_cn(self, field):
        """Get Chinese name for field"""
        field_names = {
            'topic': '主题',
            'audience': '受众',
            'purpose': '用途',
            'slide_count': '页数',
            'style': '风格'
        }
        return field_names.get(field, field)
