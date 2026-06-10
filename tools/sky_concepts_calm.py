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
_ROSEGREY_KF = [
    (0.06, dict(sky_top=(96, 110, 140), sky_mid=(150, 156, 174), sky_bot=(206, 190, 192), horizon=(224, 196, 188), star_alpha=0)),
    (0.18, dict(sky_top=(104, 122, 152), sky_mid=(158, 168, 186), sky_bot=(208, 200, 200), horizon=(222, 204, 196), star_alpha=0)),
    (0.30, dict(sky_top=(100, 116, 148), sky_mid=(152, 162, 182), sky_bot=(204, 194, 196), horizon=(220, 196, 190), star_alpha=0)),
    (0.40, dict(sky_top=(110, 116, 146), sky_mid=(168, 160, 174), sky_bot=(218, 192, 190), horizon=(232, 192, 178), star_alpha=0)),
    (0.50, dict(sky_top=(96, 100, 136), sky_mid=(158, 138, 158), sky_bot=(218, 174, 174), horizon=(238, 184, 162), star_alpha=12)),
    (0.62, dict(sky_top=(60, 66, 104), sky_mid=(104, 100, 138), sky_bot=(160, 138, 158), horizon=(202, 166, 168), star_alpha=70)),
    (0.72, dict(sky_top=(26, 28, 56), sky_mid=(48, 48, 84), sky_bot=(78, 72, 110), horizon=(120, 100, 130), star_alpha=190)),
    (0.80, dict(sky_top=(38, 40, 74), sky_mid=(72, 70, 110), sky_bot=(118, 106, 140), horizon=(176, 148, 162), star_alpha=110)),
    (0.88, dict(sky_top=(84, 96, 138), sky_mid=(150, 150, 176), sky_bot=(212, 188, 192), horizon=(238, 192, 182), star_alpha=18)),
    (0.94, dict(sky_top=(96, 110, 142), sky_mid=(154, 160, 180), sky_bot=(210, 192, 194), horizon=(230, 196, 188), star_alpha=0)),
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
_POWDER_KF = [
    (0.06, dict(sky_top=(78, 138, 204), sky_mid=(132, 184, 226), sky_bot=(192, 218, 238), horizon=(220, 232, 240), star_alpha=0)),
    (0.18, dict(sky_top=(82, 144, 212), sky_mid=(136, 190, 230), sky_bot=(196, 222, 240), horizon=(224, 234, 240), star_alpha=0)),
    (0.30, dict(sky_top=(86, 142, 206), sky_mid=(140, 188, 226), sky_bot=(200, 220, 236), horizon=(228, 230, 234), star_alpha=0)),
    (0.40, dict(sky_top=(88, 134, 196), sky_mid=(146, 180, 216), sky_bot=(206, 214, 224), horizon=(236, 222, 210), star_alpha=0)),
    (0.50, dict(sky_top=(74, 110, 174), sky_mid=(140, 154, 196), sky_bot=(206, 196, 206), horizon=(238, 206, 188), star_alpha=12)),
    (0.62, dict(sky_top=(40, 64, 124), sky_mid=(74, 110, 162), sky_bot=(132, 162, 192), horizon=(190, 198, 202), star_alpha=80)),
    (0.72, dict(sky_top=(12, 22, 60), sky_mid=(22, 48, 100), sky_bot=(38, 80, 130), horizon=(70, 118, 156), star_alpha=210)),
    (0.80, dict(sky_top=(18, 32, 78), sky_mid=(34, 70, 124), sky_bot=(60, 110, 152), horizon=(108, 152, 178), star_alpha=130)),
    (0.88, dict(sky_top=(60, 116, 186), sky_mid=(120, 170, 216), sky_bot=(188, 212, 230), horizon=(228, 224, 216), star_alpha=22)),
    (0.94, dict(sky_top=(76, 136, 202), sky_mid=(130, 184, 226), sky_bot=(192, 218, 236), horizon=(224, 230, 234), star_alpha=0)),
]

POWDER_MORNING = BiomeSpec(
    name='Powder Morning',
    note='Clean powder-blue clear day — deepened cornflower zenith, pale calm horizon — easing to a gentle cool dusk and a deep navy night.',
    keyframes=_POWDER_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.12),
)


