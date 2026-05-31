"""Render the biome + weather-event timeline keyed to PILLARS PASSED
under ``docs/screenshots/biome_event_timeline_by_pillars.png``. Run from
the repo root:

    python tools/plot_biome_timeline_by_pillars.py

Sister tool to ``tools/plot_biome_timeline.py`` — same curves and same
biome strip, but the x-axis is pillars (Pip's score) instead of
gameplay seconds. Pillars are strictly monotonic in time so each
weather event lands at a precise pillar count, which makes it obvious
where the genie milestone (LATE_GAME_SCORE = 420) sits relative to the
dusk thunderstorm, the morning thermal, the snow squall, etc.
"""
from __future__ import annotations

import bisect
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from game import biome, weather, config

CYCLE = biome.CYCLE_SECONDS
MAX_PILLARS = 600          # cover the genie milestone (420) + headroom
N = 1800                   # sample resolution across the run

GENIE_PILLAR = config.LATE_GAME_SCORE   # 420 today


def _hex(rgb):
    return "#%02x%02x%02x" % tuple(int(c) for c in rgb[:3])


def _mist_intensity(phase: float) -> float:
    """Mirrors the existing plotter — deferred cosmetic mist, no in-game
    implementation, sketched here purely so the planned bump appears on
    the timeline."""
    return weather._bump(phase, 0.05, 0.05)


THERMAL_START_S = 50.0
THERMAL_PEAK_S = 96.0
THERMAL_END_S = 112.0
GEYSER_THRESH = config.GEYSER_SPAWN_THRESHOLD

PHASE_LABELS = [
    (0.00000, "DAY"),
    (0.23125, "GOLDEN\nHOUR"),
    (0.36250, "SUNSET"),
    (0.51250, "DUSK"),
    (0.64375, "NIGHT"),
    (0.79375, "PREDAWN"),
    (0.90625, "SUNRISE"),
]

CURVES = [
    ("Dawn mist (cosmetic, planned)", _mist_intensity, "#9aa7b3"),
    ("Morning thermal (geysers)", weather.thermal_intensity, "#e0663a"),
    ("Calm breeze (leaves)",      weather.calm_breeze,      "#d68a2e"),
    ("Rain",                       weather.rain_intensity,   "#2f6fb0"),
    ("Snow squall (tailwind)",     weather.storm_intensity,  "#8a6fc0"),
]


def build_time_for_pillar(max_pillars: int) -> list:
    """Cumulative wall-clock seconds to reach each pillar, walking the
    same onboarding-ramp dwell math World uses. Each pillar's dwell is
    spacing / scroll, with both spacing + scroll interpolated on the
    same _ramp_t() quadratic ease."""
    T = [0.0]
    for pp in range(1, max_pillars + 1):
        pp_in = pp - 1
        if pp_in < config.PLATEAU_PIPES:
            t = 0.0
        else:
            denom = max(1, config.RAMP_PIPES - config.PLATEAU_PIPES)
            x = min(1.0, (pp_in - config.PLATEAU_PIPES) / denom)
            t = 1.0 - (1.0 - x) ** 2
        spacing = (config.PIPE_SPACING_NEWBIE
                   + (config.PIPE_SPACING - config.PIPE_SPACING_NEWBIE) * t)
        scroll = (config.SCROLL_NEWBIE_BASE
                  + (config.SCROLL_BASE - config.SCROLL_NEWBIE_BASE) * t)
        T.append(T[-1] + spacing / scroll)
    return T


