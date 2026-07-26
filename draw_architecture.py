"""
AIHR 智能招聘平台 - 技术架构图绘制
输出: 16:9 高分辨率 PNG，薄荷绿/青绿色调
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
from matplotlib.lines import Line2D
import matplotlib.font_manager as fm

# =============== 字体 ===============
for cand in ["Microsoft YaHei", "SimHei", "Noto Sans SC"]:
    if any(f.name == cand for f in fm.fontManager.ttflist):
        plt.rcParams["font.family"] = cand
        break
plt.rcParams["axes.unicode_minus"] = False

# =============== 配色（薄荷绿/青绿主题） ===============
TEAL_DEEP   = "#0F766E"   # 深青
TEAL        = "#14B8A6"   # 主青
TEAL_LIGHT  = "#5EEAD4"   # 浅青
MINT        = "#A7F3D0"   # 薄荷
MINT_SOFT   = "#D1FAE5"   # 极浅薄荷
SLATE       = "#0F172A"   # 主文字
SLATE_SOFT  = "#475569"   # 次文字
SLATE_MUTED = "#94A3B8"   # 辅助文字
BG          = "#FFFFFF"
BG_PANEL    = "#F0FDFA"   # 浅薄荷背景
BORDER      = "#CCFBF1"   # 边框浅色
ACCENT_AMBER= "#F59E0B"
ACCENT_PINK = "#EC4899"

# =============== 画布 ===============
FIG_W, FIG_H = 19.2, 10.8  # 16:9
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=110)
ax.set_xlim(0, 100)
ax.set_ylim(0, 56.25)  # 16:9
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(BG)


def rounded_box(x, y, w, h, fc, ec=None, lw=1.4, alpha=1.0, radius=0.6):
    """圆角矩形"""
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


def arrow(p1, p2, color=TEAL, lw=1.4, style="-", curve=0.0, alpha=1.0, label=None, label_offset=(0, 0), label_size=7):
    """带箭头直线/曲线"""
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
                bbox=dict(boxstyle="round,pad=0.18", facecolor=BG, edgecolor="none", alpha=0.9))


# ============================================================
# 标题
# ============================================================
title_y = 54.0
text_at(50, title_y, "AIHR 智能招聘平台 · 技术架构图", size=22, color=TEAL_DEEP, weight="bold")
text_at(50, title_y - 1.7, "FastAPI + Celery + React 18  ·  大模型 + RAG + 向量检索",
        size=10.5, color=SLATE_SOFT)

# 右上角图例
leg_x = 78
leg_y = 53
legend_items = [
    ("数据流 / 调用",      TEAL,    "-"),
    ("异步任务",            TEAL,    ":"),
    ("检索/Embedding",      TEAL_LIGHT,"--"),
]
text_at(leg_x, leg_y, "图例", size=9, color=TEAL_DEEP, weight="bold", ha="left")
for i, (lbl, c, ls) in enumerate(legend_items):
    y = leg_y - 1.3 - i * 1.0
    ax.add_line(Line2D([leg_x - 0.2, leg_x + 2.2], [y, y], color=c, linewidth=2, linestyle=ls))
    text_at(leg_x + 2.6, y, lbl, size=8, color=SLATE_SOFT, ha="left")


# ============================================================
# Layer 1: 前端
# ============================================================
ly1_top = 48.5
ly1_bot = 43.8

# 浏览器/用户
rounded_box(2.5, ly1_bot, 13, ly1_top - ly1_bot, MINT_SOFT, radius=0.5)
text_at(9.0, (ly1_top + ly1_bot)/2 + 1.0, "用户 / 浏览器", size=10, color=TEAL_DEEP, weight="bold")
text_at(9.0, (ly1_top + ly1_bot)/2 - 0.5, "HR 招聘官", size=9, color=SLATE_SOFT)
# 图标：圆点
for i, c in enumerate([TEAL, TEAL_LIGHT, MINT]):
    ax.add_patch(Circle((4.0 + i*1.2, ly1_top - 0.6), 0.35, color=c, zorder=5))

# React 前端 SPA
rounded_box(18.0, ly1_bot, 50, ly1_top - ly1_bot, MINT, radius=0.5)
text_at(43.0, ly1_top - 1.0, "React 18 + TypeScript + Vite + Ant Design  (SPA)", size=12, color=TEAL_DEEP, weight="bold")
modules = ["登录", "职位管理", "简历导入", "简历详情", "AI 搜索", "匹配中心", "面试题", "大模型管理", "提示词管理"]
m_w = 4.6
m_x0 = 19.2
m_y = ly1_bot + 0.6
for i, m in enumerate(modules):
    x = m_x0 + (i % 9) * m_w
    rounded_box(x, m_y, m_w - 0.4, 1.6, BG, ec=TEAL, lw=1.0, radius=0.3)
    text_at(x + (m_w - 0.4) / 2, m_y + 0.8, m, size=8.5, color=SLATE)

# Nginx 反向代理（右侧）
rounded_box(70.5, ly1_bot, 27, ly1_top - ly1_bot, MINT_SOFT, radius=0.5)
text_at(84.0, ly1_top - 1.0, "Nginx 反向代理  ·  :80  default_server",
        size=10.5, color=TEAL_DEEP, weight="bold")
text_at(84.0, ly1_bot + 1.4, "静态资源 /  ·  /api → 8000", size=9, color=SLATE_SOFT)


# ============================================================
# Layer 2: API 网关
# ============================================================
ly2_top = 41.3
ly2_bot = 37.3
rounded_box(8.0, ly2_bot, 84, ly2_top - ly2_bot, TEAL_LIGHT, radius=0.6)
text_at(50, ly2_top - 1.0, "FastAPI 后端 API 网关  ·  Uvicorn  ·  /api/v1/*",
        size=12.5, color="white", weight="bold")
endpoints = ["auth", "jobs", "resumes", "matching", "interviews", "llm-configs", "prompts", "ai-search", "dashboard"]
ew = 8.5
ex0 = 9.0
ey = ly2_bot + 0.6
for i, ep in enumerate(endpoints):
    x = ex0 + i * ew
    rounded_box(x, ey, ew - 0.6, 1.6, "white", ec=TEAL_DEEP, lw=0.8, radius=0.3)
    text_at(x + (ew - 0.6) / 2, ey + 0.8, "/" + ep, size=8.5, color=TEAL_DEEP, weight="bold")

# 箭头：前端 → API
arrow((43, 43.8), (43, 41.3), color=TEAL_DEEP, lw=1.5)
text_at(43.5, 42.55, "REST / JSON · axios", size=8, color=SLATE_SOFT, ha="left")

# 箭头：Nginx → API
arrow((78, 43.8), (74, 41.3), color=TEAL_DEEP, lw=1.2, style="--")


# ============================================================
# Layer 3: 异步任务 / 服务层
# ============================================================
ly3_top = 35.0
ly3_bot = 30.5

# Celery + Redis
rounded_box(8.0, ly3_bot, 35, ly3_top - ly3_bot, BG_PANEL, ec=TEAL, lw=1.5, radius=0.5)
text_at(25.5, ly3_top - 0.9, "Celery Worker  +  Redis Broker / Backend",
        size=11, color=TEAL_DEEP, weight="bold")
# 三个任务
task_y = ly3_bot + 0.7
for i, t in enumerate(["parse_resume", "score_resume", "generate_interview"]):
    x = 9.5 + i * 11.0
    rounded_box(x, task_y, 10.0, 1.7, MINT, ec=TEAL, lw=0.8, radius=0.3)
    text_at(x + 5.0, task_y + 0.85, t, size=8.8, color=TEAL_DEEP, weight="bold")
# 标签
text_at(25.5, ly3_bot + 0.2, "@celery_app.task   ·   async task queue",
        size=7.5, color=SLATE_MUTED, ha="center")

# 业务 Service
rounded_box(45.5, ly3_bot, 24, ly3_top - ly3_bot, BG_PANEL, ec=TEAL, lw=1.5, radius=0.5)
text_at(57.5, ly3_top - 0.9, "Business Service Layer",
        size=11, color=TEAL_DEEP, weight="bold")
for i, t in enumerate(["vector_store\n(NumPy + JSON)", "PDF/DOCX\nGenerator\n(reportlab)", "Auth / Security\n(JWT + Fernet)"]):
    y = ly3_bot + 2.0 - i * 0  # placeholder
# 改为水平排
svc_y = ly3_bot + 0.7
for i, t in enumerate(["vector_store", "PDF/DOCX Gen", "Security"]):
    x = 46.5 + i * 7.6
    rounded_box(x, svc_y, 7.0, 1.7, MINT_SOFT, ec=TEAL, lw=0.8, radius=0.3)
    text_at(x + 3.5, svc_y + 0.85, t, size=8.5, color=TEAL_DEEP, weight="bold")
text_at(57.5, ly3_bot + 0.2, "复用模块  ·  单例 + 文件锁",
        size=7.5, color=SLATE_MUTED, ha="center")

# 文件 / 任务路由
rounded_box(72.0, ly3_bot, 20, ly3_top - ly3_bot, BG_PANEL, ec=TEAL, lw=1.5, radius=0.5)
text_at(82.0, ly3_top - 0.9, "Application Bootstrap",
        size=11, color=TEAL_DEEP, weight="bold")
text_at(82.0, ly3_top - 2.0, "·  Base.metadata.create_all\n·  默认提示词 seed\n·  uploads / downloads 目录",
        size=8.5, color=SLATE_SOFT, ha="center")
text_at(82.0, ly3_bot + 0.4, "FastAPI  startup_event()",
        size=7.5, color=SLATE_MUTED, ha="center")

# 箭头：API → Celery
arrow((30, 37.3), (25, 35.0), color=TEAL_DEEP, lw=1.2)
text_at(18, 36.1, "提交任务", size=7.5, color=SLATE_SOFT)
# 箭头：API → Service
arrow((50, 37.3), (55, 35.0), color=TEAL_DEEP, lw=1.2)
# 箭头：API → Bootstrap
arrow((70, 37.3), (80, 35.0), color=TEAL_DEEP, lw=1.2, style=":")


# ============================================================
# Layer 4: 五大核心 AI 模块（重点突出区域）
# ============================================================
ly4_top = 28.0
ly4_bot = 11.0

# Layer 标题
text_at(2.5, ly4_top + 0.4, "★  五大 AI 核心模块", size=11, color=TEAL_DEEP,
        weight="bold", ha="left")

# 五个核心模块的边界框
core_x0 = 4.0
core_w  = 92.0
core_h  = ly4_top - ly4_bot
rounded_box(core_x0, ly4_bot, core_w, core_h, MINT_SOFT, ec=TEAL_LIGHT, lw=1.0, alpha=0.4, radius=0.5)

# 五个模块
mod_w = 17.4
mod_h = 14.5
mod_y = ly4_bot + 1.5
gap   = 0.5
mods_x_start = 4.5

modules_info = [
    {
        "title": "1. 大模型管理",
        "en": "LLM Configs",
        "lines": [
            ("config_type", "chat / embedding"),
            ("base_url",   "OpenAI 兼容"),
            ("provider",   "OpenAI / 硅基 / DeepSeek"),
        ],
        "sub_box": [
            ("在线 API",   "云端大模型服务",  TEAL),
            ("本地 Ollama","私有化部署",     TEAL_LIGHT),
        ],
    },
    {
        "title": "2. 提示词管理",
        "en": "Prompts",
        "lines": [
            ("类型",     "parse / score / interview"),
            ("版本",     "PromptVersion 表"),
            ("统计",     "usage_count 自增"),
        ],
        "sub_box": [],
    },
    {
        "title": "3. 简历解析 & 结构化",
        "en": "Parse & Struct",
        "lines": [
            ("文本提取", "pdfplumber / python-docx"),
            ("LLM 解析", "Chat 模型 + JSON Schema"),
            ("结构化",   "name/phone/work/skills…"),
        ],
        "sub_box": [],
    },
    {
        "title": "4. RAG · 报告 / 面试题",
        "en": "RAG & Generation",
        "lines": [
            ("评分报告", "score_resume · 5维 + 总分"),
            ("面试题",   "generate_interview · 4模块"),
            ("AI 搜索",  "ai_search · NL 语义检索"),
        ],
        "sub_box": [],
    },
    {
        "title": "5. 向量数据库",
        "en": "Vector Store",
        "lines": [
            ("存储",     "NumPy + JSON 持久化"),
            ("检索",     "余弦相似度 top_k"),
            ("重建",     "build_index  全量"),
        ],
        "sub_box": [],
    },
]

for i, m in enumerate(modules_info):
    x = mods_x_start + i * (mod_w + gap)
    # 主框
    rounded_box(x, mod_y, mod_w, mod_h, "white", ec=TEAL, lw=1.6, radius=0.5)
    # 顶部色条
    rounded_box(x, mod_y + mod_h - 2.4, mod_w, 2.4, TEAL, ec=TEAL, lw=0, radius=0.5)
    # 标题
    text_at(x + mod_w / 2, mod_y + mod_h - 0.9, m["title"],
            size=11.5, color="white", weight="bold")
    text_at(x + mod_w / 2, mod_y + mod_h - 1.9, m["en"],
            size=8.5, color=MINT, weight="normal")
    # 行内容
    for j, (k, v) in enumerate(m["lines"]):
        ly = mod_y + mod_h - 3.6 - j * 1.4
        # 标签小框
        rounded_box(x + 0.5, ly - 0.4, 4.2, 0.9, MINT_SOFT, ec=TEAL_LIGHT, lw=0.6, radius=0.2)
        text_at(x + 2.6, ly, k, size=8, color=TEAL_DEEP, weight="bold")
        # 值
        text_at(x + 5.0, ly, v, size=8, color=SLATE, ha="left")
    # 大模型管理的子框（在线/本地）
    if m["sub_box"]:
        sub_y_top = mod_y + 1.7
        sub_y_bot = mod_y + 0.3
        sub_h = sub_y_top - sub_y_bot
        for k, (name, desc, c) in enumerate(m["sub_box"]):
            slot_h = sub_h / 2
            sy = sub_y_top - (k + 0.5) * slot_h
            sx = x + 0.5
            sw = mod_w - 1.0
            rounded_box(sx, sy - slot_h/2 + 0.05, sw, slot_h - 0.1, c, ec=c, lw=0, radius=0.25, alpha=0.9)
            text_at(sx + sw/2, sy, f"{name}  ·  {desc}", size=8.2, color="white", weight="bold")


# ===== 五个核心模块之间的关系箭头 =====
# 解析 → 向量库（自动 embedding）
arrow((mods_x_start + 2*(mod_w+gap) + mod_w/2, mod_y),               # 解析 底中
      (mods_x_start + 4*(mod_w+gap) + mod_w/2, mod_y),               # 向量库 底中
      color=TEAL, lw=1.4, curve=-0.2, label="自动向量化")
text_at(50, mod_y - 0.8, "解析完成后自动调用 Embedding 写入向量库", size=7.5, color=SLATE_SOFT)

# RAG → 大模型
arrow((mods_x_start + 3*(mod_w+gap) + mod_w/2, mod_y + mod_h - 0.2),     # RAG 顶左
      (mods_x_start + 0*(mod_w+gap) + mod_w/2, mod_y + mod_h - 0.2),     # 大模型 顶右
      color=TEAL, lw=1.4, curve=0.25, label="调用 LLM")

# RAG → 提示词
arrow((mods_x_start + 3*(mod_w+gap) + mod_w/2 - 2, mod_y + mod_h - 0.2),
      (mods_x_start + 1*(mod_w+gap) + mod_w/2 + 2, mod_y + mod_h - 0.2),
      color=TEAL, lw=1.2, curve=0.12, style="--", label="使用提示词模板")

# RAG → 向量库（检索）
arrow((mods_x_start + 3*(mod_w+gap) + mod_w/2, mod_y),                # RAG 底
      (mods_x_start + 4*(mod_w+gap) + mod_w/2, mod_y + 4),            # 向量库 上
      color=TEAL_LIGHT, lw=1.4, curve=-0.18, style="--", label="检索")

# 解析 → RAG
arrow((mods_x_start + 2*(mod_w+gap) + mod_w, mod_y + mod_h/2),         # 解析 右
      (mods_x_start + 3*(mod_w+gap), mod_y + mod_h/2),                 # RAG 左
      color=TEAL, lw=1.2, label="结构化数据", label_offset=(0, 0.7))


# 五大模块向上连到 Celery / API
for i in range(5):
    cx = mods_x_start + i*(mod_w+gap) + mod_w/2
    arrow((cx, ly4_top), (cx, 35.0), color=TEAL, lw=0.9, style=":")


# ============================================================
# Layer 5: 数据 & 存储
# ============================================================
ly5_top = 8.5
ly5_bot = 2.0

data_items = [
    ("SQLite 元数据库",    "Resume / Job / Prompt\nLLMConfig / Score\nUser / TokenUsageLog",   TEAL),
    ("简历文件存储",        "uploads/resumes/\n.pdf · .doc · .docx",                          TEAL_LIGHT),
    ("报告文件存储",        "downloads/*.pdf\nreportlab  +  中文字体",                         MINT),
    ("向量数据持久化",      "chroma_db/\nvector_store.json",                                  TEAL),
    ("Redis 缓存队列",      "Broker :6379/0\nBackend :6379/1",                                TEAL_LIGHT),
]

ds_w = 17.4
ds_h = 5.0
ds_x0 = 4.5
ds_gap = 0.5

text_at(2.5, ly5_top + 0.6, "数据 & 存储层", size=11, color=TEAL_DEEP, weight="bold", ha="left")

for i, (name, desc, c) in enumerate(data_items):
    x = ds_x0 + i * (ds_w + ds_gap)
    # 主体
    rounded_box(x, ly5_bot, ds_w, ds_h, "white", ec=TEAL, lw=1.4, radius=0.4)
    # 左侧色条
    rounded_box(x, ly5_bot, 0.6, ds_h, c, ec=c, lw=0, radius=0.4)
    # 标题
    text_at(x + ds_w/2 + 0.4, ly5_bot + ds_h - 0.9, name,
            size=10, color=TEAL_DEEP, weight="bold", ha="center")
    # 描述
    text_at(x + ds_w/2 + 0.4, ly5_bot + 2.0, desc,
            size=8.2, color=SLATE_SOFT, ha="center", va="center")

# 数据层向上连到对应模块
# SQLite ← 大模型/提示词/解析/RAG/向量库
for i in range(5):
    cx = ds_x0 + i * (ds_w + ds_gap) + ds_w/2
    arrow((cx, ly5_top), (cx, 11.0), color=TEAL, lw=0.9, style=":")
# Redis ← Celery
arrow((50, 35.0), (50, 8.5), color=TEAL_LIGHT, lw=0.8, style=":", alpha=0.6)


# ============================================================
# 底部信息
# ============================================================
text_at(2.5, 0.8, "v1.0  ·  2026  ·  HR AI Platform  ·  AIHR",
        size=8.5, color=SLATE_MUTED, ha="left")
text_at(97.5, 0.8, "架构：React + FastAPI + Celery + Redis + SQLite + NumPy 向量库",
        size=8, color=SLATE_MUTED, ha="right")

# 保存
out = r"E:\AIHR\AIHR_技术架构图.png"
plt.savefig(out, dpi=180, bbox_inches="tight", facecolor=BG, pad_inches=0.2)
plt.close(fig)
print("Saved:", out)
