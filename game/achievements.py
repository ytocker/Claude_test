"""
Achievements — meta-progression for Skybit.

A run never *earns* an achievement mid-flight; the whole roster is evaluated
once at end-of-run against the finished ``World`` (zero per-frame cost). Unlock
state + lifetime counters persist locally on both build targets:

  * native  — read-modify-written under the ``"achievements"`` key of
              ``skybit_save.json`` (siblings such as a future high-score blob
              are preserved).
  * browser — a single JSON string in ``localStorage["skybit_ach"]`` via two
              actions on the closure-private ``window.__sk`` dispatcher
              (``ach_load`` / ``ach_save``), probed exactly like the
              leaderboard bridge so a missing dispatcher degrades to "nothing
              unlocked" instead of crashing.

Storage is kept behind ``load()`` / ``save()`` so a future account-scoped
cloud mirror is an additive change that never touches the engine or the UI.

Design rules:
  * Achievement ``id`` strings are PERMANENT. Renaming or reusing one orphans
    a player's saved unlock — only ever ADD new ids.
  * Adding achievements needs no migration (an id absent from ``unlocked`` is
    simply locked). ``store["v"]`` guards structural changes to the lifetime
    block; ``_migrate`` back-fills missing keys.
  * Every read/write is wrapped so a corrupt save degrades gracefully.
"""
from __future__ import annotations

import sys
import json
import time
from collections import OrderedDict
from dataclasses import dataclass

from game.config import (
    SAVE_FILE, LOTTERY_TIERS,
    RAIN_START_PILLAR, SNOW_START_PILLAR,
)

_IS_BROWSER = sys.platform == "emscripten"

# Nested under this key in skybit_save.json so unrelated save data can coexist.
_ACH_KEY = "achievements"
# localStorage key for the browser path.
_WEB_KEY = "skybit_ach"
# Schema version of the persisted lifetime block.
_SCHEMA_V = 1

# Jackpot coin delta, pulled from the live lottery table so a re-tune of the
# top tier keeps the "hit the jackpot" achievement honest.
_JACKPOT_DELTA = next((d for (label, _w, d) in LOTTERY_TIERS
                       if label == "JACKPOT"), 100)


# ── Categories ────────────────────────────────────────────────────────────────

CAT_PROGRESS = "Flight Log"      # pillars / score / day-cycle milestones
CAT_RICHES   = "Riches"          # coin totals (run + lifetime)
CAT_POWERUPS = "Power Player"    # power-up usage + collection
CAT_STORM    = "Stormchaser"     # nerve, endurance, weather biomes
CAT_SKATER   = "Skater"          # skateboard buff
CAT_SECRET   = "Mysteries"       # hidden late-game / secret unlocks

CATEGORY_ORDER = (
    CAT_PROGRESS, CAT_RICHES, CAT_POWERUPS, CAT_STORM, CAT_SKATER, CAT_SECRET,
)


@dataclass(frozen=True)
class Achievement:
    """One unlockable. ``stat`` + ``scope`` describe what is measured;
    ``target`` is the threshold (``1`` for a boolean flag)."""
    id: str            # PERMANENT — never rename or reuse
    title: str
    desc: str          # requirement / flavour; hidden+locked renders "???"
    category: str
    icon_key: str      # routes to a procedural badge drawer
    stat: str          # see _run_value / _life_value resolvers
    target: int = 1
    scope: str = "run"     # "run" (per-run World stat) | "life" (cumulative)
    hidden: bool = False   # locked row shows "???" until unlocked


# ── Roster (source of truth, ordered by category) ─────────────────────────────
#
# Every entry is derivable from signals the World already tracks — no new
# per-frame instrumentation. "Derived" stats (distinct_powerups, lottery_jackpot,
# magnet_life) are computed by the resolvers below.