# ── 3. Pale Amber Haze — warm-neutral hazy afternoon, cool zenith, indigo night ─
# The one row that owns a warm daytime read, kept UX-safe: the warmth lives only
# in the LOWER half (pale amber/sand horizon), the zenith stays a cool dusty
# blue, so the bird zone never goes warm. Hazy, sun-through-dust afternoon.
_AMBER_KF = [
    (0.06, dict(sky_top=(108, 142, 178), sky_mid=(176, 188, 192), sky_bot=(226, 214, 184), horizon=(238, 220, 178), star_alpha=0)),
    (0.18, dict(sky_top=(114, 150, 186), sky_mid=(182, 194, 196), sky_bot=(230, 218, 184), horizon=(242, 222, 176), star_alpha=0)),
    (0.30, dict(sky_top=(116, 146, 180), sky_mid=(184, 192, 190), sky_bot=(232, 214, 176), horizon=(244, 218, 166), star_alpha=0)),
    (0.40, dict(sky_top=(120, 140, 172), sky_mid=(192, 188, 178), sky_bot=(238, 212, 166), horizon=(248, 212, 152), star_alpha=0)),
    (0.50, dict(sky_top=(104, 116, 156), sky_mid=(186, 168, 162), sky_bot=(240, 200, 156), horizon=(248, 196, 138), star_alpha=12)),
    (0.62, dict(sky_top=(56, 64, 104), sky_mid=(116, 108, 124), sky_bot=(186, 162, 142), horizon=(224, 184, 142), star_alpha=78)),
    (0.72, dict(sky_top=(20, 22, 52), sky_mid=(44, 42, 72), sky_bot=(88, 76, 88), horizon=(146, 116, 100), star_alpha=195)),
    (0.80, dict(sky_top=(32, 32, 66), sky_mid=(70, 62, 90), sky_bot=(132, 110, 110), horizon=(200, 162, 130), star_alpha=115)),
    (0.88, dict(sky_top=(98, 124, 166), sky_mid=(176, 178, 180), sky_bot=(232, 210, 174), horizon=(246, 212, 162), star_alpha=20)),
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
_TEAL_KF = [
    (0.06, dict(sky_top=(58, 128, 144), sky_mid=(112, 176, 178), sky_bot=(176, 210, 200), horizon=(206, 224, 208), star_alpha=0)),
    (0.18, dict(sky_top=(54, 134, 152), sky_mid=(108, 182, 184), sky_bot=(172, 214, 202), horizon=(204, 226, 208), star_alpha=0)),
    (0.30, dict(sky_top=(58, 130, 146), sky_mid=(114, 178, 178), sky_bot=(178, 212, 198), horizon=(208, 224, 204), star_alpha=0)),
    (0.40, dict(sky_top=(62, 122, 140), sky_mid=(122, 170, 172), sky_bot=(186, 206, 192), horizon=(218, 216, 192), star_alpha=0)),
    (0.50, dict(sky_top=(56, 100, 128), sky_mid=(124, 150, 162), sky_bot=(196, 192, 184), horizon=(232, 200, 168), star_alpha=12)),
    (0.62, dict(sky_top=(28, 60, 92), sky_mid=(56, 110, 126), sky_bot=(110, 158, 158), horizon=(170, 192, 178), star_alpha=80)),
    (0.72, dict(sky_top=(6, 26, 48), sky_mid=(14, 60, 78), sky_bot=(28, 98, 104), horizon=(60, 134, 124), star_alpha=205)),
    (0.80, dict(sky_top=(10, 34, 58), sky_mid=(24, 78, 96), sky_bot=(48, 124, 124), horizon=(102, 162, 150), star_alpha=120)),
    (0.88, dict(sky_top=(46, 116, 136), sky_mid=(100, 172, 176), sky_bot=(170, 210, 198), horizon=(208, 224, 202), star_alpha=20)),
    (0.94, dict(sky_top=(56, 126, 144), sky_mid=(110, 178, 180), sky_bot=(176, 212, 200), horizon=(206, 224, 206), star_alpha=0)),
]

MISTY_TEAL = BiomeSpec(
    name='Misty Teal',
    note='Soft sea-mist teal day kept clearly teal (not green, not plain blue), through a muted aqua dusk to a saturated-dark teal night.',
    keyframes=_TEAL_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.60, 0.82, 1.0), dither_amp=2.0, zenith_dark=0.10),
)


