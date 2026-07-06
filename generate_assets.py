# Copyright 2026 Google LLC
# Generates architecture_diagram.png and cover_page_banner.png

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────────────────────────────────────
BG          = "#0D1117"
CARD_BG     = "#161B22"
CARD_BORDER = "#30363D"
ACCENT_BLUE = "#58A6FF"
ACCENT_GRN  = "#3FB950"
ACCENT_ORG  = "#D29922"
ACCENT_RED  = "#F85149"
ACCENT_PRP  = "#BC8CFF"
TEXT_MAIN   = "#E6EDF3"
TEXT_MUTED  = "#8B949E"
ARROW_COLOR = "#484F58"


def draw_box(ax, x, y, w, h, label, sublabel=None, color=ACCENT_BLUE,
             fontsize=9, subfontsize=7):
    box = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.05",
                          facecolor=CARD_BG,
                          edgecolor=color,
                          linewidth=1.5,
                          zorder=3)
    ax.add_patch(box)
    ax.text(x + w/2, y + h*0.62, label,
            ha="center", va="center", fontsize=fontsize,
            color=TEXT_MAIN, fontweight="bold", zorder=4)
    if sublabel:
        ax.text(x + w/2, y + h*0.28, sublabel,
                ha="center", va="center", fontsize=subfontsize,
                color=TEXT_MUTED, zorder=4)


def draw_arrow(ax, x1, y1, x2, y2, color=ARROW_COLOR, style="->", lw=1.5):
    ax.annotate("",
                xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(
                    arrowstyle=style,
                    color=color,
                    lw=lw,
                    connectionstyle="arc3,rad=0.0",
                ),
                zorder=2)


def draw_dbl_arrow(ax, x1, y1, x2, y2, color=ARROW_COLOR, lw=1.5):
    ax.annotate("",
                xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(
                    arrowstyle="<->",
                    color=color,
                    lw=lw,
                    connectionstyle="arc3,rad=0.0",
                ),
                zorder=2)


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 1 — ARCHITECTURE DIAGRAM
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(16, 10))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 16)
ax.set_ylim(0, 10)
ax.axis("off")

fig.suptitle("Scenario Learner Bot — System Architecture",
             fontsize=16, color=TEXT_MAIN, fontweight="bold", y=0.97)

# ── USER ────────────────────────────────────────────────────────────────────
draw_box(ax, 0.2, 4.3, 1.8, 1.4, "User", "Input / Prompt", ACCENT_BLUE, fontsize=10)

# ── ROOT AGENT ──────────────────────────────────────────────────────────────
draw_box(ax, 3.3, 3.8, 2.6, 2.4,
         "root_agent",
         "Orchestrator\n+ Security Gate\n(before_model_callback)",
         ACCENT_BLUE, fontsize=10)

# Security sub-box inside root_agent
sec_box = FancyBboxPatch((3.35, 3.85), 2.5, 0.7,
                           boxstyle="round,pad=0.03",
                           facecolor="#1C2128",
                           edgecolor=ACCENT_RED,
                           linewidth=1, zorder=4)
ax.add_patch(sec_box)
ax.text(3.6, 4.22, "[SEC] security_checkpoint", fontsize=7,
        color=ACCENT_RED, va="center", zorder=5)

# Arrow user → root_agent
draw_arrow(ax, 2.0, 5.0, 3.3, 5.0)

# ── ORCHESTRATOR DECISION BRANCH ────────────────────────────────────────────
ax.text(2.55, 5.15, "intent", fontsize=7, color=TEXT_MUTED, style="italic")

# ── SCENARIO DESIGNER ──────────────────────────────────────────────────────
draw_box(ax, 7.0, 5.2, 2.4, 1.8,
         "scenario_designer", "Generate Scenarios\n& Branching Trees",
         ACCENT_GRN, fontsize=9)

# ── FEEDBACK COACH ──────────────────────────────────────────────────────────
draw_box(ax, 7.0, 2.6, 2.4, 1.8,
         "feedback_coach", "Score Learner\nPaths & Personas",
         ACCENT_ORG, fontsize=9)

# Arrows root → designers
draw_arrow(ax, 5.9, 5.5, 7.0, 6.1)
draw_arrow(ax, 5.9, 3.5, 7.0, 3.6)
ax.text(6.45, 4.7, "feedback / score", fontsize=7, color=TEXT_MUTED, style="italic")
ax.text(6.45, 3.6, "create / generate", fontsize=7, color=TEXT_MUTED, style="italic")

