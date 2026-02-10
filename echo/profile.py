"""User profile management - ECHO.md generation and updates"""

from __future__ import annotations
from typing import TYPE_CHECKING
from pathlib import Path
import os

if TYPE_CHECKING:
    from neuromemory_client import NeuroMemoryClient


ECHO_MD_TEMPLATE = """# ECHO.md - {user_name} 的学习档案

> 这是你的个性化学习档案，由 Echo AI 助理维护。
> 详细信息存储在 NeuroMemory 后端，此文件仅作为快速索引。

---

## 👤 基本信息

- **用户 ID**: `{user_id}`
- **档案创建**: {created_date}
- **最后更新**: {last_updated}

---

## 🎯 学习偏好

{preferences}

---

## 🌳 技能树

### 已掌握 ✅
{skills_mastered}

### 学习中 📚
{skills_learning}

### 计划学习 📋
{skills_planned}

---

## 💡 兴趣领域

{interest_areas}

---

## 📊 学习统计

- **累计学习资源**: {resources_count} 个
- **知识点数量**: {knowledge_points} 个
- **学习天数**: {learning_days} 天

---

## 🔍 记忆查询指南

> 以下是获取详细信息的查询方式（供 Echo Agent 使用）

### 获取学习资源
```python
# 所有学习资源
client.files.list(user_id="{user_id}", category="learning")

# 特定主题的资源
client.files.search(user_id="{user_id}", query="[主题名称]")
```

### 搜索知识点
```python
# 搜索相关事实
client.memory.get_facts(user_id="{user_id}", category="[领域]")

# 语义检索
client.memory.search(user_id="{user_id}", query="[查询内容]")
```

### 查看学习历程
```python
# 最近学习活动
client.memory.get_episodes(user_id="{user_id}", limit=30)

# 学习时间线
client.memory.get_timeline(user_id="{user_id}")
```

### 知识图谱
```python
# 获取某个主题的知识图谱
client.graph.get_neighbors(
    user_id="{user_id}",
    node_type="Concept",
    node_id="[主题]"
)
```

---

## 📝 重要笔记

{important_notes}

---

## 🎓 当前学习重点

{current_focus}

---

**最后会话**: {last_conversation}

---

_此文件由 Echo AI 自动生成和维护。_
_详细内容存储在 NeuroMemory: https://github.com/zhuqingxun/NeuroMemory_
"""


