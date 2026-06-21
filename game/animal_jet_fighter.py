"""Secret JET FIGHTER skin — a RANDOM one of three fighter designs.

When the player flies the secret jet, the look is rolled at random from three
hand-designed fighters, so it feels like a surprise rather than a fixed skin:

  * STEEL  — gunmetal Steel Raptor (twin delta + twin afterburner)
  * NAVAL  — F-14 "Jolly Rogers" (navy + gold leading-edge rail, twin tails)
  * CHROME — retro polished bare-metal with a single blue spine stripe

All three are drawn NOSE-RIGHT, UPRIGHT, with NO baked rotation. The jet pitches
with the flappy arc on its own: the getter passes the bird's velocity tilt
(`Bird.tilt_deg`) straight through to each design's cached getter, which rotates
the sprite — so the nose pitches UP on a flap/jump and gradually noses DOWN as it
falls, exactly like a real fighter riding the arc.

Each design is its own self-contained module (game/animal_jet_*.py) so their
private helpers and palettes never collide; this module imports their getters and
dispatches `skin_jet_fighter` to one of them. The pick is made once per launch
(re-roll via ``reroll()``), stable across frames in a session. The sub-modules are
imported here directly, so their own `skin_*` ids never register as separate
store items.
"""
import random

from game.animal_jet_steel import get_steel
from game.animal_jet_naval import get_naval
from game.animal_jet_chrome import get_chrome


# The three designs the player can roll (uniform).
_POOL = (get_steel, get_naval, get_chrome)
_chosen = random.choice(_POOL)


def reroll() -> None:
    """Pick a fresh random design. Per-launch by default; call this to re-roll
    (e.g. to vary the look between runs) without touching the store wiring."""
    global _chosen
    _chosen = random.choice(_POOL)


def get_jet_fighter(frame_idx, tilt_deg):
    return _chosen(frame_idx, tilt_deg)


BUILDERS = {"skin_jet_fighter": get_jet_fighter}
