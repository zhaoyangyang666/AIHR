# AIHR 智能招聘平台 · 技术架构图

> **版本**：v1.0 · 2026-07-20
> **技术栈**：React 18 + TypeScript + Vite + Ant Design ｜ FastAPI + Celery + Redis + SQLite ｜ 大模型 + RAG + NumPy 向量库

---

## 一、整体架构总览（5 层）

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          【Layer 1】用户 / 前端层                                 │
│                                                                                   │
│   用户/浏览器 ──► React 18 + TS + Vite + Ant Design SPA ──► Nginx 反向代理(:80)   │
│   (HR招聘官)        ┌──────────────────────────────────────┐   default_server    │
│                     │ 登录│职位管理│简历导入│简历详情│AI搜索  │   /api → :8000     │
│                     │ 匹配中心│面试题│大模型管理│提示词管理  │   静态资源 /        │
│                     └──────────────────────────────────────┘                     │
└──────────────────────────────────┬──────────────────────────────────────────────┘
                                   │  REST / JSON · axios
┌──────────────────────────────────▼──────────────────────────────────────────────┐
│                         【Layer 2】API 网关层                                     │
│                                                                                   │
│              FastAPI + Uvicorn  ·  /api/v1/*                                      │
│   ┌────────┬────────┬────────┬──────────┬────────────┬─────────┬──────────┐      │
│   │ /auth  │ /jobs  │/resumes│/matching │/interviews │/llm-    │/prompts  │      │
│   │        │        │        │          │            │configs  │          │      │
│   └────────┴────────┴────────┴──────────┴────────────┴─────────┴──────────┘      │
│                          /ai-search    /dashboard                                 │
└───────┬──────────────────────┬───────────────────────┬───────────────────────────┘
        │ async task           │ 同步调用              │ startup
┌───────▼──────────┐  ┌────────▼─────────┐  ┌──────────▼──────────────┐
│ 【Layer 3】      │  │ Business Service │  │ Application Bootstrap   │
│ 异步任务/服务层  │  │  - vector_store  │  │ - Base.metadata.create  │
│                  │  │  - PDF/DOCX Gen  │  │ - 默认提示词 seed       │
│ Celery Worker    │  │  - Auth/Security │  │ - uploads/downloads 目录│
│ + Redis Broker   │  │    (JWT+Fernet)  │  │ - startup_event()       │
│                  │  └──────────────────┘  └─────────────────────────┘
│ ┌──────────────┐ │
│ │parse_resume  │ │       ┌─────────────────────────────────────────────┐
│ │score_resume  │ │       │  ★★★ 【Layer 4】五大 AI 核心模块（重点）★★★    │
│ │generate_     │──────► │                                               │
│ │ interview    │ │       │  ┌─────────┐ ┌─────────┐ ┌──────────────┐  │
│ └──────────────┘ │       │  │①大模型   │ │②提示词  │ │③简历解析&     │  │
│                  │       │  │  管理   │ │  管理   │ │  结构化       │  │
│ @celery_app.task │       │  │LLMConfig│ │ Prompt  │ │  Parse       │  │
│ task_time_limit  │       │  └────┬────┘ └────┬────┘ └──────┬───────┘  │
│ =300s            │       │       │          │              │          │
└──────────────────┘       │  ┌────▼──────────▼──────────────▼───────┐  │
                           │  │④RAG流程·报告/面试题  ⑤向量数据库      │  │
                           │  │  RAG & Generation    Vector Store    │  │
                           │  └─────────────────────────────────────┘  │
                           └──────────────────┬──────────────────────────┘
                                              │
┌─────────────────────────────────────────────▼──────────────────────────────────┐
│                          【Layer 5】数据 & 存储层                                 │
│                                                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ SQLite   │  │ 简历文件 │  │ 报告文件 │  │ 向量持久化   │  │ Redis 队列   │  │
│  │ 元数据库 │  │uploads/  │  │downloads/│  │chroma_db/    │  │:6379/0 broker│  │
│  │          │  │ resumes/ │  │ *.pdf    │  │vector_store  │  │:6379/1 backend│ │
│  └──────────┘  └──────────┘  └──────────┘  │  .json       │  └──────────────┘  │
│                                            └──────────────┘                     │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 二、五大 AI 核心模块详解（重点）

### ① 大模型管理（LLM Configs）

```
                    ┌─────────────────────────────┐
                    │      LLMConfig 模型         │
                    │  name / provider / model_name│
                    │  api_key_encrypted (Fernet) │
                    │  base_url (OpenAI 兼容)      │
                    │  price_per_million_tokens   │
                    │  config_type: chat|embedding │
                    │  is_active                  │
                    └────────────┬────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                                 │
        ┌───────▼────────┐               ┌────────▼────────┐
        │   在线模型 API  │               │  本地 Ollama    │
        │                │               │                 │
        │ · OpenAI       │               │ · 私有化部署    │
        │ · 硅基流动      │               │ · base_url 指向 │
        │ · DeepSeek     │               │   localhost:    │
        │ · 其他兼容 API  │               │   11434/v1      │
        │                │               │ · 无需 API Key  │
        │ base_url 指向   │               │ · 数据不出域   │
        │ 云端服务        │               │                 │
        └────────────────┘               └─────────────────┘
```

**关键设计**：
- 统一走 **OpenAI 兼容协议**（`openai` Python SDK），通过 `base_url` 切换云端/本地
- `config_type` 区分 **chat**（对话/解析/打分/面试题）与 **embedding**（向量化）
- embedding 类型**只允许一个 active**（`_ensure_single_active_embedding`）
- API Key 通过 **Fernet 对称加密**存储（`ENCRYPTION_KEY`）

---

### ② 提示词管理（Prompts）

```
┌─────────────────────────────────────────────────────────┐
│                    Prompt 模型                          │
│  name · type · content · is_system_default              │
│  current_version · usage_count                          │
└────────────────────────┬────────────────────────────────┘
                         │ 1:N
              ┌──────────▼──────────┐
              │  PromptVersion 模型 │  ← 版本控制
              │  prompt_id · version│
              │  content            │
              └─────────────────────┘

┌─────────────┬──────────────────────────────────────────┐
│   type      │  用途                                    │
├─────────────┼──────────────────────────────────────────┤
│  parse      │  简历解析：文本 → 结构化 JSON            │
│             │  字段：name/phone/email/skills/work_exp  │
├─────────────┼──────────────────────────────────────────┤
│  score      │  简历打分：5 维度评分 + 优劣势 + 总结    │
│             │  responsibility/skill/experience/...     │
├─────────────┼──────────────────────────────────────────┤
│  interview  │  面试题生成：4 模块结构化问题            │
│             │  工作验证/技术深度/问题解决/软技能       │
└─────────────┴──────────────────────────────────────────┘
```

**关键设计**：
- 系统启动时 `startup_event()` 自动初始化 3 个**默认提示词**（`is_system_default=True`）
- 支持版本管理，每次编辑产生新 `PromptVersion`
- 每次被任务调用 `usage_count += 1`，用于统计提示词使用频率

---

### ③ 简历解析 & 结构化（Parse）

```
┌──────────┐    ┌───────────────┐    ┌──────────────┐    ┌──────────────┐
│ PDF/DOCX │───►│ 文本提取       │───►│ LLM 结构化   │───►│ 存入 SQLite  │
│ 简历文件  │    │               │    │              │    │ + 自动向量化 │
└──────────┘    │ · pdfplumber  │    │ · Chat 模型  │    │              │
                │   (PDF)       │    │ · JSON Schema│    │ Resume表:    │
                │ · python-docx │    │ · temp=0.1   │    │  parsed_data │
                │   (DOC/DOCX)  │    │              │    │  parse_status│
                └───────────────┘    └──────────────┘    └──────┬───────┘
                                                                 │
                                                         ┌───────▼───────┐
                                                         │ 自动调用       │
                                                         │ vector_store  │
                                                         │ .add_resume() │
                                                         └───────────────┘
```

**解析流程**（`parse_resume_task`）：
1. **文件文本提取**：`pdfplumber.open()` 逐页提取 / `python-docx` 读段落
2. **LLM 调用**：`parse_text_with_llm()` → OpenAI 兼容 `chat.completions.create()`
3. **JSON 解析**：`response_format={"type": "json_object"}` + 正则兜底 `{.*}`
4. **字段回填**：`_backfill_resume_fields()` 把 name/phone/email 等写回 Resume 表
5. **自动向量化**：调用 `vector_store.add_resume()` 生成 embedding 并持久化
6. **Token 记账**：写入 `TokenUsageLog`，记录 `function_type="parse"` + 估算成本

**状态机**：`pending → parsing → success / failed`

---

### ④ RAG 流程 · 报告 / 面试题生成

```
                          ┌──────────────────────────────┐
                          │        职位描述 (Job)         │
                          │  title + description          │
                          └──────────────┬───────────────┘
                                         │
          ┌──────────────────────────────┼──────────────────────────────┐
          │                              │                              │
          ▼                              ▼                              ▼
┌─────────────────┐          ┌───────────────────┐          ┌───────────────────┐
│  简历评分报告    │          │  面试题生成        │          │  AI 语义搜索      │
│ score_resume    │          │ generate_interview│          │ ai_search         │
│                 │          │                   │          │                   │
│ 输入:           │          │ 输入:             │          │ 输入:             │
│  Job + 简历JSON │          │  Job + 简历JSON   │          │  自然语言 query   │
│                 │          │                   │          │                   │
│ 提示词:         │          │ 提示词:           │          │ 流程:             │
│  type=score     │          │  type=interview   │          │  query→embedding  │
│                 │          │                   │          │  →向量库检索      │
│ 输出:           │          │ 输出:             │          │  →top_k 简历      │
│  5维评分(0-100) │          │  4模块面试题      │          │                   │
│  优势/差距/总结 │          │  每题含考察意图   │          │ 输出:             │
│                 │          │  + 评估要点       │          │  匹配简历+相似度  │
│ 落库:           │          │                   │          │                   │
│  ResumeScore表  │          │ 落库:             │          │ 实时检索          │
│                 │          │  InterviewQuestion│          │  不落库           │
│ 导出:           │          │                   │          │                   │
│  PDF初筛报告    │          │ 导出:             │          │                   │
│  (reportlab)    │          │  PDF/DOCX         │          │                   │
└─────────────────┘          └───────────────────┘          └───────────────────┘
      │                              │                              │
      └──────────────┬───────────────┴──────────────────────────────┘
                     │
              ┌──────▼──────┐         ┌──────────────┐
              │ 调用 Chat   │◄────────│ 提示词管理    │
              │ 大模型      │         │ (Prompt模板) │
              └─────────────┘         └──────────────┘
```

**三条 RAG 子流程**：

| 流程 | 任务/接口 | 输入 | 提示词类型 | 大模型 | 输出 |
|------|-----------|------|-----------|--------|------|
| 评分报告 | `score_resume_task` | Job + 简历 JSON | `score` | chat | 5 维评分 + 优劣势，存 `ResumeScore`，可导出 PDF |
| 面试题 | `generate_interview_task` | Job + 简历 JSON | `interview` | chat | 4 模块结构化题目，存 `InterviewQuestion` |
| AI 搜索 | `POST /ai-search` | 自然语言 query | — | embedding | 检索向量库，返回 top_k 简历 + 相似度 |

---

### ⑤ 向量数据库（Vector Store）

```
┌─────────────────────────────────────────────────────────────┐
│              VectorStoreService (单例 Singleton)             │
│                                                              │
│  存储: {resume_id: {embedding, content, metadata}}           │
│  持久化: chroma_db/vector_store.json (JSON 文件)             │
│  线程安全: threading.Lock() 保护文件读写                      │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Embedding 配置获取 (_get_embedding_config)          │    │
│  │  优先级:                                              │    │
│  │   1. DB 中 config_type="embedding" 且 is_active=True │    │
│  │   2. .env: EMBEDDING_API_KEY / BASE_URL / MODEL      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  核心方法:                                                   │
│  ┌────────────────┬───────────────────────────────────┐    │
│  │ add_resume()   │ 简历文本 → Embedding API → 存储    │    │
│  │ search()       │ query → embedding → 余弦相似度排序 │    │
│  │ build_index()  │ 全量重建：遍历所有已解析简历       │    │
│  │ delete_resume()│ 删除指定简历向量                   │    │
│  └────────────────┴───────────────────────────────────┘    │
│                                                              │
│  相似度算法:                                                 │
│    cosine = dot(a,b) / (||a|| × ||b||)   ← NumPy 实现       │
└─────────────────────────────────────────────────────────────┘
```

**关键设计**：
- **不依赖 ChromaDB**，自研轻量方案：NumPy 余弦相似度 + JSON 文件持久化
- Embedding 来源有**两级 fallback**：数据库配置 → `.env` 环境变量
- `add_resume` 在简历解析成功后**自动触发**（在 `parse_resume_task` 内）
- 查询时实时生成 query embedding，与库内所有向量计算相似度后取 top_k

---

## 三、五大核心模块协作关系图

```
                    ┌────────────────┐
                    │  ② 提示词管理   │
                    │   (Prompts)    │
                    │  parse/score/  │
                    │  interview     │
                    └───────┬────────┘
                            │ 提供模板
                            │
     ┌──────────────────────┼──────────────────────┐
     │                      │                      │
     ▼                      ▼                      ▼
┌──────────┐         ┌──────────────┐       ┌──────────────┐
│ ③简历解析│         │ ④RAG 流程    │       │  ①大模型管理 │
│  &结构化 │───────► │              │─────► │  (LLM Config)│
│ (Parse)  │ 结构化  │ · 评分报告    │ 调用  │              │
│          │ 数据    │ · 面试题生成  │ LLM  │ · 在线 API   │
└────┬─────┘         │ · AI 语义搜索 │       │ · 本地Ollama │
     │               └──────┬───────┘       └──────────────┘
     │ 自动 embedding        │ 检索
     │                       │
     ▼                       ▼
┌──────────────────────────────────────────┐
│        ⑤ 向量数据库 (Vector Store)        │
│                                          │
│  · NumPy 余弦相似度                      │
│  · JSON 持久化 (vector_store.json)       │
│  · add_resume / search / build_index     │
└──────────────────────────────────────────┘
```

**关键数据流**：

| 流向 | 触发时机 | 说明 |
|------|---------|------|
| ③ → ⑤ | 解析成功后自动 | `parse_resume_task` 内调用 `vector_store.add_resume()` |
| ④ → ① | 评分/面试题生成时 | 通过 `LLMConfig` 获取 chat 模型配置调用大模型 |
| ④ → ② | 评分/面试题生成时 | 按 `type` 查询对应 `Prompt` 作为 system message |
| ④ → ⑤ | AI 搜索时 | `ai_search` 调用 `vector_store.search()` 检索 |
| ③ → ④ | 解析完成后 | 结构化数据作为 RAG 生成报告/面试题的输入 |
| ⑤ → ④ | 检索时 | 向量库返回 top_k 简历供 RAG 使用 |

---

## 四、异步任务流转（Celery）

```
                    ┌─────────────┐
                    │  HTTP 请求   │
                    │ (FastAPI)   │
                    └──────┬──────┘
                           │
                  ┌────────▼────────┐
                  │ is_celery_      │
                  │ available()?    │
                  └───┬─────────┬───┘
                      │         │
                 Yes  │         │ No (Redis 不可用)
                      │         │
              ┌───────▼───┐  ┌──▼───────────────────┐
              │ task.delay│  │ threading.Thread      │
              │ (异步)    │  │ (同步回退，后台线程)  │
              └───────┬───┘  └──────────┬────────────┘
                      │                 │
                      ▼                 ▼
              ┌──────────────────────────────────┐
              │         任务执行体               │
              │  parse_resume_task               │
              │  score_resume_task               │
              │  generate_interview_task         │
              └──────────────────────────────────┘
                      │
                      ▼
              ┌──────────────────┐
              │ Redis Backend    │
              │ (结果存储)       │
              └──────────────────┘
```

**三个异步任务**：

| 任务名 | 入口 API | 输入 | 依赖模块 | 输出 |
|--------|---------|------|---------|------|
| `parse_resume` | `POST /matching/{id}/parse` | resume_id, prompt_id, llm_config_id | ②①⑤ | 结构化数据 + 向量 |
| `score_resume` | `POST /matching/{id}/score` | resume_id, prompt_id, llm_config_id | ②① | ResumeScore 记录 |
| `generate_interview` | `POST /interviews/...` | resume_id, prompt_id, llm_config_id | ②① | InterviewQuestion 记录 |

**降级策略**：`is_celery_available()` 检测 Redis 连通性（2s 超时），不可用时自动降级为 `threading.Thread` 同步回退执行。

---

## 五、技术栈清单

| 层级 | 技术 | 用途 |
|------|------|------|
| **前端** | React 18 + TypeScript | SPA 框架 |
| | Vite | 构建工具 |
| | Ant Design | UI 组件库 |
| | axios | HTTP 客户端 |
| | React Router | 路由 |
| **后端** | FastAPI | Web 框架 |
| | Uvicorn | ASGI 服务器 |
| | SQLAlchemy | ORM |
| | Pydantic | 数据校验 |
| | python-jose (JWT) | 身份认证 |
| | cryptography (Fernet) | API Key 加密 |
| **异步** | Celery | 任务队列 |
| | Redis | Broker + Backend |
| **文档处理** | pdfplumber | PDF 文本提取 |
| | python-docx | DOC/DOCX 文本提取 |
| | reportlab | PDF 报告生成 |
| **AI** | openai (SDK) | 大模型调用（OpenAI 兼容） |
| | NumPy | 向量余弦相似度计算 |
| **存储** | SQLite | 关系型元数据 |
| | JSON 文件 | 向量数据持久化 |
| | 本地文件系统 | 简历/报告文件 |
| **部署** | Nginx | 反向代理 + 静态资源 |
| | systemd | 服务管理（Linux 生产） |

---

## 六、数据模型关系

```
┌──────────┐     ┌──────────┐     ┌──────────────┐
│   User   │     │   Job    │     │  LLMConfig   │
│ (用户)   │     │ (职位)   │     │ (大模型配置) │
└──────────┘     └────┬─────┘     └──────┬───────┘
                      │ 1:N              │ 1:N
              ┌───────▼──────────┐       │
              │     Resume       │◄──────┤ parse_llm_config_id
              │   (简历)         │◄──────┤ embedding_llm_config_id
              └───┬──────┬───────┘       │
                  │ 1:N  │ 1:N           │
          ┌───────▼┐    └▼─────────┐    │
          │Resume  │  │Interview   │    │
          │Score   │  │Question    │    │
          │(评分)  │  │(面试题)    │    │
          └───┬────┘  └────────────┘    │
              │ N:1                      │
     ┌────────▼────────┐         ┌──────▼──────┐
     │     Prompt      │         │TokenUsageLog│
     │   (提示词)      │         │ (Token消耗) │
     └────────┬────────┘         └─────────────┘
              │ 1:N
     ┌────────▼────────┐
     │ PromptVersion   │
     │ (提示词版本)     │
     └─────────────────┘
```

---

## 七、典型业务流程

### 流程 1：简历导入 → 解析 → 评分 → 报告

```
用户上传简历 (PDF/DOCX)
    │
    ▼
[POST /resumes/upload] → 存文件到 uploads/resumes/ → 创建 Resume 记录
    │
    ▼
[POST /matching/{id}/parse] → Celery: parse_resume_task
    │                          ├─ pdfplumber/docx 提取文本
    │                          ├─ LLM (chat模型) JSON 结构化
    │                          ├─ 字段回填 Resume 表
    │                          ├─ vector_store.add_resume() 自动向量化
    │                          └─ TokenUsageLog 记账
    ▼
[轮询 GET /matching/{id}/parse/status] → 前端展示解析结果
    │
    ▼
[POST /matching/{id}/score] → Celery: score_resume_task
    │                          ├─ 取 Job + Resume.parsed_data
    │                          ├─ 取 score 类型 Prompt
    │                          ├─ LLM (chat模型) 生成评分
    │                          └─ 存 ResumeScore 记录
    ▼
[GET /matching/{id}/download/score-pdf] → reportlab 生成 PDF → 下载
```

### 流程 2：AI 语义搜索

```
HR 输入自然语言查询 (如 "5年Java后端，有微服务经验")
    │
    ▼
[POST /ai-search] {query, top_k}
    │
    ▼
vector_store.search(query)
    ├─ _get_embedding_config() 取 embedding 模型
    ├─ query → Embedding API → query_vec
    ├─ 遍历 vector_store.json 所有向量
    ├─ NumPy 计算余弦相似度
    └─ 排序取 top_k
    │
    ▼
返回 [{resume, score}, ...] → 前端展示匹配简历列表
```

---

> 📌 **架构特点总结**：
> - **轻量自研**：向量库不依赖 ChromaDB，NumPy + JSON 即可运行，部署简单
> - **模型灵活**：统一 OpenAI 兼容协议，云端/本地 Ollama 自由切换
> - **异步可降级**：Celery + Redis 不可用时自动降级为线程同步执行
> - **提示词可治理**：版本管理 + 使用统计，支持持续优化
> - **成本可观测**：每次 LLM 调用都记录 Token 消耗与估算成本
