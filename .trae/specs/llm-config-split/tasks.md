# 大模型配置拆分 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 后端数据模型与 API 层扩展 LLM 配置类型
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 扩展 `LLMConfig.config_type` 支持的取值：新增 `resume_parse`、`score_report`、`interview_generate`，保留 `chat`（历史兼容）和 `embedding`
  - 修改 `_ensure_single_active_embedding` 通用化为 `_ensure_single_active`，支持对任意 config_type 确保只有一个 active
  - 更新 `llm_configs.py` 的创建和更新接口，对所有对话类类型（resume_parse/score_report/interview_generate/chat）都应用单 active 约束
  - 更新 `schemas/__init__.py` 中 `LLMConfigItem` 和 `LLMConfigCreate` 类型定义
- **Acceptance Criteria Addressed**: AC-1, AC-6, AC-8
- **Test Requirements**:
  - `programmatic` TR-1.1: 创建 `resume_parse` 类型配置并设为 active，再创建同类型第二个 active 配置时，第一个自动变为 inactive
  - `programmatic` TR-1.2: 对 `score_report`、`interview_generate` 类型同样满足单 active 约束
  - `programmatic` TR-1.3: 旧的 `chat` 类型配置仍可正常读取和编辑
  - `human-judgement` TR-1.4: 代码结构清晰，单 active 逻辑复用而不是每种类型重复写
- **Notes**: config_type 字段是 String 类型，无需数据库 migration，只需业务层扩展枚举值

## [x] Task 2: 后端任务层按业务场景选择对应模型
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 修改 `tasks/__init__.py` 中 `parse_text_with_llm` 的默认 LLM 配置查询：从 `config_type == "chat"` 改为 `config_type == "resume_parse"`
  - 修改 `tasks/__init__.py` 中 `score_resume_task` 的默认 LLM 配置查询（如果有）：使用 `score_report` 类型
  - 修改 `tasks/__init__.py` 中 `generate_interview_task` 的默认 LLM 配置查询（如果有）：使用 `interview_generate` 类型
  - 修改 `api/matching.py` 中 `trigger_score` 和 `rescore_resume` 的默认 LLM 配置查询：从 `chat` 改为 `score_report`
  - 修改 `api/interviews.py` 中 `generate_interview` 的默认 LLM 配置查询：从 `chat` 改为 `interview_generate`
  - 增加降级逻辑：如果对应业务类型没有 active 配置，回退到 `chat` 类型的 active 配置（保证向后兼容）
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5, AC-8
- **Test Requirements**:
  - `programmatic` TR-2.1: 当存在 `resume_parse` 类型 active 配置时，解析任务使用该配置
  - `programmatic` TR-2.2: 当存在 `score_report` 类型 active 配置时，打分任务使用该配置
  - `programmatic` TR-2.3: 当存在 `interview_generate` 类型 active 配置时，面试题生成任务使用该配置
  - `programmatic` TR-2.4: 当对应业务类型没有 active 配置但存在 `chat` 类型 active 配置时，回退使用 chat 配置（向后兼容）
  - `programmatic` TR-2.5: 当都没有配置时，返回与现有逻辑一致的错误提示
- **Notes**: 降级逻辑确保升级后用户即使不重新配置也能继续使用

## [x] Task 3: 前端大模型管理页面类型扩展与筛选
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 更新 `frontend/src/types/index.ts` 中 `LLMConfig` 的 `config_type` 类型定义
  - 更新 `frontend/src/pages/LLMConfigs/index.tsx` 中的 `configTypeOptions`，新增三个业务类型选项并保留历史 chat 类型
  - 配置列表中类型标签的显示映射更新
  - 新增类型筛选功能（Select 组件），支持按类型过滤列表
  - 新建配置时默认类型调整（如默认选中"简历解析模型"或保留第一个选项）
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-8
- **Test Requirements**:
  - `human-judgement` TR-3.1: 新建配置弹窗中类型下拉包含 4 种主要类型 + 1 种历史类型
  - `human-judgement` TR-3.2: 配置列表正确显示各配置对应的类型标签，颜色区分
  - `human-judgement` TR-3.3: 类型筛选器可以正确过滤列表
  - `programmatic` TR-3.4: TypeScript 类型定义更新后无类型错误
- **Notes**: 类型标签颜色建议：简历解析-蓝色、初筛报告-橙色、面试题生成-紫色、嵌入-绿色、历史chat-灰色

## [x] Task 4: Token 统计与关联展示兼容性验证
- **Priority**: medium
- **Depends On**: Task 1, Task 2
- **Description**: 
  - 验证 `TokenUsageLog.function_type`（parse/score/interview/embedding）与新配置类型的映射关系是否正确
  - 确保 Token 统计页面的功能名称映射正确显示
  - 验证简历详情页中"使用模型"信息的展示（parse_model_name、score 中的 model_name、interview 中的 model_name）
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-4.1: Token 统计 API 返回的 by_function 数据结构不变
  - `human-judgement` TR-4.2: Token 统计页面功能名称显示正确
  - `human-judgement` TR-4.3: 简历详情页各步骤使用的模型名称显示正确
- **Notes**: function_type 字段不变，仅 LLM 配置的 config_type 变化，两者是不同维度

## [x] Task 5: 端到端联调与回归测试
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4
- **Description**: 
  - 启动后端和前端，测试新建各种类型配置
  - 测试同类型多配置的 active 切换
  - 测试简历解析流程使用 resume_parse 模型
  - 测试初筛报告流程使用 score_report 模型
  - 测试面试题生成流程使用 interview_generate 模型
  - 测试降级场景：删除业务类型配置后是否回退到 chat
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5, AC-6, AC-7, AC-8
- **Test Requirements**:
  - `human-judgement` TR-5.1: 新建 4 种类型配置均成功，列表展示正确
  - `human-judgement` TR-5.2: 同类型第二个 active 配置会使第一个自动失效
  - `human-judgement` TR-5.3: 三个业务场景各自使用对应模型，Token 记录正确
  - `human-judgement` TR-5.4: 删除业务类型 active 配置后，任务能正常回退或给出明确提示
- **Notes**: 如无真实 API Key，可通过 mock 或查看请求日志验证配置选择逻辑
