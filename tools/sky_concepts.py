"""
Round-8 exploration: 10 brand-new, vivid sky concepts for Skybit.

These are FRESH BiomeSpecs authored from scratch — the old shan-shui biome
catalog is deliberately discarded here. The brief: skies that read *alive*
and *painterly* (heightened-but-true, Ghibli/Alto/GRIS territory), never the
grey-and-melancholic register the live Karst sky and half the old catalog
landed in, and never flat two-tone "PowerPoint" gradients or candy neon.

Each concept authors ~8-12 keyframes across the full 0..1 day cycle with rich
chroma and a believable day->night arc, plus a tuned `SkyParams`. The vividness
comes from craft, not saturation slammers:

  * Channel separation — a warm horizon riding against a cool zenith at the
    same instant — so the OKLab bake has a real arc to travel and the midband
    stays saturated instead of slumping to grey.
  * 5 non-uniform `positions` stops that compress most of the grade toward the
    horizon the way real air does (denser low, open up top).
  * `zenith_dark` tuned per concept to deepen the very top without muddying it.
  * Night skies kept ALIVE — saturated indigo/teal/violet with stars, never a
    neutral charcoal.

Palette truth was grounded in golden-hour / blue-hour / alpenglow / aurora /
monsoon photography and stylized-game sky references (see the task notes).

Preview-only data. Nothing on the live render path imports this module — it is
reached solely through `tools/preview_sky_concepts.py`. Pure-Pygame / pygbag-
safe (the keyframes are just color tables; the OKLab bake lives in the engine).
"""
from __future__ import annotations

from game.biome_sky import BiomeSpec, SkyParams


# Each keyframe table is keyed on the SAME phase anchors so all concepts share a
# common day->night clock; only the colors differ. Anchors, in cycle order:
#   morning 0.06 · midday 0.18 · afternoon 0.30 · golden 0.40 · sunset 0.50 ·
#   dusk 0.62 · night 0.72 · predawn 0.80 · dawn 0.88 · sunrise 0.94
# `make_palette` wraps 0.94 -> 0.06 through 1.0, so the night side is continuous.


# ── 1. Tropical Lagoon — turquoise day, teal blue-hour, warm reef sunset ───────
_LAGOON_KF = [
    (0.06, dict(sky_top=(28, 138, 204), sky_mid=(86, 196, 224), sky_bot=(168, 236, 232), horizon=(224, 250, 236), star_alpha=0)),
    (0.18, dict(sky_top=(22, 146, 216), sky_mid=(74, 200, 230), sky_bot=(158, 238, 234), horizon=(214, 248, 234), star_alpha=0)),
    (0.30, dict(sky_top=(30, 150, 214), sky_mid=(96, 206, 226), sky_bot=(176, 240, 230), horizon=(238, 246, 214), star_alpha=0)),
    (0.40, dict(sky_top=(64, 158, 206), sky_mid=(132, 214, 206), sky_bot=(244, 218, 150), horizon=(255, 222, 138), star_alpha=0)),
    (0.50, dict(sky_top=(58, 110, 168), sky_mid=(180, 142, 150), sky_bot=(255, 158, 110), horizon=(255, 188, 120), star_alpha=10)),
    (0.62, dict(sky_top=(22, 58, 110), sky_mid=(40, 116, 142), sky_bot=(120, 156, 150), horizon=(232, 162, 120), star_alpha=70)),
    (0.72, dict(sky_top=(6, 22, 56), sky_mid=(12, 56, 92), sky_bot=(26, 92, 110), horizon=(72, 132, 134), star_alpha=210)),
    (0.80, dict(sky_top=(10, 30, 70), sky_mid=(20, 76, 116), sky_bot=(48, 128, 138), horizon=(150, 178, 156), star_alpha=120)),
    (0.88, dict(sky_top=(20, 96, 162), sky_mid=(70, 168, 196), sky_bot=(190, 214, 178), horizon=(255, 216, 168), star_alpha=20)),
    (0.94, dict(sky_top=(26, 132, 198), sky_mid=(92, 198, 216), sky_bot=(214, 240, 204), horizon=(255, 230, 184), star_alpha=0)),
]

TROPICAL_LAGOON = BiomeSpec(
    name='Tropical Lagoon',
    note='Electric reef turquoise by day melting to teal blue-hour and a warm coral sunset; saltwater-bright.',
    keyframes=_LAGOON_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=2.0, zenith_dark=0.08),
)