ACHIEVEMENTS: tuple[Achievement, ...] = (
    # ── Flight Log ────────────────────────────────────────────────────────
    Achievement("first_flight", "First Delivery",
                "Clear your very first pillar.",
                CAT_PROGRESS, "pillar", "pillars_passed", 1),
    Achievement("pillar_25", "Courier in Training",
                "Pass 25 pillars in one run.",
                CAT_PROGRESS, "pillar", "pillars_passed", 25),
    Achievement("pillar_50", "Route Veteran",
                "Pass 50 pillars in one run.",
                CAT_PROGRESS, "pillar", "pillars_passed", 50),
    Achievement("pillar_100", "Centurion of the Sky",
                "Pass 100 pillars in one run.",
                CAT_PROGRESS, "pillar", "pillars_passed", 100),
    Achievement("score_100", "Triple Digits",
                "Reach a score of 100.",
                CAT_PROGRESS, "score", "score", 100),
    Achievement("score_500", "High Flyer",
                "Reach a score of 500.",
                CAT_PROGRESS, "score", "score", 500),
    Achievement("day_complete", "Round the Clock",
                "Survive a full day-into-night cycle.",
                CAT_PROGRESS, "day", "cycles_completed", 1),
    Achievement("day_three", "Three-Day Weekend",
                "Survive three full day cycles in one run.",
                CAT_PROGRESS, "day", "cycles_completed", 3),
    Achievement("frequent_flyer", "Frequent Flyer",
                "Pass 1,000 pillars all-time.",
                CAT_PROGRESS, "pillar", "total_pillars", 1000, scope="life"),
    Achievement("globetrotter", "Globetrotter",
                "Pass 10,000 pillars all-time.",
                CAT_PROGRESS, "pillar", "total_pillars", 10000, scope="life"),

    # ── Riches ────────────────────────────────────────────────────────────
    Achievement("coin_25_run", "Pocket Change",
                "Collect 25 coins in one run.",
                CAT_RICHES, "coin", "coin_count", 25),
    Achievement("coin_100_run", "Coin Run",
                "Collect 100 coins in one run.",
                CAT_RICHES, "coin", "coin_count", 100),
    Achievement("coins_500_life", "Coin Collector",
                "Collect 500 coins all-time.",
                CAT_RICHES, "coin", "total_coins", 500, scope="life"),
    Achievement("coins_5000_life", "Coin Vault",
                "Collect 5,000 coins all-time.",
                CAT_RICHES, "coin", "total_coins", 5000, scope="life"),
    Achievement("coin_tycoon", "Coin Tycoon",
                "Collect 25,000 coins all-time.",
                CAT_RICHES, "coin", "total_coins", 25000, scope="life"),
    Achievement("midas", "Midas Touch",
                "Collect 100,000 coins all-time.",
                CAT_RICHES, "coin", "total_coins", 100000, scope="life"),

    # ── Power Player ──────────────────────────────────────────────────────
    Achievement("first_powerup", "Power Up!",
                "Grab your first power-up.",
                CAT_POWERUPS, "powerup", "distinct_powerups", 1),
    Achievement("powerup_sampler", "Buffet",
                "Use 4 different power-ups in a single run.",
                CAT_POWERUPS, "powerup", "distinct_powerups", 4),
    Achievement("magnet_life", "Animal Magnetism",
                "Trigger the magnet 15 times all-time.",
                CAT_POWERUPS, "magnet", "magnet_life", 15, scope="life"),
    Achievement("powerup_collector", "Gotta Grab 'Em All",
                "Discover 10 different power-ups all-time.",
                CAT_POWERUPS, "powerup", "distinct_powerups", 10, scope="life"),
    Achievement("greasy_fingers", "Finger Lickin'",
                "Go into KFC mode.",
                CAT_POWERUPS, "kfc", "pu:kfc", 1),
    Achievement("power_hungry", "Power Hungry",
                "Collect 100 power-ups all-time.",
                CAT_POWERUPS, "powerup", "total_powerups", 100, scope="life"),
    Achievement("power_addict", "Power Addict",
                "Collect 500 power-ups all-time.",
                CAT_POWERUPS, "powerup", "total_powerups", 500, scope="life"),

    # ── Stormchaser ───────────────────────────────────────────────────────
    Achievement("near_miss_5", "Close Shave",
                "Squeak past 5 pillars in one run.",
                CAT_STORM, "nerve", "near_misses", 5),
    Achievement("near_miss_15", "Threadneedle",
                "Squeak past 15 pillars in one run.",
                CAT_STORM, "nerve", "near_misses", 15),
    Achievement("marathon", "Long Haul",
                "Stay airborne for two minutes straight.",
                CAT_STORM, "clock", "time_alive", 120),
    Achievement("storm_rider", "Storm Rider",
                "Fly into the rain.",
                CAT_STORM, "storm", "pillars_passed", RAIN_START_PILLAR),
    Achievement("snowbird", "Snowbird",
                "Reach the snow squall.",
                CAT_STORM, "storm", "pillars_passed", SNOW_START_PILLAR),
    Achievement("flap_life", "Tireless Wings",
                "Flap 5,000 times all-time.",
                CAT_STORM, "wing", "total_flaps", 5000, scope="life"),
    Achievement("headbanger", "Headbanger",
                "Bonk the ceiling 10 times in one run.",
                CAT_STORM, "ceiling", "ceiling_hits", 10),
    Achievement("hard_head", "Hard Head",
                "Bonk the ceiling 200 times all-time.",
                CAT_STORM, "ceiling", "total_ceiling", 200, scope="life"),
    Achievement("iron_wings", "Iron Wings",
                "Flap 50,000 times all-time.",
                CAT_STORM, "wing", "total_flaps", 50000, scope="life"),

    # ── Skater ────────────────────────────────────────────────────────────
    Achievement("board_meeting", "Board Meeting",
                "Catch a skateboard.",
                CAT_SKATER, "skate", "pu:skateboard", 1),
    Achievement("sponsored", "Sponsored",
                "Catch 10 skateboards all-time.",
                CAT_SKATER, "skate", "puseen:skateboard", 10, scope="life"),
    Achievement("going_pro", "Going Pro",
                "Catch 50 skateboards all-time.",
                CAT_SKATER, "skate", "puseen:skateboard", 50, scope="life"),
    Achievement("full_combo", "Full Combo",
                "Land all four trick types in one run.",
                CAT_SKATER, "skate", "trick_types", 4),
    Achievement("trickster", "Trickster",
                "Land 50 skateboard tricks all-time.",
                CAT_SKATER, "skate", "total_tricks", 50, scope="life"),
    Achievement("trick_legend", "Trick Legend",
                "Land 500 skateboard tricks all-time.",
                CAT_SKATER, "skate", "total_tricks", 500, scope="life"),
    Achievement("grinder", "Grinder",
                "Ride the rail cart 10 times all-time.",
                CAT_SKATER, "rail", "puseen:rail", 10, scope="life"),
    Achievement("rail_baron", "Rail Baron",
                "Ride the rail cart 50 times all-time.",
                CAT_SKATER, "rail", "puseen:rail", 50, scope="life"),

    # ── Mysteries (hidden) ────────────────────────────────────────────────
    Achievement("made_a_wish", "Three Wishes",
                "Summon the genie and make a wish.",
                CAT_SECRET, "genie", "pu:genie", 1, hidden=True),
    Achievement("knighted", "Knighted",
                "Survive a fatal hit under a knight's guard.",
                CAT_SECRET, "knight", "pu:knight", 1, hidden=True),
    Achievement("treasure_hunter", "X Marks the Spot",
                "Crack open a cycle-finale treasure chest.",
                CAT_SECRET, "treasure", "pu:treasure", 1, hidden=True),
    Achievement("jackpot", "Jackpot!",
                "Hit the lottery's top tier.",
                CAT_SECRET, "lottery", "lottery_jackpot", 1, hidden=True),
    Achievement("rail_rider", "Off the Rails",
                "Ride the rail cart.",
                CAT_SECRET, "rail", "pu:rail", 1, hidden=True),
    Achievement("poisoned", "Be Careful What You Wish For",
                "Discover the genie's nastier surprise.",
                CAT_SECRET, "poison", "pu:poison", 1, hidden=True),
)

