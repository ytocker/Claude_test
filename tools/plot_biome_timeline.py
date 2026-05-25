"""Render the biome + weather-event timeline under
``docs/screenshots/biome_event_timeline.png``. Run from the repo root:

    python tools/plot_biome_timeline.py

One full day-cycle is ``biome.CYCLE_SECONDS`` long. The top strip shows
the sky colour sampled live from ``biome.palette_for_time`` (so the band
always matches the real keyframes); the lower panel plots the actual
weather intensity curves pulled live from ``game.weather`` — calm breeze
(leaves), rain (drizzle / dusk storm / night residual), the lightning
window, and the predawn snow squall. Vertical markers flag where the run
starts, where each event switches on, and where each curve peaks.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from game import biome, weather

CYCLE = biome.CYCLE_SECONDS
N = 1600  # sample resolution across the cycle


def _hex(rgb):
    return "#%02x%02x%02x" % tuple(int(c) for c in rgb[:3])


def _mist_intensity(phase: float) -> float:
    """Dawn mist (peak phase 0.05 ≈ 16s) — a planned cosmetic haze the
    morning thermals would disperse. Deliberately defined HERE in the
    plotter and NOT in game/weather.py: the event is deferred, so it has
    no game code yet — this lets the planned curve appear on the timeline
    without shipping anything into the game."""
    return weather._bump(phase, 0.05, 0.05)


# ── PROPOSED morning-thermal shape (asymmetric: long buildup, short fade) ────
# Defined HERE in the plotter only — game/weather.py is NOT touched until the
# timing is approved. Long rising edge (rocks appear sparse → dense, then the
# first geyser; more geysers as it climbs) and a much shorter falling edge.
THERMAL_START_S = 50.0    # event on — first stray rocks
THERMAL_PEAK_S = 96.0     # peak — max concurrent geysers
THERMAL_END_S = 112.0     # event off — last rocks gone
GEYSER_THRESH = 0.35      # intensity above which geysers (not just rocks) spawn


def _proposed_thermal(phase: float) -> float:
    t = phase * CYCLE
    if t <= THERMAL_START_S or t >= THERMAL_END_S:
        return 0.0
    if t <= THERMAL_PEAK_S:                       # long smooth rise 0→1
        u = (t - THERMAL_START_S) / (THERMAL_PEAK_S - THERMAL_START_S)
    else:                                         # short smooth fall 1→0
        u = (THERMAL_END_S - t) / (THERMAL_END_S - THERMAL_PEAK_S)
    return u * u * (3 - 2 * u)


# Biome keyframe labels at their wall-clock timestamps (phase * cycle).
PHASE_LABELS = [
    (0.00000, "DAY"),
    (0.23125, "GOLDEN\nHOUR"),
    (0.36250, "SUNSET"),
    (0.51250, "DUSK"),
    (0.64375, "NIGHT"),
    (0.79375, "PREDAWN"),
    (0.90625, "SUNRISE"),
]

# (label, intensity-fn, line colour, peak-phase list)
CURVES = [
    ("Dawn mist (cosmetic, planned)", _mist_intensity, "#9aa7b3", [0.05]),
    ("Morning thermal (geysers) — PROPOSED", _proposed_thermal, "#e0663a",
     [THERMAL_PEAK_S / CYCLE]),
    ("Calm breeze (leaves)", weather.calm_breeze, "#d68a2e", [0.18]),
    ("Rain", weather.rain_intensity, "#2f6fb0", [0.35, 0.50, 0.62]),
    ("Snow squall (tailwind)", weather.storm_intensity, "#8a6fc0", [0.85]),
]


def main() -> None:
    out_dir = os.path.join(ROOT, "docs", "screenshots")
    os.makedirs(out_dir, exist_ok=True)

    ts = [i * CYCLE / (N - 1) for i in range(N)]
    phases = [biome.phase_for_time(t) for t in ts]

    fig, (ax_sky, ax) = plt.subplots(
        2, 1, figsize=(13, 6.2), dpi=130,
        gridspec_kw=dict(height_ratios=[1, 6], hspace=0.08),
        sharex=True,
    )

    # ── top strip: sky colour sampled from the real palette ──────────────
    for i in range(N - 1):
        col = _hex(biome.palette_for_time(ts[i])["sky_mid"])
        ax_sky.axvspan(ts[i], ts[i + 1], color=col, linewidth=0)
    ax_sky.set_yticks([])
    ax_sky.set_ylabel("sky", rotation=0, ha="right", va="center", fontsize=9)
    for phase, label in PHASE_LABELS:
        x = phase * CYCLE
        ax_sky.axvline(x, color="white", alpha=0.55, linewidth=1)
        ax_sky.text(x + 2, 0.5, label, color="white", fontsize=7.5,
                    va="center", ha="left", fontweight="bold",
                    path_effects=None)
    ax_sky.set_title(
        f"Skybit — biome cycle & weather events  "
        f"(one full cycle = {CYCLE:.0f}s)", fontsize=13, pad=8)

    # ── lower panel: weather intensity curves ────────────────────────────
    # Lightning window (shaded) — it has no intensity curve, it's a state.
    lt = [p for p in phases if weather.lightning_active(p)]
    lt_lo = min(lt) * CYCLE
    lt_hi = max(lt) * CYCLE
    ax.axvspan(lt_lo, lt_hi, color="#f2d94e", alpha=0.30, linewidth=0,
               label="Lightning / thunder window")

    for label, fn, color, peaks in CURVES:
        ys = [fn(p) for p in phases]
        ax.plot(ts, ys, color=color, linewidth=2.4, label=label)
        ax.fill_between(ts, ys, color=color, alpha=0.12)
        # Peak markers
        for pk_phase in peaks:
            x = pk_phase * CYCLE
            y = fn(pk_phase)
            ax.plot([x], [y], marker="v", color=color, markersize=9,
                    markeredgecolor="white", markeredgewidth=0.8, zorder=5)
            ax.annotate(f"{x:.0f}s", (x, y), textcoords="offset points",
                        xytext=(0, 9), ha="center", fontsize=8,
                        color=color, fontweight="bold")

    # ── Morning-thermal sub-phase annotations (the design under review) ──
    th_vals = [_proposed_thermal(p) for p in phases]
    g_on = next((ts[i] for i, v in enumerate(th_vals) if v >= GEYSER_THRESH),
                THERMAL_PEAK_S)
    g_off = next((ts[i] for i in range(len(th_vals) - 1, -1, -1)
                  if th_vals[i] >= GEYSER_THRESH), THERMAL_PEAK_S)
    ax.axvspan(THERMAL_START_S, THERMAL_PEAK_S, color="#e0663a", alpha=0.06,
               linewidth=0)                                   # long buildup
    ax.axvspan(THERMAL_PEAK_S, THERMAL_END_S, color="#c0392b", alpha=0.12,
               linewidth=0)                                   # short fade
    ax.hlines(GEYSER_THRESH, THERMAL_START_S, THERMAL_END_S, color="#e0663a",
              linestyle=":", linewidth=1.1)
    for xs, lab in ((g_on, "geysers\nbegin"), (g_off, "geysers\nend")):
        ax.axvline(xs, color="#e0663a", linestyle="--", linewidth=1.2,
                   ymax=0.95)
        ax.annotate(f"{lab}\n~{xs:.0f}s", (xs, 0.62),
                    textcoords="offset points", xytext=(0, 0), ha="center",
                    fontsize=7.5, color="#b3431f", fontweight="bold")
    ax.annotate("rocks\nbuild up\n(sparse→dense)",
                ((THERMAL_START_S + g_on) / 2, 0.17), ha="center",
                fontsize=7.5, color="#b3431f")
    ax.annotate("geyser threshold", (THERMAL_END_S + 2, GEYSER_THRESH),
                fontsize=7, color="#b3431f", va="center")
    ax.annotate(f"start ~{THERMAL_START_S:.0f}s",
                (THERMAL_START_S, 0.02), rotation=90, fontsize=7.5,
                color="#b3431f", va="bottom", ha="right", fontweight="bold")
    ax.annotate(f"end ~{THERMAL_END_S:.0f}s", (THERMAL_END_S, 0.02),
                rotation=90, fontsize=7.5, color="#b3431f", va="bottom",
                ha="left", fontweight="bold")

    # Game start marker — label rotated along the line so it clears the
    # early-morning mist/thermal peak labels at the top-left.
    ax.axvline(0, color="#222", linewidth=2)
    ax.annotate("RUN START", (0, 0.5), xytext=(6, 0),
                textcoords="offset points", rotation=90, fontsize=8.5,
                fontweight="bold", color="#222", va="center", ha="left")

    # Biome keyframe gridlines carried down into the lower panel.
    for phase, _ in PHASE_LABELS:
        ax.axvline(phase * CYCLE, color="#bbb", linestyle=":", linewidth=1,
                   zorder=0)

    ax.set_xlim(0, CYCLE)
    ax.set_ylim(0, 1.08)
    ax.set_xlabel("gameplay seconds")
    ax.set_ylabel("event intensity (0–1)")
    ax.grid(True, axis="y", alpha=0.25)
    ax.set_xticks(range(0, int(CYCLE) + 1, 20))

    # Legend below the plot (3 cols) so it never sits over the early-morning
    # mist/thermal peaks at the top-left.
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc="upper center",
              bbox_to_anchor=(0.5, -0.13), ncol=3, framealpha=0.92,
              fontsize=9)

    fig.tight_layout()
    out_path = os.path.join(out_dir, "biome_event_timeline.png")
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
