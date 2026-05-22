"""Tests for the secret late-game powerups added on top of v4_skybit.

These cover:
  - Spawn gating: nothing leaks below LATE_GAME_SCORE, everything is
    eligible at/above it.
  - SKATEBOARD collision overrides (ground / ceiling survive, side kills).
  - LOTTERY tier application with floor-at-zero on losses.
  - TREASURE BOX per-flap coin drop.
  - Plausibility chain stays valid with the new event kinds.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import math
import random
import pygame
import pytest

pygame.init()
pygame.display.set_mode((360, 640))

from game import _plausibility
from game.config import (
    BIRD_R, GROUND_Y, LATE_GAME_SCORE,
    TREASURE_BOX_DURATION, TREASURE_BOX_COINS_PER_FLAP,
    SECRET_POWERUP_WEIGHTS,
)
from game.entities import PowerUp, Coin
from game.world import World


from game.config import POWERUP_WEIGHTS
# Kinds that ONLY live in the secret pool. On v5_powerups, genie is
# in both the regular and secret pools (test mode), so it can leak
# below the late-game threshold legitimately and is excluded from
# the locked-pool assertion.
_regular_kinds = {k for k, _ in POWERUP_WEIGHTS}
SECRET_KINDS = {k for k, _ in SECRET_POWERUP_WEIGHTS} - _regular_kinds


def _force_spawn_attempts(world, n, score):
    """Repeatedly run _maybe_spawn_powerup, collecting each spawned kind.
    Returns the set of kinds that appeared.

    Bumps `pipes_spawned` above the v5_powerups TEST_SECRETS_FIRST_N_PILLARS
    window so the production-behavior tests still see the normal spawn pool
    (test mode would otherwise force secrets regardless of score)."""
    world.score = score
    world.pipes_spawned = 10_000  # bypass v5_powerups forced-secret window
    seen = set()
    for _ in range(n):
        world.powerup_cooldown = 0
        pre = len(world.powerups)
        pipe = world.pipes[0] if world.pipes else None
        if pipe is None:
            break
        world._maybe_spawn_powerup(pipe)
        if len(world.powerups) > pre:
            seen.add(world.powerups[-1].kind)
            world.powerups[-1].collected = True
            world.powerups = []
    return seen


def test_secrets_locked_below_threshold():
    random.seed(42)
    w = World()
    w.ready_t = 0
    seen = _force_spawn_attempts(w, 500, score=LATE_GAME_SCORE - 1)
    leaked = seen & SECRET_KINDS
    assert not leaked, f"secrets leaked below threshold: {leaked}"


def test_secrets_unlocked_at_threshold():
    random.seed(123)
    w = World()
    w.ready_t = 0
    seen = _force_spawn_attempts(w, 5000, score=LATE_GAME_SCORE)
    missing = SECRET_KINDS - seen
    assert not missing, f"expected secrets missing at threshold: {missing}"


def test_skateboard_survives_ground():
    w = World()
    w.ready_t = 0
    w._activate_skateboard(PowerUp(0, 0, kind="skateboard"))
    w.bird.y = GROUND_Y + 50
    w.bird.vy = 200
    w._check_collisions()
    assert w.game_over is False, "skateboard should absorb ground death"
    assert w.bird.y <= GROUND_Y - w.bird_radius() + 0.01


def test_skateboard_helmet_survives_ceiling_pillar():
    w = World()
    w.ready_t = 0
    w._activate_skateboard(PowerUp(0, 0, kind="skateboard"))
    # Manually craft a pipe whose ceiling spike sits just below the bird.
    if not w.pipes:
        pytest.skip("World seeded no pipes")
    p = w.pipes[0]
    p.x = w.bird.x - 10  # bird is within the column
    p.gap_y = w.bird.y + 60  # gap centre well below bird
    p.gap_h = 100
    # Position bird so its head (by - br) just touches gap_top.
    gap_top = p.gap_y - p.gap_h / 2
    w.bird.y = gap_top + w.bird_radius() - 2  # slightly overlapping from below
    w.bird.vy = -50  # rising into the spike
    w._check_collisions()
    assert w.game_over is False, "helmet should deflect ceiling-pillar bonk"


def test_skateboard_side_still_lethal():
    w = World()
    w.ready_t = 0
    w._activate_skateboard(PowerUp(0, 0, kind="skateboard"))
    if not w.pipes:
        pytest.skip("World seeded no pipes")
    p = w.pipes[0]
    p.x = w.bird.x - 5
    p.gap_y = w.bird.y + 200  # far below bird so the upper pillar is huge
    p.gap_h = 50
    # Bird at the same height as the upper pillar's body (side collision).
    # Move bird up to a y where the upper pillar's solid body is at bird.y.
    w.bird.y = 50  # well above the gap
    w.bird.vy = 0
    w._check_collisions()
    assert w.game_over is True, "side hit should still kill during skateboard"


def test_backflip_triggers_on_3_taps_within_window():
    from game.config import BACKFLIP_DURATION
    w = World()
    w.ready_t = 0
    w._activate_skateboard(PowerUp(0, 0, kind="skateboard"))
    assert w.bird.backflip_t == 0
    w.flap(); w.flap(); w.flap()
    assert w.bird.backflip_t == BACKFLIP_DURATION


def test_backflip_does_not_trigger_without_skateboard():
    w = World()
    w.ready_t = 0
    assert w.skateboard_timer == 0
    w.flap(); w.flap(); w.flap()
    assert w.bird.backflip_t == 0


def test_backflip_does_not_chain_while_active():
    from game.config import BACKFLIP_DURATION
    w = World()
    w.ready_t = 0
    w._activate_skateboard(PowerUp(0, 0, kind="skateboard"))
    w.flap(); w.flap(); w.flap()
    assert w.bird.backflip_t == BACKFLIP_DURATION
    # 3 more taps mid-flip must NOT reset the timer to full duration.
    w.bird.backflip_t = BACKFLIP_DURATION / 2
    w.flap(); w.flap(); w.flap()
    assert w.bird.backflip_t == BACKFLIP_DURATION / 2


def test_backflip_window_resets_streak_on_slow_taps():
    from game.config import BACKFLIP_TAP_WINDOW
    w = World()
    w.ready_t = 0
    w._activate_skateboard(PowerUp(0, 0, kind="skateboard"))
    # First two taps land in the window.
    w.flap(); w.flap()
    assert w._tap_streak == 2
    # Advance the world clock past the window so the next tap restarts
    # the streak rather than completing it.
    w._idle_t += BACKFLIP_TAP_WINDOW + 0.1
    w.flap()
    assert w._tap_streak == 1
    assert w.bird.backflip_t == 0


def test_backflip_rotates_tilt_360():
    from game.config import BACKFLIP_DURATION
    w = World()
    w.ready_t = 0
    w._activate_skateboard(PowerUp(0, 0, kind="skateboard"))
    w.bird.vy = 0
    base = w.bird.tilt_deg
    w.bird.backflip_t = BACKFLIP_DURATION
    w.bird.backflip_dur = BACKFLIP_DURATION
    # At t=0 progress is 0 → tilt matches base.
    assert abs(w.bird.tilt_deg - base) < 1e-3
    # At mid-flip → +180°.
    w.bird.backflip_t = BACKFLIP_DURATION / 2
    assert abs(w.bird.tilt_deg - base - 180) < 1e-3
    # At end → +360° (equivalent to base + 360, full rotation).
    w.bird.backflip_t = 0.001
    assert abs(w.bird.tilt_deg - base - 360) < 5


def test_lottery_bust_capped_at_zero():
    w = World()
    w.ready_t = 0
    w.score = 10
    w.lottery_anim = {
        "t": 0.0, "tier": "BUST", "delta": -50,
        "x": 100, "y": 100, "applied": False,
    }
    w._apply_lottery_result()
    assert w.score == 0, "lottery loss must not push score below zero"


def test_lottery_jackpot_adds_full_amount():
    w = World()
    w.ready_t = 0
    w.score = 500
    w.lottery_anim = {
        "t": 0.0, "tier": "JACKPOT", "delta": 100,
        "x": 100, "y": 100, "applied": False,
    }
    w._apply_lottery_result()
    assert w.score == 600


def test_treasure_box_arms_buff_and_drops_coins_per_flap():
    w = World()
    w.ready_t = 0
    assert w.treasure_box_timer == 0
    w._activate_heist(PowerUp(0, 0, kind="heist"))
    assert w.treasure_box_timer == TREASURE_BOX_DURATION

    initial = w.score
    w.flap()
    assert w.score == initial + TREASURE_BOX_COINS_PER_FLAP

    # Triple buff multiplies the per-flap drop x3.
    from game.config import TRIPLE_DURATION
    w.triple_timer = TRIPLE_DURATION
    pre = w.score
    w.flap()
    assert w.score == pre + TREASURE_BOX_COINS_PER_FLAP * 3

    # Buff expires after TREASURE_BOX_DURATION seconds.
    w.update(TREASURE_BOX_DURATION + 0.1)
    assert w.treasure_box_timer == 0
    no_buff_pre = w.score
    w.flap()
    assert w.score == no_buff_pre  # no drop once the buff has expired


def test_plausibility_chain_survives_treasure_box_and_lottery():
    """Chain hash + ledger total must still pass plausibility after a
    score-affecting secret powerup."""
    random.seed(99)
    w = World()
    w.ready_t = 0
    # v5_powerups test-mode bootstrap pre-fills score / coin_count / ledger
    # with fake values so the storm jolt has coins to lose. Reset all three
    # so this plausibility test runs from a true zero baseline.
    w.score = 0
    w.coin_count = 0
    w._proof = type(w._proof)()
    # Pretend the player picked up a treasure box and flapped a couple
    # of times so the ledger records "treasure_box" event kinds.
    w._activate_heist(PowerUp(0, 0, kind="heist"))
    w.flap()
    w.flap()
    # And lottery winning + losing rolls.
    w.score = 100
    w.lottery_anim = {
        "t": 0.0, "tier": "WIN", "delta": 15,
        "x": 0, "y": 0, "applied": False,
    }
    w._apply_lottery_result()
    w.lottery_anim = {
        "t": 0.0, "tier": "LOSS", "delta": -10,
        "x": 0, "y": 0, "applied": False,
    }
    w._apply_lottery_result()
    # Verify plausibility passes with the new event kinds in the chain.
    _plausibility.check(
        score=w._proof.score(),
        pillars_passed=w.pillars_passed,
        coin_count=w.coin_count,
        time_alive=w.time_alive,
        events=w._proof.events_tuple(),
        chain_hex=w._proof.chain_hex(),
    )


def test_powerup_help_excludes_secrets():
    """Sanity-check that none of the secret kinds leaked into the help
    screen's documented tuple."""
    from game.powerup_help import POWERUPS
    documented_kinds = {k for (k, _label, _desc) in POWERUPS}
    leaked = documented_kinds & SECRET_KINDS
    assert not leaked, f"secrets leaked into help screen: {leaked}"