# ── 5. Slate Blue-Hour — the pure Alto blue-hour, deep slate all cycle ────────
# The most recessive concept: a perpetual cool slate-blue that only shifts value
# across the day, with a single faint warm horizon ember at sunset. The maximum-
# RECEDE option — backdrop as pure negative space for the foreground.
_SLATE_KF = [
    (0.06, dict(sky_top=(72, 96, 138), sky_mid=(120, 146, 178), sky_bot=(176, 196, 214), horizon=(204, 216, 224), star_alpha=0)),
    (0.18, dict(sky_top=(78, 104, 148), sky_mid=(126, 154, 186), sky_bot=(182, 202, 218), horizon=(210, 220, 226), star_alpha=0)),
    (0.30, dict(sky_top=(74, 100, 144), sky_mid=(122, 150, 182), sky_bot=(178, 198, 214), horizon=(206, 216, 222), star_alpha=0)),
    (0.40, dict(sky_top=(70, 92, 134), sky_mid=(120, 142, 172), sky_bot=(180, 192, 204), horizon=(214, 210, 206), star_alpha=0)),
    (0.50, dict(sky_top=(62, 78, 122), sky_mid=(118, 128, 162), sky_bot=(184, 180, 192), horizon=(226, 198, 178), star_alpha=12)),
    (0.62, dict(sky_top=(36, 50, 92), sky_mid=(68, 90, 132), sky_bot=(120, 148, 178), horizon=(176, 192, 200), star_alpha=85)),
    (0.72, dict(sky_top=(10, 18, 50), sky_mid=(20, 40, 84), sky_bot=(36, 70, 114), horizon=(66, 106, 146), star_alpha=215)),
    (0.80, dict(sky_top=(16, 28, 66), sky_mid=(30, 58, 104), sky_bot=(54, 96, 138), horizon=(100, 142, 172), star_alpha=135)),
    (0.88, dict(sky_top=(56, 84, 130), sky_mid=(108, 138, 176), sky_bot=(172, 196, 214), horizon=(208, 216, 222), star_alpha=22)),
    (0.94, dict(sky_top=(70, 96, 138), sky_mid=(118, 146, 180), sky_bot=(176, 198, 216), horizon=(204, 216, 224), star_alpha=0)),
]

SLATE_BLUE_HOUR = BiomeSpec(
    name='Slate Blue-Hour',
    note='Pure recessive Alto blue-hour — a perpetual cool slate-blue that shifts only in value, with one faint warm horizon ember at sunset. Maximum recede.',
    keyframes=_SLATE_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.14),
)


# ── 6. Lavender Dusk — muted lilac-violet day, dove-grey-violet dusk, plum night ─
# A restrained lavender that holds its violet identity at low chroma: a soft
# grey-violet zenith over a paler lilac mid, the warmth (a faint rose) kept at
# the horizon only. Plum-saturated night. Distinct from Rose-Grey by leaning
# cooler/bluer-violet rather than rose.
_LAVENDER_KF = [
    (0.06, dict(sky_top=(110, 110, 168), sky_mid=(162, 158, 198), sky_bot=(204, 196, 218), horizon=(218, 200, 210), star_alpha=0)),
    (0.18, dict(sky_top=(116, 116, 176), sky_mid=(168, 164, 204), sky_bot=(208, 200, 222), horizon=(220, 204, 214), star_alpha=0)),
    (0.30, dict(sky_top=(112, 112, 172), sky_mid=(164, 160, 200), sky_bot=(206, 196, 218), horizon=(216, 198, 210), star_alpha=0)),
    (0.40, dict(sky_top=(116, 110, 168), sky_mid=(172, 158, 192), sky_bot=(214, 194, 210), horizon=(228, 196, 200), star_alpha=0)),
    (0.50, dict(sky_top=(104, 92, 156), sky_mid=(166, 140, 178), sky_bot=(218, 184, 196), horizon=(236, 190, 178), star_alpha=12)),
    (0.62, dict(sky_top=(60, 50, 106), sky_mid=(108, 90, 146), sky_bot=(164, 138, 174), horizon=(206, 174, 180), star_alpha=78)),
    (0.72, dict(sky_top=(24, 18, 58), sky_mid=(50, 38, 90), sky_bot=(86, 64, 118), horizon=(128, 96, 138), star_alpha=200)),
    (0.80, dict(sky_top=(36, 28, 74), sky_mid=(74, 56, 112), sky_bot=(124, 96, 146), horizon=(184, 144, 170), star_alpha=115)),
    (0.88, dict(sky_top=(100, 100, 162), sky_mid=(158, 152, 196), sky_bot=(208, 196, 218), horizon=(226, 200, 208), star_alpha=20)),
    (0.94, dict(sky_top=(110, 112, 170), sky_mid=(162, 160, 200), sky_bot=(204, 198, 220), horizon=(218, 202, 212), star_alpha=0)),
]