# ── 2. Aurora Tundra — cold cyan day, green-violet curtains over indigo night ─
_AURORA_KF = [
    (0.06, dict(sky_top=(36, 96, 168), sky_mid=(96, 168, 206), sky_bot=(176, 214, 224), horizon=(214, 234, 230), star_alpha=0)),
    (0.18, dict(sky_top=(30, 104, 182), sky_mid=(88, 176, 214), sky_bot=(170, 216, 228), horizon=(206, 232, 230), star_alpha=0)),
    (0.30, dict(sky_top=(38, 100, 176), sky_mid=(102, 172, 208), sky_bot=(182, 216, 224), horizon=(222, 232, 222), star_alpha=0)),
    (0.40, dict(sky_top=(58, 92, 158), sky_mid=(128, 168, 188), sky_bot=(214, 210, 196), horizon=(244, 222, 186), star_alpha=0)),
    (0.50, dict(sky_top=(46, 64, 132), sky_mid=(108, 110, 160), sky_bot=(204, 158, 160), horizon=(248, 188, 154), star_alpha=20)),
    (0.62, dict(sky_top=(18, 36, 92), sky_mid=(34, 92, 122), sky_bot=(72, 158, 142), horizon=(168, 184, 150), star_alpha=110)),
    (0.72, dict(sky_top=(6, 14, 48), sky_mid=(16, 60, 86), sky_bot=(34, 130, 118), horizon=(96, 176, 138), star_alpha=235)),
    (0.80, dict(sky_top=(10, 18, 56), sky_mid=(24, 70, 100), sky_bot=(58, 132, 134), horizon=(126, 168, 150), star_alpha=170)),
    (0.88, dict(sky_top=(22, 48, 108), sky_mid=(56, 116, 158), sky_bot=(128, 184, 196), horizon=(206, 218, 204), star_alpha=40)),
    (0.94, dict(sky_top=(32, 86, 158), sky_mid=(92, 162, 200), sky_bot=(178, 212, 220), horizon=(226, 230, 220), star_alpha=10)),
]

AURORA_TUNDRA = BiomeSpec(
    name='Aurora Tundra',
    note='Frozen cyan daylight giving way to green-violet aurora curtains over a deep indigo, star-thick night.',
    keyframes=_AURORA_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.60, 0.80, 1.0), dither_amp=1.8, zenith_dark=0.14),
)


# ── 3. Mars Glow Desert — butterscotch dome, dusty-rose haze, blue solar dusk ─
_MARS_KF = [
    (0.06, dict(sky_top=(150, 120, 110), sky_mid=(206, 168, 130), sky_bot=(236, 196, 146), horizon=(246, 206, 150), star_alpha=0)),
    (0.18, dict(sky_top=(160, 132, 118), sky_mid=(214, 178, 138), sky_bot=(240, 202, 152), horizon=(248, 210, 152), star_alpha=0)),
    (0.30, dict(sky_top=(168, 128, 112), sky_mid=(220, 172, 130), sky_bot=(244, 198, 144), horizon=(250, 204, 144), star_alpha=0)),
    (0.40, dict(sky_top=(150, 100, 100), sky_mid=(214, 150, 116), sky_bot=(246, 184, 132), horizon=(252, 192, 128), star_alpha=0)),
    (0.50, dict(sky_top=(96, 72, 110), sky_mid=(168, 110, 116), sky_bot=(226, 158, 128), horizon=(150, 158, 180), star_alpha=20)),
    (0.62, dict(sky_top=(48, 40, 78), sky_mid=(98, 64, 84), sky_bot=(168, 104, 100), horizon=(108, 130, 176), star_alpha=90)),
    (0.72, dict(sky_top=(18, 14, 36), sky_mid=(44, 26, 42), sky_bot=(84, 46, 50), horizon=(58, 74, 124), star_alpha=215)),
    (0.80, dict(sky_top=(30, 22, 48), sky_mid=(72, 44, 58), sky_bot=(132, 78, 72), horizon=(96, 102, 150), star_alpha=120)),
    (0.88, dict(sky_top=(110, 84, 104), sky_mid=(190, 132, 116), sky_bot=(236, 176, 134), horizon=(214, 178, 162), star_alpha=20)),
    (0.94, dict(sky_top=(150, 116, 110), sky_mid=(214, 166, 128), sky_bot=(242, 194, 142), horizon=(246, 202, 148), star_alpha=0)),
]

