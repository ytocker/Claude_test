"""
Round-12 exploration: 10 RESTRAINED, UX-flattering sky concepts for Skybit.

The journey: the live sky read grey/melancholic -> round-11 answered with 10
*vivid* concepts -> the user found those too vivid. This is the third target:
a cool, restrained, harmonious backdrop that RECEDES, so the game's warm, busy
foreground (scarlet bird, gold coins, tan pillars, warm power-up bursts) pops
and long runs stay easy on the eye. NOT a swing back to grey.

The register is the Alto's Odyssey / Monument Valley / GRIS / Sky: Children of
the Light family — recessive pastel/jewel gradients that keep foreground
silhouettes readable. Every concept is authored to ALL of these rules:

  * Cool-biased, MODERATE chroma. Hue families bias blue/teal/slate/lavender/
    dawn rose-grey/pale amber — clean pastels or hazy jewel tones, never neon.
  * Muted != grey. Each row's hue identity stays DECISIVE even at low chroma;
    no phase is allowed to collapse to neutral charcoal/beige.
  * Value-managed for the HUD: the top ~10% band is kept a touch deeper /
    stronger-hued (zenith_dark + a deepened sky_top stop) so white+gold HUD
    text reads; the upper sky is never near-white.
  * Calm bird zone (upper-mid): low-contrast, no warm saturated red/orange and
    no saturated green up there (the bird owns scarlet, foliage owns green).
    Warm accents are allowed ONLY low / at the horizon, kept subtle.
  * Alive nights: deep indigo/teal/violet + stars — saturated-dark, never grey.
  * Distinctiveness via hue family + time-of-day; each a tight analogous palette
    with at most one quiet complementary horizon accent. No two rows alike.

Palette truth was grounded in blue-hour / high-altitude-haze / overcast /
pre-dawn photography and the recessive game-sky references (see task notes):
blue-hour descent #87c7de->#1d51a6->#0d0548, cloud-blue haze #A2B6B9.

Preview-only data. Nothing on the live render path imports this module — it is
reached solely through `tools/preview_sky_concepts_calm.py`. Pure-Pygame /
pygbag-safe (the keyframes are just color tables; the OKLab bake lives in the
engine). Authored as a NEW module so the round-11 vivid set stays intact.
"""
from __future__ import annotations

from game.biome_sky import BiomeSpec, SkyParams


# All concepts share the SAME phase clock as round 11 so the columns line up:
#   morning 0.06 · midday 0.18 · afternoon 0.30 · golden 0.40 · sunset 0.50 ·
#   dusk 0.62 · night 0.72 · predawn 0.80 · dawn 0.88 · sunrise 0.94
# `make_palette` wraps 0.94 -> 0.06 through 1.0, so the night side is continuous.
#
# Authoring discipline for the calm target, applied to every row:
#   - Day phases (0.06-0.40): keep the upper-mid (sky_top/sky_mid) cool and
#     close in value; let the horizon carry the one warm/hue accent, kept low.
#   - Sunset (0.50): a SINGLE quiet warm step at the horizon only — no full-sky
#     fire. The zenith stays cool.
#   - Dusk/predawn (0.62/0.80): blue-hour — cool, deepening, the most "Alto".
#   - Night (0.72): saturated-dark jewel tone + stars.


# ── 1. Dawn Rose-Grey — hazy rose-mauve morning, slate noon, blue-hour night ──
# A muted rose-grey that stays decisively warm-neutral-cool without tipping to
# beige: a smoky slate-blue zenith over a soft dusty-rose horizon by day, the
# warmth held LOW so the bird zone is cool. Pre-dawn is its signature — a true
# muted rose-grey blue-hour.
# Sunrise/sunset signature: a rose-gold / warm-mauve bloom that climbs from the
# horizon into sky_bot and washes the mid mauve, the slate zenith holding cool
# above it. Held wide via 0.44/0.56 (sunset) and 0.84/0.90 (sunrise) keyframes.
_ROSEGREY_KF = [
    (0.06, dict(sky_top=(96, 110, 140), sky_mid=(150, 156, 174), sky_bot=(206, 190, 192), horizon=(224, 196, 188), star_alpha=0)),
    (0.18, dict(sky_top=(104, 122, 152), sky_mid=(158, 168, 186), sky_bot=(208, 200, 200), horizon=(222, 204, 196), star_alpha=0)),
    (0.30, dict(sky_top=(100, 116, 148), sky_mid=(152, 162, 182), sky_bot=(204, 194, 196), horizon=(220, 196, 190), star_alpha=0)),
    (0.40, dict(sky_top=(112, 112, 144), sky_mid=(184, 156, 168), sky_bot=(236, 178, 168), horizon=(248, 174, 148), star_alpha=0)),
    (0.44, dict(sky_top=(108, 104, 140), sky_mid=(190, 150, 164), sky_bot=(244, 168, 158), horizon=(252, 162, 134), star_alpha=0)),
    (0.50, dict(sky_top=(100, 92, 136), sky_mid=(186, 138, 158), sky_bot=(244, 156, 150), horizon=(250, 150, 124), star_alpha=10)),
    (0.56, dict(sky_top=(86, 80, 128), sky_mid=(168, 124, 152), sky_bot=(226, 146, 148), horizon=(240, 144, 126), star_alpha=24)),
    (0.62, dict(sky_top=(60, 60, 106), sky_mid=(120, 100, 144), sky_bot=(178, 132, 156), horizon=(216, 152, 152), star_alpha=70)),
    (0.72, dict(sky_top=(26, 28, 56), sky_mid=(48, 48, 84), sky_bot=(78, 72, 110), horizon=(120, 100, 130), star_alpha=190)),
    (0.80, dict(sky_top=(42, 40, 78), sky_mid=(92, 72, 118), sky_bot=(150, 108, 142), horizon=(206, 144, 152), star_alpha=110)),
    (0.84, dict(sky_top=(60, 56, 100), sky_mid=(134, 104, 144), sky_bot=(206, 144, 152), horizon=(244, 160, 142), star_alpha=56)),
    (0.88, dict(sky_top=(82, 80, 124), sky_mid=(172, 138, 162), sky_bot=(236, 168, 162), horizon=(250, 170, 144), star_alpha=24)),
    (0.90, dict(sky_top=(92, 96, 136), sky_mid=(176, 150, 170), sky_bot=(232, 180, 176), horizon=(246, 182, 158), star_alpha=12)),
    (0.94, dict(sky_top=(96, 110, 142), sky_mid=(160, 160, 178), sky_bot=(214, 192, 192), horizon=(234, 194, 182), star_alpha=0)),
]

