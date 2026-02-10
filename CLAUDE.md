# CLAUDE.md

这个文件提供给 Claude Code 的项目上下文和开发指南。

## 项目概述

**Echo** 是一个基于 NeuroMemory 的 AI 个人学习助理，帮助用户：
- 📚 构建知识图谱
- 🎓 规划学习路径
- 💡 智能推荐资源
- 🔄 跟踪学习进度

## 核心依赖

### NeuroMemory (记忆系统)

**项目位置**: `/Users/jacky/code/NeuroMemory`

**作用**: Echo 的记忆和存储后端，提供：
- 会话存储 (KV)
- 知识图谱 (Apache AGE)
- 文档管理 (OBS)
- 向量检索 (pgvector)

**Python SDK 集成**:
```python
from neuromemory_client import NeuroMemoryClient

# 初始化客户端
client = NeuroMemoryClient(
    api_key="nm_xxx",
    base_url="http://localhost:8765"
)

# 高层 API (推荐使用)
client.conversations.add_message(user_id, role, content)
client.memory.search(user_id, query)
client.files.add_document(user_id, file_path)

# 底层 API
client.preferences.set(user_id, key, value)
client.add_memory(user_id, content, memory_type)
client.search(user_id, query)
```

**关键文档**:
- `/Users/jacky/code/NeuroMemory/README.md` - 项目总览
- `/Users/jacky/code/NeuroMemory/CLAUDE.md` - NeuroMemory 开发指南
- `/Users/jacky/code/NeuroMemory/docs/HIGH_LEVEL_API_DESIGN.md` - 高层 API 设计
- `/Users/jacky/code/NeuroMemory/docs/HIGH_LEVEL_API_EXAMPLES.md` - 使用示例
- `/Users/jacky/code/NeuroMemory/sdk/README.md` - SDK 文档

## Echo 项目结构

```
echo/
├── echo/
│   ├── agent.py              # 核心 Agent (重要！)
│   ├── cli.py                # CLI 命令行界面
│   ├── config.py             # 配置管理
│   ├── knowledge/            # 知识管理模块
│   │   ├── graph.py          # 知识图谱
│   │   └── path.py           # 学习路径规划
│   └── utils/
│       └── prompts.py        # Prompt 模板 (重要！)
├── tests/                    # 测试代码
├── pyproject.toml           # 依赖配置
└── .env                     # 环境变量 (需创建)
```

## 快速开始

### 1. 启动 NeuroMemory 服务

```bash
# 方式 1: 使用 Docker (推荐)
cd /Users/jacky/code/NeuroMemory
docker compose -f docker-compose.v2.yml up -d

# 方式 2: 本地运行
cd /Users/jacky/code/NeuroMemory
source .venv/bin/activate
uvicorn server.app.main:app --reload --port 8765
```

### 2. 配置 Echo 环境

```bash
cd /Users/jacky/code/echo
cp .env.example .env

# 编辑 .env 填入:
# ANTHROPIC_API_KEY=sk-ant-xxx
# NEUROMEMORY_API_KEY=nm_xxx
# NEUROMEMORY_BASE_URL=http://localhost:8765
```

### 3. 安装 Echo

```bash
cd /Users/jacky/code/echo
pip install -e .
```

## 开发约定

### 1. 使用 NeuroMemory 存储记忆

**推荐方式 - 高层 API**:
```python
from neuromemory_client import NeuroMemoryClient

class EchoAgent:
    def __init__(self, user_id: str):
        self.memory = NeuroMemoryClient(api_key="...", base_url="...")
        self.user_id = user_id

    def chat(self, message: str) -> str:
        # 1. 检索相关上下文
        context = self.memory.memory.search(
            user_id=self.user_id,
            query=message,
            memory_types=["preference", "fact", "episodic"],
            limit=5
        )

        # 2. 调用 LLM
        response = call_llm(message, context)

        # 3. 存储对话 (自动触发记忆提取)
        self.memory.conversations.add_messages(
            user_id=self.user_id,
            messages=[
                {"role": "user", "content": message},
                {"role": "assistant", "content": response}
            ]
        )

        return response
```

**底层 API (需要时使用)**:
```python
# 手动添加偏好
self.memory.preferences.set(user_id, "learning_style", "visual")

# 手动添加记忆
self.memory.add_memory(
    user_id=user_id,
    content="用户擅长 Python 编程",
    memory_type="fact"
)

# 语义检索
results = self.memory.search(user_id, "用户的编程技能")
```

### 2. 知识图谱管理

Echo 使用 NeuroMemory 的图数据库功能存储知识结构：

```python
# 创建概念节点
self.memory.graph.create_node(
    user_id=user_id,
    node_type="Concept",
    node_id="rust_ownership",
    properties={"name": "所有权", "difficulty": "hard"}
)

# 创建概念关系
self.memory.graph.create_edge(
    user_id=user_id,
    source_type="Concept",
    source_id="rust_basics",
    edge_type="PREREQUISITE",
    target_type="Concept",
    target_id="rust_ownership"
)

# 查询知识图谱
neighbors = self.memory.graph.get_neighbors(
    user_id=user_id,
    node_type="Concept",
    node_id="rust_ownership"
)
```