MARS_GLOW_DESERT = BiomeSpec(
    name='Mars Glow Desert',
    note='Butterscotch iron-dust dome with a rare blue solar twilight; alien-warm by day, cold indigo at night.',
    keyframes=_MARS_KF,
    sky=SkyParams(positions=(0.0, 0.28, 0.56, 0.82, 1.0), dither_amp=2.6, zenith_dark=0.10),
)


# ── 4. Monsoon Storm Front — bruised slate-teal day, green squall, rain-dusk ──
_MONSOON_KF = [
    (0.06, dict(sky_top=(64, 92, 110), sky_mid=(108, 142, 150), sky_bot=(160, 188, 184), horizon=(196, 214, 200), star_alpha=0)),
    (0.18, dict(sky_top=(56, 86, 108), sky_mid=(98, 134, 146), sky_bot=(150, 182, 178), horizon=(188, 210, 196), star_alpha=0)),
    (0.30, dict(sky_top=(46, 74, 96), sky_mid=(82, 120, 132), sky_bot=(128, 166, 162), horizon=(170, 196, 180), star_alpha=0)),
    (0.40, dict(sky_top=(40, 64, 88), sky_mid=(74, 108, 118), sky_bot=(132, 158, 142), horizon=(200, 196, 150), star_alpha=0)),
    (0.50, dict(sky_top=(52, 56, 92), sky_mid=(108, 100, 120), sky_bot=(178, 150, 128), horizon=(230, 178, 124), star_alpha=10)),
    (0.62, dict(sky_top=(26, 36, 68), sky_mid=(52, 72, 96), sky_bot=(96, 122, 122), horizon=(168, 158, 132), star_alpha=80)),
    (0.72, dict(sky_top=(8, 16, 40), sky_mid=(20, 38, 62), sky_bot=(40, 70, 84), horizon=(74, 108, 110), star_alpha=190)),
    (0.80, dict(sky_top=(14, 24, 52), sky_mid=(34, 56, 84), sky_bot=(64, 98, 108), horizon=(120, 142, 134), star_alpha=110)),
    (0.88, dict(sky_top=(40, 62, 92), sky_mid=(80, 116, 134), sky_bot=(130, 168, 162), horizon=(198, 200, 168), star_alpha=20)),
    (0.94, dict(sky_top=(54, 82, 104), sky_mid=(98, 136, 146), sky_bot=(152, 184, 178), horizon=(208, 212, 184), star_alpha=0)),
]

MONSOON_STORM_FRONT = BiomeSpec(
    name='Monsoon Storm Front',
    note='Bruised slate-teal sky shot with a sickly-green squall line and a thin amber rain-break at sunset; moody, alive.',
    keyframes=_MONSOON_KF,
    sky=SkyParams(positions=(0.0, 0.34, 0.62, 0.84, 1.0), dither_amp=2.4, zenith_dark=0.12),
)


# ── 5. Cherry-Blossom Spring — periwinkle day, sakura-pink horizon, lilac dusk ─
_SAKURA_KF = [
    (0.06, dict(sky_top=(108, 150, 220), sky_mid=(176, 200, 238), sky_bot=(234, 224, 236), horizon=(255, 224, 226), star_alpha=0)),
    (0.18, dict(sky_top=(96, 146, 224), sky_mid=(168, 198, 240), sky_bot=(228, 222, 238), horizon=(252, 222, 228), star_alpha=0)),
    (0.30, dict(sky_top=(110, 152, 222), sky_mid=(182, 202, 238), sky_bot=(238, 222, 234), horizon=(255, 220, 222), star_alpha=0)),
    (0.40, dict(sky_top=(130, 150, 216), sky_mid=(218, 196, 220), sky_bot=(255, 214, 206), horizon=(255, 210, 196), star_alpha=0)),
    (0.50, dict(sky_top=(132, 116, 184), sky_mid=(220, 162, 192), sky_bot=(255, 188, 184), horizon=(255, 202, 188), star_alpha=10)),
    (0.62, dict(sky_top=(64, 56, 124), sky_mid=(134, 100, 162), sky_bot=(212, 152, 176), horizon=(248, 184, 184), star_alpha=70)),
    (0.72, dict(sky_top=(16, 16, 56), sky_mid=(40, 32, 84), sky_bot=(82, 60, 112), horizon=(150, 110, 138), star_alpha=205)),
    (0.80, dict(sky_top=(30, 26, 78), sky_mid=(66, 52, 116), sky_bot=(126, 96, 150), horizon=(212, 162, 178), star_alpha=110)),
    (0.88, dict(sky_top=(96, 110, 192), sky_mid=(190, 176, 218), sky_bot=(252, 206, 212), horizon=(255, 212, 204), star_alpha=20)),
    (0.94, dict(sky_top=(110, 146, 214), sky_mid=(190, 198, 232), sky_bot=(248, 220, 228), horizon=(255, 220, 220), star_alpha=0)),
]