DAWN_ROSE_GREY = BiomeSpec(
    name='Dawn Rose-Grey',
    note='Smoky slate-blue zenith over a soft dusty-rose horizon — muted rose-grey that never tips to beige — sinking to a true blue-hour night.',
    keyframes=_ROSEGREY_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.60, 0.82, 1.0), dither_amp=2.0, zenith_dark=0.10),
)


# ── 2. Powder Morning — clean powder-blue clear day, gentle cool dusk, navy ───
# The classic "clear blue morning" but pastel and recessive: a deepened
# cornflower zenith opening to a powder-blue mid and a barely-warm pale horizon.
# The most universally-readable backdrop — calm, cool, foreground-first.
# Sunrise/sunset signature: a soft peach low that rises into the powder-blue mid
# as periwinkle, so warm-below / cool-above reads as a clean pastel dawn. The
# cornflower zenith stays cool. Widened via 0.44/0.56 and 0.84/0.90.
_POWDER_KF = [
    (0.06, dict(sky_top=(136, 166, 204), sky_mid=(196, 214, 232), sky_bot=(224, 232, 242), horizon=(236, 236, 240), star_alpha=0)),
    (0.18, dict(sky_top=(140, 170, 208), sky_mid=(198, 218, 234), sky_bot=(226, 234, 242), horizon=(238, 238, 240), star_alpha=0)),
    (0.30, dict(sky_top=(140, 168, 204), sky_mid=(200, 216, 230), sky_bot=(226, 232, 240), horizon=(238, 236, 238), star_alpha=0)),
    (0.40, dict(sky_top=(134, 154, 196), sky_mid=(204, 200, 222), sky_bot=(244, 216, 214), horizon=(252, 206, 184), star_alpha=0)),
    (0.44, dict(sky_top=(128, 146, 192), sky_mid=(208, 192, 216), sky_bot=(250, 206, 200), horizon=(254, 194, 168), star_alpha=0)),
    (0.50, dict(sky_top=(118, 134, 186), sky_mid=(200, 178, 210), sky_bot=(250, 196, 192), horizon=(254, 184, 156), star_alpha=10)),
    (0.56, dict(sky_top=(96, 112, 172), sky_mid=(172, 158, 198), sky_bot=(234, 184, 188), horizon=(248, 180, 158), star_alpha=26)),
    (0.62, dict(sky_top=(50, 74, 134), sky_mid=(102, 130, 178), sky_bot=(170, 178, 198), horizon=(224, 192, 184), star_alpha=80)),
    (0.72, dict(sky_top=(14, 24, 62), sky_mid=(24, 50, 102), sky_bot=(40, 82, 132), horizon=(72, 120, 158), star_alpha=210)),
    (0.80, dict(sky_top=(22, 36, 84), sky_mid=(48, 76, 130), sky_bot=(98, 116, 158), horizon=(170, 158, 168), star_alpha=130)),
    (0.84, dict(sky_top=(40, 56, 110), sky_mid=(108, 116, 168), sky_bot=(196, 168, 184), horizon=(248, 184, 162), star_alpha=58)),
    (0.88, dict(sky_top=(88, 116, 176), sky_mid=(176, 184, 216), sky_bot=(238, 206, 206), horizon=(252, 200, 178), star_alpha=24)),
    (0.90, dict(sky_top=(106, 138, 192), sky_mid=(186, 198, 224), sky_bot=(236, 218, 216), horizon=(248, 214, 198), star_alpha=12)),
    (0.94, dict(sky_top=(122, 160, 204), sky_mid=(174, 202, 228), sky_bot=(212, 226, 238), horizon=(232, 232, 234), star_alpha=0)),
]

