"""Persistent wallet + inventory for the coin Store.

Native play:  reads/writes a local JSON file (STORE_FILE from config).
Browser (emscripten): delegates to the closure-private ``window.__sk``
              dispatcher injected by inject_theme.py, using the synchronous
              ``store_load`` / ``store_save`` actions (localStorage is
              synchronous, so unlike the leaderboard fetch there is no
              ``*_done`` poll loop).

Cosmetics are device-local and carry no competitive weight, so — unlike
the leaderboard — the wallet is client-trusted on both targets and needs
no proof bundle or plausibility gate.

State is cached in a module-level dict and written through on every
mutation, so the hot path (rendering the store, banking coins at death)
never blocks on a per-call file/bridge round-trip beyond the initial load.
"""
from __future__ import annotations

import sys
import json
import time
import random

from game.config import STORE_FILE
from game import store_catalog

_IS_BROWSER = sys.platform == "emscripten"

_VERSION = 1

# Equip slots map one-to-one onto the cosmetic ``kind``s that can be worn.
# Boosts are consumables, not equippable, so they have no slot here.
_EQUIP_SLOTS = ("skin", "pillar", "ground", "trail", "parcel")

_STATE: "dict | None" = None  # lazy: populated on first load()


# Death-pillar histogram is capped so a marathon run can't grow the save file
# without bound; the final bucket reads as "that pillar or beyond".
_HIST_CAP = 200


def _default_stats() -> dict:
    """Persistent Profile stats — lifetime totals, personal bests, the
    death-context counters the Stats / Hall of Shame sections read, and the
    container state the Arcade curios persist into. All start empty; record_run
    folds each finished run in. Kept under one key so the wallet/equip paths
    never have to know these exist."""
    return {
        # lifetime totals
        "runs_played": 0,
        "total_time_s": 0.0,
        "total_pillars": 0,
        "total_coins_earned": 0,
        "total_flaps": 0,
        "total_near_misses": 0,
        "total_powerups": 0,
        "powerups_by_kind": {},
        "coins_ignored": 0,
        # personal bests (best single run, not lifetime sums)
        "best_score": 0,
        "best_pillars": 0,
        "best_time_s": 0.0,
        "best_near_misses": 0,
        # death context — what your crashes look like
        "scoreless_deaths": 0,
        "pillar1_deaths": 0,
        "sub3s_deaths": 0,
        "deaths_with_powerup": {},
        "last_death_pillar": -1,
        "same_pillar_streak": 0,
        "death_pillar_histogram": [],
        "max_flaps_per_sec": 0,
        # "days since last dignified flight" board
        "last_dignified_date": "",
        "dignified_record_gap": 0,
        # interactive-section state (owned by shame.py / arcade.py)
        "equipped_title": "",
        "unlocked_shame": {},
        "junk_drawer": [],
        "wisdom_scroll": [],
        "prophecy": {},
        "crystal_last_session": "",
    }


def _default_state() -> dict:
    return {
        "version": _VERSION,
        "wallet": 0,
        "owned": [],
        "equipped_skin": store_catalog.BASE_SKIN,
        "equipped_pillar": None,
        "equipped_ground": None,
        "equipped_trail": None,
        "equipped_parcel": store_catalog.PARCEL_BASE,
        "last_daily": "",
        # skin_id -> design index, for skins whose look is a random 1-of-N
        # pick locked at unlock (e.g. the secret jet fighter).
        "skin_variants": {},
        "stats": _default_stats(),
    }


