import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe

fig, ax = plt.subplots(figsize=(14, 20))
ax.set_xlim(0, 14)
ax.set_ylim(0, 20)
ax.axis("off")
fig.patch.set_facecolor("#F8F9FA")
ax.set_facecolor("#F8F9FA")

COLORS = {
    "gray_fill":    "#E8E8E6",
    "gray_stroke":  "#5F5E5A",
    "teal_fill":    "#D0EFE4",
    "teal_stroke":  "#0F6E56",
    "purple_fill":  "#DDDAF8",
    "purple_stroke":"#534AB7",
    "amber_fill":   "#FDE8B0",
    "amber_stroke": "#BA7517",
    "blue_fill":    "#D0E6F8",
    "blue_stroke":  "#185FA5",
    "coral_fill":   "#FAD5C8",
    "coral_stroke": "#993C1D",
    "base_bg":      "#E6F5EE",
    "base_border":  "#1D9E75",
    "ext_bg":       "#EAF2FB",
    "ext_border":   "#185FA5",
    "text_dark":    "#1A1A1A",
    "text_mid":     "#4A4A4A",
    "text_light":   "#6B6B6B",
}


def draw_box(ax, x, y, w, h, fill, stroke, title, subtitle=None, radius=0.25):
    """Draw a rounded rectangle with title and optional subtitle."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        linewidth=1.2,
        edgecolor=stroke,
        facecolor=fill,
        zorder=3,
    )
    ax.add_patch(box)
    if subtitle:
        ax.text(x + w / 2, y + h * 0.62, title,
                ha="center", va="center", fontsize=9.5, fontweight="bold",
                color=COLORS["text_dark"], zorder=4)
        ax.text(x + w / 2, y + h * 0.28, subtitle,
                ha="center", va="center", fontsize=8,
                color=COLORS["text_mid"], zorder=4)
    else:
        ax.text(x + w / 2, y + h / 2, title,
                ha="center", va="center", fontsize=9.5, fontweight="bold",
                color=COLORS["text_dark"], zorder=4)


def draw_section(ax, x, y, w, h, fill, border, label):
    """Draw a dashed section container with label."""
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0,rounding_size=0.3",
        linewidth=1.5,
        edgecolor=border,
        facecolor=fill,
        linestyle="--",
        zorder=1,
        alpha=0.5,
    )
    ax.add_patch(rect)
    ax.text(x + 0.25, y + h - 0.22, label,
            ha="left", va="center", fontsize=9, fontweight="bold",
            color=border, zorder=2)


def arrow(ax, x1, y1, x2, y2, color="#888780", style="->", lw=1.4, dashed=False):
    """Draw an arrow between two points."""
    ls = (0, (4, 3)) if dashed else "solid"
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle=style,
            color=color,
            lw=lw,
            linestyle=ls,
            connectionstyle="arc3,rad=0.0",
        ),
        zorder=5,
    )


def label_arrow(ax, x, y, text, color="#6B6B6B"):
    ax.text(x, y, text, ha="center", va="center",
            fontsize=7.5, color=color, style="italic", zorder=6)

ax.text(7, 19.55, "Image Quality Assessment & Enhancement — Full Pipeline",
        ha="center", va="center", fontsize=13, fontweight="bold",
        color=COLORS["text_dark"])

draw_section(ax, 0.4, 11.8, 13.2, 7.1,
             COLORS["base_bg"], COLORS["base_border"],
             "Base Project — Quality Assessment")

# 1. Input image
draw_box(ax, 3.8, 18.1, 6.4, 0.75,
         COLORS["gray_fill"], COLORS["gray_stroke"],
         "Input Image",
         "Photo taken by visually impaired user")

arrow(ax, 7, 18.1, 7, 17.5, COLORS["gray_stroke"])

# 2. Pre-processing
draw_box(ax, 3.8, 16.7, 6.4, 0.75,
         COLORS["teal_fill"], COLORS["teal_stroke"],
         "Pre-processing",
         "Resize  →  Normalize  →  Batch tensor")

arrow(ax, 7, 16.7, 7, 16.1, COLORS["teal_stroke"])

# 3. Multi-task model
draw_box(ax, 2.8, 15.3, 8.4, 0.75,
         COLORS["purple_fill"], COLORS["purple_stroke"],
         "Multi-Task Deep Learning Model",
         "Shared CNN backbone  →  Dual output heads")

# Branch arrows from model
arrow(ax, 5.5, 15.3, 3.5, 14.55, COLORS["purple_stroke"])
arrow(ax, 8.5, 15.3, 10.5, 14.55, COLORS["purple_stroke"])

# 4a. Quality score
draw_box(ax, 0.8, 13.7, 5.4, 0.75,
         COLORS["purple_fill"], COLORS["purple_stroke"],
         "Global Quality Score",
         "Single value: 0.0 → 1.0")

# 4b. Distortion scores
draw_box(ax, 7.8, 13.7, 5.4, 0.75,
         COLORS["purple_fill"], COLORS["purple_stroke"],
         "Distortion Scores",
         "Blurry · Shaky · Bright · Dark · Grainy")

draw_section(ax, 0.4, 0.4, 13.2, 11.2,
             COLORS["ext_bg"], COLORS["ext_border"],
             "Extension — Adaptive Enhancement Pipeline")

# Bridge arrow (base → extension)
arrow(ax, 7, 13.7, 7, 12.85, COLORS["gray_stroke"])
label_arrow(ax, 8.3, 13.25, "scores passed to enhancement")

# 5. Select mode
draw_box(ax, 3.5, 12.05, 7.0, 0.75,
         COLORS["amber_fill"], COLORS["amber_stroke"],
         "Select Enhancement Mode",
         "Based on quality score & distortion profile")

# Branch arrows to modes
arrow(ax, 5.5, 12.05, 3.2, 11.2, COLORS["amber_stroke"])
arrow(ax, 8.5, 12.05, 10.8, 11.2, COLORS["amber_stroke"])

label_arrow(ax, 2.6, 11.55, "Mode A")
label_arrow(ax, 11.4, 11.55, "Mode B")

draw_box(ax, 0.6, 10.35, 5.2, 0.75,
         COLORS["blue_fill"], COLORS["blue_stroke"],
         "One-Shot Enhancement",
         "1 model call · single pass")

arrow(ax, 3.2, 10.35, 3.2, 9.65, COLORS["blue_stroke"])

draw_box(ax, 0.6, 8.8, 5.2, 0.8,
         COLORS["blue_fill"], COLORS["blue_stroke"],
         "Apply Targeted Filters",
         "Sharpen · Denoise · Brightness · Gamma · Combined")

draw_box(ax, 8.2, 10.35, 5.2, 0.75,
         COLORS["coral_fill"], COLORS["coral_stroke"],
         "Iterative Adaptive Enhancement",
         "5 model calls · re-evaluated each step")

arrow(ax, 10.8, 10.35, 10.8, 9.65, COLORS["coral_stroke"])

draw_box(ax, 8.2, 8.8, 5.2, 0.8,
         COLORS["coral_fill"], COLORS["coral_stroke"],
         "Feedback Loop  ×5 Steps",
         "Re-score → pick worst distortion → fix → repeat")

# Loop-back arrow for iterative
ax.annotate("", xy=(13.5, 10.72), xytext=(13.5, 9.2),
            arrowprops=dict(arrowstyle="->", color=COLORS["coral_stroke"],
                            lw=1.2, connectionstyle="arc3,rad=0.0"), zorder=5)
ax.plot([13.2, 13.5], [9.2, 9.2], color=COLORS["coral_stroke"], lw=1.2, zorder=5)
ax.plot([13.2, 13.5], [10.72, 10.72], color=COLORS["coral_stroke"], lw=1.2,
        linestyle=(0, (4, 3)), zorder=5)
ax.text(13.55, 9.96, "loop", ha="left", va="center", fontsize=7.5,
        color=COLORS["coral_stroke"], style="italic")

arrow(ax, 3.2, 8.8, 3.2, 8.1, COLORS["blue_stroke"])
arrow(ax, 10.8, 8.8, 10.8, 8.1, COLORS["coral_stroke"])

# Converge lines → single point
ax.plot([3.2, 7.0], [8.1, 7.7], color=COLORS["gray_stroke"], lw=1.2, zorder=5)
ax.plot([10.8, 7.0], [8.1, 7.7], color=COLORS["gray_stroke"], lw=1.2, zorder=5)
arrow(ax, 7.0, 7.7, 7.0, 7.2, COLORS["gray_stroke"])

# 6. Final enhanced image
draw_box(ax, 3.5, 6.4, 7.0, 0.75,
         COLORS["teal_fill"], COLORS["teal_stroke"],
         "Final Enhanced Image",
         "Clearer · Usable · Quality-verified")

arrow(ax, 7.0, 6.4, 7.0, 5.7, COLORS["teal_stroke"])

# 7. Output
draw_box(ax, 3.5, 4.9, 7.0, 0.75,
         COLORS["gray_fill"], COLORS["gray_stroke"],
         "Output to User / Assistive System",
         "OCR  ·  Object detection  ·  Human review")

legend_y = 0.78
legend_items = [
    (COLORS["base_bg"],  COLORS["base_border"],  "Base Project — Quality Assessment"),
    (COLORS["ext_bg"],   COLORS["ext_border"],   "Extension — Enhancement Pipeline"),
    (COLORS["purple_fill"], COLORS["purple_stroke"], "Deep learning model / outputs"),
    (COLORS["blue_fill"],   COLORS["blue_stroke"],   "One-shot mode"),
    (COLORS["coral_fill"],  COLORS["coral_stroke"],  "Iterative adaptive mode"),
    (COLORS["teal_fill"],   COLORS["teal_stroke"],   "Processing / final output"),
]

start_x = 0.6
for i, (fill, stroke, label) in enumerate(legend_items):
    bx = start_x + i * 2.23
    patch = FancyBboxPatch((bx, legend_y - 0.13), 0.35, 0.26,
                           boxstyle="round,pad=0,rounding_size=0.06",
                           linewidth=1, edgecolor=stroke, facecolor=fill, zorder=6)
    ax.add_patch(patch)
    ax.text(bx + 0.45, legend_y, label, ha="left", va="center",
            fontsize=6.8, color=COLORS["text_mid"], zorder=7)

plt.tight_layout(pad=0.3)
plt.savefig("workflow_diagram.png", dpi=200, bbox_inches="tight",
            facecolor=fig.get_facecolor())
print("Saved: workflow_diagram.png")
plt.show()