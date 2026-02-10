# Echo - AI 个人学习助理

> 基于 NeuroMemory 的智能学习伙伴，帮助你梳理知识体系，提升专业技能

## 🎯 产品定位

Echo 是一个 AI 驱动的个人学习助理，专注于：
- 📚 **知识体系梳理** - 自动构建你的专属知识图谱
- 🎓 **技能提升规划** - 基于现有基础制定学习路径
- 💡 **智能内容推荐** - 发现最相关的学习资源
- 🔄 **持续学习跟踪** - 记录学习历程，巩固知识

## 核心特性

### 1. 知识图谱自动构建
```
用户输入：我想学习 Rust 编程语言

Echo 自动：
├─ 分析用户背景（已掌握 Python, C++）
├─ 构建 Rust 知识图谱
│   ├─ 基础概念（所有权、借用、生命周期）
│   ├─ 核心特性（类型系统、并发、宏）
│   ├─ 应用领域（系统编程、Web 后端、CLI 工具）
│   └─ 学习资源（官方书籍、项目实战、视频教程）
└─ 生成个性化学习路径
```

### 2. 学习资源智能管理
- 自动下载和整理网页文章
- 提取 PDF/文档核心内容
- 关联相关知识点
- 生成学习笔记

### 3. 知识巩固助手
- 定期复习提醒（遗忘曲线）
- 生成测试题目
- 知识点关联回顾
- 学习进度可视化

### 4. 个性化推荐引擎
- 基于知识图谱推荐下一步学习内容
- 发现知识盲区
- 推荐相关项目实践
- 推荐学习伙伴

## 技术架构

```
┌─────────────────────────────────────────┐
│           Echo 用户界面                  │
│  - CLI 命令行工具                        │
│  - Web 界面（可选）                      │
│  - VS Code 插件（未来）                  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│           Echo Agent 核心                │
│  - 对话管理器                            │
│  - 知识图谱构建器                        │
│  - 学习路径规划器                        │
│  - 内容推荐引擎                          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         NeuroMemory 记忆系统             │
│  - 会话存储                              │
│  - 知识图谱 (Apache AGE)                 │
│  - 文档管理 (OBS)                        │
│  - 向量检索 (pgvector)                   │
└─────────────────────────────────────────┘
```

## 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/echo.git
cd echo

# 安装依赖
pip install -e .

# 配置
cp .env.example .env
# 编辑 .env，填入 API Keys
```

### 基础使用

```bash
# 启动 Echo CLI
echo chat

# 或者使用 Python API
python
>>> from echo import EchoAgent
>>> agent = EchoAgent(user_id="your_name")
>>> agent.chat("我想学习 Rust 编程语言")
```

## 使用场景

### 场景 1: 学习新技术
```
你: 我想学习 Kubernetes，但我只有基础的 Docker 知识

Echo:
好的！我会帮你规划学习路径：

1. 基础准备（1-2周）
   - Docker 进阶（网络、存储）
   - 容器编排概念

2. K8s 核心概念（2-3周）
   - Pods, Deployments, Services
   - ConfigMap, Secrets
   - 实战：部署简单应用

3. 高级特性（3-4周）
   - StatefulSets, DaemonSets
   - 网络策略
   - 实战：部署微服务

我已经为你收集了以下资源：
- [官方文档] Kubernetes 基础教程
- [视频课程] K8s 入门到实战
- [实战项目] 部署一个博客系统

需要我详细讲解哪个部分？
```

### 场景 2: 知识梳理
```
你: 帮我整理一下我学过的后端技术

Echo:
根据我们的对话记录，你的后端技术栈：

编程语言：
├─ Python (熟练)
│   └─ FastAPI, Django, SQLAlchemy
├─ Java (中级)
│   └─ Spring Boot, MyBatis
└─ Go (入门)

数据库：
├─ PostgreSQL (熟练)
├─ Redis (中级)
└─ MongoDB (了解)

知识图谱已更新！要查看详细图谱吗？
```

### 场景 3: 添加学习资源
```
你: 我找到一篇很好的 Rust 文章 https://doc.rust-lang.org/book/

