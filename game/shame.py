"""Wall of Shame — anti-achievement badge registry + saddled titles.

Pure data + predicates over store_data.all_stats(); no drawing here. Every
badge roasts the *play*, never the player, and each trigger is out-grindable —
a goal to escape, not a sentence. The Profile's SHAME section calls
earned()/locked() to render the tarnished grid and current_title() for the
demeaning title under the player name. Roast copy is generated per-player so the
real numbers land.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Badge:
    id: str
    name: str
    tier: str                       # parody rank: "bronze" | "silver" | "gold"
    earned: Callable[[dict], bool]
    roast: Callable[[dict], str]
    progress: Callable[[dict], tuple]   # (current, target) for the locked bar


def _sum_powerup_deaths(s: dict) -> int:
    return sum(int(v) for v in (s.get("deaths_with_powerup") or {}).values())


def _ghost_deaths(s: dict) -> int:
    return int((s.get("deaths_with_powerup") or {}).get("ghost", 0))


def _kfc_deaths(s: dict) -> int:
    return int((s.get("deaths_with_powerup") or {}).get("kfc", 0))


def _hist_at(s: dict, idx: int) -> int:
    h = s.get("death_pillar_histogram") or []
    return int(h[idx]) if 0 <= idx < len(h) else 0


# Ordered roughly bronze→gold so the grid reads as a tarnished medal wall.
BADGES: "list[Badge]" = [
    Badge(
        "goose_egg", "The Goose Egg", "bronze",
        lambda s: int(s.get("scoreless_deaths", 0)) >= 1,
        lambda s: f"{int(s.get('scoreless_deaths', 0))} flights. Zero points. "
                  f"A flawless record of absolutely nothing.",
        lambda s: (int(s.get("scoreless_deaths", 0)), 1),
    ),
    Badge(
        "icarus", "The Icarus Award", "bronze",
        lambda s: int(s.get("pillar1_deaths", 0)) >= 1,
        lambda s: "Flew too close to the sun. The sun was 4 seconds away. "
                  f"(Pillar-1 deaths: {int(s.get('pillar1_deaths', 0))}.)",
        lambda s: (int(s.get("pillar1_deaths", 0)), 1),
    ),
    Badge(
        "hummingbird", "The Hummingbird", "bronze",
        lambda s: int(s.get("max_flaps_per_sec", 0)) >= 10,
        lambda s: f"{int(s.get('max_flaps_per_sec', 0))} flaps in one second. "
                  f"The bird is fine. You are not.",
        lambda s: (int(s.get("max_flaps_per_sec", 0)), 10),
    ),
    Badge(
        "early_checkout", "Early Checkout", "bronze",
        lambda s: int(s.get("sub3s_deaths", 0)) >= 10,
        lambda s: f"{int(s.get('sub3s_deaths', 0))} runs ended before the music "
                  f"finished loading. A new personal pace.",
        lambda s: (int(s.get("sub3s_deaths", 0)), 10),
    ),
    Badge(
        "denial", "Denial", "silver",
        lambda s: _sum_powerup_deaths(s) >= 1,
        lambda s: "Died holding a power-up. It came to help. You flew into a "
                  "wall instead. That takes effort.",
        lambda s: (_sum_powerup_deaths(s), 1),
    ),
    Badge(
        "habit", "Creature of Habit", "silver",
        lambda s: int(s.get("same_pillar_streak", 0)) >= 3,
        lambda s: f"Pillar {int(s.get('last_death_pillar', 0))} again. It's not "
                  f"the pillar. We both know it's not the pillar.",
        lambda s: (int(s.get("same_pillar_streak", 0)), 3),
    ),
    Badge(
        "kfc_incident", "The KFC Incident", "silver",
        lambda s: _kfc_deaths(s) >= 1,
        lambda s: "Died as a flying fry, in front of a KFC-branded pillar. "
                  "Finger lickin' fatal.",
        lambda s: (_kfc_deaths(s), 1),
    ),
    Badge(
        "scrooge", "The Scrooge", "silver",
        lambda s: int(s.get("coins_ignored", 0)) >= 1000,
        lambda s: f"You have flown past {int(s.get('coins_ignored', 0)):,} coins. "
                  f"They're still out there. Waiting. Judging.",
        lambda s: (int(s.get("coins_ignored", 0)), 1000),
    ),
    Badge(
        "the_49er", "The 49er", "gold",
        lambda s: _hist_at(s, 49) >= 1,
        lambda s: "Died on pillar 49, one short of the genie. The genie was "
                  "RIGHT THERE. It saw the whole thing.",
        lambda s: (_hist_at(s, 49), 1),
    ),
    Badge(
        "ghost_wall", "Ghost Who Hit a Wall", "gold",
        lambda s: _ghost_deaths(s) >= 1,
        lambda s: "You died phasing-immune. You flew around the hole and into "
                  "the wall. A genuine achievement.",
        lambda s: (_ghost_deaths(s), 1),
    ),
    Badge(
        "frequent_flyer", "Frequent Flyer (One-Way)", "gold",
        lambda s: int(s.get("runs_played", 0)) >= 100,
        lambda s: f"{int(s.get('runs_played', 0))} departures. "
                  f"{int(s.get('runs_played', 0))} crashes. A perfect record.",
        lambda s: (int(s.get("runs_played", 0)), 100),
    ),
]

_BADGES_BY_ID = {b.id: b for b in BADGES}


def badge(badge_id: str) -> "Badge | None":
    return _BADGES_BY_ID.get(badge_id)


def earned(stats: dict) -> "list[Badge]":
    return [b for b in BADGES if b.earned(stats)]


def locked(stats: dict) -> "list[Badge]":
    return [b for b in BADGES if not b.earned(stats)]


# Saddled titles, most-specific first: the player wears the rarest shame they
# qualify for, so the title varies and the generic "you crashed a lot" only
# shows when nothing more interesting applies. Neutral default never shames a
# newcomer for being new.
_TITLE_RULES: "list[tuple[str, Callable[[dict], bool]]]" = [
    ("Ghost Who Hit a Wall", lambda s: _ghost_deaths(s) >= 1),
    ("Honorary Fry",         lambda s: int((s.get("powerups_by_kind") or {}).get("kfc", 0)) >= 5),
    ("Master of Nothing",    lambda s: int(s.get("scoreless_deaths", 0)) >= 3),
    ("Generous to Pillars",  lambda s: int(s.get("pillar1_deaths", 0)) >= 10),
    ("Professional Faller",  lambda s: int(s.get("sub3s_deaths", 0)) >= 10),
    ("Coin-Blind",           lambda s: int(s.get("coins_ignored", 0)) >= 1000),
    ("Wall Inspector",       lambda s: int(s.get("runs_played", 0)) >= 20),
]

DEFAULT_TITLE = "Fledgling Flyer"


def current_title(stats: dict) -> str:
    """The demeaning title shown under the player name — the rarest shame they
    qualify for, or a neutral default for a player who hasn't earned one."""
    for title, qualifies in _TITLE_RULES:
        if qualifies(stats):
            return title
    return DEFAULT_TITLE
