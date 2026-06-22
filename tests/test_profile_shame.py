"""Unit tests for the pure Profile logic: derivations (profile_stats) and the
Wall of Shame registry + saddled titles (shame). No pygame, no state mutation.
"""
from game import profile_stats as ps
from game import shame
from game.store_data import _default_stats


def _stats(**kw):
    s = _default_stats()
    s.update(kw)
    return s


# ── profile_stats ─────────────────────────────────────────────────────────────

def test_gerald_needs_threshold():
    assert ps.gerald(_stats(death_pillar_histogram=[])) is None
    assert ps.gerald(_stats(death_pillar_histogram=[0, 2, 1])) is None  # max 2 < 3
    g = ps.gerald(_stats(death_pillar_histogram=[0, 1, 5, 2]))
    assert g == {"pillar": 2, "deaths": 5}


def test_favourite_powerup():
    assert ps.favourite_powerup(_stats()) is None
    assert ps.favourite_powerup(
        _stats(powerups_by_kind={"magnet": 2, "ghost": 5})) == "ghost"


def test_days_since_dignified():
    assert ps.days_since_dignified(_stats()) is None
    s = _stats(last_dignified_date="2026-06-20")
    assert ps.days_since_dignified(s, today="2026-06-22") == 2


def test_fmt_duration():
    assert ps.fmt_duration(42) == "42s"
    assert ps.fmt_duration(125) == "2m 05s"
    assert ps.fmt_duration(3 * 3600 + 14 * 60) == "3h 14m"


# ── shame ─────────────────────────────────────────────────────────────────────

def test_badges_earned_and_roast_fills():
    s = _stats(scoreless_deaths=4, pillar1_deaths=1)
    earned_ids = {b.id for b in shame.earned(s)}
    assert "goose_egg" in earned_ids
    assert "icarus" in earned_ids
    assert "ghost_wall" not in earned_ids
    goose = shame.badge("goose_egg")
    assert "4 flights" in goose.roast(s)
    assert goose.progress(s) == (4, 1)


def test_locked_complement():
    s = _stats(scoreless_deaths=1)
    earned_ids = {b.id for b in shame.earned(s)}
    locked_ids = {b.id for b in shame.locked(s)}
    assert earned_ids.isdisjoint(locked_ids)
    assert earned_ids | locked_ids == {b.id for b in shame.BADGES}


def test_the_49er_reads_histogram():
    hist = [0] * 60
    hist[49] = 1
    assert shame.badge("the_49er").earned(_stats(death_pillar_histogram=hist))


def test_title_picks_rarest_first():
    # A grinder who also wasted a Ghost wears the specific shame, not "Wall
    # Inspector", even though both qualify.
    s = _stats(runs_played=300, deaths_with_powerup={"ghost": 1})
    assert shame.current_title(s) == "Ghost Who Hit a Wall"
    # Only the generic threshold met → the flagship fallback.
    assert shame.current_title(_stats(runs_played=50)) == "Wall Inspector"
    # A newcomer is never shamed.
    assert shame.current_title(_stats(runs_played=2)) == shame.DEFAULT_TITLE