CHERRY_BLOSSOM_SPRING = BiomeSpec(
    name='Cherry-Blossom Spring',
    note='Soft periwinkle daytime with a perpetual sakura-pink wash at the horizon, blooming to a lilac dusk.',
    keyframes=_SAKURA_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.56, 0.80, 1.0), dither_amp=1.8, zenith_dark=0.06),
)


# ── 6. Savanna Ember Dusk — gold-hazed day, ember-orange dusk, hot-coal night ─
_SAVANNA_KF = [
    (0.06, dict(sky_top=(86, 142, 198), sky_mid=(176, 196, 196), sky_bot=(240, 222, 178), horizon=(255, 220, 158), star_alpha=0)),
    (0.18, dict(sky_top=(74, 140, 206), sky_mid=(170, 196, 196), sky_bot=(236, 218, 172), horizon=(252, 216, 150), star_alpha=0)),
    (0.30, dict(sky_top=(96, 138, 192), sky_mid=(196, 192, 168), sky_bot=(248, 212, 150), horizon=(255, 206, 130), star_alpha=0)),
    (0.40, dict(sky_top=(132, 124, 158), sky_mid=(236, 174, 116), sky_bot=(255, 196, 110), horizon=(255, 192, 92), star_alpha=0)),
    (0.50, dict(sky_top=(120, 70, 96), sky_mid=(220, 110, 70), sky_bot=(255, 150, 66), horizon=(255, 174, 70), star_alpha=10)),
    (0.62, dict(sky_top=(56, 30, 60), sky_mid=(132, 56, 56), sky_bot=(208, 100, 50), horizon=(248, 140, 60), star_alpha=80)),
    (0.72, dict(sky_top=(18, 12, 32), sky_mid=(48, 22, 32), sky_bot=(98, 44, 38), horizon=(176, 82, 44), star_alpha=200)),
    (0.80, dict(sky_top=(30, 20, 44), sky_mid=(78, 38, 48), sky_bot=(146, 70, 50), horizon=(214, 112, 54), star_alpha=110)),
    (0.88, dict(sky_top=(96, 78, 118), sky_mid=(206, 138, 100), sky_bot=(252, 178, 100), horizon=(255, 188, 92), star_alpha=20)),
    (0.94, dict(sky_top=(90, 134, 188), sky_mid=(214, 178, 134), sky_bot=(252, 204, 132), horizon=(255, 204, 120), star_alpha=0)),
]

SAVANNA_EMBER_DUSK = BiomeSpec(
    name='Savanna Ember Dusk',
    note='Dust-gold afternoon blazing into an ember-orange dusk and a smouldering hot-coal night horizon.',
    keyframes=_SAVANNA_KF,
    sky=SkyParams(positions=(0.0, 0.28, 0.56, 0.82, 1.0), dither_amp=2.4, zenith_dark=0.08),
)


# ── 7. Oceanic Blue-Hour — deep cobalt day, ultramarine dusk, abyssal night ───
_OCEANIC_KF = [
    (0.06, dict(sky_top=(20, 70, 158), sky_mid=(64, 128, 204), sky_bot=(146, 192, 232), horizon=(202, 224, 240), star_alpha=0)),
    (0.18, dict(sky_top=(16, 76, 172), sky_mid=(56, 134, 212), sky_bot=(140, 196, 234), horizon=(196, 224, 240), star_alpha=0)),
    (0.30, dict(sky_top=(22, 72, 162), sky_mid=(70, 130, 204), sky_bot=(154, 196, 232), horizon=(214, 224, 232), star_alpha=0)),
    (0.40, dict(sky_top=(34, 64, 146), sky_mid=(96, 124, 184), sky_bot=(190, 196, 212), horizon=(240, 220, 196), star_alpha=0)),
    (0.50, dict(sky_top=(32, 44, 122), sky_mid=(82, 88, 158), sky_bot=(176, 154, 170), horizon=(244, 186, 152), star_alpha=20)),
    (0.62, dict(sky_top=(14, 24, 82), sky_mid=(28, 56, 122), sky_bot=(66, 108, 160), horizon=(150, 168, 184), star_alpha=120)),
    (0.72, dict(sky_top=(4, 10, 42), sky_mid=(10, 28, 78), sky_bot=(22, 58, 110), horizon=(56, 104, 146), star_alpha=235)),
    (0.80, dict(sky_top=(8, 16, 58), sky_mid=(18, 44, 100), sky_bot=(40, 88, 142), horizon=(96, 138, 168), star_alpha=160)),
    (0.88, dict(sky_top=(16, 52, 128), sky_mid=(48, 104, 176), sky_bot=(120, 172, 212), horizon=(200, 210, 220), star_alpha=30)),
    (0.94, dict(sky_top=(20, 68, 154), sky_mid=(62, 126, 202), sky_bot=(148, 196, 230), horizon=(214, 226, 234), star_alpha=0)),
]

