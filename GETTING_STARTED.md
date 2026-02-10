# Echo 快速上手指南

## 给新的 Claude Code 窗口的说明

如果你是在新的 Claude Code 窗口中打开这个项目，请按照以下步骤快速了解项目：

### 步骤 1: 阅读核心文档

**必读文档（按顺序）**:
1. `README.md` - 项目概览和功能介绍
2. `CLAUDE.md` - 开发指南和 NeuroMemory 集成说明 ⭐
3. 这个文件 - 快速上手

### 步骤 2: 了解 NeuroMemory

Echo 依赖 NeuroMemory 作为记忆后端。

**NeuroMemory 核心概念**:
```
NeuroMemory = 通用记忆管理系统
    ├─ 会话存储 (conversations)
    ├─ 偏好管理 (preferences)
    ├─ 向量检索 (embeddings)
    ├─ 知识图谱 (graph)
    └─ 文档管理 (files)
```

**关键文档位置**:
- `/Users/jacky/code/NeuroMemory/CLAUDE.md`
- `/Users/jacky/code/NeuroMemory/docs/HIGH_LEVEL_API_DESIGN.md`
- `/Users/jacky/code/NeuroMemory/docs/HIGH_LEVEL_API_EXAMPLES.md`

### 步骤 3: 查看核心代码

**重要文件（优先级排序）**:

1. **`echo/agent.py`** - Agent 核心逻辑
   - 查看 `EchoAgent` 类
   - 重点看 `chat()` 方法如何使用 NeuroMemory

2. **`echo/utils/prompts.py`** - Prompt 模板
   - 了解系统 Prompt
   - 查看各种任务的 Prompt 设计

3. **`echo/cli.py`** - CLI 命令
   - 了解可用命令
   - 查看用户交互方式

4. **`echo/config.py`** - 配置管理
   - 环境变量配置

### 步骤 4: 使用 Claude Code 技巧

#### 方法 1: 使用 `/prime` 命令（推荐）

在 Claude Code 中输入：
```
/prime
```

然后告诉 Claude：
```
请帮我理解 Echo 项目和它如何使用 NeuroMemory。
我想开发新功能，需要知道如何正确使用记忆系统。
```

#### 方法 2: 直接提问

```
我在开发 Echo 学习助理项目。
请先阅读 CLAUDE.md 了解项目上下文，
然后告诉我如何添加一个新功能来追踪用户的学习进度。
```

#### 方法 3: 让 Claude 搜索相关代码

```
请搜索项目中所有使用 NeuroMemory client 的地方，
帮我理解 Echo 是如何集成记忆系统的。
```

## 环境搭建

### 前置条件

1. **Python 3.10+**
2. **NeuroMemory 服务** (必须运行中)
3. **Claude API Key**

### 安装步骤

```bash
# 1. 确保在正确的目录
cd /Users/jacky/code/echo

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -e .

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入真实的 API Keys
```

### 启动 NeuroMemory 服务

```bash
# 在另一个终端窗口
cd /Users/jacky/code/NeuroMemory
docker compose -f docker-compose.v2.yml up -d

# 验证服务
curl http://localhost:8765/v1/health
```

### 测试 Echo

```bash
# 回到 Echo 目录
cd /Users/jacky/code/echo

# 启动交互式对话
echo chat

# 或直接使用 Python
python
>>> from echo import EchoAgent
>>> agent = EchoAgent(user_id="test_user")
>>> response = agent.chat("你好")
>>> print(response)
```

## 典型开发工作流

### 场景 1: 添加新的学习功能

1. **在 Claude Code 中提问**:
   ```
   我想添加一个功能：根据用户的学习历史，
   自动推荐接下来应该学习的内容。
   这个功能应该如何实现？
   ```

2. **Claude 会帮你**:
   - 分析现有代码结构
   - 建议在哪里添加新功能
   - 展示如何使用 NeuroMemory 查询学习历史
   - 生成示例代码

3. **实施和测试**:
   ```bash
   # 运行测试
   pytest tests/test_agent.py

   # 手动测试
   echo chat
   ```

