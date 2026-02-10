"""Prompt templates for Echo agent"""

SYSTEM_PROMPT = """你是 Echo，一个 AI 个人学习助理。你的职责是：

1. 帮助用户梳理知识体系，构建知识图谱
2. 根据用户背景制定个性化学习路径
3. 推荐相关学习资源和实践项目
4. 跟踪学习进度，提供复习建议

核心原则：
- 基于用户已有知识背景提供建议
- 循序渐进，避免一次性给太多信息
- 注重实践，推荐动手项目
- 记住用户的学习偏好和风格

回答时保持：
- 友好、鼓励的语气
- 结构化、条理清晰
- 具体可执行的建议
"""


def build_context_prompt(message: str, context: dict) -> str:
    """Build prompt with user context

    Args:
        message: User message
        context: Retrieved context from memory

    Returns:
        Complete prompt with context
    """
    context_str = ""

    # Add relevant memories
    if context.get("relevant_memories"):
        context_str += "用户的相关背景信息：\n"
        for mem in context["relevant_memories"][:3]:
            context_str += f"- {mem['content']}\n"
        context_str += "\n"

    # Add preferences
    if context.get("preferences"):
        context_str += "用户偏好：\n"
        for pref in context["preferences"][:5]:
            context_str += f"- {pref['key']}: {pref['value']}\n"
        context_str += "\n"

    prompt = f"""{context_str}用户问题：{message}

请基于用户的背景信息回答问题。"""

    return prompt


KNOWLEDGE_GRAPH_PROMPT = """为主题 "{topic}" 构建知识图谱。

请生成：
1. 核心概念列表（5-10个关键概念）
2. 概念之间的关系和依赖
3. 推荐的学习顺序
4. 每个概念的难度级别（初级/中级/高级）
5. 每个概念的重要性评分（1-5）

返回格式（JSON）：
{{
  "topic": "{topic}",
  "concepts": [
    {{
      "name": "概念名称",
      "level": "beginner|intermediate|advanced",
      "importance": 1-5,
      "description": "概念描述",
      "prerequisites": ["前置概念1", "前置概念2"]
    }}
  ],
  "relationships": [
    {{
      "from": "概念A",
      "to": "概念B",
      "type": "prerequisite|related|part_of"
    }}
  ],
  "learning_path": ["概念1", "概念2", "概念3", ...]
}}
"""


LEARNING_PATH_PROMPT = """为用户创建 "{topic}" 的学习路径。

用户背景：
{background}

用户当前水平：{level}

请生成：
1. 学习阶段划分（3-5个阶段）
2. 每个阶段的学习目标
3. 每个阶段的学习内容
4. 预估学习时间
5. 推荐的学习资源类型（文档/视频/项目等）
6. 实践项目建议

返回格式（JSON）：
{{
  "topic": "{topic}",
  "total_duration": "X 周",
  "stages": [
    {{
      "name": "阶段名称",
      "duration": "X 周",
      "level": "beginner|intermediate|advanced",
      "objectives": ["目标1", "目标2"],
      "topics": ["主题1", "主题2"],
      "resources": ["资源类型1", "资源类型2"],
      "projects": ["项目建议1", "项目建议2"]
    }}
  ]
}}
"""


REVIEW_QUESTIONS_PROMPT = """基于以下知识点，生成复习问题：

{knowledge_points}

请生成：
1. 5-10 个复习问题
2. 包含不同难度级别（简单/中等/困难）
3. 包含不同问题类型（概念理解/应用/综合）

返回格式（JSON）：
{{
  "questions": [
    {{
      "question": "问题内容",
      "type": "concept|application|synthesis",
      "difficulty": "easy|medium|hard",
      "hints": ["提示1", "提示2"],
      "answer_outline": "答案要点"
    }}
  ]
}}
"""


RESOURCE_ANALYSIS_PROMPT = """分析以下学习资源并提取关键信息：

标题：{title}
内容摘要：{content_preview}

请提取：
1. 主要涵盖的知识点（3-5个）
2. 适合的学习阶段（beginner/intermediate/advanced）
3. 资源类型（tutorial/reference/practice/theory）
4. 重点章节或部分
5. 与其他知识点的关联

返回格式（JSON）：
{{
  "topics": ["主题1", "主题2"],
  "level": "beginner|intermediate|advanced",
  "type": "tutorial|reference|practice|theory",
  "highlights": ["重点1", "重点2"],
  "related_concepts": ["关联概念1", "关联概念2"]
}}
"""
