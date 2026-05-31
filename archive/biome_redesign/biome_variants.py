"""
Biome candidate registry for the exploration sheet. Each biome is a BiomeSpec
(its own day-cycle keyframes + silhouette params + signature/foliage callbacks).
The 10 day-stage columns fall out of interpolating each biome's keyframes.

Round 0 ships ONE reference biome (desert_mesa) to prove the shared engine
before Groups A/B are authored.
"""
import scene_engine as se
from scene_engine import BiomeSpec, SkyParams, RidgeParams, GroundParams
import biome_motifs as bm


# ── The 10 day-stage columns (predawn → night arc), tunable in one place ──────
STAGES = [
    ("predawn",   0.80),
    ("dawn",      0.88),
    ("sunrise",   0.94),
    ("morning",   0.06),
    ("midday",    0.18),
    ("afternoon", 0.30),
    ("golden",    0.40),
    ("sunset",    0.50),
    ("dusk",      0.62),
    ("night",     0.70),
]


# ── Biome 1 — Desert Mesa (Group A reference) ─────────────────────────────────
_DESERT_KF = [
    (0.06, dict(  # morning
        sky_top=(55, 125, 205), sky_mid=(150, 195, 225), sky_bot=(215, 230, 238),
        horizon=(250, 238, 210),
        mtn_far=(186, 168, 156), mtn_mid=(172, 144, 120), mtn_near=(150, 116, 90),
        struct_light=(228, 198, 150), struct_mid=(192, 152, 106),
        struct_dark=(120, 86, 56), struct_accent=(165, 120, 80),
        ground_top=(214, 184, 124), ground_mid=(176, 142, 92), ground_bot=(120, 90, 56),
        star_alpha=0)),
    (0.18, dict(  # midday
        sky_top=(60, 120, 210), sky_mid=(132, 182, 226), sky_bot=(202, 226, 240),
        horizon=(246, 236, 206),
        mtn_far=(190, 172, 160), mtn_mid=(176, 148, 124), mtn_near=(154, 120, 94),
        struct_light=(232, 202, 154), struct_mid=(196, 156, 110),
        struct_dark=(124, 90, 60), struct_accent=(168, 124, 84),
        ground_top=(216, 186, 126), ground_mid=(178, 144, 94), ground_bot=(122, 92, 58),
        star_alpha=0)),
    (0.40, dict(  # golden
        sky_top=(96, 124, 190), sky_mid=(236, 182, 122), sky_bot=(255, 206, 150),
        horizon=(255, 222, 150),
        mtn_far=(196, 160, 150), mtn_mid=(186, 138, 108), mtn_near=(160, 108, 78),
        struct_light=(244, 196, 132), struct_mid=(208, 150, 92),
        struct_dark=(132, 84, 52), struct_accent=(184, 120, 70),
        ground_top=(224, 176, 110), ground_mid=(186, 134, 80), ground_bot=(124, 84, 50),
        star_alpha=0)),
    (0.50, dict(  # sunset
        sky_top=(110, 68, 122), sky_mid=(236, 110, 90), sky_bot=(255, 160, 92),
        horizon=(255, 192, 120),
        mtn_far=(150, 108, 130), mtn_mid=(150, 92, 96), mtn_near=(122, 70, 66),
        struct_light=(236, 158, 110), struct_mid=(196, 110, 78),
        struct_dark=(108, 60, 56), struct_accent=(176, 96, 70),
        ground_top=(200, 132, 92), ground_mid=(158, 98, 70), ground_bot=(104, 64, 46),
        star_alpha=0)),
    (0.62, dict(  # dusk
        sky_top=(40, 35, 82), sky_mid=(92, 60, 122), sky_bot=(182, 112, 120),
        horizon=(240, 162, 132),
        mtn_far=(96, 86, 124), mtn_mid=(86, 70, 100), mtn_near=(66, 52, 74),
        struct_light=(150, 116, 120), struct_mid=(118, 84, 92),
        struct_dark=(72, 50, 58), struct_accent=(104, 74, 80),
        ground_top=(130, 96, 96), ground_mid=(96, 70, 74), ground_bot=(70, 52, 52),
        star_alpha=40)),
    (0.70, dict(  # night
        sky_top=(10, 14, 40), sky_mid=(22, 32, 70), sky_bot=(46, 60, 100),
        horizon=(120, 122, 150),
        mtn_far=(40, 48, 78), mtn_mid=(34, 40, 64), mtn_near=(26, 30, 50),
        struct_light=(96, 100, 120), struct_mid=(62, 66, 84),
        struct_dark=(36, 40, 56), struct_accent=(74, 78, 98),
        ground_top=(48, 56, 78), ground_mid=(36, 42, 60), ground_bot=(26, 30, 44),
        glow_color=(210, 220, 255), star_alpha=210)),
    (0.80, dict(  # predawn
        sky_top=(26, 30, 72), sky_mid=(52, 56, 112), sky_bot=(114, 92, 142),
        horizon=(202, 152, 162),
        mtn_far=(70, 70, 108), mtn_mid=(58, 56, 88), mtn_near=(44, 42, 66),
        struct_light=(132, 116, 130), struct_mid=(98, 82, 96),
        struct_dark=(58, 48, 62), struct_accent=(86, 72, 86),
        ground_top=(96, 84, 100), ground_mid=(72, 62, 78), ground_bot=(52, 46, 58),
        glow_color=(255, 200, 200), star_alpha=110)),
    (0.94, dict(  # sunrise
        sky_top=(70, 110, 180), sky_mid=(255, 166, 140), sky_bot=(255, 216, 166),
        horizon=(255, 236, 182),
        mtn_far=(196, 162, 158), mtn_mid=(190, 142, 124), mtn_near=(166, 116, 92),
        struct_light=(248, 198, 150), struct_mid=(212, 152, 104),
        struct_dark=(132, 86, 58), struct_accent=(188, 122, 78),
        ground_top=(226, 184, 124), ground_mid=(188, 142, 90), ground_bot=(126, 90, 56),
        star_alpha=0)),
]

DESERT_MESA = BiomeSpec(
    name="Desert Mesa",
    note="Flat-topped sandstone buttes + eroded arch over rolling dunes; bone-dry warm palette.",
    keyframes=_DESERT_KF,
    sky=SkyParams(positions=(0.0, 0.28, 0.58, 0.84, 1.0), dither_amp=2.2, zenith_dark=0.05),
    ridges=[
        RidgeParams(base_h=0.16, octaves=((0.008, 18), (0.020, 10)), parallax=0.06,
                    color_key='mtn_far', seed=1),
        RidgeParams(base_h=0.20, octaves=((0.012, 22),), parallax=0.14,
                    color_key='mtn_mid', flat_top=14, seed=3),
        RidgeParams(base_h=0.12, octaves=((0.015, 14),), parallax=0.26,
                    color_key='mtn_near', flat_top=18, seed=5),
    ],
    signature=bm.draw_mesa_arch,
    foliage=None,
    ground=GroundParams(),
)


# ── registry ──────────────────────────────────────────────────────────────────
BIOMES = {
    "desert_mesa": DESERT_MESA,
}
GROUP_A = ["desert_mesa"]
GROUP_B = []
BIOME_NAMES = {k: v.name for k, v in BIOMES.items()}
BIOME_NOTES = {k: v.note for k, v in BIOMES.items()}