LAVENDER_DUSK = BiomeSpec(
    name='Lavender Dusk',
    note='Muted lilac-violet day holding its hue at low chroma — soft grey-violet zenith, faint rose horizon — deepening to a plum-saturated night.',
    keyframes=_LAVENDER_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.60, 0.82, 1.0), dither_amp=2.0, zenith_dark=0.10),
)


# ── 7. Starlit Navy — deep cool navy day, ultramarine dusk, galaxy night ──────
# The deepest, coolest, most night-leaning row — a permanently dusk-blue sky
# that stays gorgeous and saturated-dark, carrying a faint starfield even by
# day. Owns the "deep starlit navy" win from the vivid set, kept restrained:
# rich but never neon, the strongest starfield of the band.
_NAVY_KF = [
    (0.06, dict(sky_top=(34, 60, 124), sky_mid=(58, 102, 168), sky_bot=(110, 156, 198), horizon=(160, 196, 216), star_alpha=30)),
    (0.18, dict(sky_top=(32, 66, 134), sky_mid=(54, 110, 178), sky_bot=(104, 162, 204), horizon=(154, 200, 220), star_alpha=22)),
    (0.30, dict(sky_top=(36, 62, 128), sky_mid=(60, 106, 172), sky_bot=(112, 158, 200), horizon=(162, 196, 216), star_alpha=20)),
    (0.40, dict(sky_top=(38, 56, 118), sky_mid=(70, 98, 158), sky_bot=(128, 150, 190), horizon=(184, 196, 210), star_alpha=18)),
    (0.50, dict(sky_top=(36, 46, 108), sky_mid=(78, 82, 146), sky_bot=(150, 138, 176), horizon=(216, 184, 176), star_alpha=28)),
    (0.62, dict(sky_top=(20, 30, 80), sky_mid=(38, 62, 120), sky_bot=(78, 116, 162), horizon=(140, 174, 192), star_alpha=120)),
    (0.72, dict(sky_top=(6, 10, 44), sky_mid=(12, 28, 80), sky_bot=(24, 58, 116), horizon=(50, 100, 150), star_alpha=240)),
    (0.80, dict(sky_top=(8, 16, 56), sky_mid=(20, 44, 100), sky_bot=(40, 86, 142), horizon=(88, 138, 176), star_alpha=160)),
    (0.88, dict(sky_top=(28, 50, 110), sky_mid=(50, 96, 164), sky_bot=(104, 156, 198), horizon=(160, 198, 216), star_alpha=50)),
    (0.94, dict(sky_top=(34, 58, 122), sky_mid=(56, 102, 168), sky_bot=(110, 156, 198), horizon=(160, 196, 216), star_alpha=34)),
]

STARLIT_NAVY = BiomeSpec(
    name='Starlit Navy',
    note='Deep cool navy by day that never goes near-white — ultramarine dusk, the band\'s densest galaxy night — rich, recessive, never neon.',
    keyframes=_NAVY_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.80, 1.0), dither_amp=1.6, zenith_dark=0.18),
)


