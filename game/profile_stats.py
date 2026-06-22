"""Derived read-helpers over the persistent Profile stats (store_data.all_stats).

Pure functions — they never mutate state. The Stats / Hall of Shame / Arcade
sections and the nemesis-pillar "Gerald" all read through here so a derivation
(favourite power-up, days-since-dignified, distance flown, formatting) lives in
one place instead of being recomputed per section.
"""
from __future__ import annotations

import time
from datetime import date

# A pillar has to kill you at least this many times before it earns a name —
# one unlucky crash isn't a nemesis.
GERALD_MIN_DEATHS = 3

# Distance is a friendlier headline than a raw pillar count; the constant is
# purely cosmetic (a round, legible km scale), not a physical measurement.
_KM_PER_PILLAR = 0.012


def gerald(stats: dict) -> "dict | None":
    """The nemesis pillar — the pillar number you die at most, once it crosses
    GERALD_MIN_DEATHS. Returns ``{"pillar", "deaths"}`` or None if no pillar has
    earned the title yet. Shared by the histogram, crystal ball, and vending."""
    hist = stats.get("death_pillar_histogram") or []
    best_i, best_n = -1, 0
    for i, n in enumerate(hist):
        if int(n) > best_n:
            best_i, best_n = i, int(n)
    if best_i < 0 or best_n < GERALD_MIN_DEATHS:
        return None
    return {"pillar": best_i, "deaths": best_n}


def favourite_powerup(stats: dict) -> "str | None":
    """The most-grabbed power-up kind lifetime, or None if none picked yet."""
    by = stats.get("powerups_by_kind") or {}
    best, best_n = None, 0
    for k, n in by.items():
        if int(n) > best_n:
            best, best_n = k, int(n)
    return best


def days_since_dignified(stats: dict, today: "str | None" = None) -> "int | None":
    """Whole days since the last dignified run, or None if the player has never
    logged one (the safety board shows a placeholder in that case)."""
    last = stats.get("last_dignified_date") or ""
    if not last:
        return None
    today = today or time.strftime("%Y-%m-%d")
    try:
        return max(0, (date.fromisoformat(today) - date.fromisoformat(last)).days)
    except (TypeError, ValueError):
        return None


def distance_km(stats: dict) -> float:
    return round(int(stats.get("total_pillars", 0)) * _KM_PER_PILLAR, 1)


def fmt_int(n) -> str:
    return f"{int(n):,}"


def fmt_duration(seconds) -> str:
    """Compact, human time for the 'time aloft' counters: '2h 14m', '14m 03s',
    or '42s'. Totals can run to hours, so seconds-only would be unreadable."""
    s = max(0, int(seconds))
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h:
        return f"{h}h {m:02d}m"
    if m:
        return f"{m}m {sec:02d}s"
    return f"{sec}s"
