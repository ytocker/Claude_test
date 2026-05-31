"""Guard tests for the biome keyframe palettes.

The sky/pillar/ground palettes are interpolated by ``biome._blend`` which
iterates the keys of the *first* keyframe and looks each up in the second. A
key present in one keyframe but missing from another therefore raises
``KeyError`` only at the phase span between them — a crash that wouldn't show
until that exact time of day in a run. These tests catch a divergent key set
and exercise the interpolation across the whole cycle.
"""
from game import biome


def test_keyframes_share_identical_key_set():
    ref = set(biome._KEYFRAMES[0][1].keys())
    for phase, kf in biome._KEYFRAMES:
        assert set(kf.keys()) == ref, f"keyframe @ {phase} diverges: {set(kf) ^ ref}"


def test_palette_for_phase_covers_cycle_without_crash():
    # Sample finer than the 32 phase buckets so every interpolation span and
    # both wrap boundaries are exercised.
    for i in range(128):
        pal = biome.palette_for_phase(i / 128)
        assert set(pal.keys()) == set(biome._KEYFRAMES[0][1].keys())
