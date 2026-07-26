# 大模型配置拆分 - Product Requirement Document

## Overview
- **Summary**: 将当前统一的"对话模型"配置拆分为三个独立的业务场景模型配置：简历解析模型、初筛报告模型、面试题生成模型，使用户可以为不同业务场景配置不同的大模型。
- **Purpose**: 解决当前所有对话类任务共用同一个对话模型配置的问题，使不同业务场景可以灵活选用最适合的模型（如简历解析可用高性价比模型，面试题生成可用推理能力更强的模型），提升生成质量的同时优化成本。
- **Target Users**: HR 管理员、系统管理员

## Goals
- 将 LLM 配置类型从 `chat | embedding` 扩展为 `resume_parse | score_report | interview_generate | embedding` 四种类型
- 大模型管理页面支持按类型分类展示和管理
- 简历解析、初筛报告生成、面试题生成分别使用各自场景对应的默认模型配置
- 保持向后兼容：现有 `chat` 类型配置可自动映射或迁移

## Non-Goals (Out of Scope)
- 不修改向量化模型（embedding）的现有逻辑
- 不新增模型供应商或 API 协议支持
- 不修改提示词管理的现有逻辑
- 不改变 Token 消耗统计的核心逻辑

## Background & Context
当前系统中，`LLMConfig` 模型的 `config_type` 字段仅有 `chat` 和 `embedding` 两种取值。所有对话类任务（简历解析、初筛报告、面试题生成）都共用同一个"对话模型"配置——即取第一个 `is_active=True` 且 `config_type="chat"` 的配置。

这种设计的局限性：
1. 无法为不同业务场景选择最适合的模型（如简历解析侧重结构化输出准确性，面试题生成侧重推理能力和创意）
2. 无法按业务场景精细化控制成本
3. 不同场景对模型参数（temperature、max_tokens 等）的需求不同，当前无法分别配置

## Functional Requirements
- **FR-1**: LLM 配置类型扩展为四种：`resume_parse`（简历解析模型）、`score_report`（初筛报告模型）、`interview_generate`（面试题生成模型）、`embedding`（向量化模型）
- **FR-2**: 大模型管理页面支持按类型筛选展示，新建/编辑时可选择四种类型之一
- **FR-3**: 每种业务对话类型支持多个配置，但只有一个 active 配置作为默认
- **FR-4**: 简历解析任务默认使用 `resume_parse` 类型的 active 配置
- **FR-5**: 初筛报告（打分）任务默认使用 `score_report` 类型的 active 配置
- **FR-6**: 面试题生成任务默认使用 `interview_generate` 类型的 active 配置
- **FR-7**: Token 消耗统计保持按功能维度（parse/score/interview/embedding）统计
- **FR-8**: 向后兼容：现有 `chat` 类型配置在数据迁移时自动转为对应业务类型，或保留但不作为默认

## Non-Functional Requirements
- **NFR-1**: 数据迁移：升级时现有 `chat` 类型配置应保留，不丢失任何配置数据
- **NFR-2**: 接口兼容：现有 API 接口不做破坏性变更，新增字段使用可选参数
- **NFR-3**: 性能：配置查询性能不低于现有水平

## Constraints
- **Technical**: Python / FastAPI 后端，React + Ant Design 前端，SQLAlchemy ORM
- **Business**: 不破坏现有用户数据，升级后用户原有配置仍然可用
- **Dependencies**: 依赖现有的 LLMConfig 数据模型和 API 接口

## Assumptions
- 用户希望为不同业务场景使用不同模型配置，以达到质量和成本的最优平衡
- 每种业务对话类型只需一个 active 默认配置即可满足需求（与 embedding 类似）
- 现有 `chat` 类型配置可以保留作为历史数据，但不作为默认选择

## Acceptance Criteria

### AC-1: 配置类型扩展
- **Given**: 用户进入大模型管理页面
- **When**: 用户点击"新建配置"
- **Then**: 配置类型下拉选项包含：简历解析模型、初筛报告模型、面试题生成模型、嵌入模型，共 4 种
- **Verification**: `human-judgment`

### AC-2: 按类型筛选展示
- **Given**: 大模型管理页面有多种类型的配置
- **When**: 用户查看配置列表
- **Then**: 列表中每条配置显示其对应类型标签，且支持按类型筛选
- **Verification**: `human-judgment`

### AC-3: 简历解析使用对应模型
- **Given**: 存在一个 `resume_parse` 类型且 active 的模型配置
- **When**: 触发简历解析任务且未指定 llm_config_id
- **Then**: 系统使用该 `resume_parse` 类型的 active 配置进行解析
- **Verification**: `programmatic`

### AC-4: 初筛报告使用对应模型
- **Given**: 存在一个 `score_report` 类型且 active 的模型配置
- **When**: 触发初筛报告打分任务且未指定 llm_config_id
- **Then**: 系统使用该 `score_report` 类型的 active 配置进行打分
- **Verification**: `programmatic`

### AC-5: 面试题生成使用对应模型
- **Given**: 存在一个 `interview_generate` 类型且 active 的模型配置
- **When**: 触发面试题生成任务且未指定 llm_config_id
- **Then**: 系统使用该 `interview_generate` 类型的 active 配置生成面试题
- **Verification**: `programmatic`

### AC-6: 同类型只有一个 active
- **Given**: 某类型已有一个 active 配置
- **When**: 用户将同类型的另一个配置设为 active
- **Then**: 原 active 配置自动变为 inactive，确保同类型只有一个 active
- **Verification**: `programmatic`

### AC-7: Token 统计正常
- **Given**: 各业务场景均有 Token 消耗记录
- **When**: 查看 Token 统计
- **Then**: 按功能维度（简历识别/AI打分/面试题生成/向量化）的统计数据准确无误
- **Verification**: `programmatic`

### AC-8: 历史数据兼容
- **Given**: 数据库中存在旧的 `chat` 类型配置
- **When**: 系统升级后
- **Then**: 旧配置数据不丢失，仍可在列表中查看和编辑，类型标记为"对话模型(历史)"
- **Verification**: `programmatic`

## Open Questions
- [ ] 旧的 `chat` 类型配置在升级后，是否需要自动迁移为某一种新类型（如全部转为 resume_parse），还是保留原状仅做展示兼容？
- [ ] 是否需要在前端提供"一键将 chat 类型配置复制为各业务类型"的快捷操作？
