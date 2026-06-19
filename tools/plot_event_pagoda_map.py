"""Render the run's content map on a PAGODAS-PASSED axis under
``docs/screenshots/event_pagoda_map.png``. Run from the repo root:

    python tools/plot_event_pagoda_map.py

Companion to ``plot_biome_timeline.py``: same biome + weather content, but
plotted against the pillars the player actually scores rather than wall-clock
seconds — the axis you reason about when deciding *where* in a run a new event
(here: the clown event) should slot in. Pillar→phase uses the authoritative
``weather._phase_for_pillar`` (the same dwell math the live game integrates,
including the first-pillar seeded travel and the onboarding ramp), so every
landmark lands on the real gameplay axis.

Shows the three GAMEPLAY weather events (morning-thermal geysers, rain /
thunderstorm, snow squall), the end-of-day treasure-box finale, and the newbie
plateau + ramp. Cosmetic-only phenomena (calm breeze, dawn mist) are omitted.
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

from game import biome, weather, config

# Biome keyframe phase → label (same list the seconds-axis plotter uses).
PHASE_LABELS = [
    (0.00000, "DAY"),
    (0.23125, "GOLDEN\nHOUR"),
    (0.36250, "SUNSET"),
    (0.51250, "DUSK"),
    (0.64375, "NIGHT"),
    (0.79375, "PREDAWN"),
    (0.90625, "SUNRISE"),
]

# The three gameplay weather events: (label, intensity-fn, colour).
CURVES = [
    ("Morning thermal (geysers)", weather.thermal_intensity, "#e0663a"),
    ("Rain / thunderstorm", weather.rain_intensity, "#2f6fb0"),
    ("Snow squall (tailwind)", weather.storm_intensity, "#8a6fc0"),
]


def _hex(rgb):
    return "#%02x%02x%02x" % tuple(int(c) for c in rgb[:3])


def _pillar_for_phase(phase, phases):
    """First pillar index whose cumulative phase reaches `phase` (linear
    interp between the bracketing samples for a smooth label position)."""
    for p in range(1, len(phases)):
        if phases[p] >= phase:
            lo, hi = phases[p - 1], phases[p]
            frac = (phase - lo) / (hi - lo) if hi > lo else 0.0
            return (p - 1) + frac
    return float(len(phases) - 1)


def main() -> None:
    out_dir = os.path.join(ROOT, "docs", "screenshots")
    os.makedirs(out_dir, exist_ok=True)

    # Walk pillars until phase wraps past 1.0 (the day boundary), then keep the
    # finale-rush pillars so the end-of-day event sits fully on-screen.
    pillars = [0]
    phases = [0.0]
    p = 1
    day_end = None
    while True:
        ph = weather._phase_for_pillar(p)
        pillars.append(p)
        phases.append(ph)
        if day_end is None and ph >= 1.0:
            day_end = p
        if day_end is not None and p >= day_end + config.CYCLE_FINALE_RUSH_PILLARS + 2:
            break
        p += 1
        if p > 400:  # safety net
            break

    fig, (ax_sky, ax) = plt.subplots(
        2, 1, figsize=(13, 6.2), dpi=130,
        gridspec_kw=dict(height_ratios=[1, 6], hspace=0.08),
        sharex=True,
    )

    # ── top strip: sky colour sampled from the real palette per pillar ───────
    for i in range(len(pillars) - 1):
        col = _hex(biome.palette_for_phase(phases[i])["sky_mid"])
        ax_sky.axvspan(pillars[i], pillars[i + 1], color=col, linewidth=0)
    ax_sky.set_yticks([])
    ax_sky.set_ylabel("sky", rotation=0, ha="right", va="center", fontsize=9)
    for phase, label in PHASE_LABELS:
        x = _pillar_for_phase(phase, phases)
        ax_sky.axvline(x, color="white", alpha=0.55, linewidth=1)
        ax_sky.text(x + 1, 0.5, label, color="white", fontsize=7.5,
                    va="center", ha="left", fontweight="bold")
    ax_sky.set_title(
        f"Skybit — game content map by pagodas passed  "
        f"(one full day ≈ {day_end} pagodas)", fontsize=13, pad=8)

    # ── lower panel: the three gameplay weather events vs pillar ─────────────
    # Lightning window (shaded) — a state, not an intensity curve.
    lt = [pillars[i] for i in range(len(pillars))
          if weather.lightning_active(phases[i])]
    if lt:
        ax.axvspan(min(lt), max(lt), color="#f2d94e", alpha=0.30, linewidth=0,
                   label="Lightning / thunder window")

    for label, fn, color in CURVES:
        ys = [fn(ph) for ph in phases]
        ax.plot(pillars, ys, color=color, linewidth=2.4, label=label)
        ax.fill_between(pillars, ys, color=color, alpha=0.12)
        # Peak marker annotated with its pillar number.
        pk_i = max(range(len(ys)), key=lambda i: ys[i])
        ax.plot([pillars[pk_i]], [ys[pk_i]], marker="v", color=color,
                markersize=9, markeredgecolor="white", markeredgewidth=0.8,
                zorder=5)
        ax.annotate(f"≈ pillar {pillars[pk_i]}", (pillars[pk_i], ys[pk_i]),
                    textcoords="offset points", xytext=(0, 10), ha="center",
                    fontsize=8, color=color, fontweight="bold")

    # Rain sub-peak labels (drizzle vs storm) at their anchored pillars.
    rx_drizzle = _pillar_for_phase(weather.RAIN_DRIZZLE_PEAK, phases)
    rx_storm = _pillar_for_phase(weather.RAIN_STORM_PEAK, phases)
    ax.annotate("drizzle",
                (rx_drizzle, weather.rain_intensity(weather.RAIN_DRIZZLE_PEAK)),
                textcoords="offset points", xytext=(-18, 26),
                ha="center", fontsize=7.5, color="#2f6fb0")
    ax.annotate("storm peak",
                (rx_storm, weather.rain_intensity(weather.RAIN_STORM_PEAK)),
                textcoords="offset points", xytext=(6, 26),
                ha="center", fontsize=7.5, color="#2f6fb0", fontweight="bold")

    # ── newbie onboarding band — plateau then ramp, in pillars ───────────────
    ax.axvspan(0, config.PLATEAU_PIPES, color="#3ca34d", alpha=0.22,
               linewidth=0, label="Newbie plateau / ramp", zorder=0)
    ax.axvspan(config.PLATEAU_PIPES, config.RAMP_PIPES, color="#3ca34d",
               alpha=0.11, linewidth=0, zorder=0)
    ax.annotate(f"plateau\n0–{config.PLATEAU_PIPES}",
                (config.PLATEAU_PIPES, 0.93), textcoords="offset points",
                xytext=(-3, 0), ha="right", va="top", fontsize=7.5,
                color="#1f6e2b", fontweight="bold")
    ax.annotate(f"ramp settles\npillar {config.RAMP_PIPES}",
                (config.RAMP_PIPES, 0.93), textcoords="offset points",
                xytext=(4, 0), ha="left", va="top", fontsize=7.5,
                color="#1f6e2b", fontweight="bold")

    # ── end-of-day event — treasure-box finale at the phase-wrap pillar ──────
    if day_end is not None:
        box_pillar = day_end + config.CYCLE_FINALE_BOX_INDEX
        ax.axvspan(day_end, day_end + config.CYCLE_FINALE_RUSH_PILLARS,
                   color="#caa23a", alpha=0.30, linewidth=0,
                   label="End of day — treasure-box finale")
        ax.axvline(day_end, color="#8a6b1f", linewidth=2)
        ax.annotate(
            f"END OF DAY\n+{config.TREASURE_BOX_GRANT} box @ pillar {box_pillar}",
            (day_end, 0.5), textcoords="offset points", xytext=(6, 0),
            rotation=90, fontsize=8, fontweight="bold", color="#6b520f",
            va="center", ha="left")

    # Run-start marker + biome gridlines carried into the lower panel.
    ax.axvline(0, color="#222", linewidth=2)
    ax.annotate("RUN START", (0, 0.5), xytext=(6, 0),
                textcoords="offset points", rotation=90, fontsize=8.5,
                fontweight="bold", color="#222", va="center", ha="left")
    for phase, _ in PHASE_LABELS:
        ax.axvline(_pillar_for_phase(phase, phases), color="#bbb",
                   linestyle=":", linewidth=1, zorder=0)

    ax.set_xlim(0, pillars[-1])
    ax.set_ylim(0, 1.08)
    ax.set_xlabel("pagodas passed (pillars scored)")
    ax.set_ylabel("event intensity (0–1)")
    ax.grid(True, axis="y", alpha=0.25)
    ax.set_xticks(range(0, pillars[-1] + 1, 10))

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc="upper center",
              bbox_to_anchor=(0.5, -0.13), ncol=3, framealpha=0.92,
              fontsize=9)

    fig.tight_layout()
    out_path = os.path.join(out_dir, "event_pagoda_map.png")
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out_path}")
    print(f"day boundary pillar = {day_end}")
    for label, fn, _ in CURVES:
        ys = [fn(ph) for ph in phases]
        pk_i = max(range(len(ys)), key=lambda i: ys[i])
        print(f"  {label}: peak at pillar {pillars[pk_i]} (intensity {ys[pk_i]:.2f})")


if __name__ == "__main__":
    main()