# Return arrows (dashed)
ax.annotate("",
            xy=(5.9, 5.0), xytext=(7.0, 5.2),
            arrowprops=dict(arrowstyle="<-", color=ACCENT_GRN, lw=1.2,
                            linestyle="dashed", connectionstyle="arc3,rad=0.0"), zorder=2)
ax.annotate("",
            xy=(5.9, 4.0), xytext=(7.0, 2.6),
            arrowprops=dict(arrowstyle="<-", color=ACCENT_ORG, lw=1.2,
                            linestyle="dashed", connectionstyle="arc3,rad=0.0"), zorder=2)

# ── MCP SERVER ─────────────────────────────────────────────────────────────
draw_box(ax, 10.6, 2.6, 3.0, 4.0, "mcp_server.py",
         "FastMCP | stdio transport",
         ACCENT_PRP, fontsize=9)

mcp_tools = [
    "generate_scenario_seed",
    "build_branching_tree",
    "simulate_learner_persona",
    "score_learner_path",
]
for i, tool in enumerate(mcp_tools):
    ty = 6.15 - i * 0.72
    box = FancyBboxPatch((10.75, ty), 2.7, 0.55,
                           boxstyle="round,pad=0.03",
                           facecolor="#1C2128",
                           edgecolor=ACCENT_PRP,
                           linewidth=0.8, zorder=4)
    ax.add_patch(box)
    ax.text(10.9, ty + 0.27, f"  • {tool}", fontsize=7.5,
            color=ACCENT_PRP, va="center", zorder=5)

# Arrows designer/coach → MCP
draw_arrow(ax, 9.4, 4.3, 10.6, 4.3, ACCENT_PRP, lw=1.3)
draw_arrow(ax, 9.4, 3.5, 10.6, 3.5, ACCENT_PRP, lw=1.3)
ax.text(10.0, 4.5, "MCP tools", fontsize=7, color=TEXT_MUTED, style="italic")

# Arrow root → MCP (direct security log)
ax.annotate("",
            xy=(10.6, 4.0), xytext=(5.9, 4.5),
            arrowprops=dict(arrowstyle="->", color=ACCENT_RED, lw=1.0,
                            linestyle="dotted", connectionstyle="arc3,rad=0.0"), zorder=2)
ax.text(8.0, 5.1, "audit log", fontsize=7, color=ACCENT_RED, style="italic")

# ── RETURN TO USER ─────────────────────────────────────────────────────────
draw_arrow(ax, 3.3, 5.0, 2.0, 5.0)
# Response label
ax.text(2.55, 5.65, "response", fontsize=7, color=TEXT_MUTED, style="italic")

