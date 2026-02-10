"""Echo Agent - Core learning assistant logic"""

from __future__ import annotations

import logging
from typing import Optional

from anthropic import Anthropic
from neuromemory_client import NeuroMemoryClient

from echo.config import get_settings
from echo.knowledge.graph import KnowledgeGraph
from echo.knowledge.path import LearningPath
from echo.profile import UserProfile
from echo.utils.prompts import SYSTEM_PROMPT, build_context_prompt

logger = logging.getLogger(__name__)


class EchoAgent:
    """Echo - AI Personal Learning Assistant

    Features:
    - Knowledge graph construction
    - Learning path planning
    - Resource management
    - Progress tracking

    Example:
        >>> agent = EchoAgent(user_id="alice")
        >>> agent.chat("我想学习 Rust 编程语言")
        >>> agent.build_knowledge_graph("Rust")
    """

    def __init__(
        self,
        user_id: str,
        neuromemory_api_key: Optional[str] = None,
        claude_api_key: Optional[str] = None,
        user_name: Optional[str] = None,
    ):
        """Initialize Echo agent

        Args:
            user_id: Unique user identifier
            neuromemory_api_key: NeuroMemory API key (optional, from env)
            claude_api_key: Claude API key (optional, from env)
            user_name: User display name (optional, for profile generation)
        """
        settings = get_settings()

        self.user_id = user_id
        self.user_name = user_name or user_id
        self.session_id = None  # Will be set on first interaction
        self._conversation_count = 0  # Track conversations for profile updates

        # Initialize NeuroMemory client
        self.memory = NeuroMemoryClient(
            api_key=neuromemory_api_key or settings.neuromemory_api_key,
            base_url=settings.neuromemory_base_url,
        )

        # Initialize Claude client
        self.claude = Anthropic(
            api_key=claude_api_key or settings.anthropic_api_key
        )

        # Initialize knowledge components
        self.knowledge_graph = KnowledgeGraph(self.memory, user_id)
        self.learning_path = LearningPath(self.memory, user_id)

        # Initialize user profile manager
        self.profile = UserProfile(self.memory, user_id)

        # Load existing profile for quick context
        self.profile_content = self.profile.load()
        if self.profile_content:
            logger.info(f"Loaded existing profile for user: {user_id}")

        # Enable auto memory extraction
        try:
            self.memory.conversations.enable_auto_extract(
                user_id=user_id,
                trigger="message_count",
                threshold=10
            )
        except Exception as e:
            logger.warning(f"Failed to enable auto-extract: {e}")

        logger.info(f"Echo agent initialized for user: {user_id}")

    def chat(self, message: str) -> str:
        """Main chat interface

        Args:
            message: User message

        Returns:
            Assistant response

        Example:
            >>> response = agent.chat("我想学习 Python")
            >>> print(response)
        """
        try:
            # 1. Retrieve relevant context from memory
            context = self._get_context(message)

            # 2. Build prompt with context
            prompt = build_context_prompt(message, context)

            # 3. Call Claude
            response = self.claude.messages.create(
                model="claude-sonnet-4",
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2048,
            )

            answer = response.content[0].text

            # 4. Store conversation in memory
            self._store_conversation(message, answer)

            # 5. Check if this is a learning-related query
            self._process_learning_intent(message, answer)

            return answer

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"抱歉，处理您的请求时出现错误：{str(e)}"

    def build_knowledge_graph(self, topic: str) -> dict:
        """Build knowledge graph for a topic

        Args:
            topic: Learning topic (e.g., "Rust", "Machine Learning")

        Returns:
            Graph structure

        Example:
            >>> graph = agent.build_knowledge_graph("Rust")
            >>> print(graph['concepts'])
        """
        logger.info(f"Building knowledge graph for: {topic}")

        try:
            # Use LLM to generate knowledge structure
            prompt = f"""为主题 "{topic}" 构建知识图谱。

请生成：
1. 核心概念列表（5-10个）
2. 概念之间的关系
3. 学习的先后顺序
4. 每个概念的难度级别

以 JSON 格式返回。"""

            response = self.claude.messages.create(
                model="claude-sonnet-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2048,
            )

            # Parse and store in graph database
            graph_data = self._parse_knowledge_graph(response.content[0].text)
            self.knowledge_graph.build_from_data(topic, graph_data)

            logger.info(f"Knowledge graph built for {topic}")

            # Update profile after significant learning event
            self.update_profile()

            return graph_data

        except Exception as e:
            logger.error(f"Failed to build knowledge graph: {e}")
            return {"error": str(e)}

    def create_learning_path(
        self,
        topic: str,
        current_level: str = "beginner"
    ) -> dict:
        """Create personalized learning path

        Args:
            topic: What to learn
            current_level: beginner/intermediate/advanced

        Returns:
            Learning path structure

        Example:
            >>> path = agent.create_learning_path("Kubernetes", "beginner")
            >>> for step in path['steps']:
            ...     print(step['title'])
        """
        logger.info(f"Creating learning path for {topic} (level: {current_level})")

        # Get user's background from memory
        background = self._get_user_background()

        # Generate learning path using LLM
        path = self.learning_path.plan(
            topic=topic,
            current_level=current_level,
            background=background
        )

        # Store in memory
        self.memory.add_memory(
            user_id=self.user_id,
            content=f"学习路径：{topic}",
            memory_type="plan",
            metadata={
                "topic": topic,
                "level": current_level,
                "path": path
            }
        )

        return path

    def add_resource(
        self,
        url: str,
        category: str = "learning",
        tags: Optional[list[str]] = None
    ) -> dict:
        """Add learning resource (URL or document)

        Args:
            url: Resource URL
            category: Resource category
            tags: Tags for categorization

        Returns:
            Resource metadata

        Example:
            >>> resource = agent.add_resource(
            ...     "https://doc.rust-lang.org/book/",
            ...     tags=["rust", "official"]
            ... )
        """
        logger.info(f"Adding resource: {url}")

        try:
            # Download and store using NeuroMemory
            doc = self.memory.files.add_url(
                user_id=self.user_id,
                url=url,
                category=category,
                auto_extract=True,
                format="markdown"
            )

            # Extract and link to knowledge graph
            self._link_resource_to_knowledge(doc)

            # Update profile after adding resource
            self.update_profile()

            return doc

        except Exception as e:
            logger.error(f"Failed to add resource: {e}")
            return {"error": str(e)}

    def get_learning_progress(self) -> dict:
        """Get user's learning progress

        Returns:
            Progress summary
        """
        # Query from memory
        profile = self.memory.memory.get_user_profile(self.user_id)

        # Calculate progress metrics
        progress = {
            "topics": self._get_learning_topics(),
            "resources_added": profile.get("documents_count", 0),
            "knowledge_points": self._count_knowledge_points(),
            "recent_activities": self._get_recent_activities(),
        }

        return progress

    def review_knowledge(self, topic: Optional[str] = None) -> list[dict]:
        """Generate review questions

        Args:
            topic: Specific topic to review (optional)

        Returns:
            List of review questions
        """
        # Get knowledge points to review
        if topic:
            knowledge = self.memory.memory.get_facts(
                user_id=self.user_id,
                category=topic
            )
        else:
            knowledge = self.memory.memory.get_facts(
                user_id=self.user_id,
                limit=10
            )

        # Generate review questions using LLM
        questions = self._generate_review_questions(knowledge)

        return questions

    def update_profile(self) -> str:
        """Update user's ECHO.md profile

        Returns:
            Path to the updated profile file

        Example:
            >>> agent.update_profile()
            '/Users/alice/.echo/profiles/alice_ECHO.md'
        """
        logger.info(f"Updating profile for user: {self.user_id}")

        try:
            self.profile.update(user_name=self.user_name)
            self.profile_content = self.profile.load()
            logger.info("Profile updated successfully")
            return str(self.profile.profile_path)

        except Exception as e:
            logger.error(f"Failed to update profile: {e}")
            return ""

    def get_profile_path(self) -> str:
        """Get path to user's ECHO.md profile

        Returns:
            Absolute path to profile file
        """
        return str(self.profile.profile_path)

    # ========== Private Helper Methods ==========

    def _get_context(self, message: str) -> dict:
        """Retrieve relevant context from memory"""
        # Semantic search across all memory types
        results = self.memory.memory.search(
            user_id=self.user_id,
            query=message,
            memory_types=["preference", "fact", "episodic", "document"],
            limit=5
        )

        return {
            "relevant_memories": results,
            "preferences": self.memory.memory.get_preferences(self.user_id),
        }

    def _store_conversation(self, user_message: str, assistant_response: str):
        """Store conversation in memory"""
        try:
            self.memory.conversations.add_messages(
                user_id=self.user_id,
                session_id=self.session_id,
                messages=[
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": assistant_response}
                ]
            )

            # Update conversation counter
            self._conversation_count += 1

            # Update profile every 10 conversations
            if self._conversation_count % 10 == 0:
                logger.info("Triggering profile update after 10 conversations")
                self.update_profile()

        except Exception as e:
            logger.warning(f"Failed to store conversation: {e}")

    def _process_learning_intent(self, message: str, response: str):
        """Detect and process learning-related intents"""
        # Keywords that indicate learning intent
        learning_keywords = ["学习", "想学", "教我", "了解", "掌握", "提升"]

        if any(kw in message for kw in learning_keywords):
            logger.info("Learning intent detected, will trigger knowledge graph building")
            # Could trigger background task here

    def _get_user_background(self) -> dict:
        """Get user's background knowledge"""
        facts = self.memory.memory.get_facts(
            user_id=self.user_id,
            category="skill",
            limit=20
        )

        return {
            "skills": [f["content"] for f in facts],
        }

    def _parse_knowledge_graph(self, llm_response: str) -> dict:
        """Parse LLM response into graph structure"""
        # TODO: Implement JSON parsing and validation
        import json
        try:
            return json.loads(llm_response)
        except:
            return {"raw": llm_response}

    def _link_resource_to_knowledge(self, doc: dict):
        """Link resource to knowledge graph"""
        # TODO: Extract topics and link to graph
        pass

    def _get_learning_topics(self) -> list[str]:
        """Get all topics user is learning"""
        # Query from graph or memory
        return []

    def _count_knowledge_points(self) -> int:
        """Count total knowledge points"""
        facts = self.memory.memory.get_facts(self.user_id, limit=1000)
        return len(facts)

    def _get_recent_activities(self, days: int = 7) -> list[dict]:
        """Get recent learning activities"""
        episodes = self.memory.memory.get_episodes(
            user_id=self.user_id,
            limit=10
        )
        return episodes

    def _generate_review_questions(self, knowledge: list[dict]) -> list[dict]:
        """Generate review questions from knowledge points"""
        # TODO: Use LLM to generate questions
        return []

    def close(self):
        """Cleanup resources"""
        self.memory.close()