def _coerce(raw: "dict | None") -> dict:
    """Merge a loaded dict onto fresh defaults so a state written by an
    older build (missing keys) or a partially-corrupt file degrades to
    sane values rather than KeyError-ing the store open."""
    state = _default_state()
    if isinstance(raw, dict):
        try:
            state["wallet"] = max(0, int(raw.get("wallet", 0)))
        except (TypeError, ValueError):
            pass
        owned = raw.get("owned", [])
        if isinstance(owned, list):
            # Drop ids no longer in the catalog so a renamed item can't
            # leave a dangling entry that looks owned but can't be equipped.
            state["owned"] = [str(i) for i in owned if store_catalog.exists(str(i))]
        for key in ("equipped_skin", "equipped_pillar", "equipped_ground",
                    "equipped_trail", "equipped_parcel"):
            v = raw.get(key)
            if v is None:
                continue
            v = str(v)
            # Guard against a stale equip pointing at a skin removed/renamed in
            # a later build: fall back to the slot default so the store never
            # shows the wrong card as "equipped" while the renderer silently
            # draws the base look. (The base skin / base parcel are always valid.)
            if v not in (store_catalog.BASE_SKIN, store_catalog.PARCEL_BASE) \
                    and not store_catalog.exists(v):
                continue
            state[key] = v
        if isinstance(raw.get("last_daily"), str):
            state["last_daily"] = raw["last_daily"]
        variants = raw.get("skin_variants")
        if isinstance(variants, dict):
            for k, v in variants.items():
                k = str(k)
                if not store_catalog.exists(k):
                    continue  # drop a roll for a renamed/removed skin
                try:
                    state["skin_variants"][k] = int(v)
                except (TypeError, ValueError):
                    pass
        _coerce_stats(state["stats"], raw.get("stats"))
    return state


def _coerce_stats(base: dict, raw: "dict | None") -> None:
    """Merge a loaded stats blob onto fresh defaults in place, copying each
    known key only when the loaded value matches the default's type. Unknown
    keys are dropped and missing keys keep their default, so a save from an
    older build (before a counter existed) upgrades silently."""
    if not isinstance(raw, dict):
        return
    for key, default in base.items():
        if key not in raw:
            continue
        v = raw[key]
        if isinstance(default, bool):
            continue  # no bool stats today; guard against int/bool confusion
        if isinstance(default, float):
            try:
                base[key] = float(v)
            except (TypeError, ValueError):
                pass
        elif isinstance(default, int):
            try:
                base[key] = int(v)
            except (TypeError, ValueError):
                pass
        elif isinstance(default, str):
            if isinstance(v, str):
                base[key] = v
        elif isinstance(default, list):
            if isinstance(v, list):
                base[key] = v
        elif isinstance(default, dict):
            if isinstance(v, dict):
                base[key] = dict(v)


# ── Native local-JSON helpers (mirror leaderboard._load_local/_save_local) ────

def _load_native() -> dict:
    try:
        with open(STORE_FILE, "r", encoding="utf-8") as f:
            return _coerce(json.load(f))
    except Exception:
        return _default_state()


