"""Render a BEFORE/AFTER comparison of the day→night sky-timing swap on a
PAGODAS-PASSED axis under ``docs/screenshots/sky_earlier_before_after_v5.png``.

    python tools/plot_sky_earlier_before_after.py

"Before" = the previous biome timing (full DAY_EXTRA on every evening keyframe,
solid-day hold at 0.60 → sky frozen until ~pillar 42). "After" = the current
biome (GOLDEN..NIGHT pulled earlier by NIGHT_BORROW_SECONDS, hold at 0.51 → sky
leaves daytime by ~pillar 27, night ~15 pillars longer). The "before" keyframes
are reconstructed from the live palettes paired with their old phase positions,
so the only thing that differs between the two strips is the timing.
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

_BASE = biome._BASE_CYCLE_SECONDS
_DE = config.DAY_EXTRA_SECONDS
_CYCLE = biome.CYCLE_SECONDS

# Base (pre-remap) phase fractions, in palette order. The DAY-hold (index 1) and
# the wrap (last) are derived, not base keyframes.
_BASE_FRACS = [0.0, None, 0.23125, 0.36250, 0.51250, 0.64375, 0.79375, 0.90625, 1.0]
_NAMES = ["DAY", "", "GOLDEN\nHOUR", "SUNSET", "DUSK", "NIGHT", "PREDAWN", "SUNRISE", ""]


def _old_phase(frac):
    return (frac * _BASE + _DE) / _CYCLE


def _before_keyframes():
    """Old phases (full DAY_EXTRA shift, hold 0.60) paired with the live
    palettes (palettes are identical before/after — only timing changed)."""
    pals = [dict(p) for _, p in biome._KEYFRAMES]
    golden_old = _old_phase(0.23125)
    phases = []
    for i, frac in enumerate(_BASE_FRACS):
        if i == 1:
            phases.append(golden_old * 0.60)   # the previous DAY_HOLD_FRAC
        else:
            phases.append(0.0 if frac == 0.0 else 1.0 if frac == 1.0 else _old_phase(frac))
    return list(zip(phases, pals))


def _hex(rgb):
    return "#%02x%02x%02x" % tuple(int(c) for c in rgb[:3])


def main() -> None:
    out_dir = os.path.join(ROOT, "docs", "screenshots")
    os.makedirs(out_dir, exist_ok=True)

    # Pillar→phase is the live time-warp, unaffected by the keyframe timing, so
    # both strips share one axis. Walk one full day plus the finale rush.
    pillars, phases = [0], [0.0]
    p, day_end = 1, None
    while True:
        ph = weather._phase_for_pillar(p)
        pillars.append(p); phases.append(ph)
        if day_end is None and ph >= 1.0:
            day_end = p
        if day_end is not None and p >= day_end + config.CYCLE_FINALE_RUSH_PILLARS + 2:
            break
        p += 1
        if p > 400:
            break

    def _pillar_for_phase(phase):
        for q in range(1, len(phases)):
            if phases[q] >= phase:
                lo, hi = phases[q - 1], phases[q]
                f = (phase - lo) / (hi - lo) if hi > lo else 0.0
                return (q - 1) + f
        return float(len(phases) - 1)

    after_kf = list(biome._KEYFRAMES)
    before_kf = _before_keyframes()

    fig, axes = plt.subplots(2, 1, figsize=(13, 4.2), dpi=130,
                             gridspec_kw=dict(hspace=0.55), sharex=True)

    for ax, kf, title, hold_lbl in (
        (axes[0], before_kf, "BEFORE  ·  sky held solid day until ~pillar 42", None),
        (axes[1], after_kf, "AFTER  ·  sky starts changing by ~pillar 27, night ~15 pillars longer", None),
    ):
        biome._KEYFRAMES[:] = kf            # palette_for_phase reads this global
        for i in range(len(pillars) - 1):
            ax.axvspan(pillars[i], pillars[i + 1],
                       color=_hex(biome.palette_for_phase(phases[i])["sky_mid"]),
                       linewidth=0)
        ax.set_yticks([])
        ax.set_ylabel("sky", rotation=0, ha="right", va="center", fontsize=9)
        ax.set_title(title, fontsize=11, pad=6, loc="left")

        # Named phase boundaries from this version's own keyframes.
        for (phase, _), name in zip(kf, _NAMES):
            if not name or phase <= 0.0 or phase >= 1.0:
                continue
            x = _pillar_for_phase(phase)
            ax.axvline(x, color="white", alpha=0.5, linewidth=1)
            ax.text(x + 0.8, 0.5, name, color="white", fontsize=7,
                    va="center", ha="left", fontweight="bold")

        # Mark where the sky first leaves SOLID day (the hold-end, index 1).
        hx = _pillar_for_phase(kf[1][0])
        ax.axvline(hx, color="#ff2d2d", alpha=0.9, linewidth=2)
        ax.annotate(f"sky starts to change\n≈ pillar {round(hx)}",
                    (hx, 0.5), textcoords="offset points", xytext=(6, 0),
                    ha="left", va="center", fontsize=8, color="#ff2d2d",
                    fontweight="bold")

    biome._KEYFRAMES[:] = after_kf          # restore live state
    axes[1].set_xlabel("pagodas passed (≈ pillars scored)", fontsize=9)
    axes[1].set_xlim(0, pillars[-1])
    fig.suptitle("Skybit — day→night sky timing: trim the day, lengthen the night",
                 fontsize=12, y=0.99)

    out = os.path.join(out_dir, "sky_earlier_before_after_v5.png")
    fig.savefig(out, bbox_inches="tight")
    print("wrote", out, "  day_end =", day_end)


if __name__ == "__main__":
    main()