POWDER_MORNING = BiomeSpec(
    name='Powder Morning',
    note='The lightest, airiest porcelain-periwinkle clear day — high-value low-chroma blue clearly above Slate, a hair warm — easing to a gentle cool dusk and a deep navy night.',
    keyframes=_POWDER_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.24),
)


# ── 3. Pale Amber Haze — warm-neutral hazy afternoon, cool zenith, indigo night ─
# The one row that owns a warm daytime read, kept UX-safe: the warmth lives only
# in the LOWER half (pale amber/sand horizon), the zenith stays a cool dusty
# blue, so the bird zone never goes warm. Hazy, sun-through-dust afternoon.
# Sunrise/sunset signature: this row's natural strength — a rich honey-amber that
# floods sky_bot and warms the mid to gold, the cool dusty-blue zenith above. The
# most full-bodied bloom of the set. Widened via 0.44/0.56 and 0.84/0.90.
_AMBER_KF = [
    (0.06, dict(sky_top=(110, 144, 180), sky_mid=(170, 190, 200), sky_bot=(224, 214, 188), horizon=(238, 220, 178), star_alpha=0)),
    (0.18, dict(sky_top=(110, 142, 184), sky_mid=(160, 178, 200), sky_bot=(228, 216, 184), horizon=(244, 220, 172), star_alpha=0)),
    (0.30, dict(sky_top=(112, 138, 178), sky_mid=(160, 174, 196), sky_bot=(230, 212, 176), horizon=(246, 216, 162), star_alpha=0)),
    (0.40, dict(sky_top=(116, 134, 174), sky_mid=(196, 182, 168), sky_bot=(248, 198, 130), horizon=(252, 184, 104), star_alpha=0)),
    (0.44, dict(sky_top=(112, 124, 168), sky_mid=(202, 174, 154), sky_bot=(250, 188, 116), horizon=(254, 172, 90), star_alpha=0)),
    (0.50, dict(sky_top=(102, 108, 158), sky_mid=(200, 162, 142), sky_bot=(250, 178, 108), horizon=(252, 160, 80), star_alpha=10)),
    (0.56, dict(sky_top=(82, 86, 134), sky_mid=(178, 142, 124), sky_bot=(238, 166, 106), horizon=(244, 150, 80), star_alpha=26)),
    (0.62, dict(sky_top=(56, 60, 104), sky_mid=(128, 102, 110), sky_bot=(204, 152, 116), horizon=(234, 162, 110), star_alpha=78)),
    (0.72, dict(sky_top=(20, 22, 52), sky_mid=(44, 42, 72), sky_bot=(88, 76, 88), horizon=(146, 116, 100), star_alpha=195)),
    (0.80, dict(sky_top=(34, 32, 66), sky_mid=(80, 64, 88), sky_bot=(158, 116, 96), horizon=(224, 162, 110), star_alpha=115)),
    (0.84, dict(sky_top=(56, 52, 96), sky_mid=(132, 102, 110), sky_bot=(214, 154, 104), horizon=(250, 168, 96), star_alpha=58)),
    (0.88, dict(sky_top=(86, 96, 144), sky_mid=(184, 162, 150), sky_bot=(242, 192, 128), horizon=(252, 184, 112), star_alpha=24)),
    (0.90, dict(sky_top=(100, 122, 162), sky_mid=(190, 178, 168), sky_bot=(238, 200, 148), horizon=(248, 198, 140), star_alpha=12)),
    (0.94, dict(sky_top=(108, 142, 180), sky_mid=(180, 190, 192), sky_bot=(228, 214, 182), horizon=(240, 218, 174), star_alpha=0)),
]

PALE_AMBER_HAZE = BiomeSpec(
    name='Pale Amber Haze',
    note='Sun-through-dust afternoon — cool dusty-blue zenith over a pale amber/sand horizon, the warmth held low — cooling to a deep indigo night.',
    keyframes=_AMBER_KF,
    sky=SkyParams(positions=(0.0, 0.34, 0.62, 0.84, 1.0), dither_amp=2.4, zenith_dark=0.08),
)