def _save_native(state: dict) -> None:
    try:
        with open(STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except Exception:
        pass


# ── Browser bridge helpers ────────────────────────────────────────────────────

def _bridge():
    """Return a callable ``window.__sk`` if the JS bridge has booted, else
    None. Same getattr-based probe as leaderboard._resolve — never raises."""
    try:
        import platform as _pgb  # type: ignore
        win = getattr(_pgb, "window", None)
        if win is None:
            return None
        return getattr(win, "__sk", None)
    except Exception:
        return None


def _load_web() -> dict:
    sk = _bridge()
    if sk is None:
        return _default_state()
    try:
        raw = sk("store_load")
        if not raw:
            return _default_state()
        return _coerce(json.loads(str(raw)))
    except Exception:
        return _default_state()


def _save_web(state: dict) -> None:
    sk = _bridge()
    if sk is None:
        return  # bridge not ready: keep the in-memory wallet, retry next save
    try:
        sk("store_save", json.dumps(state, separators=(",", ":")))
    except Exception:
        pass


# ── Public API ────────────────────────────────────────────────────────────────

def load() -> None:
    """Populate the module cache. Idempotent — repeated calls are no-ops
    once loaded so callers can ``load()`` defensively before any read."""
    global _STATE
    if _STATE is not None:
        return
    _STATE = _load_web() if _IS_BROWSER else _load_native()


def save() -> None:
    if _STATE is None:
        return
    if _IS_BROWSER:
        _save_web(_STATE)
    else:
        _save_native(_STATE)


def _ensure() -> dict:
    if _STATE is None:
        load()
    return _STATE  # type: ignore[return-value]


def balance() -> int:
    return int(_ensure()["wallet"])


def add_coins(n: int) -> None:
    """Bank coins earned in a run. Negative/zero is ignored so a stray call
    can't drain the wallet — spending goes through try_spend/try_purchase."""
    n = int(n)
    if n <= 0:
        return
    st = _ensure()
    st["wallet"] = int(st["wallet"]) + n
    save()


# ── Profile stats ─────────────────────────────────────────────────────────────

def all_stats() -> dict:
    """The live persistent-stats dict (see _default_stats). Callers read it for
    the Profile's Stats / Shame / Arcade sections; mutate only through the
    helpers below so every change is written through."""
    st = _ensure()
    if not isinstance(st.get("stats"), dict):
        st["stats"] = _default_stats()
    return st["stats"]


def _days_between(d1: str, d2: str) -> int:
    """Whole calendar days between two ISO dates, or 0 if either is unparseable
    — never raises, so a corrupt date can't break the run record."""
    try:
        from datetime import date
        return abs((date.fromisoformat(d2) - date.fromisoformat(d1)).days)
    except Exception:
        return 0


def record_run(world) -> None:
    """Fold one finished run into the persistent Profile stats: lifetime totals,
    personal bests, and the death-context counters the Stats / Hall of Shame /
    Arcade sections read. Called once per run from scenes._on_death, right after
    the wallet is credited. Never raises into the game loop — a stats glitch
    must not cost the player their run-end flow."""
    try:
        s = all_stats()
        score = int(getattr(world, "score", 0))
        pillars = int(getattr(world, "pillars_passed", 0))
        t_alive = float(getattr(world, "time_alive", 0.0))
        coins = int(getattr(world, "coin_count", 0))
        spawned = int(getattr(world, "coins_spawned", 0))
        flaps = int(getattr(world, "flap_count", 0))
        nmiss = int(getattr(world, "near_misses", 0))
        picked = dict(getattr(world, "powerups_picked", {}) or {})

        s["runs_played"] = int(s["runs_played"]) + 1
        s["total_time_s"] = float(s["total_time_s"]) + t_alive
        s["total_pillars"] = int(s["total_pillars"]) + pillars
        s["total_coins_earned"] = int(s["total_coins_earned"]) + coins
        s["total_flaps"] = int(s["total_flaps"]) + flaps
        s["total_near_misses"] = int(s["total_near_misses"]) + nmiss
        s["total_powerups"] = int(s["total_powerups"]) + sum(
            int(v) for v in picked.values())
        for k, v in picked.items():
            s["powerups_by_kind"][k] = int(s["powerups_by_kind"].get(k, 0)) + int(v)
        s["coins_ignored"] = int(s["coins_ignored"]) + max(0, spawned - coins)

        s["best_score"] = max(int(s["best_score"]), score)
        s["best_pillars"] = max(int(s["best_pillars"]), pillars)
        s["best_time_s"] = max(float(s["best_time_s"]), t_alive)
        s["best_near_misses"] = max(int(s["best_near_misses"]), nmiss)

        if score == 0:
            s["scoreless_deaths"] = int(s["scoreless_deaths"]) + 1
        if pillars == 0:
            s["pillar1_deaths"] = int(s["pillar1_deaths"]) + 1
        if t_alive < 3.0:
            s["sub3s_deaths"] = int(s["sub3s_deaths"]) + 1
        for kind in (getattr(world, "death_powerups", []) or []):
            s["deaths_with_powerup"][kind] = int(
                s["deaths_with_powerup"].get(kind, 0)) + 1

        if pillars == int(s["last_death_pillar"]):
            s["same_pillar_streak"] = int(s["same_pillar_streak"]) + 1
        else:
            s["same_pillar_streak"] = 1
        s["last_death_pillar"] = pillars

        hist = s["death_pillar_histogram"]
        if not isinstance(hist, list):
            hist, s["death_pillar_histogram"] = [], []
            hist = s["death_pillar_histogram"]
        idx = min(pillars, _HIST_CAP)
        while len(hist) <= idx:
            hist.append(0)
        hist[idx] = int(hist[idx]) + 1

        s["max_flaps_per_sec"] = max(int(s["max_flaps_per_sec"]),
                                     int(getattr(world, "max_flaps_per_sec", 0)))

        # A "dignified" run is simply one that wasn't an instant, scoreless, or
        # pillar-one washout; the safety board counts days since the last one.
        if not (score == 0 or t_alive < 3.0 or pillars == 0):
            today = time.strftime("%Y-%m-%d")
            prev = s.get("last_dignified_date") or ""
            if prev:
                s["dignified_record_gap"] = max(
                    int(s["dignified_record_gap"]), _days_between(prev, today))
            s["last_dignified_date"] = today

        save()
    except Exception:
        pass


def is_owned(item_id: str) -> bool:
    if item_id in (store_catalog.BASE_SKIN, store_catalog.PARCEL_BASE):
        return True
    return item_id in _ensure()["owned"]


def owned_ids() -> set:
    return set(_ensure()["owned"])


def skin_variant(item_id: str) -> "int | None":
    """The design index rolled for a random-look skin at unlock, or None if the
    skin has no rolled variant. Read by the art module to render the locked
    look (the same fighter every run)."""
    v = _ensure().get("skin_variants", {}).get(item_id)
    return None if v is None else int(v)


def _roll_skin_variant(st: dict, item_id: str) -> None:
    """If a skin's look is a random 1-of-N pick locked at unlock, roll it once
    and persist the index. The pool size is owned by the art module, lazy-
    imported here so the wallet path stays pygame-free until an actual variant
    skin is unlocked."""
    pools = {
        "skin_jet_fighter": lambda: __import__(
            "game.animal_jet_fighter", fromlist=["POOL_SIZE"]).POOL_SIZE,
    }
    get_n = pools.get(item_id)
    if get_n is None:
        return
    try:
        st.setdefault("skin_variants", {})[item_id] = random.randrange(int(get_n()))
    except Exception:
        pass


def _slot_key(slot: str) -> str:
    return "equipped_skin" if slot == "skin" else "equipped_" + slot


def equipped(slot: str) -> "str | None":
    """The id worn in ``slot`` (one of _EQUIP_SLOTS). Skin defaults to the
    base parrot; the other slots default to None (= the run's procedural
    default look)."""
    return _ensure().get(_slot_key(slot))


def equip(item_id: str) -> bool:
    """Wear an owned cosmetic. Returns False (no change) if it isn't owned
    or its kind has no equip slot."""
    if not is_owned(item_id):
        return False
    if store_catalog.exists(item_id):
        k = store_catalog.kind(item_id)
    elif item_id == store_catalog.BASE_SKIN:
        k = "skin"
    elif item_id == store_catalog.PARCEL_BASE:
        k = "parcel"
    else:
        k = None
    if k not in _EQUIP_SLOTS:
        return False
    _ensure()[_slot_key(k)] = item_id
    save()
    return True


def try_purchase(item_id: str) -> "tuple[bool, str]":
    """Atomically buy a catalog item: validates it exists and is unowned and
    that the wallet covers the cost, then deducts + records ownership. Returns
    ``(ok, reason)`` where reason ∈ {"", "badid", "owned", "insufficient"}."""
    if not store_catalog.exists(item_id):
        return False, "badid"
    if is_owned(item_id):
        return False, "owned"
    st = _ensure()
    price = store_catalog.cost(item_id)
    if int(st["wallet"]) < price:
        return False, "insufficient"
    st["wallet"] = int(st["wallet"]) - price
    st["owned"].append(item_id)
    _roll_skin_variant(st, item_id)
    save()
    return True, ""


def try_spend(n: int) -> bool:
    """Deduct a raw coin amount (e.g. a Prize Machine roll) if affordable.
    Records no ownership — the caller decides what the spend buys."""
    n = int(n)
    st = _ensure()
    if n <= 0 or int(st["wallet"]) < n:
        return False
    st["wallet"] = int(st["wallet"]) - n
    save()
    return True


def grant(item_id: str) -> bool:
    """Add an item to the inventory without charging (Prize Machine win,
    daily-reward unlock). No-op if already owned or unknown."""
    if not store_catalog.exists(item_id) or is_owned(item_id):
        return False
    st = _ensure()
    st["owned"].append(item_id)
    _roll_skin_variant(st, item_id)
    save()
    return True


def claim_daily() -> int:
    """Grant the daily coin reward once per calendar day. Returns the amount
    credited (0 if already claimed today)."""
    from game.config import DAILY_REWARD
    today = time.strftime("%Y-%m-%d")
    st = _ensure()
    if st.get("last_daily") == today:
        return 0
    st["last_daily"] = today
    st["wallet"] = int(st["wallet"]) + int(DAILY_REWARD)
    save()
    return int(DAILY_REWARD)


def daily_available() -> bool:
    return _ensure().get("last_daily") != time.strftime("%Y-%m-%d")


def _reset_for_test() -> None:
    """Drop the cached state so a test can re-load from a freshly
    monkeypatched STORE_FILE. Test-only; not used by the game."""
    global _STATE
    _STATE = None
