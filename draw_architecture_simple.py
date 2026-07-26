"""
AIHR 智能招聘平台 - 技术架构图（简版）
基于 AIHR_技术架构图（简版）.md 绘制
输出: 16:9 高分辨率 PNG，薄荷绿/青绿色调
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from matplotlib.lines import Line2D
import matplotlib.font_manager as fm

# =============== 字体 ===============
for cand in ["Microsoft YaHei", "SimHei", "Noto Sans SC"]:
    if any(f.name == cand for f in fm.fontManager.ttflist):
        plt.rcParams["font.family"] = cand
        break
plt.rcParams["axes.unicode_minus"] = False

# =============== 配色（薄荷绿/青绿主题） ===============
TEAL_DEEP   = "#0F766E"
TEAL        = "#14B8A6"
TEAL_LIGHT  = "#5EEAD4"
MINT        = "#A7F3D0"
MINT_SOFT   = "#D1FAE5"
MINT_BG     = "#F0FDFA"
SLATE       = "#0F172A"
SLATE_SOFT  = "#475569"
SLATE_MUTED = "#94A3B8"
BG          = "#FFFFFF"

# =============== 画布 ===============
FIG_W, FIG_H = 19.2, 10.8  # 16:9
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=110)
ax.set_xlim(0, 100)
ax.set_ylim(0, 56.25)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(BG)


# =============== 工具函数 ===============
def rounded_box(x, y, w, h, fc, ec=None, lw=1.4, alpha=1.0, radius=0.6):
    if ec is None:
        ec = TEAL
    box = FancyBboxPatch(
        (x, y), w, h, boxstyle=f"round,pad=0.02,rounding_size={radius}",
        linewidth=lw, edgecolor=ec, facecolor=fc, alpha=alpha,
    )
    ax.add_patch(box)
    return box


def text_at(x, y, s, size=8.5, color=SLATE, weight="normal", ha="center", va="center"):
    ax.text(x, y, s, fontsize=size, color=color, weight=weight,
            ha=ha, va=va, zorder=10)


def arrow(p1, p2, color=TEAL, lw=1.4, style="-", curve=0.0, alpha=1.0,
          label=None, label_offset=(0, 0), label_size=7.5):
    if curve == 0:
        a = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=12,
                            color=color, linewidth=lw, linestyle=style, alpha=alpha,
                            shrinkA=2, shrinkB=2)
    else:
        a = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=12,
                            color=color, linewidth=lw, linestyle=style, alpha=alpha,
                            connectionstyle=f"arc3,rad={curve}", shrinkA=2, shrinkB=2)
    ax.add_patch(a)
    if label:
        mx = (p1[0] + p2[0]) / 2 + label_offset[0]
        my = (p1[1] + p2[1]) / 2 + label_offset[1]
        ax.text(mx, my, label, fontsize=label_size, color=SLATE_SOFT, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.2", facecolor=BG, edgecolor="none", alpha=0.92))


# ============================================================
# 标题
# ============================================================
text_at(50, 54.5, "AIHR 智能招聘平台 · 技术架构图", size=22, color=TEAL_DEEP, weight="bold")
text_at(50, 52.6, "React 18 + TS + Vite + Ant Design  ｜  FastAPI + Celery + Redis + SQLite  ｜  大模型 + RAG + NumPy 向量库",
        size=9.5, color=SLATE_SOFT)

# 右上角图例
leg_x, leg_y = 80, 53.5
legend_items = [
    ("数据流 / 调用", TEAL, "-"),
    ("异步任务",       TEAL, ":"),
    ("检索/Embedding", TEAL_LIGHT, "--"),
]
text_at(leg_x, leg_y, "图例", size=9, color=TEAL_DEEP, weight="bold", ha="left")
for i, (lbl, c, ls) in enumerate(legend_items):
    y = leg_y - 1.2 - i * 0.95
    ax.add_line(Line2D([leg_x - 0.2, leg_x + 2.0], [y, y], color=c, linewidth=2, linestyle=ls))
    text_at(leg_x + 2.4, y, lbl, size=7.5, color=SLATE_SOFT, ha="left")


# ============================================================
# Layer 1: 用户 / 前端层
# ============================================================
ly1_top, ly1_bot = 50.5, 45.5

# Layer 标签
text_at(3.0, (ly1_top + ly1_bot) / 2, "Layer 1\n用户/前端", size=8.5, color=SLATE_MUTED, weight="bold", ha="left")

# 用户/浏览器
rounded_box(10, ly1_bot, 14, ly1_top - ly1_bot, MINT_SOFT, radius=0.5)
text_at(17, ly1_bot + 3.2, "用户 / 浏览器", size=10.5, color=TEAL_DEEP, weight="bold")
text_at(17, ly1_bot + 1.6, "HR 招聘官", size=9, color=SLATE_SOFT)
for i, c in enumerate([TEAL, TEAL_LIGHT, MINT]):
    ax.add_patch(Circle((12.5 + i * 1.0, ly1_top - 0.7), 0.3, color=c, zorder=5))

# React SPA
rounded_box(26, ly1_bot, 46, ly1_top - ly1_bot, MINT, radius=0.5)
text_at(49, ly1_top - 1.0, "React 18 + TypeScript + Vite + Ant Design (SPA)", size=11, color=TEAL_DEEP, weight="bold")
modules = ["登录", "职位管理", "简历导入", "简历详情", "AI搜索", "匹配中心", "面试题", "大模型管理", "提示词管理"]
m_w = 4.8
for i, m in enumerate(modules):
    x = 27.2 + i * m_w
    rounded_box(x, ly1_bot + 0.6, m_w - 0.3, 1.5, "white", ec=TEAL, lw=1.0, radius=0.3)
    text_at(x + (m_w - 0.3) / 2, ly1_bot + 1.35, m, size=8.2, color=SLATE)

# Nginx
rounded_box(74, ly1_bot, 22, ly1_top - ly1_bot, MINT_SOFT, radius=0.5)
text_at(85, ly1_top - 1.0, "Nginx 反向代理 · :80", size=10, color=TEAL_DEEP, weight="bold")
text_at(85, ly1_bot + 1.5, "default_server\n静态资源 /  ·  /api → :8000", size=8, color=SLATE_SOFT)

# 箭头
arrow((49, ly1_bot), (49, 44.0), color=TEAL_DEEP, lw=1.5)
text_at(51.5, 44.75, "REST / JSON · axios", size=7.5, color=SLATE_SOFT, ha="left")


# ============================================================
# Layer 2: API 网关层
# ============================================================
ly2_top, ly2_bot = 43.5, 39.5
text_at(3.0, (ly2_top + ly2_bot) / 2, "Layer 2\nAPI网关", size=8.5, color=SLATE_MUTED, weight="bold", ha="left")

rounded_box(10, ly2_bot, 86, ly2_top - ly2_bot, TEAL_LIGHT, radius=0.6)
text_at(53, ly2_top - 1.0, "FastAPI + Uvicorn  ·  /api/v1/*", size=12, color="white", weight="bold")

endpoints = ["auth", "jobs", "resumes", "matching", "interviews", "llm-configs", "prompts", "ai-search", "dashboard"]
ew = 9.2
ex0 = 10.8
ey = ly2_bot + 0.5
for i, ep in enumerate(endpoints):
    x = ex0 + i * ew
    rounded_box(x, ey, ew - 0.5, 1.5, "white", ec=TEAL_DEEP, lw=0.8, radius=0.3)
    text_at(x + (ew - 0.5) / 2, ey + 0.75, "/" + ep, size=8.2, color=TEAL_DEEP, weight="bold")


# ============================================================
# Layer 3: 异步任务 / 服务层
# ============================================================
ly3_top, ly3_bot = 37.5, 32.5
text_at(3.0, (ly3_top + ly3_bot) / 2, "Layer 3\n异步/服务", size=8.5, color=SLATE_MUTED, weight="bold", ha="left")

# Celery + Redis
rounded_box(10, ly3_bot, 34, ly3_top - ly3_bot, MINT_BG, ec=TEAL, lw=1.5, radius=0.5)
text_at(27, ly3_top - 0.8, "Celery Worker + Redis Broker", size=10.5, color=TEAL_DEEP, weight="bold")
tasks = ["parse_resume", "score_resume", "generate_interview"]
for i, t in enumerate(tasks):
    x = 11.0 + i * 10.8
    rounded_box(x, ly3_bot + 0.6, 9.8, 1.6, MINT, ec=TEAL, lw=0.8, radius=0.3)
    text_at(x + 4.9, ly3_bot + 1.4, t, size=8.5, color=TEAL_DEEP, weight="bold")
text_at(27, ly3_bot + 0.2, "@celery_app.task  ·  task_time_limit=300s", size=7, color=SLATE_MUTED)

# Business Service
rounded_box(46, ly3_bot, 24, ly3_top - ly3_bot, MINT_BG, ec=TEAL, lw=1.5, radius=0.5)
text_at(58, ly3_top - 0.8, "Business Service", size=10.5, color=TEAL_DEEP, weight="bold")
svc = ["vector_store", "PDF/DOCX Gen", "Auth / Security"]
for i, s in enumerate(svc):
    x = 47.0 + i * 7.6
    rounded_box(x, ly3_bot + 0.6, 7.0, 1.6, MINT_SOFT, ec=TEAL, lw=0.8, radius=0.3)
    text_at(x + 3.5, ly3_bot + 1.4, s, size=8.2, color=TEAL_DEEP, weight="bold")
text_at(58, ly3_bot + 0.2, "复用模块 · 单例 + 文件锁", size=7, color=SLATE_MUTED)

# Bootstrap
rounded_box(72, ly3_bot, 24, ly3_top - ly3_bot, MINT_BG, ec=TEAL, lw=1.5, radius=0.5)
text_at(84, ly3_top - 0.8, "Application Bootstrap", size=10.5, color=TEAL_DEEP, weight="bold")
text_at(84, ly3_bot + 2.5, "· metadata.create_all\n· 默认提示词 seed\n· 目录初始化", size=8, color=SLATE_SOFT)
text_at(84, ly3_bot + 0.2, "startup_event()", size=7, color=SLATE_MUTED)

# 箭头 API → Layer 3
arrow((27, 39.5), (27, 37.5), color=TEAL_DEEP, lw=1.2, style=":")
text_at(22, 38.5, "提交任务", size=7, color=SLATE_SOFT)
arrow((55, 39.5), (55, 37.5), color=TEAL_DEEP, lw=1.0)
arrow((80, 39.5), (80, 37.5), color=TEAL_DEEP, lw=1.0, style=":")


# ============================================================
# Layer 4: 五大 AI 核心模块（重点）
# ============================================================
ly4_top, ly4_bot = 30.0, 11.5
text_at(3.0, (ly4_top + ly4_bot) / 2 + 3, "Layer 4", size=8.5, color=SLATE_MUTED, weight="bold", ha="left")
text_at(3.0, (ly4_top + ly4_bot) / 2 + 1, "五大AI", size=8.5, color=TEAL_DEEP, weight="bold", ha="left")
text_at(3.0, (ly4_top + ly4_bot) / 2 - 0.5, "核心模块", size=8.5, color=TEAL_DEEP, weight="bold", ha="left")
text_at(3.0, (ly4_top + ly4_bot) / 2 - 2, "★★★", size=10, color=TEAL, ha="left")

# 高亮背景框
rounded_box(7, ly4_bot, 89, ly4_top - ly4_bot, MINT_SOFT, ec=TEAL_LIGHT, lw=1.2, alpha=0.35, radius=0.6)

# 五个模块
mod_w = 16.8
mod_h = 16.5
mod_y = ly4_bot + 1.0
gap = 0.6
x_start = 7.8

modules_info = [
    {
        "title": "① 大模型管理",
        "en": "LLM Configs",
        "lines": [
            ("config_type", "chat / embedding"),
            ("base_url", "OpenAI 兼容"),
            ("provider", "OpenAI / 硅基 / DeepSeek"),
            ("安全", "Fernet 加密 API Key"),
        ],
        "sub_box": [
            ("在线 API", "云端大模型", TEAL),
            ("本地 Ollama", "私有化部署", TEAL_LIGHT),
        ],
    },
    {
        "title": "② 提示词管理",
        "en": "Prompts",
        "lines": [
            ("类型", "parse / score / interview"),
            ("版本", "PromptVersion 表"),
            ("统计", "usage_count 自增"),
            ("管理", "创建 / 启用 / 回滚"),
        ],
        "sub_box": [],
    },
    {
        "title": "③ 简历解析 & 结构化",
        "en": "Parse & Struct",
        "lines": [
            ("文本提取", "pdfplumber / python-docx"),
            ("LLM 解析", "Chat 模型 + JSON"),
            ("结构化", "姓名/手机/邮箱/经历"),
            ("触发", "上传后异步执行"),
        ],
        "sub_box": [],
    },
    {
        "title": "④ RAG · 报告/面试题",
        "en": "RAG & Generation",
        "lines": [
            ("评分报告", "score_resume · 5维"),
            ("面试题", "generate_interview · 4模块"),
            ("AI 搜索", "ai_search · 语义检索"),
            ("输出", "PDF / DOCX 下载"),
        ],
        "sub_box": [],
    },
    {
        "title": "⑤ 向量数据库",
        "en": "Vector Store",
        "lines": [
            ("存储", "NumPy + JSON 持久化"),
            ("检索", "余弦相似度 top_k"),
            ("重建", "build_index 全量"),
            ("路径", "chroma_db/"),
        ],
        "sub_box": [],
    },
]

for i, m in enumerate(modules_info):
    x = x_start + i * (mod_w + gap)
    # 主框
    rounded_box(x, mod_y, mod_w, mod_h, "white", ec=TEAL, lw=1.6, radius=0.5)
    # 顶部色条
    rounded_box(x, mod_y + mod_h - 2.6, mod_w, 2.6, TEAL, ec=TEAL, lw=0, radius=0.5)
    text_at(x + mod_w / 2, mod_y + mod_h - 0.9, m["title"], size=11, color="white", weight="bold")
    text_at(x + mod_w / 2, mod_y + mod_h - 2.0, m["en"], size=8, color=MINT)
    # 行内容
    for j, (k, v) in enumerate(m["lines"]):
        ly = mod_y + mod_h - 4.0 - j * 1.45
        rounded_box(x + 0.4, ly - 0.4, 4.8, 0.9, MINT_SOFT, ec=TEAL_LIGHT, lw=0.5, radius=0.2)
        text_at(x + 2.8, ly, k, size=7.8, color=TEAL_DEEP, weight="bold")
        text_at(x + 5.5, ly, v, size=7.8, color=SLATE, ha="left")
    # 子框
    if m["sub_box"]:
        sub_y_top = mod_y + 1.8
        sub_y_bot = mod_y + 0.3
        sub_h = sub_y_top - sub_y_bot
        for k, (name, desc, c) in enumerate(m["sub_box"]):
            slot_h = sub_h / 2
            sy = sub_y_top - (k + 0.5) * slot_h
            sx = x + 0.4
            sw = mod_w - 0.8
            rounded_box(sx, sy - slot_h / 2 + 0.05, sw, slot_h - 0.1, c, ec=c, lw=0, radius=0.25, alpha=0.9)
            text_at(sx + sw / 2, sy, f"{name}  ·  {desc}", size=8, color="white", weight="bold")


# ===== 模块间关系箭头 =====
# 解析 → 向量库（自动 embedding）
arrow((x_start + 2 * (mod_w + gap) + mod_w / 2, mod_y),
      (x_start + 4 * (mod_w + gap) + mod_w / 2, mod_y),
      color=TEAL, lw=1.4, curve=-0.25, label="自动向量化", label_offset=(0, -0.8))

# RAG → 大模型（调用 LLM）
arrow((x_start + 3 * (mod_w + gap) + mod_w / 2, mod_y + mod_h - 0.2),
      (x_start + 0 * (mod_w + gap) + mod_w / 2, mod_y + mod_h - 0.2),
      color=TEAL, lw=1.4, curve=0.3, label="调用 LLM", label_offset=(0, 0.6))

# RAG → 提示词（使用模板）
arrow((x_start + 3 * (mod_w + gap) + mod_w / 2 - 2, mod_y + mod_h - 0.2),
      (x_start + 1 * (mod_w + gap) + mod_w / 2 + 2, mod_y + mod_h - 0.2),
      color=TEAL, lw=1.2, curve=0.15, style="--", label="使用提示词", label_offset=(0, 0.5))

# RAG → 向量库（检索）
arrow((x_start + 3 * (mod_w + gap) + mod_w / 2, mod_y),
      (x_start + 4 * (mod_w + gap) + mod_w / 2, mod_y + 4),
      color=TEAL_LIGHT, lw=1.4, curve=-0.2, style="--", label="检索", label_offset=(2, -0.5))

# 解析 → RAG（结构化数据）
arrow((x_start + 2 * (mod_w + gap) + mod_w, mod_y + mod_h / 2),
      (x_start + 3 * (mod_w + gap), mod_y + mod_h / 2),
      color=TEAL, lw=1.2, label="结构化数据", label_offset=(0, 0.6))

# 模块向上连到 Layer 3
for i in range(5):
    cx = x_start + i * (mod_w + gap) + mod_w / 2
    arrow((cx, ly4_top), (cx, ly3_bot), color=TEAL, lw=0.8, style=":", alpha=0.5)


# ============================================================
# Layer 5: 数据 & 存储层
# ============================================================
ly5_top, ly5_bot = 9.0, 2.5
text_at(3.0, (ly5_top + ly5_bot) / 2, "Layer 5\n数据存储", size=8.5, color=SLATE_MUTED, weight="bold", ha="left")

data_items = [
    ("SQLite 元数据库", "Resume / Job / Prompt\nLLMConfig / Score 等", TEAL),
    ("简历文件存储", "uploads/resumes/\n.pdf · .doc · .docx", TEAL_LIGHT),
    ("报告文件存储", "downloads/*.pdf\nreportlab + 中文字体", MINT),
    ("向量数据持久化", "chroma_db/\nvector_store.json", TEAL),
    ("Redis 缓存队列", "Broker :6379/0\nBackend :6379/1", TEAL_LIGHT),
]

ds_w = 16.8
ds_h = 5.5
ds_x0 = 7.8
ds_gap = 0.6

for i, (name, desc, c) in enumerate(data_items):
    x = ds_x0 + i * (ds_w + ds_gap)
    rounded_box(x, ly5_bot, ds_w, ds_h, "white", ec=TEAL, lw=1.4, radius=0.4)
    rounded_box(x, ly5_bot, 0.6, ds_h, c, ec=c, lw=0, radius=0.4)
    text_at(x + ds_w / 2 + 0.4, ly5_bot + ds_h - 0.9, name, size=9.5, color=TEAL_DEEP, weight="bold")
    text_at(x + ds_w / 2 + 0.4, ly5_bot + 2.2, desc, size=8, color=SLATE_SOFT)

# 数据层向上连到对应模块
for i in range(5):
    cx = ds_x0 + i * (ds_w + ds_gap) + ds_w / 2
    arrow((cx, ly5_top), (cx, ly4_bot), color=TEAL, lw=0.8, style=":", alpha=0.5)


# ============================================================
# 底部信息
# ============================================================
text_at(3.0, 1.0, "v1.0  ·  2026-07-20  ·  HR AI Platform",
        size=8, color=SLATE_MUTED, ha="left")
text_at(97.0, 1.0, "React + FastAPI + Celery + Redis + SQLite + NumPy 向量库",
        size=8, color=SLATE_MUTED, ha="right")

# 保存
out = r"E:\AIHR\AIHR_技术架构图_简版.png"
plt.savefig(out, dpi=180, bbox_inches="tight", facecolor=BG, pad_inches=0.2)
plt.close(fig)
print("Saved:", out)