class UserProfile:
    """User profile manager for ECHO.md"""

    def __init__(self, memory: NeuroMemoryClient, user_id: str, profile_dir: str = None):
        """Initialize profile manager

        Args:
            memory: NeuroMemory client
            user_id: User identifier
            profile_dir: Directory to store ECHO.md (default: ~/.echo/profiles/)
        """
        self.memory = memory
        self.user_id = user_id

        # Default profile directory
        if profile_dir is None:
            profile_dir = os.path.expanduser("~/.echo/profiles")

        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(parents=True, exist_ok=True)

        self.profile_path = self.profile_dir / f"{user_id}_ECHO.md"

    def generate(self, user_name: str = None) -> str:
        """Generate ECHO.md from NeuroMemory data

        Args:
            user_name: User display name (optional)

        Returns:
            Generated ECHO.md content
        """
        from datetime import datetime

        # Gather data from NeuroMemory
        profile_data = self._gather_profile_data()

        # Format template
        content = ECHO_MD_TEMPLATE.format(
            user_name=user_name or self.user_id,
            user_id=self.user_id,
            created_date=profile_data.get("created_date", datetime.now().strftime("%Y-%m-%d")),
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M"),
            preferences=self._format_preferences(profile_data.get("preferences", [])),
            skills_mastered=self._format_skills(profile_data.get("skills_mastered", [])),
            skills_learning=self._format_skills(profile_data.get("skills_learning", [])),
            skills_planned=self._format_skills(profile_data.get("skills_planned", [])),
            interest_areas=self._format_interests(profile_data.get("interests", [])),
            resources_count=profile_data.get("resources_count", 0),
            knowledge_points=profile_data.get("knowledge_points", 0),
            learning_days=profile_data.get("learning_days", 0),
            important_notes=self._format_notes(profile_data.get("important_notes", [])),
            current_focus=self._format_focus(profile_data.get("current_focus", [])),
            last_conversation=profile_data.get("last_conversation", "N/A"),
        )

        return content

    def save(self, content: str = None, user_name: str = None):
        """Save ECHO.md to file

        Args:
            content: Profile content (if None, will generate)
            user_name: User display name
        """
        if content is None:
            content = self.generate(user_name)

        with open(self.profile_path, "w", encoding="utf-8") as f:
            f.write(content)

    def load(self) -> str:
        """Load ECHO.md content

        Returns:
            Profile content or empty string if not exists
        """
        if self.profile_path.exists():
            with open(self.profile_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def update(self, user_name: str = None):
        """Update ECHO.md with latest data from NeuroMemory"""
        self.save(user_name=user_name)

    def _gather_profile_data(self) -> dict:
        """Gather user data from NeuroMemory"""
        try:
            # Get user profile from NeuroMemory
            profile = self.memory.memory.get_user_profile(self.user_id)

            # Get preferences
            preferences = self.memory.memory.get_preferences(self.user_id)

            # Get facts (skills, interests)
            facts = self.memory.memory.get_facts(self.user_id, limit=50)

            # Categorize skills
            skills_mastered = []
            skills_learning = []
            skills_planned = []

            for fact in facts:
                content = fact.get("content", "")
                if "擅长" in content or "熟练" in content:
                    skills_mastered.append(content)
                elif "学习" in content or "正在学" in content:
                    skills_learning.append(content)
                elif "计划" in content or "想学" in content:
                    skills_planned.append(content)

            # Get interests
            interests = [f for f in facts if "感兴趣" in f.get("content", "") or "喜欢" in f.get("content", "")]

            return {
                "preferences": preferences[:5],  # Top 5 preferences
                "skills_mastered": skills_mastered[:5],
                "skills_learning": skills_learning[:3],
                "skills_planned": skills_planned[:3],
                "interests": interests[:5],
                "resources_count": profile.get("documents_count", 0),
                "knowledge_points": len(facts),
                "learning_days": self._calculate_learning_days(),
                "important_notes": self._get_important_notes(),
                "current_focus": self._get_current_focus(),
                "last_conversation": self._get_last_conversation(),
                "created_date": self._get_creation_date(),
            }

        except Exception as e:
            # Return minimal data on error
            return {
                "preferences": [],
                "skills_mastered": [],
                "skills_learning": [],
                "skills_planned": [],
                "interests": [],
                "resources_count": 0,
                "knowledge_points": 0,
                "learning_days": 0,
                "important_notes": [],
                "current_focus": [],
                "last_conversation": "N/A",
                "created_date": "N/A",
            }

    def _format_preferences(self, preferences: list) -> str:
        """Format preferences section"""
        if not preferences:
            return "（暂无记录）"

        lines = []
        for pref in preferences:
            key = pref.get("key", "")
            value = pref.get("value", "")
            # Translate common keys
            key_display = self._translate_key(key)
            lines.append(f"- **{key_display}**: {value}")

        return "\n".join(lines)

    def _format_skills(self, skills: list) -> str:
        """Format skills section"""
        if not skills:
            return "（暂无记录）"

        lines = []
        for skill in skills[:5]:  # Limit to 5
            lines.append(f"- {skill}")

        return "\n".join(lines)

    def _format_interests(self, interests: list) -> str:
        """Format interests section"""
        if not interests:
            return "（暂无记录）"

        # Extract interest keywords
        lines = []
        for interest in interests:
            content = interest.get("content", "")
            lines.append(f"- {content}")

        return "\n".join(lines)

    def _format_notes(self, notes: list) -> str:
        """Format important notes"""
        if not notes:
            return "（暂无重要笔记）"

        lines = []
        for note in notes[:5]:
            lines.append(f"- {note}")

        return "\n".join(lines)

    def _format_focus(self, focus_items: list) -> str:
        """Format current learning focus"""
        if not focus_items:
            return "（暂无特定学习重点）"

        lines = []
        for item in focus_items:
            lines.append(f"- {item}")

        return "\n".join(lines)

    def _translate_key(self, key: str) -> str:
        """Translate preference keys to Chinese"""
        translations = {
            "learning_style": "学习风格",
            "preferred_language": "首选语言",
            "daily_learning_time": "每日学习时间",
            "learning_goal": "学习目标",
            "difficulty_preference": "难度偏好",
        }
        return translations.get(key, key)

    def _calculate_learning_days(self) -> int:
        """Calculate total learning days"""
        # TODO: Query from episodes
        return 0

    def _get_important_notes(self) -> list:
        """Get important notes"""
        # TODO: Query high-priority notes
        return []

    def _get_current_focus(self) -> list:
        """Get current learning focus"""
        # TODO: Query recent learning topics
        try:
            episodes = self.memory.memory.get_episodes(self.user_id, limit=10)
            # Extract topics from recent episodes
            focus = []
            for ep in episodes[:3]:
                content = ep.get("content", "")
                if "学习" in content:
                    focus.append(content[:50] + "...")
            return focus
        except:
            return []

    def _get_last_conversation(self) -> str:
        """Get last conversation timestamp"""
        # TODO: Query from conversations
        return "N/A"

    def _get_creation_date(self) -> str:
        """Get profile creation date"""
        if self.profile_path.exists():
            import datetime
            timestamp = self.profile_path.stat().st_ctime
            return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
        return "N/A"
