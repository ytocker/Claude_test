"""Data-driven variety for the sidewalk cast/props.

The promenade used one fixed template per object, so the street read as a loop of
clones. This module supplies the SELECTION half of the fix: a stable, per-world-
slot, weather- and day-arc-aware pick into a per-family pool of variant
descriptors. The drawers consume a descriptor (palette / pose flags / accessory
flags) so adding variety is appending DATA rows here, not new code branches.

Stability (no flicker) comes from two things, mirroring the rest of the
foreground: the pick is a PURE function of (seed, beat, weather-bucket) with the
seed fixed per world slot `k`, and callers resolve it ONCE inside their existing
`_slot_latch` decision (frozen for the slot's whole on-screen traversal). The
beat/weather inputs are coarsely quantised so a slot rarely straddles a boundary,
and even then only not-yet-entered slots see the new mix.

`select_variant` returns 0 (== each drawer's legacy look) whenever a family pool
is empty or short, so this can be wired through every call site before any art
exists — a non-breaking identity until the registry is filled.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from game.config import WEATHER_UMBRELLA_RAIN_AT

# Day-arc beats — the ordinal vocabulary the variant weights key off. Matches the
# phase windows of foreground_promenade._roster_for so a variant can be "common at
# the morning market, rare at the night festival" etc.
BEAT_MARKET = 0     # p < 0.14   — food-market rush
BEAT_MORNING = 1    # 0.14–0.25 and 0.85–1.0 — calm morning / sunrise vendors
BEAT_GOLDEN = 2     # 0.25–0.40  — afternoon stroll
BEAT_DUSK = 3       # 0.40–0.58  — lamps lighting
BEAT_FESTIVAL = 4   # 0.58–0.80  — night festival
BEAT_PREDAWN = 5    # 0.80–0.85  — teardown

# Weather buckets — kept in lockstep with the umbrella/coat gate so wet-weather
# variants appear exactly when brollies do.
WB_CLEAR = 0
WB_RAIN = 1
WB_SNOW = 2


def beat_for_phase(phase: float) -> int:
    # Windows follow the REMAPPED biome keyframes (biome.py shifts every keyframe
    # by DAY_EXTRA/NIGHT_BORROW): day-hold ends 0.157, golden 0.309, sunset 0.416,
    # night 0.644, first flakes 0.785, sunrise 0.924.
    p = phase % 1.0
    if p < 0.157:
        return BEAT_MARKET
    if p < 0.309:
        return BEAT_MORNING
    if p < 0.416:
        return BEAT_GOLDEN
    if p < 0.644:
        return BEAT_DUSK
    if p < 0.785:
        return BEAT_FESTIVAL
    if p < 0.924:
        return BEAT_PREDAWN
    return BEAT_MORNING            # sunrise vendors share the calm-morning cast


def weather_bucket(rain: float, snow: float) -> int:
    if snow >= 0.35:
        return WB_SNOW
    if rain >= WEATHER_UMBRELLA_RAIN_AT:
        return WB_RAIN
    return WB_CLEAR


def slot_seed(k: int, salt: int) -> int:
    """Stable per-instance seed from the world slot `k` (same hash family as
    foreground_promenade._slot_on so it composes cleanly)."""
    return ((k * 0x9E3779B1) ^ (salt * 0x85EBCA77)) & 0xFFFFFFFF


@dataclass(frozen=True)
class Variant:
    """One look in a family pool. `palette` maps named colour roles the drawer
    reads (e.g. {'coat': (...), 'coat_dk': (...), 'hair': (...)}); `pose` and
    `accessory` are flag sets the drawer toggles existing code paths on; `attrs`
    carries family-specific scalars/strings (e.g. archetype, height, stoop,
    build). Weights shift the mix by day-arc beat and weather bucket."""
    palette: dict = field(default_factory=dict)
    pose: frozenset = field(default_factory=frozenset)
    accessory: frozenset = field(default_factory=frozenset)
    base_weight: float = 1.0
    beat_weights: dict = field(default_factory=dict)       # beat -> multiplier
    weather_weights: dict = field(default_factory=dict)    # wbucket -> multiplier
    attrs: dict = field(default_factory=dict)              # family-specific params


# Per-family pools. Index 0 of every family MUST reproduce the drawer's legacy
# look (so `variant=0` is a no-op). Filled family-by-family by the design loop.
_VARIANT_REGISTRY: dict[str, list[Variant]] = {}


def register(family: str, variants: list[Variant]) -> None:
    _VARIANT_REGISTRY[family] = list(variants)


def pool(family: str) -> list[Variant]:
    return _VARIANT_REGISTRY.get(family, ())


def variant_count(family: str) -> int:
    return len(_VARIANT_REGISTRY.get(family, ()))


def get(family: str, index: int) -> "Variant | None":
    p = _VARIANT_REGISTRY.get(family)
    if not p:
        return None
    return p[index % len(p)]


def _weighted_pick(seed: int, weights: list) -> int:
    total = 0.0
    for w in weights:
        if w > 0:
            total += w
    if total <= 0.0:
        return 0
    # Deterministic uniform in [0,total) from the integer seed.
    h = ((seed ^ 0x27D4EB2F) * 0x165667B1) & 0xFFFFFFFF
    x = (h / 4294967296.0) * total
    acc = 0.0
    for i, w in enumerate(weights):
        if w > 0:
            acc += w
            if x < acc:
                return i
    return len(weights) - 1


# ── deal-not-roll ────────────────────────────────────────────────────────────
# A with-replacement weighted roll repeats early (by the birthday principle a
# 50-pool shows a duplicate within ~8 draws), which is exactly the "same people
# over and over" read. Selection is therefore DEALT: each family holds a deck of
# not-yet-seen indices and every pick removes one, so the whole pool is walked
# before any repeat; the beat/weather weights still bias WHICH remaining index
# goes next. Two recency exclusions keep neighbours distinct — the last few
# dealt indices, and the last couple of silhouette-height classes (outline
# variety is what actually kills the loop read at 18 px; palette alone doesn't).
# Callers only invoke this at decision time (slot latch / entity spawn), so the
# statefulness never destabilises an on-screen figure.
_RECENT_IDX_N = 3
_RECENT_CLASS_N = 2
_deck_remaining: dict[str, list[int]] = {}
_deck_recent_idx: dict[str, list[int]] = {}
_deck_recent_cls: dict[str, list[str]] = {}
# Some call sites (the scenario _pick) re-resolve their variants EVERY FRAME and
# rely on select_variant being stable for identical arguments — so each dealt
# result is memoised by its full argument tuple: the deck advances on the first
# resolution only and every re-ask returns the frozen answer (no flicker).
_dealt_memo: dict[tuple, int] = {}
_MEMO_CAP = 4096


def reset_decks() -> None:
    """Fresh decks (called per run) so every day deals its pools in a new order."""
    _deck_remaining.clear()
    _deck_recent_idx.clear()
    _deck_recent_cls.clear()
    _dealt_memo.clear()


def _sil_class(v: Variant) -> str:
    """Coarse silhouette-height class — the outline read at 18 px."""
    a = v.attrs.get("arch", "")
    if a in ("pole", "yoke", "headload"):
        return "carry"
    if v.attrs.get("stoop", 0.0) > 0.05:
        return "stooped"
    if v.attrs.get("height", 1.0) >= 1.04:
        return "tall"
    if v.attrs.get("build", 1.0) >= 1.08:
        return "broad"
    return "mid"


def select_variant(family: str, seed: int, beat: int, wbucket: int) -> int:
    """Variant index for a family at (seed, beat, weather), dealt without
    replacement. Returns 0 (the legacy look) when the family pool is
    empty/singleton, so it's safe to call everywhere before the registry is
    populated. Callers must resolve this ONCE per slot/entity (latch it)."""
    p = _VARIANT_REGISTRY.get(family)
    if not p or len(p) == 1:
        return 0
    memo_key = (family, seed, beat, wbucket)
    hit = _dealt_memo.get(memo_key)
    if hit is not None:
        return hit
    rem = _deck_remaining.get(family)
    if not rem:
        rem = list(range(len(p)))
        _deck_remaining[family] = rem
    recent = _deck_recent_idx.setdefault(family, [])
    recent_cls = _deck_recent_cls.setdefault(family, [])
    # Candidate order of preference: unseen + not recent + fresh outline class →
    # unseen + not recent → unseen. Weather-zero weights are ALWAYS respected
    # (a snow-only coat must never deal into a clear noon just to empty a deck).
    def _w(i):
        v = p[i]
        return (v.base_weight
                * v.beat_weights.get(beat, 1.0)
                * v.weather_weights.get(wbucket, 1.0))
    live = [i for i in rem if _w(i) > 0.0]
    if not live:
        # nothing in the deck suits this weather/beat — deal from the full pool
        live = [i for i in range(len(p)) if _w(i) > 0.0]
        if not live:
            return 0
    cands = [i for i in live if i not in recent and _sil_class(p[i]) not in recent_cls]
    if not cands:
        cands = [i for i in live if i not in recent] or live
    pick = cands[_weighted_pick(seed ^ (beat << 3) ^ (wbucket << 6),
                                [_w(i) for i in cands])]
    if pick in rem:
        rem.remove(pick)
    recent.append(pick)
    del recent[:-_RECENT_IDX_N]
    recent_cls.append(_sil_class(p[pick]))
    del recent_cls[:-_RECENT_CLASS_N]
    if len(_dealt_memo) >= _MEMO_CAP:
        # evict only the OLDEST quarter (insertion order): those slots scrolled
        # off long ago, so a re-ask that could flip a visible actor never loses
        # its memo — bulk clearing here caused a one-frame variant pop
        for k in list(_dealt_memo)[:_MEMO_CAP // 4]:
            del _dealt_memo[k]
    _dealt_memo[memo_key] = pick
    return pick