OCEANIC_BLUE_HOUR = BiomeSpec(
    name='Oceanic Blue-Hour',
    note='Saturated cobalt-to-ultramarine sky that lives in the blue hour; deep, cool, oceanic, glittering at night.',
    keyframes=_OCEANIC_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.16),
)


# ── 8. Emerald Rainforest — jade-warm day, chartreuse haze, deep viridian night ─
_RAINFOREST_KF = [
    (0.06, dict(sky_top=(70, 150, 158), sky_mid=(150, 204, 178), sky_bot=(216, 234, 192), horizon=(238, 240, 196), star_alpha=0)),
    (0.18, dict(sky_top=(60, 150, 162), sky_mid=(140, 202, 178), sky_bot=(208, 232, 190), horizon=(232, 238, 194), star_alpha=0)),
    (0.30, dict(sky_top=(64, 146, 150), sky_mid=(146, 198, 166), sky_bot=(214, 230, 178), horizon=(240, 236, 178), star_alpha=0)),
    (0.40, dict(sky_top=(78, 140, 138), sky_mid=(172, 196, 142), sky_bot=(232, 222, 154), horizon=(248, 224, 152), star_alpha=0)),
    (0.50, dict(sky_top=(76, 104, 116), sky_mid=(160, 158, 120), sky_bot=(226, 192, 130), horizon=(248, 204, 134), star_alpha=10)),
    (0.62, dict(sky_top=(28, 60, 70), sky_mid=(56, 110, 96), sky_bot=(118, 158, 112), horizon=(196, 188, 132), star_alpha=80)),
    (0.72, dict(sky_top=(6, 22, 34), sky_mid=(14, 56, 56), sky_bot=(28, 96, 80), horizon=(76, 140, 100), star_alpha=205)),
    (0.80, dict(sky_top=(10, 30, 44), sky_mid=(24, 76, 76), sky_bot=(52, 124, 100), horizon=(118, 164, 122), star_alpha=120)),
    (0.88, dict(sky_top=(50, 118, 134), sky_mid=(120, 186, 158), sky_bot=(196, 224, 178), horizon=(230, 236, 184), star_alpha=20)),
    (0.94, dict(sky_top=(66, 146, 156), sky_mid=(146, 202, 176), sky_bot=(214, 234, 190), horizon=(238, 240, 192), star_alpha=0)),
]

EMERALD_RAINFOREST = BiomeSpec(
    name='Emerald Rainforest',
    note='Humid jade-and-chartreuse canopy light by day sinking to a deep viridian, firefly-starred night.',
    keyframes=_RAINFOREST_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=2.0, zenith_dark=0.10),
)


# ── 9. High-Altitude Cosmos — thin violet-blue day, magenta dusk, galactic night ─
_COSMOS_KF = [
    (0.06, dict(sky_top=(48, 56, 150), sky_mid=(108, 124, 200), sky_bot=(180, 192, 226), horizon=(220, 220, 232), star_alpha=20)),
    (0.18, dict(sky_top=(42, 54, 158), sky_mid=(100, 122, 206), sky_bot=(174, 190, 228), horizon=(214, 218, 232), star_alpha=10)),
    (0.30, dict(sky_top=(52, 56, 150), sky_mid=(114, 122, 198), sky_bot=(186, 190, 224), horizon=(224, 218, 226), star_alpha=10)),
    (0.40, dict(sky_top=(72, 58, 144), sky_mid=(148, 120, 184), sky_bot=(220, 188, 212), horizon=(244, 210, 212), star_alpha=10)),
    (0.50, dict(sky_top=(72, 40, 122), sky_mid=(146, 70, 150), sky_bot=(224, 138, 174), horizon=(250, 178, 178), star_alpha=30)),
    (0.62, dict(sky_top=(36, 20, 88), sky_mid=(80, 38, 116), sky_bot=(150, 78, 142), horizon=(206, 138, 160), star_alpha=130)),
    (0.72, dict(sky_top=(8, 6, 38), sky_mid=(26, 18, 70), sky_bot=(56, 36, 100), horizon=(116, 78, 130), star_alpha=245)),
    (0.80, dict(sky_top=(14, 10, 52), sky_mid=(40, 28, 92), sky_bot=(84, 56, 128), horizon=(160, 110, 152), star_alpha=180)),
    (0.88, dict(sky_top=(40, 36, 124), sky_mid=(100, 88, 174), sky_bot=(176, 158, 206), horizon=(228, 196, 212), star_alpha=50)),
    (0.94, dict(sky_top=(50, 54, 148), sky_mid=(116, 120, 198), sky_bot=(190, 190, 224), horizon=(232, 216, 226), star_alpha=20)),
]