# Derived lookups, built once.
BY_ID: dict[str, Achievement] = {a.id: a for a in ACHIEVEMENTS}

BY_CAT: "OrderedDict[str, list[Achievement]]" = OrderedDict(
    (cat, [a for a in ACHIEVEMENTS if a.category == cat])
    for cat in CATEGORY_ORDER
)


# ── Persistence ───────────────────────────────────────────────────────────────

def _blank() -> dict:
    """A fresh, fully-formed save blob."""
    return {
        "v": _SCHEMA_V,
        "unlocked": {},                 # id -> unlock unix timestamp
        "life": {
            "total_runs": 0,
            "total_coins": 0,
            "total_pillars": 0,
            "total_flaps": 0,
            "total_time": 0,
            "best_cycles": 0,
            "total_tricks": 0,          # skateboard tricks landed, all-time
            "total_ceiling": 0,         # ceiling bonks, all-time
            "powerups_seen": {},        # kind -> lifetime pickup count
        },
    }


def _migrate(store: dict) -> dict:
    """Back-fill any keys a newer build expects onto an older save. Additive
    only — never drops a player's unlocked ids."""
    if not isinstance(store, dict):
        return _blank()
    base = _blank()
    out = {
        "v": _SCHEMA_V,
        "unlocked": dict(store.get("unlocked") or {}),
        "life": {**base["life"], **(store.get("life") or {})},
    }
    seen = out["life"].get("powerups_seen")
    if not isinstance(seen, dict):
        out["life"]["powerups_seen"] = {}
    return out