### 3. 文档和资源管理

```python
# 添加 URL 资源 (自动下载并索引)
doc = self.memory.files.add_url(
    user_id=user_id,
    url="https://doc.rust-lang.org/book/",
    category="learning",
    auto_extract=True
)

# 上传文档
doc = self.memory.files.add_document(
    user_id=user_id,
    file_path="/path/to/tutorial.pdf",
    auto_extract=True
)

# 搜索文档内容
results = self.memory.files.search(
    user_id=user_id,
    query="如何处理错误"
)
```

### 4. Prompt 工程

核心 Prompt 定义在 `echo/utils/prompts.py`：

- `SYSTEM_PROMPT` - Agent 系统提示词
- `KNOWLEDGE_GRAPH_PROMPT` - 知识图谱构建
- `LEARNING_PATH_PROMPT` - 学习路径规划
- `REVIEW_QUESTIONS_PROMPT` - 复习题生成

修改 Prompt 时要考虑：
- 保持与用户记忆的关联
- 利用 NeuroMemory 提供的上下文
- 个性化和适应用户水平

### 5. 错误处理

```python
try:
    result = self.memory.some_operation(...)
except Exception as e:
    logger.error(f"NeuroMemory operation failed: {e}")
    # 降级处理或重试
```

## 常见开发任务

### 添加新功能

1. **在 agent.py 添加方法**
   ```python
   def new_feature(self, ...):
       # 1. 从 NeuroMemory 检索相关信息
       context = self.memory.memory.search(...)

       # 2. 调用 LLM 处理
       result = self.claude.messages.create(...)

       # 3. 存储结果到 NeuroMemory
       self.memory.add_memory(...)

       return result
   ```

2. **在 cli.py 添加命令**
   ```python
   @app.command()
   def new_command(...):
       """命令描述"""
       agent = EchoAgent(user_id)
       result = agent.new_feature(...)
       console.print(result)
   ```

3. **添加测试**
   ```python
   def test_new_feature():
       agent = EchoAgent(user_id="test_user")
       result = agent.new_feature(...)
       assert result is not None
   ```

### 优化 Prompt

1. 编辑 `echo/utils/prompts.py`
2. 测试新 Prompt 效果
3. 迭代优化

### 调试技巧

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看 NeuroMemory 调用
logger.debug(f"Memory search: {query}")
logger.debug(f"Results: {results}")
```

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_agent.py

# 带覆盖率
pytest --cov=echo
```

## 重要提示

### NeuroMemory 依赖
- Echo **强依赖** NeuroMemory 服务
- 开发前确保 NeuroMemory 服务已启动
- 使用高层 API 简化开发

### 数据隔离
- 每个用户的数据通过 `user_id` 隔离
- 测试时使用独立的 `user_id`
- 生产环境使用真实用户标识

### 性能考虑
- 批量操作使用 `add_messages` 而非 `add_message`
- 控制检索结果数量 (`limit` 参数)
- 合理使用缓存

## 相关资源

### NeuroMemory 文档
- [高层 API 设计](/Users/jacky/code/NeuroMemory/docs/HIGH_LEVEL_API_DESIGN.md)
- [使用示例](/Users/jacky/code/NeuroMemory/docs/HIGH_LEVEL_API_EXAMPLES.md)
- [REST API 文档](/Users/jacky/code/NeuroMemory/docs/REST_API.md)

### Echo 文档
- [README.md](./README.md) - 项目概览
- [pyproject.toml](./pyproject.toml) - 依赖管理

### 外部资源
- [Claude API 文档](https://docs.anthropic.com/)
- [Typer 文档](https://typer.tiangolo.com/)
- [Rich 文档](https://rich.readthedocs.io/)

## 开发流程建议

1. **新功能开发**
   - 先在 `agent.py` 实现核心逻辑
   - 充分利用 NeuroMemory 的记忆能力
   - 添加 CLI 命令
   - 编写测试

2. **Bug 修复**
   - 检查 NeuroMemory 服务状态
   - 查看日志定位问题
   - 修复并添加测试

3. **性能优化**
   - 减少 LLM 调用次数
   - 优化 NeuroMemory 查询
   - 使用缓存

## Git 工作流

```bash
# 创建功能分支
git checkout -b feature/new-feature

# 提交变更
git add .
git commit -m "feat: add new feature"

# 推送到远程
git push origin feature/new-feature
```

## 需要帮助？

如果遇到问题：
1. 查看 NeuroMemory 文档
2. 检查日志输出
3. 参考示例代码
4. 在新的 Claude Code 窗口中提问

---

**让我们一起构建最好的 AI 学习助理！** 🚀