Echo:
正在下载和分析...

✓ 已下载并解析《The Rust Programming Language》
✓ 提取了 150 个知识点
✓ 关联到你的 Rust 学习路径
✓ 生成了 5 个重点章节摘要

这本书涵盖了：
- 所有权系统（你之前想学的！）
- 错误处理
- 泛型和 Trait
- 并发编程

要我生成学习计划吗？
```

## 项目结构

```
echo/
├── README.md
├── pyproject.toml
├── .env.example
├── echo/
│   ├── __init__.py
│   ├── agent.py              # 核心 Agent 逻辑
│   ├── cli.py                # CLI 命令行界面
│   ├── knowledge/            # 知识管理模块
│   │   ├── graph.py          # 知识图谱构建
│   │   ├── path.py           # 学习路径规划
│   │   └── recommender.py    # 推荐引擎
│   ├── content/              # 内容处理模块
│   │   ├── downloader.py     # 资源下载
│   │   ├── extractor.py      # 内容提取
│   │   └── summarizer.py     # 摘要生成
│   ├── memory/               # NeuroMemory 集成
│   │   └── client.py         # 记忆客户端封装
│   └── utils/
│       ├── llm.py            # LLM 调用封装
│       └── prompts.py        # Prompt 模板
├── tests/
├── docs/
└── examples/
```

## 核心功能模块

### 1. Agent 核心 (`agent.py`)
```python
class EchoAgent:
    """Echo 学习助理核心"""

    def chat(self, message: str) -> str:
        """对话入口"""

    def build_knowledge_graph(self, topic: str):
        """构建知识图谱"""

    def create_learning_path(self, topic: str, level: str):
        """创建学习路径"""

    def add_resource(self, url: str):
        """添加学习资源"""

    def review_knowledge(self):
        """复习知识点"""
```

### 2. 知识图谱 (`knowledge/graph.py`)
```python
class KnowledgeGraph:
    """知识图谱管理"""

    def build_from_topic(self, topic: str):
        """从主题构建图谱"""

    def add_concept(self, concept: str, related_to: list):
        """添加概念节点"""

    def visualize(self):
        """可视化知识图谱"""
```

### 3. 学习路径规划 (`knowledge/path.py`)
```python
class LearningPath:
    """学习路径规划器"""

    def plan(self, topic: str, user_level: str) -> dict:
        """规划学习路径"""

    def get_next_step(self):
        """获取下一步建议"""
```

## 与 NeuroMemory 集成

Echo 充分利用 NeuroMemory 的能力：

| NeuroMemory 功能 | Echo 使用场景 |
|-----------------|--------------|
| 会话存储 | 记录所有对话，提取学习意图 |
| 偏好管理 | 记住学习风格、时间偏好 |
| 向量检索 | 查找相关学习资源和笔记 |
| 知识图谱 | 存储概念关系、技能树 |
| 文档管理 | 管理下载的教程、文章 |

## 开发路线图

### MVP (4周)

**Week 1-2: 核心对话能力**
- [x] 基础对话流程
- [ ] 学习意图识别
- [ ] 简单的知识点记录

**Week 3-4: 知识图谱 v1**
- [ ] 基础图谱构建
- [ ] 简单的学习路径生成
- [ ] 与 NeuroMemory 集成

### V1.0 (8周)

- [ ] 完整的知识图谱系统
- [ ] 智能学习路径规划
- [ ] 资源自动下载和整理
- [ ] CLI 命令行工具

### V2.0 (12周)

- [ ] Web 界面
- [ ] 学习进度可视化
- [ ] 复习提醒系统
- [ ] 社区功能（分享知识图谱）

## 相关项目

- **Echo**: https://github.com/jackylk/echo - AI 个人学习助理
- **NeuroMemory**: https://github.com/zhuqingxun/NeuroMemory - 通用记忆管理系统

## 贡献指南

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License

---

**让 AI 成为你最好的学习伙伴！** 🚀