# Native local-JSON (mirrors leaderboard._load_local / _save_local).

def _load_native() -> dict:
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            doc = json.load(f)
        return _migrate(doc.get(_ACH_KEY))
    except Exception:
        return _blank()


def _save_native(store: dict) -> None:
    try:
        doc = {}
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                doc = json.load(f) or {}
        except Exception:
            doc = {}
        if not isinstance(doc, dict):
            doc = {}
        doc[_ACH_KEY] = store
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(doc, f)
    except Exception:
        pass


# Browser localStorage via window.__sk (probed like leaderboard._resolve).

def _web_dispatcher():
    try:
        import platform as _p  # type: ignore
        win = getattr(_p, "window", None)
        return getattr(win, "__sk", None) if win is not None else None
    except Exception:
        return None


def _load_web() -> dict:
    try:
        sk = _web_dispatcher()
        if sk is None:
            return _blank()
        raw = sk("ach_load", _WEB_KEY)
        if not raw:
            return _blank()
        return _migrate(json.loads(str(raw)))
    except Exception:
        return _blank()


def _save_web(store: dict) -> None:
    try:
        sk = _web_dispatcher()
        if sk is None:
            return
        sk("ach_save", json.dumps(store, separators=(",", ":")), _WEB_KEY)
    except Exception:
        pass


# Module-level cached store so the screen + engine share one in-memory copy.
_store: "dict | None" = None


def load() -> dict:
    """Return the (cached) save blob, loading from disk/localStorage once."""
    global _store
    if _store is None:
        _store = _load_web() if _IS_BROWSER else _load_native()
    return _store


def save(store: "dict | None" = None) -> None:
    """Persist the store (defaults to the cached one)."""
    global _store
    if store is not None:
        _store = store
    if _store is None:
        return
    if _IS_BROWSER:
        _save_web(_store)
    else:
        _save_native(_store)


def reset_cache() -> None:
    """Drop the in-memory copy (tests / forced reload)."""
    global _store
    _store = None


# ── Stat resolvers ────────────────────────────────────────────────────────────

def _has_jackpot(world) -> bool:
    """Scan the proof ledger for a lottery event that landed the top tier."""
    proof = getattr(world, "_proof", None)
    if proof is None:
        return False
    try:
        for (_t, dscore, kind) in proof.events_tuple():
            if kind == "lottery" and int(dscore) >= _JACKPOT_DELTA:
                return True
    except Exception:
        return False
    return False


def _run_value(world, ach: Achievement) -> int:
    """Current value of a run-scope achievement's stat for this finished run."""
    s = ach.stat
    pp = getattr(world, "powerups_picked", {}) or {}
    if s == "distinct_powerups":
        return sum(1 for v in pp.values() if v > 0)
    if s == "lottery_jackpot":
        return 1 if _has_jackpot(world) else 0
    if s == "trick_types":
        return len(getattr(world, "tricks_landed_types", ()) or ())
    if s.startswith("pu:"):
        return int(pp.get(s[3:], 0) or 0)
    return int(getattr(world, s, 0) or 0)