# ── 4. Misty Teal — soft sea-mist teal day, muted aqua dusk, deep teal night ──
# A cool teal that stays clearly teal (not foliage-green, not plain blue):
# desaturated sea-mist by day, the horizon a touch paler. Owns the teal hue at
# moderate chroma, with a saturated-dark teal night.
# Sunrise/sunset signature: a coral/salmon afterglow — teal's complementary —
# that floods sky_bot and warms the mid to peach while the teal zenith holds
# cool above, the warm/cool meeting line making the pop read. Held wide via
# 0.44/0.56 (sunset) and 0.84/0.90 (sunrise) keyframes.
_TEAL_KF = [
    (0.06, dict(sky_top=(132, 148, 158), sky_mid=(176, 190, 196), sky_bot=(202, 216, 218), horizon=(216, 224, 222), star_alpha=0)),
    (0.18, dict(sky_top=(134, 152, 164), sky_mid=(178, 194, 200), sky_bot=(204, 218, 220), horizon=(218, 226, 224), star_alpha=0)),
    (0.30, dict(sky_top=(134, 150, 160), sky_mid=(178, 192, 198), sky_bot=(204, 216, 216), horizon=(218, 224, 222), star_alpha=0)),
    (0.40, dict(sky_top=(120, 138, 156), sky_mid=(178, 184, 192), sky_bot=(232, 196, 178), horizon=(250, 178, 142), star_alpha=0)),
    (0.44, dict(sky_top=(108, 128, 154), sky_mid=(178, 174, 186), sky_bot=(242, 182, 160), horizon=(254, 162, 122), star_alpha=0)),
    (0.50, dict(sky_top=(92, 114, 150), sky_mid=(172, 160, 180), sky_bot=(246, 168, 146), horizon=(252, 148, 110), star_alpha=12)),
    (0.56, dict(sky_top=(70, 98, 138), sky_mid=(140, 146, 174), sky_bot=(230, 158, 142), horizon=(244, 142, 112), star_alpha=28)),
    (0.62, dict(sky_top=(48, 74, 108), sky_mid=(90, 124, 150), sky_bot=(176, 154, 158), horizon=(224, 156, 138), star_alpha=80)),
    (0.72, dict(sky_top=(8, 26, 56), sky_mid=(16, 58, 94), sky_bot=(28, 96, 124), horizon=(58, 132, 146), star_alpha=205)),
    (0.80, dict(sky_top=(12, 34, 66), sky_mid=(28, 78, 112), sky_bot=(86, 124, 140), horizon=(200, 138, 128), star_alpha=120)),
    (0.84, dict(sky_top=(30, 56, 92), sky_mid=(70, 108, 140), sky_bot=(178, 150, 152), horizon=(244, 148, 116), star_alpha=64)),
    (0.88, dict(sky_top=(78, 116, 146), sky_mid=(154, 168, 186), sky_bot=(228, 182, 166), horizon=(252, 162, 128), star_alpha=22)),
    (0.90, dict(sky_top=(96, 130, 154), sky_mid=(160, 180, 192), sky_bot=(226, 198, 186), horizon=(248, 180, 150), star_alpha=12)),
    (0.94, dict(sky_top=(116, 144, 160), sky_mid=(162, 188, 198), sky_bot=(206, 214, 212), horizon=(228, 210, 196), star_alpha=0)),
]

MISTY_TEAL = BiomeSpec(
    name='Misty Teal',
    note='Whisper of blue-teal sea-mist — low-chroma, hue pushed past cyan to blue-teal so it reads as recessive backdrop not foliage — coral/salmon afterglow at the edges, saturated-dark teal night.',
    keyframes=_TEAL_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.60, 0.82, 1.0), dither_amp=2.0, zenith_dark=0.10),
)


# ── 5. Slate Blue-Hour — the pure Alto blue-hour, deep slate all cycle ────────
# The most recessive concept: a perpetual cool slate-blue that only shifts value
# across the day. Day and night stay maximum-recede — backdrop as pure negative
# space for the foreground.
# Sunrise/sunset signature: a warm ember-orange horizon that blooms UP through
# sky_bot and flushes the mid amber-bronze, the deep slate zenith pressing cool
# above it so the ember reads as a glowing event inside the blue hour. Held wide
# via 0.44/0.56 (sunset) and 0.84/0.90 (sunrise) keyframes.
_SLATE_KF = [
    (0.06, dict(sky_top=(72, 96, 138), sky_mid=(120, 146, 178), sky_bot=(176, 196, 214), horizon=(204, 216, 224), star_alpha=0)),
    (0.18, dict(sky_top=(78, 104, 148), sky_mid=(126, 154, 186), sky_bot=(182, 202, 218), horizon=(210, 220, 226), star_alpha=0)),
    (0.30, dict(sky_top=(74, 100, 144), sky_mid=(122, 150, 182), sky_bot=(178, 198, 214), horizon=(206, 216, 222), star_alpha=0)),
    (0.40, dict(sky_top=(66, 84, 130), sky_mid=(122, 134, 166), sky_bot=(206, 178, 168), horizon=(244, 168, 116), star_alpha=0)),
    (0.44, dict(sky_top=(60, 76, 124), sky_mid=(126, 124, 158), sky_bot=(220, 168, 148), horizon=(250, 154, 98), star_alpha=0)),
    (0.50, dict(sky_top=(54, 66, 116), sky_mid=(124, 114, 150), sky_bot=(228, 158, 134), horizon=(250, 142, 86), star_alpha=12)),
    (0.56, dict(sky_top=(44, 56, 104), sky_mid=(104, 100, 142), sky_bot=(210, 150, 132), horizon=(240, 138, 90), star_alpha=30)),
    (0.62, dict(sky_top=(36, 50, 92), sky_mid=(74, 88, 130), sky_bot=(150, 144, 162), horizon=(212, 158, 124), star_alpha=85)),
    (0.72, dict(sky_top=(10, 18, 50), sky_mid=(20, 40, 84), sky_bot=(36, 70, 114), horizon=(66, 106, 146), star_alpha=215)),
    (0.80, dict(sky_top=(16, 28, 66), sky_mid=(32, 58, 102), sky_bot=(86, 100, 140), horizon=(188, 138, 124), star_alpha=135)),
    (0.84, dict(sky_top=(30, 44, 88), sky_mid=(78, 88, 134), sky_bot=(176, 142, 144), horizon=(238, 142, 100), star_alpha=70)),
    (0.88, dict(sky_top=(50, 72, 122), sky_mid=(116, 124, 162), sky_bot=(200, 166, 158), horizon=(246, 156, 108), star_alpha=22)),
    (0.90, dict(sky_top=(60, 86, 132), sky_mid=(120, 138, 172), sky_bot=(198, 184, 184), horizon=(240, 174, 138), star_alpha=12)),
    (0.94, dict(sky_top=(70, 96, 138), sky_mid=(118, 146, 180), sky_bot=(180, 196, 210), horizon=(218, 206, 200), star_alpha=0)),
]