# ── 8. Alpine Haze — cool high-altitude haze day, periwinkle dusk, deep blue night ─
# The thin-air high-altitude register grounded in cloud-blue #A2B6B9: a deep
# clean cobalt zenith fading to a hazy cool-grey-blue horizon (the haze line of
# distant peaks). Crisp and airy, the horizon paler/cooler than Powder Morning,
# with a clean cool-blue night.
_ALPINE_KF = [
    (0.06, dict(sky_top=(56, 110, 184), sky_mid=(116, 162, 204), sky_bot=(172, 196, 210), horizon=(198, 212, 216), star_alpha=0)),
    (0.18, dict(sky_top=(52, 116, 194), sky_mid=(112, 168, 210), sky_bot=(170, 200, 214), horizon=(198, 214, 218), star_alpha=0)),
    (0.30, dict(sky_top=(58, 112, 186), sky_mid=(118, 164, 204), sky_bot=(176, 196, 210), horizon=(202, 212, 214), star_alpha=0)),
    (0.40, dict(sky_top=(58, 104, 174), sky_mid=(122, 154, 194), sky_bot=(182, 192, 204), horizon=(210, 210, 210), star_alpha=0)),
    (0.50, dict(sky_top=(52, 84, 152), sky_mid=(118, 134, 182), sky_bot=(186, 184, 200), horizon=(224, 200, 188), star_alpha=12)),
    (0.62, dict(sky_top=(28, 46, 104), sky_mid=(62, 96, 152), sky_bot=(118, 152, 184), horizon=(178, 192, 200), star_alpha=80)),
    (0.72, dict(sky_top=(8, 16, 52), sky_mid=(16, 42, 96), sky_bot=(32, 76, 126), horizon=(64, 116, 158), star_alpha=210)),
    (0.80, dict(sky_top=(12, 26, 68), sky_mid=(26, 60, 116), sky_bot=(50, 102, 148), horizon=(98, 148, 180), star_alpha=130)),
    (0.88, dict(sky_top=(46, 96, 168), sky_mid=(104, 154, 200), sky_bot=(166, 194, 210), horizon=(200, 212, 214), star_alpha=20)),
    (0.94, dict(sky_top=(54, 108, 182), sky_mid=(114, 162, 204), sky_bot=(172, 196, 210), horizon=(198, 212, 216), star_alpha=0)),
]

ALPINE_HAZE = BiomeSpec(
    name='Alpine Haze',
    note='Thin high-altitude air — deep clean cobalt zenith fading to a cool cloud-blue haze line at the horizon — crisp, airy, clean cool-blue night.',
    keyframes=_ALPINE_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.14),
)


# ── 9. Cool Eucalyptus — pale sage-cyan day, kept COOL (not foliage), slate night ─
# The sage/eucalyptus direction steered firmly COOL so it never competes with
# foliage green: a hazy desaturated sage-cyan (clearly blue-green, not leaf
# green) zenith over a paler dust-sage horizon. Soft, dry, herbal. The chroma is
# low and the hue sits past cyan toward blue at the top to stay off-foliage.
_EUCALYPTUS_KF = [
    (0.06, dict(sky_top=(96, 150, 158), sky_mid=(154, 192, 184), sky_bot=(198, 216, 198), horizon=(214, 222, 200), star_alpha=0)),
    (0.18, dict(sky_top=(98, 156, 166), sky_mid=(158, 198, 190), sky_bot=(200, 220, 200), horizon=(216, 224, 200), star_alpha=0)),
    (0.30, dict(sky_top=(100, 152, 160), sky_mid=(160, 194, 186), sky_bot=(202, 216, 196), horizon=(216, 220, 196), star_alpha=0)),
    (0.40, dict(sky_top=(100, 144, 154), sky_mid=(162, 186, 178), sky_bot=(206, 212, 190), horizon=(222, 216, 188), star_alpha=0)),
    (0.50, dict(sky_top=(88, 120, 142), sky_mid=(158, 166, 168), sky_bot=(210, 200, 182), horizon=(232, 204, 174), star_alpha=12)),
    (0.62, dict(sky_top=(44, 70, 96), sky_mid=(86, 124, 134), sky_bot=(146, 174, 166), horizon=(196, 204, 184), star_alpha=78)),
    (0.72, dict(sky_top=(12, 28, 46), sky_mid=(24, 64, 76), sky_bot=(46, 104, 102), horizon=(86, 144, 130), star_alpha=200)),
    (0.80, dict(sky_top=(18, 36, 56), sky_mid=(36, 80, 92), sky_bot=(66, 126, 122), horizon=(124, 168, 152), star_alpha=118)),
    (0.88, dict(sky_top=(84, 138, 150), sky_mid=(146, 188, 182), sky_bot=(196, 216, 198), horizon=(214, 222, 200), star_alpha=20)),
    (0.94, dict(sky_top=(94, 148, 158), sky_mid=(152, 192, 184), sky_bot=(198, 216, 198), horizon=(214, 222, 200), star_alpha=0)),
]

