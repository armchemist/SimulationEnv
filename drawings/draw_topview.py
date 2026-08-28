"""Build a dimensioned top-view drawing from the Blender ortho render."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.image as mpimg
import os

matplotlib.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
RENDER = os.path.join(HERE, "topview.png")
OUT = os.path.join(HERE, "bench_topview_dimensioned.png")

# the render covers exactly this rectangle, in millimetres
X0, X1 = -700.0, 700.0
Y0, Y1 = -194.6, 405.4

INK = "#1a1a1a"
DIM = "#0b4f8a"
NOTE = "#8a3b0b"

fig, ax = plt.subplots(figsize=(23, 15))
ax.set_aspect("equal")
ax.axis("off")
ax.set_xlim(-1130, 1130)
ax.set_ylim(-620, 700)

# ---- underlay: composite the transparent render over white -------------
rgba = mpimg.imread(RENDER).astype(float)
if rgba.shape[2] == 4:
    a = rgba[:, :, 3:4]
    img = rgba[:, :, :3] * a + (1.0 - a)
else:
    img = rgba[:, :, :3]
img = img * 0.80 + 0.20                      # screen back slightly
ax.imshow(img, extent=(X0, X1, Y0, Y1), zorder=1, interpolation="bilinear")
ax.add_patch(Rectangle((X0, Y0), X1 - X0, Y1 - Y0, fill=False, ec=INK, lw=2.0, zorder=6))

# ---- dimension helpers -------------------------------------------------
TICK = 8.0

def dim_h(x1, x2, y, label, ext_from=None, fs=13):
    if ext_from is not None:
        for x in (x1, x2):
            y_end = y + (10 if y > ext_from else -10)
            ax.plot([x, x], [ext_from, y_end], color=DIM, lw=0.7, ls=(0, (5, 4)), zorder=4)
    ax.annotate("", xy=(x1, y), xytext=(x2, y),
                arrowprops=dict(arrowstyle="<|-|>,head_width=0.26,head_length=0.7",
                                color=DIM, lw=1.1, shrinkA=0, shrinkB=0), zorder=6)
    for x in (x1, x2):
        ax.plot([x, x], [y - TICK, y + TICK], color=DIM, lw=1.1, zorder=6)
    ax.text((x1 + x2) / 2, y + 8, label, ha="center", va="bottom",
            fontsize=fs, color=DIM, zorder=7, bbox=dict(fc="white", ec="none", pad=1.0))

def dim_v(y1, y2, x, label, ext_from=None, fs=13, side="left"):
    if ext_from is not None:
        for y in (y1, y2):
            x_end = x + (10 if x > ext_from else -10)
            ax.plot([ext_from, x_end], [y, y], color=DIM, lw=0.7, ls=(0, (5, 4)), zorder=4)
    ax.annotate("", xy=(x, y1), xytext=(x, y2),
                arrowprops=dict(arrowstyle="<|-|>,head_width=0.26,head_length=0.7",
                                color=DIM, lw=1.1, shrinkA=0, shrinkB=0), zorder=6)
    for y in (y1, y2):
        ax.plot([x - TICK, x + TICK], [y, y], color=DIM, lw=1.1, zorder=6)
    ax.text(x + (-8 if side == "left" else 8), (y1 + y2) / 2, label,
            ha="right" if side == "left" else "left", va="center", rotation=90,
            fontsize=fs, color=DIM, zorder=7, bbox=dict(fc="white", ec="none", pad=1.0))

def leader(x, y, tx, ty, text, fs=11.5):
    ax.annotate(text, xy=(x, y), xytext=(tx, ty), fontsize=fs, color=NOTE, ha="center",
                va="center", zorder=9,
                arrowprops=dict(arrowstyle="-", color=NOTE, lw=0.9, shrinkA=0, shrinkB=3),
                bbox=dict(fc="white", ec=NOTE, lw=0.7, pad=3.0, alpha=0.96))

# ---- group spans (mm, measured from the scene) -------------------------
WS = (-652.0, -495.0)      # ① 폐기통
BK = (-399.0, -239.0)      # ② 비커
RK = (-143.0, 202.0)       # ③ 실린더 홀더
BT = (298.0, 652.0)        # ④ 시약

# ---- X chain below the frame ------------------------------------------
chain = [(X0, WS[0], "48"), (WS[0], WS[1], "157"), (WS[1], BK[0], "96"),
         (BK[0], BK[1], "160"), (BK[1], RK[0], "96"), (RK[0], RK[1], "345"),
         (RK[1], BT[0], "96"), (BT[0], BT[1], "354"), (BT[1], X1, "48")]
for a, b, t in chain:
    dim_h(a, b, -260.0, t, ext_from=Y0, fs=12)
for (lo, hi), txt in ((WS, "① 폐기통"), (BK, "② 비커 ×2"),
                      (RK, "③ 실린더 홀더 ×2"), (BT, "④ 시약 ×5")):
    ax.text((lo + hi) / 2, -320, txt, ha="center", va="center", fontsize=13.5,
            color=INK, zorder=8, bbox=dict(fc="white", ec=INK, lw=0.8, pad=3.5))
dim_h(X0, X1, -400.0, "1400 mm", ext_from=Y0, fs=18)

# ---- X detail above the frame -----------------------------------------
dim_h(-364.0, -274.0, 452.0, "90", ext_from=Y1, fs=12)       # beaker pitch
dim_h(-143.0, 22.0, 452.0, "165", ext_from=Y1, fs=12)        # holder L
dim_h(37.0, 202.0, 452.0, "165", ext_from=Y1, fs=12)         # holder R
for x1, x2 in ((335.5, 405.5), (405.5, 475.5), (475.5, 545.5), (545.5, 615.5)):
    dim_h(x1, x2, 452.0, "70", ext_from=Y1, fs=12)
dim_h(-652.0, -495.0, 522.0, "⌀157", ext_from=Y1, fs=12)     # bucket
dim_h(-60.5, 119.5, 522.0, "180", ext_from=Y1, fs=12)        # holder pitch
dim_h(22.0, 37.0, 592.0, "15", ext_from=Y1, fs=11)           # holder gap
dim_h(-201.6, 193.4, 592.0, "395  OMX PLATE", ext_from=Y1, fs=12)
dim_h(-500.0, 500.0, 662.0, "1000  LINEAR RAIL", ext_from=Y1, fs=15)

# ---- Y dimensions ------------------------------------------------------
dim_v(Y0, Y1, -800.0, "600 mm", ext_from=X0, fs=18)
dim_v(-84.5, -41.5, -930.0, "43", ext_from=X0, fs=11)
dim_v(241.5, 398.5, -1050.0, "157", ext_from=X0, fs=11)      # bucket depth
dim_v(Y0, 295.0, 800.0, "489.6", ext_from=X1, fs=12, side="right")
dim_v(295.0, 365.0, 800.0, "70", ext_from=X1, fs=12, side="right")
dim_v(365.0, Y1, 800.0, "40.4", ext_from=X1, fs=12, side="right")
dim_v(305.0, 355.0, 930.0, "50", ext_from=X1, fs=11, side="right")
dim_v(-123.1, 16.9, 930.0, "140", ext_from=X1, fs=11, side="right")
dim_v(295.0, 330.0, 1050.0, "35", ext_from=X1, fs=11, side="right")

# ---- centre line -------------------------------------------------------
ax.plot([0, 0], [Y0 - 230, Y1 + 30], color="#c02020", lw=0.9,
        ls=(0, (14, 5, 3, 5)), zorder=5)
ax.text(-8, Y0 - 240, "CL  X=0", ha="right", va="top", fontsize=11, color="#c02020", zorder=8)

# ---- callouts, placed on empty floor ----------------------------------
leader(-573.5, 320, -560, 130, "① 폐기통  ⌀157 × H204\n상단 개구 ⌀136  |  Y = 320")
leader(-319.0, 330, -230, 60, "② 비커  ⌀70 × H95\nY = 330  |  피치 90")
leader(-60.5, 330, 30, 130, "③ 실린더 홀더  165 × 50 × H80\n슬롯 6개  |  피치 180, 틈 15")
leader(405.5, 365, 470, 130, "④ 시약 5개  지그재그\n앞 3 (Y=295) / 뒤 2 (Y=365)\n열 피치 70")
leader(-250.0, -63, -430, -150, "리니어 레일 1 m + 캐리지")
leader(108.5, 75, 450, -60, "OMX 모듈 ×2\n마운팅 플레이트 395 × 140")

for x, y, n in ((335.5, 295, "H2O2"), (405.5, 365, "ETHANOL"), (475.5, 295, "SOLVENT"),
                (545.5, 365, "ACID"), (615.5, 295, "NaOH")):
    ax.text(x, y, n, ha="center", va="center", fontsize=8.5, color=INK, zorder=10,
            bbox=dict(fc="white", ec=INK, lw=0.5, pad=1.6, alpha=0.9))
ax.text(-573.5, 320, "WASTE", ha="center", va="center", fontsize=9, color="#c02020",
        zorder=10, bbox=dict(fc="white", ec="#c02020", lw=0.6, pad=2.0, alpha=0.9))

# ---- origin axis marker ------------------------------------------------
ox, oy = X0 + 45, Y0 + 45
ax.annotate("", xy=(ox + 80, oy), xytext=(ox, oy),
            arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3), zorder=8)
ax.annotate("", xy=(ox, oy + 80), xytext=(ox, oy),
            arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3), zorder=8)
ax.text(ox + 90, oy, "X", fontsize=13, va="center", color=INK, zorder=8)
ax.text(ox, oy + 90, "Y", fontsize=13, ha="center", color=INK, zorder=8)

# ---- sheet border + title block ---------------------------------------
SX0, SY0, SX1, SY1 = -1115, -605, 1115, 690
ax.add_patch(Rectangle((SX0, SY0), SX1 - SX0, SY1 - SY0, fill=False, ec=INK, lw=2.4, zorder=11))
tw, th = 700, 145
tx, ty = SX1 - 14 - tw, SY0 + 14
ax.add_patch(Rectangle((tx, ty), tw, th, fill=True, fc="white", ec=INK, lw=1.6, zorder=12))
ax.plot([tx, tx + tw], [ty + 70, ty + 70], color=INK, lw=1.0, zorder=13)
ax.plot([tx + 350, tx + 350], [ty, ty + 70], color=INK, lw=1.0, zorder=13)
ax.text(tx + 18, ty + 108, "LAB BENCH LAYOUT — TOP VIEW", fontsize=18, va="center",
        color=INK, zorder=13, fontweight="bold")
ax.text(tx + 18, ty + 47, "단위   mm", fontsize=12.5, va="center", color=INK, zorder=13)
ax.text(tx + 18, ty + 20, "시트   1400 × 600", fontsize=12.5, va="center", color=INK, zorder=13)
ax.text(tx + 368, ty + 47, "축척   1 : 1 (정투상 탑뷰)", fontsize=12.5, va="center", color=INK, zorder=13)
ax.text(tx + 368, ty + 20, "원본   화학 실험.blend", fontsize=12.5, va="center", color=INK, zorder=13)

fig.subplots_adjust(0, 0, 1, 1)
fig.savefig(OUT, dpi=150, facecolor="white", bbox_inches="tight", pad_inches=0.12)
print("wrote", OUT)