SLATE_BLUE_HOUR = BiomeSpec(
    name='Slate Blue-Hour',
    note='Pure recessive Alto blue-hour — a perpetual cool slate-blue that shifts only in value, with a warm ember-orange that blooms up from the horizon at sunrise/sunset. Maximum recede otherwise.',
    keyframes=_SLATE_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.14),
)


# ── 6. Lavender Dusk — muted lilac-violet day, dove-grey-violet dusk, plum night ─
# A restrained lavender that holds its violet identity at low chroma: a soft
# grey-violet zenith over a paler lilac mid, kept calm and cool by day.
# Plum-saturated night. Distinct from Rose-Grey by leaning cooler/bluer-violet.
# Sunrise/sunset signature: the lilac intensifies and floods up into a vivid
# magenta/pink bloom through sky_bot and the mid, the grey-violet zenith holding
# cool above it. Held wide via 0.44/0.56 (sunset) and 0.84/0.90 (sunrise).
_LAVENDER_KF = [
    (0.06, dict(sky_top=(110, 110, 168), sky_mid=(162, 158, 198), sky_bot=(204, 196, 218), horizon=(218, 200, 210), star_alpha=0)),
    (0.18, dict(sky_top=(116, 116, 176), sky_mid=(168, 164, 204), sky_bot=(208, 200, 222), horizon=(220, 204, 214), star_alpha=0)),
    (0.30, dict(sky_top=(112, 112, 172), sky_mid=(164, 160, 200), sky_bot=(206, 196, 218), horizon=(216, 198, 210), star_alpha=0)),
    (0.40, dict(sky_top=(112, 102, 162), sky_mid=(182, 148, 192), sky_bot=(232, 168, 198), horizon=(246, 158, 178), star_alpha=0)),
    (0.44, dict(sky_top=(106, 92, 158), sky_mid=(190, 138, 190), sky_bot=(240, 154, 192), horizon=(250, 146, 174), star_alpha=0)),
    (0.50, dict(sky_top=(98, 80, 152), sky_mid=(188, 124, 182), sky_bot=(242, 142, 184), horizon=(250, 138, 168), star_alpha=12)),
    (0.56, dict(sky_top=(82, 66, 138), sky_mid=(166, 110, 170), sky_bot=(224, 134, 178), horizon=(240, 134, 166), star_alpha=30)),
    (0.62, dict(sky_top=(60, 50, 106), sky_mid=(116, 86, 148), sky_bot=(180, 124, 168), horizon=(216, 142, 168), star_alpha=78)),
    (0.72, dict(sky_top=(24, 18, 58), sky_mid=(50, 38, 90), sky_bot=(86, 64, 118), horizon=(128, 96, 138), star_alpha=200)),
    (0.80, dict(sky_top=(36, 28, 74), sky_mid=(82, 52, 116), sky_bot=(146, 90, 150), horizon=(208, 130, 168), star_alpha=115)),
    (0.84, dict(sky_top=(54, 40, 100), sky_mid=(126, 84, 154), sky_bot=(206, 124, 172), horizon=(244, 138, 168), star_alpha=62)),
    (0.88, dict(sky_top=(96, 84, 152), sky_mid=(172, 134, 188), sky_bot=(228, 162, 192), horizon=(248, 156, 176), star_alpha=20)),
    (0.90, dict(sky_top=(104, 98, 160), sky_mid=(170, 150, 194), sky_bot=(220, 178, 202), horizon=(242, 170, 184), star_alpha=12)),
    (0.94, dict(sky_top=(110, 112, 170), sky_mid=(162, 160, 200), sky_bot=(208, 196, 218), horizon=(228, 196, 204), star_alpha=0)),
]

LAVENDER_DUSK = BiomeSpec(
    name='Lavender Dusk',
    note='Muted lilac-violet day holding its hue at low chroma — soft grey-violet zenith — flaring to a vivid magenta/pink bloom at sunrise/sunset, deepening to a plum-saturated night.',
    keyframes=_LAVENDER_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.60, 0.82, 1.0), dither_amp=2.0, zenith_dark=0.10),
)