def main() -> None:
    out_dir = os.path.join(ROOT, "docs", "screenshots")
    os.makedirs(out_dir, exist_ok=True)

    time_for_pillar = build_time_for_pillar(MAX_PILLARS + 10)
    t_max = time_for_pillar[MAX_PILLARS]

    # Inverse: time → pillar (linear interp between consecutive entries).
    def pillar_for_time(t: float) -> float:
        i = bisect.bisect_left(time_for_pillar, t)
        if i <= 0:
            return 0.0
        if i >= len(time_for_pillar):
            return float(len(time_for_pillar) - 1)
        t0, t1 = time_for_pillar[i - 1], time_for_pillar[i]
        if t1 == t0:
            return float(i - 1)
        return (i - 1) + (t - t0) / (t1 - t0)

    # Sample timeline.
    ts = [i * t_max / (N - 1) for i in range(N)]
    pillars = [pillar_for_time(t) for t in ts]
    phases = [biome.phase_for_time(t) for t in ts]

    fig, (ax_sky, ax) = plt.subplots(
        2, 1, figsize=(14, 6.8), dpi=130,
        gridspec_kw=dict(height_ratios=[1, 6], hspace=0.08),
        sharex=True,
    )

    # ── top strip: sky colour vs pillars ─────────────────────────────────
    for i in range(N - 1):
        col = _hex(biome.palette_for_time(ts[i])["sky_mid"])
        ax_sky.axvspan(pillars[i], pillars[i + 1], color=col, linewidth=0)
    ax_sky.set_yticks([])
    ax_sky.set_ylabel("sky", rotation=0, ha="right", va="center", fontsize=9)

    # Biome keyframe labels, drawn once per cycle present in the range.
    n_cycles = int(t_max / CYCLE) + 1
    for c in range(n_cycles):
        cycle_start_t = c * CYCLE
        if cycle_start_t > t_max:
            break
        for phase, label in PHASE_LABELS:
            t = cycle_start_t + phase * CYCLE
            if t > t_max:
                continue
            p = pillar_for_time(t)
            ax_sky.axvline(p, color="white", alpha=0.45, linewidth=0.9)
            ax_sky.text(p + 1.5, 0.5, label, color="white", fontsize=7,
                        va="center", ha="left", fontweight="bold")

    ax_sky.set_title(
        f"Skybit — biome + weather events vs pillars passed  "
        f"(1 biome cycle = {CYCLE:.0f} s ≈ "
        f"{pillar_for_time(CYCLE):.0f} pillars after the newbie ramp)",
        fontsize=12, pad=8)

    # ── lower panel: weather intensity curves vs pillars ─────────────────
    # Lightning windows — shade ANY pillar range where lightning is active.
    # Curves wrap each cycle, so the storm hits multiple times across the run.
    in_window = False
    win_start = None
    legend_added = False
    for i, p in enumerate(phases):
        active = weather.lightning_active(p)
        if active and not in_window:
            win_start = pillars[i]
            in_window = True
        elif not active and in_window:
            ax.axvspan(win_start, pillars[i], color="#f2d94e", alpha=0.30,
                       linewidth=0,
                       label=("Lightning / thunder window"
                              if not legend_added else None))
            legend_added = True
            in_window = False
    if in_window:
        ax.axvspan(win_start, pillars[-1], color="#f2d94e", alpha=0.30,
                   linewidth=0,
                   label=("Lightning / thunder window"
                          if not legend_added else None))

    for label, fn, color in CURVES:
        ys = [fn(p) for p in phases]
        ax.plot(pillars, ys, color=color, linewidth=2.0, label=label)
        ax.fill_between(pillars, ys, color=color, alpha=0.10)

    # ── Genie milestone marker (the headline annotation) ─────────────────
    ax.axvline(GENIE_PILLAR, color="#d12f2f", linewidth=2.3, alpha=0.85,
               linestyle="-", zorder=4)
    ax.annotate(f"GENIE @ {GENIE_PILLAR}",
                (GENIE_PILLAR, 1.02), textcoords="offset points",
                xytext=(0, 2), ha="center", fontsize=10,
                fontweight="bold", color="#d12f2f")

    # ── Newbie ramp band ─────────────────────────────────────────────────
    ax.axvspan(0, config.PLATEAU_PIPES, color="#3ca34d", alpha=0.22,
               linewidth=0, label="Newbie plateau / ramp", zorder=0)
    ax.axvspan(config.PLATEAU_PIPES, config.RAMP_PIPES, color="#3ca34d",
               alpha=0.10, linewidth=0, zorder=0)
    ax.annotate(f"ramp settles\n@ pillar {config.RAMP_PIPES}",
                (config.RAMP_PIPES, 0.94),
                textcoords="offset points", xytext=(3, 0),
                ha="left", va="top", fontsize=7.5, color="#1f6e2b",
                fontweight="bold")

    # ── Biome cycle boundaries (one cycle of weather = one cycle of biome) ─
    for c in range(1, n_cycles):
        t_boundary = c * CYCLE
        if t_boundary > t_max:
            break
        x_boundary = pillar_for_time(t_boundary)
        ax.axvline(x_boundary, color="#999", linestyle=":", linewidth=1,
                   zorder=0)
        ax.annotate(f"cycle {c + 1}\n@ p{int(x_boundary)}",
                    (x_boundary, 0.05),
                    textcoords="offset points", xytext=(3, 0),
                    ha="left", fontsize=7, color="#666")

    # ── Per-cycle annotation: where does each event peak in pillars? ─────
    # For each cycle, mark the storm peak (phase 0.50) — that's the event
    # that overlaps the genie milestone today.
    for c in range(n_cycles):
        t_storm_peak = c * CYCLE + 0.50 * CYCLE
        if t_storm_peak > t_max:
            continue
        p_storm = pillar_for_time(t_storm_peak)
        y = weather.rain_intensity(0.50)
        ax.plot([p_storm], [y], marker="v", color="#2f6fb0", markersize=8,
                markeredgecolor="white", markeredgewidth=0.8, zorder=5)
        ax.annotate(f"storm peak\n@ p{int(p_storm)}", (p_storm, y),
                    textcoords="offset points", xytext=(0, 9),
                    ha="center", fontsize=7.5, color="#2f6fb0",
                    fontweight="bold")

    ax.set_xlim(0, MAX_PILLARS)
    ax.set_ylim(0, 1.08)
    ax.set_xlabel("pillars passed (= player's score)")
    ax.set_ylabel("event intensity (0–1)")
    ax.grid(True, axis="y", alpha=0.25)
    xticks = list(range(0, MAX_PILLARS + 1, 50))
    if GENIE_PILLAR not in xticks:
        xticks.append(GENIE_PILLAR)
        xticks.sort()
    ax.set_xticks(xticks)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc="upper center",
              bbox_to_anchor=(0.5, -0.13), ncol=3, framealpha=0.92,
              fontsize=9)

    fig.tight_layout()
    out_path = os.path.join(out_dir, "biome_event_timeline_by_pillars.png")
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out_path}")

    # Sanity check: pillar_for_time(time at pillar 25) should = 25.
    t_at_25 = time_for_pillar[25]
    p_25 = pillar_for_time(t_at_25)
    print(f"sanity: pillar_for_time(t at 25) = {p_25:.3f} (expected ≈ 25)")
    print(f"pillars per cycle (post-ramp): "
          f"{pillar_for_time(CYCLE) - pillar_for_time(0):.1f}")
    print(f"Total time for {MAX_PILLARS} pillars: {t_max:.1f} s "
          f"({t_max / CYCLE:.2f} biome cycles)")


if __name__ == "__main__":
    main()