def _life_value(store: dict, ach: Achievement) -> int:
    """Current value of a life-scope achievement's stat from the save blob."""
    life = store.get("life", {}) or {}
    seen = life.get("powerups_seen", {}) or {}
    s = ach.stat
    if s == "distinct_powerups":
        return sum(1 for v in seen.values() if v > 0)
    if s == "magnet_life":
        return int(seen.get("magnet", 0) or 0) + int(seen.get("megamagnet", 0) or 0)
    if s == "total_powerups":
        return sum(int(v or 0) for v in seen.values())
    if s.startswith("puseen:"):
        return int(seen.get(s[7:], 0) or 0)
    return int(life.get(s, 0) or 0)


def current_value(store: dict, ach: Achievement) -> "int | None":
    """Value to show on a locked progress bar. Only life-scope achievements
    expose live progress (per-run bests aren't persisted); run-scope returns
    ``None`` so the screen omits the bar."""
    if ach.scope == "life":
        return _life_value(store, ach)
    return None


# ── End-of-run engine ─────────────────────────────────────────────────────────

def _accumulate(store: dict, world) -> None:
    """Fold the just-finished run into the persistent lifetime counters."""
    life = store["life"]
    life["total_runs"] = int(life.get("total_runs", 0)) + 1
    life["total_coins"] = int(life.get("total_coins", 0)) + int(getattr(world, "coin_count", 0) or 0)
    life["total_pillars"] = int(life.get("total_pillars", 0)) + int(getattr(world, "pillars_passed", 0) or 0)
    life["total_flaps"] = int(life.get("total_flaps", 0)) + int(getattr(world, "flap_count", 0) or 0)
    life["total_time"] = int(life.get("total_time", 0)) + int(getattr(world, "time_alive", 0) or 0)
    life["best_cycles"] = max(int(life.get("best_cycles", 0)),
                              int(getattr(world, "cycles_completed", 0) or 0))
    life["total_tricks"] = int(life.get("total_tricks", 0)) + int(getattr(world, "tricks_landed", 0) or 0)
    life["total_ceiling"] = int(life.get("total_ceiling", 0)) + int(getattr(world, "ceiling_hits", 0) or 0)
    seen = life.setdefault("powerups_seen", {})
    for kind, n in (getattr(world, "powerups_picked", {}) or {}).items():
        if n:
            seen[kind] = int(seen.get(kind, 0)) + int(n)


def evaluate_run(world, store: "dict | None" = None) -> list[str]:
    """Evaluate the whole roster against a finished run. Accumulates lifetime
    counters, unlocks any newly-earned achievements, persists once, and returns
    the list of newly-unlocked ids (in roster order) for the unlock toast."""
    if store is None:
        store = load()
    _accumulate(store, world)

    unlocked = store["unlocked"]
    now = int(time.time())
    newly: list[str] = []
    for ach in ACHIEVEMENTS:
        if ach.id in unlocked:
            continue
        value = _run_value(world, ach) if ach.scope == "run" else _life_value(store, ach)
        if value >= ach.target:
            unlocked[ach.id] = now
            newly.append(ach.id)

    save(store)
    return newly


# ── Read helpers for the screen ───────────────────────────────────────────────

def is_unlocked(store: dict, ach_id: str) -> bool:
    return ach_id in (store.get("unlocked") or {})


def unlocked_count() -> int:
    store = load()
    return len(store.get("unlocked") or {})


def category_progress(store: dict, category: str) -> "tuple[int, int]":
    """(unlocked, total) for a category's section header."""
    items = BY_CAT.get(category, [])
    got = sum(1 for a in items if is_unlocked(store, a.id))
    return got, len(items)


def unlocked_signature(store: dict) -> tuple:
    """Stable key for the screen's render cache — changes only when the set of
    unlocked ids changes."""
    return tuple(sorted((store.get("unlocked") or {}).keys()))