# ── 7. Starlit Navy — deep cool navy day, ultramarine dusk, galaxy night ──────
# The deepest, coolest, most night-leaning row — a permanently dusk-blue sky
# that stays gorgeous and saturated-dark, carrying a faint starfield even by
# day. Owns the "deep starlit navy" win, kept restrained: rich but never neon.
# Sunrise/sunset signature: a deep ultramarine flushed with a saturated
# magenta/indigo glow low — the warmth stays NIGHT-LEANING (no bright high-value
# bloom that would kill the starfield), a jewel ember rising into the mid against
# the navy zenith. Held wide via 0.44/0.56 (sunset) and 0.84/0.90 (sunrise),
# stars dimming but never gone.
_NAVY_KF = [
    (0.06, dict(sky_top=(24, 42, 96), sky_mid=(38, 70, 126), sky_bot=(62, 102, 150), horizon=(94, 134, 170), star_alpha=40)),
    (0.18, dict(sky_top=(22, 46, 102), sky_mid=(36, 76, 134), sky_bot=(60, 108, 156), horizon=(92, 140, 176), star_alpha=32)),
    (0.30, dict(sky_top=(26, 44, 100), sky_mid=(40, 72, 128), sky_bot=(64, 104, 152), horizon=(96, 136, 170), star_alpha=30)),
    (0.40, dict(sky_top=(28, 40, 96), sky_mid=(58, 60, 124), sky_bot=(118, 80, 146), horizon=(170, 96, 142), star_alpha=30)),
    (0.44, dict(sky_top=(28, 36, 96), sky_mid=(68, 56, 126), sky_bot=(140, 74, 144), horizon=(196, 90, 136), star_alpha=34)),
    (0.50, dict(sky_top=(28, 34, 94), sky_mid=(74, 52, 124), sky_bot=(152, 70, 140), horizon=(206, 84, 130), star_alpha=42)),
    (0.56, dict(sky_top=(24, 30, 88), sky_mid=(64, 50, 122), sky_bot=(138, 70, 140), horizon=(190, 88, 138), star_alpha=64)),
    (0.62, dict(sky_top=(20, 30, 80), sky_mid=(44, 56, 118), sky_bot=(98, 90, 152), horizon=(160, 116, 168), star_alpha=120)),
    (0.72, dict(sky_top=(6, 10, 44), sky_mid=(12, 28, 80), sky_bot=(24, 58, 116), horizon=(50, 100, 150), star_alpha=240)),
    (0.80, dict(sky_top=(8, 16, 56), sky_mid=(24, 42, 102), sky_bot=(64, 70, 138), horizon=(150, 96, 154), star_alpha=160)),
    (0.84, dict(sky_top=(16, 24, 74), sky_mid=(48, 48, 116), sky_bot=(118, 70, 142), horizon=(190, 88, 138), star_alpha=92)),
    (0.88, dict(sky_top=(26, 38, 96), sky_mid=(60, 60, 124), sky_bot=(122, 84, 148), horizon=(180, 100, 146), star_alpha=58)),
    (0.90, dict(sky_top=(26, 42, 98), sky_mid=(52, 66, 126), sky_bot=(98, 96, 150), horizon=(158, 116, 158), star_alpha=46)),
    (0.94, dict(sky_top=(24, 42, 96), sky_mid=(38, 70, 126), sky_bot=(62, 102, 150), horizon=(108, 130, 168), star_alpha=42)),
]

STARLIT_NAVY = BiomeSpec(
    name='Starlit Navy',
    note='Deep cool navy by day that never goes near-white — a saturated magenta/indigo dusk flush kept night-leaning, the band\'s densest galaxy night — rich, recessive, never neon.',
    keyframes=_NAVY_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.80, 1.0), dither_amp=1.6, zenith_dark=0.18),
)


# ── 8. Alpine Haze — cool high-altitude haze day, periwinkle dusk, deep blue night ─
# The thin-air high-altitude register grounded in cloud-blue #A2B6B9: a deep
# clean cobalt zenith fading to a hazy cool-grey-blue horizon (the haze line of
# distant peaks). Crisp and airy by day, with a clean cool-blue night.
# Sunrise/sunset signature: classic alpenglow — the glacial cyan gives way to a
# warm apricot/peach that floods sky_bot and warms the mid, the cyan zenith
# pressing cool above so the peach reads as light on snow. Held wide via
# 0.44/0.56 (sunset) and 0.84/0.90 (sunrise) keyframes.
_ALPINE_KF = [
    (0.06, dict(sky_top=(86, 158, 186), sky_mid=(150, 192, 202), sky_bot=(196, 212, 210), horizon=(214, 218, 212), star_alpha=0)),
    (0.18, dict(sky_top=(76, 168, 192), sky_mid=(144, 198, 208), sky_bot=(196, 214, 212), horizon=(216, 220, 212), star_alpha=0)),
    (0.30, dict(sky_top=(86, 160, 188), sky_mid=(152, 192, 204), sky_bot=(198, 212, 208), horizon=(216, 218, 210), star_alpha=0)),
    (0.40, dict(sky_top=(80, 148, 180), sky_mid=(160, 184, 196), sky_bot=(234, 200, 178), horizon=(252, 184, 144), star_alpha=0)),
    (0.44, dict(sky_top=(68, 138, 174), sky_mid=(166, 178, 192), sky_bot=(244, 188, 162), horizon=(254, 170, 124), star_alpha=0)),
    (0.50, dict(sky_top=(58, 124, 166), sky_mid=(160, 168, 188), sky_bot=(248, 178, 150), horizon=(254, 158, 110), star_alpha=12)),
    (0.56, dict(sky_top=(46, 102, 150), sky_mid=(132, 152, 182), sky_bot=(234, 170, 148), horizon=(248, 152, 112), star_alpha=28)),
    (0.62, dict(sky_top=(34, 76, 116), sky_mid=(86, 130, 164), sky_bot=(178, 168, 174), horizon=(226, 162, 134), star_alpha=80)),
    (0.72, dict(sky_top=(8, 28, 62), sky_mid=(16, 64, 104), sky_bot=(34, 104, 136), horizon=(70, 144, 164), star_alpha=210)),
    (0.80, dict(sky_top=(12, 38, 78), sky_mid=(28, 86, 124), sky_bot=(92, 130, 148), horizon=(204, 152, 130), star_alpha=130)),
    (0.84, dict(sky_top=(28, 70, 114), sky_mid=(74, 124, 162), sky_bot=(184, 164, 160), horizon=(248, 158, 118), star_alpha=66)),
    (0.88, dict(sky_top=(70, 138, 174), sky_mid=(150, 178, 196), sky_bot=(232, 192, 170), horizon=(252, 172, 134), star_alpha=20)),
    (0.90, dict(sky_top=(78, 148, 180), sky_mid=(152, 186, 198), sky_bot=(226, 200, 184), horizon=(248, 188, 154), star_alpha=12)),
    (0.94, dict(sky_top=(84, 156, 184), sky_mid=(148, 192, 202), sky_bot=(200, 212, 208), horizon=(228, 212, 198), star_alpha=0)),
]