HIGH_ALTITUDE_COSMOS = BiomeSpec(
    name='High-Altitude Cosmos',
    note='Thin near-space air: violet-blue daylight, a magenta solar dusk, and a star-dense galactic indigo night.',
    keyframes=_COSMOS_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.80, 1.0), dither_amp=1.6, zenith_dark=0.18),
)


# ── 10. Rose-Gold Salt Flat — mirror-pale day, peach-gold sunset, mauve night ─
_SALTFLAT_KF = [
    (0.06, dict(sky_top=(132, 168, 214), sky_mid=(206, 216, 224), sky_bot=(250, 234, 218), horizon=(255, 228, 206), star_alpha=0)),
    (0.18, dict(sky_top=(120, 166, 220), sky_mid=(200, 214, 224), sky_bot=(248, 232, 216), horizon=(255, 226, 202), star_alpha=0)),
    (0.30, dict(sky_top=(138, 168, 212), sky_mid=(214, 216, 220), sky_bot=(252, 230, 210), horizon=(255, 222, 194), star_alpha=0)),
    (0.40, dict(sky_top=(160, 162, 200), sky_mid=(240, 204, 186), sky_bot=(255, 218, 184), horizon=(255, 210, 172), star_alpha=0)),
    (0.50, dict(sky_top=(146, 116, 168), sky_mid=(238, 162, 158), sky_bot=(255, 196, 162), horizon=(255, 204, 168), star_alpha=10)),
    (0.62, dict(sky_top=(72, 56, 112), sky_mid=(154, 102, 132), sky_bot=(226, 154, 150), horizon=(252, 188, 166), star_alpha=70)),
    (0.72, dict(sky_top=(20, 18, 54), sky_mid=(52, 38, 78), sky_bot=(102, 70, 102), horizon=(178, 130, 140), star_alpha=200)),
    (0.80, dict(sky_top=(34, 28, 72), sky_mid=(80, 58, 104), sky_bot=(146, 104, 132), horizon=(228, 168, 168), star_alpha=110)),
    (0.88, dict(sky_top=(120, 124, 192), sky_mid=(212, 190, 204), sky_bot=(255, 210, 198), horizon=(255, 206, 190), star_alpha=20)),
    (0.94, dict(sky_top=(134, 164, 210), sky_mid=(216, 214, 218), sky_bot=(255, 226, 210), horizon=(255, 222, 200), star_alpha=0)),
]

ROSE_GOLD_SALT_FLAT = BiomeSpec(
    name='Rose-Gold Salt Flat',
    note='Pale mirror-bright daylight warming to a peach-gold sunset and a quiet mauve, faintly-rose night.',
    keyframes=_SALTFLAT_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.60, 0.82, 1.0), dither_amp=1.6, zenith_dark=0.05),
)


# Ordered (id, spec) list — the 10 concept rows in sheet order.
CONCEPTS = [
    ('tropical_lagoon', TROPICAL_LAGOON),
    ('aurora_tundra', AURORA_TUNDRA),
    ('mars_glow_desert', MARS_GLOW_DESERT),
    ('monsoon_storm_front', MONSOON_STORM_FRONT),
    ('cherry_blossom_spring', CHERRY_BLOSSOM_SPRING),
    ('savanna_ember_dusk', SAVANNA_EMBER_DUSK),
    ('oceanic_blue_hour', OCEANIC_BLUE_HOUR),
    ('emerald_rainforest', EMERALD_RAINFOREST),
    ('high_altitude_cosmos', HIGH_ALTITUDE_COSMOS),
    ('rose_gold_salt_flat', ROSE_GOLD_SALT_FLAT),
]