### 场景 2: 优化 Prompt

1. **告诉 Claude**:
   ```
   我发现知识图谱生成的 Prompt 效果不好，
   请帮我优化 KNOWLEDGE_GRAPH_PROMPT。
   ```

2. **Claude 会**:
   - 读取当前 Prompt
   - 分析问题
   - 提供优化建议
   - 生成改进版本

### 场景 3: 调试问题

1. **描述问题**:
   ```
   用户添加学习资源时报错，
   错误信息是 "Failed to add resource: Connection refused"。
   帮我排查问题。
   ```

2. **Claude 会**:
   - 检查相关代码
   - 验证 NeuroMemory 连接
   - 提供解决方案

## 使用 NeuroMemory 的最佳实践

### ✅ 推荐做法

```python
# 使用高层 API
self.memory.conversations.add_messages(...)
self.memory.memory.search(...)
self.memory.files.add_url(...)

# 批量操作
messages = [{"role": "user", "content": "..."}, ...]
self.memory.conversations.add_messages(user_id, messages)

# 适当的 limit
results = self.memory.memory.search(user_id, query, limit=5)
```

### ❌ 避免做法

```python
# 不要逐条添加消息（效率低）
for msg in messages:
    self.memory.conversations.add_message(user_id, msg["role"], msg["content"])

# 不要过度检索（性能问题）
results = self.memory.memory.search(user_id, query, limit=1000)

# 不要忘记错误处理
result = self.memory.some_operation(...)  # 如果失败会中断程序
```

## 常见问题 FAQ

### Q1: NeuroMemory 服务连接失败？

**检查步骤**:
```bash
# 1. 确认服务运行
curl http://localhost:8765/v1/health

# 2. 检查 .env 配置
cat .env | grep NEUROMEMORY

# 3. 查看服务日志
cd /Users/jacky/code/NeuroMemory
docker compose logs -f
```

### Q2: 如何查看 NeuroMemory 中存储的数据？

```python
from neuromemory_client import NeuroMemoryClient

client = NeuroMemoryClient(api_key="...", base_url="...")

# 查看会话
sessions = client.conversations.list_sessions(user_id="test_user")

# 查看偏好
prefs = client.memory.get_preferences(user_id="test_user")

# 查看事实
facts = client.memory.get_facts(user_id="test_user")

# 查看文档
files = client.files.list(user_id="test_user")
```

### Q3: 如何重置用户数据？

⚠️ **警告**: 这会删除所有数据！

```python
# TODO: NeuroMemory 需要提供清除用户数据的 API
# 目前需要直接操作数据库
```

### Q4: Claude Code 不理解项目上下文？

**解决方法**:
```
请先阅读以下文件来了解项目：
1. /Users/jacky/code/echo/CLAUDE.md
2. /Users/jacky/code/echo/README.md
3. /Users/jacky/code/NeuroMemory/docs/HIGH_LEVEL_API_DESIGN.md

然后帮我 [你的问题]
```

## 项目资源链接

### 本地文件
- Echo 项目: `/Users/jacky/code/echo`
- NeuroMemory 项目: `/Users/jacky/code/NeuroMemory`

### GitHub
- Echo: https://github.com/jackylk/echo
- NeuroMemory: https://github.com/zhuqingxun/NeuroMemory

### 文档
- [NeuroMemory 高层 API 设计](/Users/jacky/code/NeuroMemory/docs/HIGH_LEVEL_API_DESIGN.md)
- [NeuroMemory 使用示例](/Users/jacky/code/NeuroMemory/docs/HIGH_LEVEL_API_EXAMPLES.md)
- [NeuroMemory SDK README](/Users/jacky/code/NeuroMemory/sdk/README.md)

## 下一步

现在你已经了解了基础知识，可以：

1. ✅ **阅读 CLAUDE.md** 了解详细的开发约定
2. ✅ **运行 `echo chat`** 体验基础功能
3. ✅ **查看 `echo/agent.py`** 理解核心逻辑
4. ✅ **开始开发新功能** 🚀

祝你开发愉快！有任何问题随时在 Claude Code 中提问。