ALPINE_HAZE = BiomeSpec(
    name='Alpine Haze',
    note='Thin high-altitude air — glacial cyan-cool zenith desaturating into a pale cloud-grey haze line by day — giving way to a warm apricot/peach alpenglow at sunrise/sunset, clean cool-cyan night.',
    keyframes=_ALPINE_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.14),
)


# ── 9. Cool Eucalyptus — pale sage-cyan day, kept COOL (not foliage), slate night ─
# The sage/eucalyptus direction steered firmly COOL so it never competes with
# foliage green: a hazy desaturated sage-cyan (clearly blue-green, not leaf
# green) zenith over a paler dust-sage horizon by day. Soft, dry, herbal.
# Sunrise/sunset signature: the dust-sage warms through a gold-green into a low
# apricot bloom in sky_bot and the mid, the cool grey-blue zenith holding above
# so the warmth stays a ground-glow (off the bird zone). Held wide via 0.44/0.56
# (sunset) and 0.84/0.90 (sunrise) keyframes.
_EUCALYPTUS_KF = [
    (0.06, dict(sky_top=(104, 128, 162), sky_mid=(160, 180, 196), sky_bot=(202, 214, 200), horizon=(216, 220, 192), star_alpha=0)),
    (0.18, dict(sky_top=(106, 132, 168), sky_mid=(164, 184, 200), sky_bot=(204, 216, 200), horizon=(218, 222, 192), star_alpha=0)),
    (0.30, dict(sky_top=(108, 130, 164), sky_mid=(166, 182, 196), sky_bot=(206, 214, 196), horizon=(218, 218, 188), star_alpha=0)),
    (0.40, dict(sky_top=(104, 124, 156), sky_mid=(174, 178, 178), sky_bot=(224, 206, 158), horizon=(244, 198, 132), star_alpha=0)),
    (0.44, dict(sky_top=(98, 116, 152), sky_mid=(180, 174, 168), sky_bot=(234, 198, 142), horizon=(250, 186, 116), star_alpha=0)),
    (0.50, dict(sky_top=(88, 104, 144), sky_mid=(178, 166, 160), sky_bot=(238, 188, 132), horizon=(250, 174, 106), star_alpha=12)),
    (0.56, dict(sky_top=(70, 88, 128), sky_mid=(152, 150, 152), sky_bot=(222, 178, 132), horizon=(238, 166, 108), star_alpha=28)),
    (0.62, dict(sky_top=(46, 66, 102), sky_mid=(98, 118, 138), sky_bot=(176, 168, 144), horizon=(218, 178, 136), star_alpha=78)),
    (0.72, dict(sky_top=(12, 26, 52), sky_mid=(24, 58, 80), sky_bot=(48, 102, 100), horizon=(92, 146, 126), star_alpha=200)),
    (0.80, dict(sky_top=(18, 34, 62), sky_mid=(38, 74, 92), sky_bot=(96, 122, 108), horizon=(196, 158, 124), star_alpha=118)),
    (0.84, dict(sky_top=(36, 54, 88), sky_mid=(84, 110, 124), sky_bot=(178, 158, 132), horizon=(240, 168, 110), star_alpha=64)),
    (0.88, dict(sky_top=(88, 114, 148), sky_mid=(160, 174, 178), sky_bot=(216, 200, 158), horizon=(246, 184, 120), star_alpha=20)),
    (0.90, dict(sky_top=(96, 122, 156), sky_mid=(160, 180, 188), sky_bot=(212, 206, 174), horizon=(240, 196, 144), star_alpha=12)),
    (0.94, dict(sky_top=(102, 126, 160), sky_mid=(158, 180, 196), sky_bot=(204, 214, 196), horizon=(224, 214, 184), star_alpha=0)),
]

