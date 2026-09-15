# -*- coding: utf-8 -*-
"""V400 状态热力图（401 题版）：五方 × 四桶。

口径：
- 114 原题沿用 CRF/脚本/tag_lit_vs_field.mjs 的四桶打标（AS-OF 2026-09-09）。
- 非 114 题 = 260 扩题 + 6 设计题 + 21 GAP 新题，均按 V400 交付口径计入「研究空白」。
- 五方维度取 nodes.json 的 section 主归属，因此 401 题无遗漏、无重复。
"""
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import BoundaryNorm, ListedColormap
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NODES_PATH = ROOT / "可视化" / "web" / "data" / "nodes.json"
TAG_PATH = ROOT / "脚本" / "tag_lit_vs_field.mjs"
OUT_PNG = ROOT / "汇报材料" / "热力图_v400_状态_五方四桶.png"
OUT_MD = ROOT / "汇报材料" / "热力图_v400_状态_明细.md"

# 中文字体
for font_path in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf"]:
    if Path(font_path).exists():
        font_manager.fontManager.addfont(font_path)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=font_path).get_name()
        plt.rcParams["axes.unicode_minus"] = False
        break

ROWS = [
    ("enterprise", "企业 Enterprise"),
    ("institution", "院系 Institution"),
    ("instructor", "教师 Instructor"),
    ("ta", "助教 TA"),
    ("student", "学生 Student"),
]
COLS = [
    ("lit", "文献已覆盖"),
    ("field", "研究空白"),
    ("transfer", "理论迁移"),
    ("gray", "待核实"),
]
COL_CN = {k: v for k, v in COLS}
ROW_CN = {k: v for k, v in ROWS}

# 解析 114 原题四桶；TCH-13~22 在原脚本中为程序化生成的「研究空白 / 置信 2」。
tag_src = TAG_PATH.read_text(encoding="utf-8")
tags = dict(re.findall(r"'([A-Z]+-\d+)': \['(lit|field|transfer|gray)'", tag_src))
for i in range(13, 23):
    tags[f"TCH-{i:02d}"] = "field"

nodes = json.loads(NODES_PATH.read_text(encoding="utf-8"))
mat = np.zeros((len(ROWS), len(COLS)), dtype=int)
for n in nodes:
    bucket = tags.get(n["id"], "field")
    row = [r for r, _ in ROWS].index(n["section"])
    col = [c for c, _ in COLS].index(bucket)
    mat[row, col] += 1

row_totals = mat.sum(axis=1)
col_totals = mat.sum(axis=0)
pct = np.zeros_like(mat, dtype=float)
for i, total in enumerate(row_totals):
    if total:
        pct[i] = mat[i] / total * 100.0

# 绘图
cmap = ListedColormap([
    "#ffffff", "#fde0dd", "#fbb4b9", "#f768a1",
    "#dd3497", "#ae017e", "#7a0177", "#49006a",
])
norm_raw = BoundaryNorm([0, 0.5, 1.5, 3.5, 8.5, 20.5, 50.5, 140.5], cmap.N)
norm_pct = BoundaryNorm([0, 0.5, 2.5, 6.5, 12.5, 25.5, 50.5, 100.1], cmap.N)

fig, axes = plt.subplots(
    1, 2, figsize=(17.2, 6.2),
    gridspec_kw={"width_ratios": [1.04, 1]},
)