# ── LEGEND ──────────────────────────────────────────────────────────────────
legend_items = [
    (ACCENT_BLUE, "Orchestrator / Root Agent"),
    (ACCENT_GRN,  "scenario_designer sub-agent"),
    (ACCENT_ORG,  "feedback_coach sub-agent"),
    (ACCENT_PRP,  "MCP Server / Tools"),
    (ACCENT_RED,  "Security Layer"),
]
for i, (color, label) in enumerate(legend_items):
    lx, ly = 0.3 + (i % 3) * 5.3, 1.3 - (i // 3) * 0.6
    rect = FancyBboxPatch((lx, ly), 0.3, 0.3,
                           boxstyle="round,pad=0.02",
                           facecolor=color, edgecolor="none", zorder=4)
    ax.add_patch(rect)
    ax.text(lx + 0.45, ly + 0.15, label, fontsize=7.5,
            color=TEXT_MUTED, va="center", zorder=4)

# ── PHASE TAGS ─────────────────────────────────────────────────────────────
phase_tags = [
    (0.2, 8.8, "Phase 1–2  ·  Multi-Agent + Routing"),
    (5.8, 8.8, "Phase 3     ·  MCP Server"),
    (9.8, 8.8, "Phase 3     ·  MCP Tools"),
    (0.2, 0.6, "Phase 4     ·  Security checkpoint (PII / Injection / Content filter)"),
    (5.8, 0.6, "Phase 5     ·  Unit + Integration Tests"),
    (9.8, 0.6, "Phase 6     ·  README / Submission Write-up"),
]
for tx, ty, label in phase_tags:
    ax.text(tx, ty, label, fontsize=7, color=ACCENT_BLUE,
            style="italic", zorder=4)

plt.tight_layout(rect=[0, 0.02, 1, 0.95])
fig.savefig("d:/Dev/Antigravity/ADK-playground/scenario-learner-bot/assets/architecture_diagram.png",
            dpi=150, bbox_inches="tight", facecolor=BG)
print("OK architecture_diagram.png saved")
plt.close()


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 2 — COVER PAGE BANNER
# ─────────────────────────────────────────────────────────────────────────────
fig2, ax2 = plt.subplots(figsize=(16, 6))
fig2.patch.set_facecolor(BG)
ax2.set_facecolor(BG)
ax2.set_xlim(0, 16)
ax2.set_ylim(0, 6)
ax2.axis("off")

# Gradient-like background bands using rectangles
for i in range(20):
    alpha = 0.04 + 0.02 * abs(8 - i) / 8
    rect = plt.Rectangle((i, 0), 1, 6, color=ACCENT_BLUE, alpha=alpha)
    ax2.add_patch(rect)

# Accent top bar
top_bar = FancyBboxPatch((0, 5.2), 16, 0.8,
                          boxstyle="square,pad=0",
                          facecolor=ACCENT_BLUE, edgecolor="none", alpha=0.85)
ax2.add_patch(top_bar)
ax2.text(8, 5.6, "AGENTS FOR GOOD  |  EDUCATION  |  2026 ADK COMPETITION",
         ha="center", va="center", fontsize=9.5, color=TEXT_MAIN,
         fontweight="bold", zorder=5)

# Subtle grid lines
for y in np.arange(0.5, 5.2, 0.5):
    ax2.axhline(y=y, color=CARD_BORDER, lw=0.4, alpha=0.4, zorder=1)

for x in np.arange(1, 16, 1):
    ax2.axvline(x=x, color=CARD_BORDER, lw=0.4, alpha=0.2, zorder=1)

# Main title
ax2.text(8, 3.9, "Scenario Learner Bot",
         ha="center", va="center", fontsize=28,
         color=TEXT_MAIN, fontweight="bold", zorder=4)

# Tag line
ax2.text(8, 3.1, "Interactive Role-Play Scenario Generator for Corporate & Academic Training",
         ha="center", va="center", fontsize=11,
         color=ACCENT_BLUE, zorder=4)

# Feature chips
chips = [
    ("Multi-Agent Architecture", ACCENT_BLUE),
    ("MCP Server Tools", ACCENT_GRN),
    ("Security Gate", ACCENT_RED),
    ("A2A Protocol", ACCENT_ORG),
    ("Gemini 2.5 Flash", ACCENT_PRP),
]
total_w = sum(len(c[0]) for c in chips) * 0.13 + len(chips) * 0.4
start_x = 8 - total_w / 2
for i, (label, color) in enumerate(chips):
    cx = start_x + i * (len(label) * 0.13 + 0.4) + (len(label) * 0.13 + 0.4) / 2
    chip_rect = FancyBboxPatch((start_x + i * (len(label) * 0.13 + 0.4), 2.2),
                                len(label) * 0.13 + 0.3, 0.5,
                                boxstyle="round,pad=0.05",
                                facecolor=color, edgecolor="none", alpha=0.8, zorder=4)
    ax2.add_patch(chip_rect)
    ax2.text(cx, 2.45, label, ha="center", va="center",
             fontsize=8, color=BG, fontweight="bold", zorder=5)

# Prompt example
prompt_box = FancyBboxPatch((2.5, 0.5), 11, 1.3,
                               boxstyle="round,pad=0.1",
                               facecolor=CARD_BG,
                               edgecolor=ACCENT_BLUE,
                               linewidth=1.5, zorder=3)
ax2.add_patch(prompt_box)
ax2.text(8, 1.45, "\"Create a training scenario about conflict resolution for new hires\"",
         ha="center", va="center", fontsize=9.5,
         color=TEXT_MUTED, style="italic", zorder=4)
ax2.text(8, 0.75, "→ Generates scenario seed + branching dialogue tree + learner feedback model",
         ha="center", va="center", fontsize=8.5,
         color=ACCENT_GRN, zorder=4)

# Bottom bar
bot_bar = FancyBboxPatch((0, 0), 16, 0.55,
                          boxstyle="square,pad=0",
                          facecolor=ACCENT_BLUE, edgecolor="none", alpha=0.6)
ax2.add_patch(bot_bar)
ax2.text(8, 0.27, "Google ADK 2.3.0   ·   FastMCP   ·   Gemini 2.5 Flash   ·   FastAPI   ·   Python 3.11+",
         ha="center", va="center", fontsize=8,
         color=TEXT_MAIN, zorder=5)

plt.tight_layout(rect=[0, 0, 1, 1])
fig2.savefig("d:/Dev/Antigravity/ADK-playground/scenario-learner-bot/assets/cover_page_banner.png",
             dpi=150, bbox_inches="tight", facecolor=BG)
print("OK cover_page_banner.png saved")
plt.close()