COOL_EUCALYPTUS = BiomeSpec(
    name='Cool Eucalyptus',
    note='Grey-blue slate zenith with the eucalyptus sage confined to a low dust-sage horizon band — cool up high by day, warming through gold-green to a low apricot bloom at sunrise/sunset — to a deep slate-teal night.',
    keyframes=_EUCALYPTUS_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.60, 0.82, 1.0), dither_amp=2.2, zenith_dark=0.10),
)


# ── 10. Pearl Overcast — soft pearl-grey-blue day with low warmth, blue-grey night ─
# The "overcast pearl with warmth" brief, kept off neutral grey by a decisive
# cool-blue cast in the zenith/mid and a barely-warm cream wash low by day. The
# softest, most diffuse, lowest-contrast backdrop — overcast but luminous.
# Night is a saturated blue-grey, not black.
# Sunrise/sunset signature: the whole lower sky lifts to a luminous warm
# peach-grey glow that rises into the mid — soft and diffuse to match the
# overcast register (no hard band), the cool pearl zenith holding above. Held
# wide via 0.44/0.56 (sunset) and 0.84/0.90 (sunrise) keyframes.
_PEARL_KF = [
    (0.06, dict(sky_top=(140, 142, 170), sky_mid=(190, 192, 208), sky_bot=(218, 218, 222), horizon=(230, 224, 216), star_alpha=0)),
    (0.18, dict(sky_top=(144, 146, 176), sky_mid=(192, 196, 212), sky_bot=(220, 220, 224), horizon=(232, 226, 218), star_alpha=0)),
    (0.30, dict(sky_top=(142, 144, 174), sky_mid=(190, 194, 210), sky_bot=(218, 218, 222), horizon=(230, 224, 214), star_alpha=0)),
    (0.40, dict(sky_top=(138, 136, 166), sky_mid=(196, 184, 192), sky_bot=(238, 204, 188), horizon=(248, 196, 166), star_alpha=0)),
    (0.44, dict(sky_top=(132, 128, 162), sky_mid=(200, 178, 186), sky_bot=(244, 196, 178), horizon=(250, 188, 156), star_alpha=0)),
    (0.50, dict(sky_top=(122, 116, 156), sky_mid=(198, 170, 180), sky_bot=(246, 190, 172), horizon=(250, 182, 150), star_alpha=12)),
    (0.56, dict(sky_top=(100, 94, 138), sky_mid=(180, 156, 174), sky_bot=(234, 184, 172), horizon=(242, 180, 154), star_alpha=28)),
    (0.62, dict(sky_top=(66, 66, 110), sky_mid=(122, 120, 150), sky_bot=(192, 178, 184), horizon=(224, 188, 178), star_alpha=72)),
    (0.72, dict(sky_top=(28, 26, 58), sky_mid=(50, 54, 92), sky_bot=(86, 96, 126), horizon=(132, 142, 160), star_alpha=185)),
    (0.80, dict(sky_top=(38, 38, 76), sky_mid=(74, 74, 112), sky_bot=(140, 128, 148), horizon=(204, 174, 172), star_alpha=108)),
    (0.84, dict(sky_top=(58, 56, 100), sky_mid=(120, 112, 144), sky_bot=(200, 172, 174), horizon=(244, 184, 158), star_alpha=58)),
    (0.88, dict(sky_top=(124, 120, 158), sky_mid=(186, 176, 196), sky_bot=(228, 204, 198), horizon=(246, 192, 166), star_alpha=18)),
    (0.90, dict(sky_top=(132, 132, 164), sky_mid=(188, 186, 204), sky_bot=(224, 212, 210), horizon=(240, 204, 186), star_alpha=10)),
    (0.94, dict(sky_top=(140, 142, 172), sky_mid=(190, 192, 208), sky_bot=(218, 218, 222), horizon=(232, 220, 208), star_alpha=0)),
]

PEARL_OVERCAST = BiomeSpec(
    name='Pearl Overcast',
    note='Softest diffuse backdrop — pearl-grey-blue held cool by a decisive blue cast — lifting to a luminous warm peach-grey glow at sunrise/sunset, overcast but luminous, blue-grey night, never charcoal.',
    keyframes=_PEARL_KF,
    sky=SkyParams(positions=(0.0, 0.34, 0.62, 0.84, 1.0), dither_amp=2.4, zenith_dark=0.15),
)


# Ordered (id, spec) list — the 10 concept rows in sheet order.
CONCEPTS = [
    ('dawn_rose_grey', DAWN_ROSE_GREY),
    ('powder_morning', POWDER_MORNING),
    ('pale_amber_haze', PALE_AMBER_HAZE),
    ('misty_teal', MISTY_TEAL),
    ('slate_blue_hour', SLATE_BLUE_HOUR),
    ('lavender_dusk', LAVENDER_DUSK),
    ('starlit_navy', STARLIT_NAVY),
    ('alpine_haze', ALPINE_HAZE),
    ('cool_eucalyptus', COOL_EUCALYPTUS),
    ('pearl_overcast', PEARL_OVERCAST),
]