def draw(ax, data, title, norm, fmt):
    ax.imshow(data, cmap=cmap, norm=norm, aspect="auto")
    ax.set_xticks(range(len(COLS)))
    ax.set_xticklabels([v for _, v in COLS], fontsize=12.5, fontweight="bold")
    ax.set_yticks(range(len(ROWS)))
    ax.set_yticklabels([v for _, v in ROWS], fontsize=13, fontweight="bold")
    ax.tick_params(left=False, bottom=False)
    ax.set_xticks(np.arange(-0.5, len(COLS), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(ROWS), 1), minor=True)
    ax.grid(which="minor", color="#9a9a9a", linewidth=1.0)
    ax.tick_params(which="minor", length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    for i in range(len(ROWS)):
        for j in range(len(COLS)):
            v = data[i, j]
            if v == 0:
                ax.text(j, i, "0", ha="center", va="center", fontsize=13,
                        color="#b8b8b8", fontstyle="italic", fontweight="bold")
            else:
                color = "white" if v >= (8 if fmt == "n" else 13) else "black"
                label = str(int(v)) if fmt == "n" else f"{v:.1f}%"
                ax.text(j, i, label, ha="center", va="center",
                        fontsize=16 if fmt == "n" else 14,
                        fontweight="bold", color=color)
    ax.set_title(title, fontsize=14.5, fontweight="bold", pad=13)


draw(axes[0], mat, "① 401 题状态：五方 × 四桶（题数）", norm_raw, "n")
draw(axes[1], pct, "② 每方内部占比（%）", norm_pct, "pct")

fig.suptitle(
    "CRF V400 状态热力图 · 401 题：研究空白是主体，院系/企业的「已覆盖 + 理论迁移」是当前证据底座",
    fontsize=17, fontweight="bold", y=0.99,
)
fig.text(
    0.5, 0.012,
    "口径：114 原题四桶沿用 tag_lit_vs_field.mjs（AS-OF 2026-09-09）；260 扩题 + 6 设计题 + 21 GAP 新题统一计入研究空白。"
    "五方维度按 section 主归属，401 题无遗漏。数据源：可视化/web/data/nodes.json。",
    ha="center", fontsize=8.6, color="#555555",
)
plt.tight_layout(rect=[0, 0.06, 1, 0.945])
OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUT_PNG, dpi=160, bbox_inches="tight", facecolor="white")
plt.close(fig)

# Markdown 明细
now = "2026-09-15"
total = int(mat.sum())
lines = [
    "# CRF V400 状态热力图 · 明细",
    "",
    f"> 生成日期：{now} · 数据源：`可视化/web/data/nodes.json` · 原题四桶源：`脚本/tag_lit_vs_field.mjs`",
    "",
    "## 口径",
    "",
    "- 五方维度 = `nodes.json.section` 主归属，401 题无重复计数。",
    "- 114 原题沿用 2026-09-09 四桶打标；`TCH-13~22` 为程序化生成的「研究空白 / 置信 2」。",
    "- 非 114 题（260 扩题 + 6 设计题 + 21 GAP 新题）按 V400 交付口径统一计入「研究空白」。",
    "",
    "## 总账",
    "",
    "| 桶 | 题数 | 占 401 |",
    "|---|---:|---:|",
]
for c, label in COLS:
    lines.append(f"| {label} | {int(col_totals[COLS.index((c, label))])} | {col_totals[COLS.index((c, label))] / total * 100:.1f}% |")
lines.append(f"| **合计** | **{total}** | 100% |")
lines += ["", "## 五方 × 四桶", "", "| 五方 | 文献已覆盖 | 研究空白 | 理论迁移 | 待核实 | 合计 |", "|---|---:|---:|---:|---:|---:|"]
for i, (key, label) in enumerate(ROWS):
    lines.append(f"| {label} | {mat[i,0]} | {mat[i,1]} | {mat[i,2]} | {mat[i,3]} | {int(row_totals[i])} |")
lines += [
    "| **合计** | " + " | ".join("**" + str(int(v)) + "**" for v in col_totals) + " | **" + str(total) + "** |",
    "",
    "## 图片",
    "",
    f"- `汇报材料/热力图_v400_状态_五方四桶.png`",
    "",
]
OUT_MD.write_text("\n".join(lines), encoding="utf-8")

print("matrix:")
for i, (key, label) in enumerate(ROWS):
    print(f"  {label}: " + "  ".join(f"{COLS[j][1]}={mat[i,j]}" for j in range(len(COLS))))
print("column totals:", {COLS[j][1]: int(col_totals[j]) for j in range(len(COLS))})
print("total:", total)
print("saved png:", OUT_PNG)
print("saved md:", OUT_MD)