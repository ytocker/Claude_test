"""Tests for the secret late-game powerups added on top of v4_skybit.

These cover:
  - Spawn gating: nothing leaks below LATE_GAME_SCORE, everything is
    eligible at/above it (except NIGHTGLOW which is biome-gated).
  - SKATEBOARD collision overrides (ground / ceiling survive, side kills).
  - SHRINK collision radius.
  - LOTTERY tier application with floor-at-zero on losses.
  - TREASURE BOX per-flap coin drop.
  - MEGA MAGNET coin vacuum.
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

from game import _plausibility, biome
from game.config import (
    BIRD_R, SHRINK_SCALE, GROUND_Y, LATE_GAME_SCORE,
    TREASURE_BOX_DURATION, TREASURE_BOX_COINS_PER_FLAP,
    SECRET_POWERUP_WEIGHTS,
)
from game.entities import PowerUp, Coin
from game.world import World


SECRET_KINDS = {k for k, _ in SECRET_POWERUP_WEIGHTS}


def _force_spawn_attempts(world, n, score, biome_phase_t=0.0):
    """Repeatedly run _maybe_spawn_powerup, collecting each spawned kind.
    Returns the set of kinds that appeared.

    Bumps `pipes_spawned` above the v5_powerups TEST_SECRETS_FIRST_N_PILLARS
    window so the production-behavior tests still see the normal spawn pool
    (test mode would otherwise force secrets regardless of score)."""
    world.score = score
    world.biome_time = biome_phase_t
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


def test_secrets_unlocked_at_threshold_day():
    random.seed(123)
    w = World()
    w.ready_t = 0
    seen = _force_spawn_attempts(w, 5000, score=LATE_GAME_SCORE,
                                 biome_phase_t=0.0)  # day
    # Everything except nightglow should appear given 5000 attempts.
    expected = SECRET_KINDS - {"nightglow"}
    missing = expected - seen
    assert not missing, f"expected secrets missing at threshold (day): {missing}"
    # nightglow must NOT leak in day biome.
    assert "nightglow" not in seen, "nightglow leaked during day biome"


def test_nightglow_requires_night():
    random.seed(7)
    w = World()
    w.ready_t = 0
    # Night biome (NIGHT keyframe at phase 0.64375)
    seen = _force_spawn_attempts(w, 5000, score=LATE_GAME_SCORE,
                                 biome_phase_t=biome.CYCLE_SECONDS * 0.64)
    assert "nightglow" in seen, "nightglow should appear at night biome"


def test_shrink_changes_collision_radius():
    w = World()
    w.ready_t = 0
    assert w.bird_radius() == BIRD_R  # baseline
    w._activate_shrink(PowerUp(0, 0, kind="shrink"))
    assert abs(w.bird_radius() - BIRD_R * SHRINK_SCALE) < 1e-6
    assert w.bird.shrink_active is True


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


def test_vacuum_collects_all_coins():
    w = World()
    w.ready_t = 0
    w.coins = [Coin(200, 200), Coin(150, 250), Coin(300, 180)]
    initial_score = w.score
    w._activate_vacuum(PowerUp(0, 0, kind="vacuum"))
    # Tick the update loop enough to consume the travel animation.
    for _ in range(60):
        w.update(1 / 60)
    # All coins collected → score should have increased by at least 3.
    assert w.score - initial_score >= 3



def test_nightglow_sets_state():
    w = World()
    w.ready_t = 0
    w._activate_nightglow(PowerUp(0, 0, kind="nightglow"))
    assert w.nightglow_timer > 0
    assert w.bird.nightglow_active is True


def test_rail_claims_pipes():
    w = World()
    w.ready_t = 0
    w._activate_rail(PowerUp(0, 0, kind="rail"))
    # Either claimed some immediately or queued the rest.
    total = len(w.rail_pipes) + w.rail_pending
    assert total >= 1


def test_plausibility_chain_survives_treasure_box_and_lottery():
    """Chain hash + ledger total must still pass plausibility after a
    score-affecting secret powerup."""
    random.seed(99)
    w = World()
    w.ready_t = 0
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