COOL_EUCALYPTUS = BiomeSpec(
    name='Cool Eucalyptus',
    note='Hazy pale sage-cyan day steered COOL (clearly blue-green, never leaf green) over a dust-sage horizon — soft, dry, herbal — to a deep slate-teal night.',
    keyframes=_EUCALYPTUS_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.60, 0.82, 1.0), dither_amp=2.2, zenith_dark=0.10),
)


# ── 10. Pearl Overcast — soft pearl-grey-blue day with low warmth, blue-grey night ─
# The "overcast pearl with warmth" brief, kept off neutral grey by a decisive
# cool-blue cast in the zenith/mid and a single barely-warm cream wash low at
# the horizon. The softest, most diffuse, lowest-contrast backdrop — overcast
# but luminous, never flat charcoal. Night is a saturated blue-grey, not black.
_PEARL_KF = [
    (0.06, dict(sky_top=(118, 142, 172), sky_mid=(174, 192, 206), sky_bot=(214, 220, 220), horizon=(230, 226, 214), star_alpha=0)),
    (0.18, dict(sky_top=(122, 148, 180), sky_mid=(178, 198, 212), sky_bot=(216, 222, 222), horizon=(232, 228, 216), star_alpha=0)),
    (0.30, dict(sky_top=(120, 144, 176), sky_mid=(176, 194, 208), sky_bot=(214, 220, 218), horizon=(230, 224, 212), star_alpha=0)),
    (0.40, dict(sky_top=(120, 138, 168), sky_mid=(178, 190, 200), sky_bot=(218, 218, 212), horizon=(236, 222, 204), star_alpha=0)),
    (0.50, dict(sky_top=(106, 118, 156), sky_mid=(174, 174, 192), sky_bot=(220, 208, 202), horizon=(240, 212, 188), star_alpha=12)),
    (0.62, dict(sky_top=(56, 68, 108), sky_mid=(108, 124, 152), sky_bot=(170, 184, 192), horizon=(212, 212, 204), star_alpha=72)),
    (0.72, dict(sky_top=(20, 26, 56), sky_mid=(42, 54, 90), sky_bot=(78, 96, 124), horizon=(126, 142, 158), star_alpha=185)),
    (0.80, dict(sky_top=(30, 38, 72), sky_mid=(62, 76, 112), sky_bot=(116, 132, 152), horizon=(186, 188, 184), star_alpha=108)),
    (0.88, dict(sky_top=(106, 130, 164), sky_mid=(168, 188, 204), sky_bot=(214, 220, 218), horizon=(232, 224, 210), star_alpha=18)),
    (0.94, dict(sky_top=(118, 142, 174), sky_mid=(174, 194, 208), sky_bot=(214, 220, 220), horizon=(230, 226, 214), star_alpha=0)),
]

PEARL_OVERCAST = BiomeSpec(
    name='Pearl Overcast',
    note='Softest diffuse backdrop — pearl-grey-blue held cool by a decisive blue cast with one barely-warm cream wash low — overcast but luminous, blue-grey night, never charcoal.',
    keyframes=_PEARL_KF,
    sky=SkyParams(positions=(0.0, 0.34, 0.62, 0.84, 1.0), dither_amp=2.4, zenith_dark=0.09),
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
