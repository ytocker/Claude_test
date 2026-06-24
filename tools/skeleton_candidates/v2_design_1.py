"""v2_design_1 — BONEWHITE-MACAW: the definitive clean PARROT skeleton.

Evolves the v1 BONEWHITE winner with the corrected anatomy from ``_v2_anatomy``:
pure-white bone on a near-black flesh floor, but now unmistakably a *parrot* —
a big hooked bone beak and a long bony tail. No theme gear; the value split and
the silhouette carry it. Scratch only — never registered in BUILDERS.
"""
from game.store_skins import _make_prebuilt_skin
from tools.skeleton_candidates import _v2_anatomy as A


P = A.WHITE


def _build(wing_angle_deg):
    return A.build_skeleton(wing_angle_deg, P)


build = _make_prebuilt_skin(_build)
