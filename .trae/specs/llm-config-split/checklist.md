# 大模型配置拆分 - Verification Checklist

## 后端数据模型与 API
- [x] LLMConfig.config_type 支持 resume_parse、score_report、interview_generate、chat、embedding 五种取值
- [x] 所有对话类类型（resume_parse/score_report/interview_generate/chat）均满足同类型只有一个 active 的约束
- [x] 创建配置时指定新类型能成功保存
- [x] 更新配置时修改类型能成功保存
- [x] 删除配置功能正常
- [x] 列表接口返回的 config_type 字段正确
- [x] 旧的 chat 类型配置数据不丢失，可正常读取和编辑

## 任务层模型选择
- [x] 简历解析任务默认使用 resume_parse 类型的 active 配置
- [x] 初筛报告（打分）任务默认使用 score_report 类型的 active 配置
- [x] 面试题生成任务默认使用 interview_generate 类型的 active 配置
- [x] 当对应业务类型没有 active 配置时，回退到 chat 类型的 active 配置（向后兼容）
- [x] 当所有相关类型都没有配置时，返回明确的错误提示
- [x] 触发解析/打分/面试题时指定 llm_config_id 仍可正常工作（显式指定优先级最高）

## 前端大模型管理页面
- [x] 新建配置弹窗中类型下拉包含：简历解析模型、初筛报告模型、面试题生成模型、嵌入模型、对话模型(历史)
- [x] 配置列表中每条配置显示正确的类型标签和颜色
- [x] 类型筛选器可以按类型过滤列表
- [x] 编辑配置时可以修改类型
- [x] 新建配置时默认类型合理（resume_parse）
- [x] Token 统计页面功能名称映射正确（简历识别/AI打分/面试题生成/向量化）

## 关联展示
- [x] 简历详情页的解析模型名称显示正确（通过 parse_llm_config 关系获取）
- [x] 简历详情页的打分模型名称显示正确（通过 llm_config 关系获取）
- [x] 简历详情页的面试题模型名称显示正确（通过 llm_config 关系获取）
- [x] 初筛报告 PDF 中的"使用模型"信息正确（通过 llm_config 关系获取）
- [x] 面试题 PDF/DOCX 中的模型信息正确（如有）

## 兼容性与回归
- [x] 现有 chat 类型配置升级后不丢失
- [x] embedding 类型配置逻辑未受影响
- [x] 提示词管理功能正常
- [x] Token 消耗统计数据准确（按功能维度 function_type，与 config_type 无关）
- [x] 前端 TypeScript 类型检查无错误
- [x] 后端 Python 语法检查通过
