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
from game.pillar_variants import draw_pine_trio, draw_cairn
from game.draw import draw_wuling_pine, draw_side_shrub


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
        # Mid + near both quantize to plateaus but at different step sizes and
        # extra low-freq octaves, so the buttes vary in width/height + carry a
        # stepped bench rather than reading as a row of equal rectangles.
        RidgeParams(base_h=0.20, octaves=((0.012, 22), (0.005, 12)), parallax=0.14,
                    color_key='mtn_mid', flat_top=14, seed=3),
        RidgeParams(base_h=0.12, octaves=((0.015, 14), (0.006, 9)), parallax=0.26,
                    color_key='mtn_near', flat_top=20, seed=5),
    ],
    signature=bm.draw_mesa_arch,
    foliage=None,
    ground=GroundParams(),
)


# ── Biome 2 — Alpine Snowpeak ─────────────────────────────────────────────────
# Tall jagged snow-capped granite; cold blue-white, crisp high-altitude air.
_ALPINE_KF = [
    (0.06, dict(  # morning — pale glacier-blue sky
        sky_top=(78, 140, 210), sky_mid=(150, 196, 232), sky_bot=(210, 232, 244),
        horizon=(232, 240, 246),
        mtn_far=(150, 168, 196), mtn_mid=(120, 140, 172), mtn_near=(92, 110, 144),
        struct_light=(238, 244, 252), struct_mid=(150, 164, 188),
        struct_dark=(86, 100, 128), struct_accent=(120, 138, 170),
        foliage_top=(70, 112, 92), foliage_mid=(44, 84, 68), foliage_dark=(26, 56, 46),
        foliage_accent=(110, 150, 120),
        ground_top=(196, 214, 224), ground_mid=(150, 172, 190), ground_bot=(96, 118, 142),
        snow_tint=(244, 248, 254), star_alpha=0)),
    (0.18, dict(  # midday — strongest light, deep zenith
        sky_top=(58, 128, 214), sky_mid=(138, 190, 232), sky_bot=(206, 230, 244),
        horizon=(228, 238, 246),
        mtn_far=(152, 170, 200), mtn_mid=(122, 142, 176), mtn_near=(92, 112, 148),
        struct_light=(244, 248, 255), struct_mid=(154, 168, 194),
        struct_dark=(88, 102, 132), struct_accent=(124, 142, 176),
        foliage_top=(72, 116, 94), foliage_mid=(46, 86, 70), foliage_dark=(26, 56, 46),
        foliage_accent=(112, 152, 122),
        ground_top=(202, 220, 230), ground_mid=(152, 176, 194), ground_bot=(98, 120, 146),
        snow_tint=(248, 252, 255), star_alpha=0)),
    (0.40, dict(  # golden — alpenglow warming the snow
        sky_top=(110, 150, 206), sky_mid=(232, 200, 176), sky_bot=(255, 222, 188),
        horizon=(255, 226, 192),
        mtn_far=(178, 168, 188), mtn_mid=(160, 142, 158), mtn_near=(128, 110, 130),
        struct_light=(255, 230, 210), struct_mid=(196, 176, 184),
        struct_dark=(110, 100, 122), struct_accent=(190, 150, 140),
        foliage_top=(78, 110, 86), foliage_mid=(48, 80, 64), foliage_dark=(28, 52, 44),
        foliage_accent=(120, 148, 118),
        ground_top=(228, 214, 206), ground_mid=(176, 166, 174), ground_bot=(110, 110, 132),
        snow_tint=(255, 232, 214), star_alpha=0)),
    (0.50, dict(  # sunset — rose alpenglow on cooling rock
        sky_top=(96, 96, 150), sky_mid=(228, 140, 132), sky_bot=(255, 178, 150),
        horizon=(255, 198, 168),
        mtn_far=(150, 130, 160), mtn_mid=(134, 108, 134), mtn_near=(102, 82, 108),
        struct_light=(255, 206, 196), struct_mid=(178, 150, 168),
        struct_dark=(92, 80, 108), struct_accent=(186, 130, 132),
        foliage_top=(64, 88, 76), foliage_mid=(40, 64, 56), foliage_dark=(24, 44, 40),
        foliage_accent=(100, 122, 104),
        ground_top=(206, 180, 184), ground_mid=(150, 134, 152), ground_bot=(96, 92, 118),
        snow_tint=(255, 208, 196), star_alpha=20)),
    (0.62, dict(  # dusk — blue hour, snow holds last light
        sky_top=(40, 48, 96), sky_mid=(86, 86, 140), sky_bot=(150, 130, 158),
        horizon=(204, 168, 168),
        mtn_far=(86, 96, 134), mtn_mid=(70, 78, 116), mtn_near=(52, 60, 92),
        struct_light=(196, 200, 224), struct_mid=(120, 130, 164),
        struct_dark=(64, 72, 104), struct_accent=(140, 140, 170),
        foliage_top=(44, 62, 62), foliage_mid=(28, 44, 48), foliage_dark=(18, 30, 38),
        foliage_accent=(70, 88, 84),
        ground_top=(140, 148, 172), ground_mid=(98, 108, 138), ground_bot=(60, 70, 100),
        snow_tint=(206, 212, 234), star_alpha=70)),
    (0.70, dict(  # night — moonlit snow is the hero, cool rim on rock
        sky_top=(10, 16, 44), sky_mid=(22, 34, 72), sky_bot=(44, 60, 100),
        horizon=(110, 124, 158),
        mtn_far=(40, 52, 86), mtn_mid=(32, 42, 72), mtn_near=(24, 32, 56),
        struct_light=(168, 184, 218), struct_mid=(86, 100, 138),
        struct_dark=(42, 52, 84), struct_accent=(110, 126, 166),
        foliage_top=(34, 50, 56), foliage_mid=(22, 34, 42), foliage_dark=(14, 22, 30),
        foliage_accent=(54, 72, 74),
        ground_top=(96, 112, 146), ground_mid=(62, 76, 110), ground_bot=(36, 46, 74),
        snow_tint=(176, 192, 226), glow_color=(200, 220, 255), star_alpha=215)),
    (0.80, dict(  # predawn — cold violet, faint star wash
        sky_top=(26, 32, 78), sky_mid=(54, 60, 116), sky_bot=(112, 110, 154),
        horizon=(184, 162, 176),
        mtn_far=(66, 74, 114), mtn_mid=(52, 58, 96), mtn_near=(40, 44, 74),
        struct_light=(192, 196, 224), struct_mid=(116, 126, 162),
        struct_dark=(58, 66, 100), struct_accent=(134, 138, 172),
        foliage_top=(40, 56, 60), foliage_mid=(26, 40, 46), foliage_dark=(16, 26, 34),
        foliage_accent=(64, 82, 80),
        ground_top=(132, 138, 166), ground_mid=(92, 100, 134), ground_bot=(56, 64, 96),
        snow_tint=(204, 208, 232), glow_color=(210, 222, 255), star_alpha=120)),
    (0.94, dict(  # sunrise — first warm light on the ridge
        sky_top=(84, 142, 206), sky_mid=(248, 196, 184), sky_bot=(255, 220, 196),
        horizon=(255, 228, 202),
        mtn_far=(172, 168, 192), mtn_mid=(150, 142, 168), mtn_near=(120, 110, 138),
        struct_light=(255, 232, 218), struct_mid=(188, 176, 190),
        struct_dark=(104, 100, 124), struct_accent=(186, 152, 148),
        foliage_top=(74, 112, 90), foliage_mid=(46, 82, 66), foliage_dark=(28, 52, 44),
        foliage_accent=(116, 150, 120),
        ground_top=(222, 216, 214), ground_mid=(172, 168, 178), ground_bot=(108, 112, 134),
        snow_tint=(255, 234, 220), star_alpha=0)),
]

ALPINE_SNOWPEAK = BiomeSpec(
    name="Alpine Snowpeak",
    note="Tall jagged snow-capped granite over a dark conifer treeline; cold blue-white, crisp high-altitude air.",
    keyframes=_ALPINE_KF,
    sky=SkyParams(positions=(0.0, 0.34, 0.66, 0.88, 1.0), dither_amp=1.6, zenith_dark=0.10),
    ridges=[
        # Far snowfield wall: broad, low jag, snow-capped high.
        RidgeParams(base_h=0.26, octaves=((0.007, 26), (0.018, 14)), parallax=0.06,
                    color_key='mtn_far', jag=0.30, snow_line=0.58, seed=2),
        # Mid peaks: taller, sharper teeth.
        RidgeParams(base_h=0.34, octaves=((0.010, 30), (0.026, 18)), parallax=0.14,
                    color_key='mtn_mid', jag=0.42, snow_line=0.50, seed=4),
        # Near summits: tallest + most jagged, caps reach lower.
        RidgeParams(base_h=0.40, octaves=((0.013, 34), (0.030, 20)), parallax=0.26,
                    color_key='mtn_near', jag=0.48, snow_line=0.46, seed=6),
    ],
    signature=bm.draw_summit_shrine,
    foliage=bm.draw_alpine_conifers,
    ground=GroundParams(),
)


# ── Biome 3 — Volcanic Caldera ────────────────────────────────────────────────
# Caldera-rim ridges with a central crater notch; ash/charcoal terrain, smoky
# ember sky that stays moody even at "day". Lava glow is the night hero.
_VOLCANO_KF = [
    (0.06, dict(  # morning — hazy brown daylight, never clean blue
        sky_top=(120, 96, 96), sky_mid=(168, 130, 110), sky_bot=(196, 156, 128),
        horizon=(210, 158, 118),
        mtn_far=(96, 84, 84), mtn_mid=(74, 64, 64), mtn_near=(52, 46, 48),
        struct_light=(150, 120, 110), struct_mid=(96, 84, 82),
        struct_dark=(52, 46, 48), struct_accent=(170, 96, 64),
        ground_top=(86, 76, 76), ground_mid=(60, 54, 54), ground_bot=(38, 34, 36),
        glow_color=(255, 120, 44), star_alpha=0)),
    (0.18, dict(  # midday — ash haze thins a little, still smoky
        sky_top=(132, 110, 108), sky_mid=(180, 144, 122), sky_bot=(206, 166, 136),
        horizon=(216, 162, 120),
        mtn_far=(100, 88, 88), mtn_mid=(78, 68, 68), mtn_near=(54, 48, 50),
        struct_light=(156, 126, 114), struct_mid=(100, 88, 86),
        struct_dark=(54, 48, 50), struct_accent=(178, 100, 66),
        ground_top=(90, 80, 80), ground_mid=(62, 56, 56), ground_bot=(40, 36, 38),
        glow_color=(255, 124, 48), star_alpha=0)),
    (0.40, dict(  # golden — sulphur-orange wash
        sky_top=(122, 86, 90), sky_mid=(214, 130, 86), sky_bot=(244, 162, 96),
        horizon=(252, 168, 92),
        mtn_far=(108, 84, 82), mtn_mid=(82, 62, 62), mtn_near=(56, 44, 46),
        struct_light=(188, 130, 96), struct_mid=(116, 84, 76),
        struct_dark=(58, 44, 46), struct_accent=(216, 110, 56),
        ground_top=(98, 78, 74), ground_mid=(66, 54, 52), ground_bot=(42, 36, 36),
        glow_color=(255, 130, 50), star_alpha=0)),
    (0.50, dict(  # sunset — bruised red sky, ember strengthening
        sky_top=(86, 52, 70), sky_mid=(190, 78, 66), sky_bot=(230, 116, 64),
        horizon=(248, 138, 64),
        mtn_far=(96, 66, 70), mtn_mid=(74, 50, 52), mtn_near=(50, 36, 40),
        struct_light=(168, 104, 84), struct_mid=(108, 70, 66),
        struct_dark=(54, 38, 42), struct_accent=(232, 96, 50),
        ground_top=(90, 64, 62), ground_mid=(62, 46, 46), ground_bot=(40, 32, 34),
        glow_color=(255, 120, 46), star_alpha=20)),
    (0.62, dict(  # dusk — deep maroon, lava read rising
        sky_top=(46, 28, 46), sky_mid=(108, 42, 50), sky_bot=(170, 74, 54),
        horizon=(214, 100, 50),
        mtn_far=(70, 48, 54), mtn_mid=(54, 36, 42), mtn_near=(38, 26, 32),
        struct_light=(130, 80, 70), struct_mid=(84, 54, 54),
        struct_dark=(44, 30, 36), struct_accent=(238, 92, 44),
        ground_top=(70, 48, 50), ground_mid=(50, 36, 40), ground_bot=(32, 26, 30),
        glow_color=(255, 112, 40), star_alpha=70)),
    (0.70, dict(  # night — black ash + molten glow is the hero
        sky_top=(16, 12, 24), sky_mid=(40, 18, 26), sky_bot=(78, 30, 28),
        horizon=(150, 56, 34),
        mtn_far=(40, 28, 34), mtn_mid=(30, 22, 28), mtn_near=(22, 16, 22),
        struct_light=(96, 60, 56), struct_mid=(58, 40, 42),
        struct_dark=(30, 22, 26), struct_accent=(255, 90, 36),
        ground_top=(46, 30, 32), ground_mid=(32, 22, 26), ground_bot=(20, 14, 18),
        glow_color=(255, 96, 32), star_alpha=170)),
    (0.80, dict(  # predawn — cold ash returning, ember still pooling
        sky_top=(28, 22, 40), sky_mid=(64, 34, 44), sky_bot=(118, 56, 48),
        horizon=(176, 80, 46),
        mtn_far=(56, 40, 46), mtn_mid=(42, 30, 36), mtn_near=(30, 22, 28),
        struct_light=(116, 74, 66), struct_mid=(72, 48, 48),
        struct_dark=(38, 26, 32), struct_accent=(244, 92, 40),
        ground_top=(58, 40, 42), ground_mid=(42, 30, 34), ground_bot=(26, 18, 22),
        glow_color=(255, 104, 36), star_alpha=110)),
    (0.94, dict(  # sunrise — smoky orange daybreak
        sky_top=(110, 78, 86), sky_mid=(224, 124, 84), sky_bot=(248, 158, 96),
        horizon=(252, 162, 88),
        mtn_far=(104, 82, 82), mtn_mid=(80, 62, 64), mtn_near=(54, 44, 48),
        struct_light=(178, 124, 96), struct_mid=(112, 82, 76),
        struct_dark=(56, 44, 46), struct_accent=(224, 106, 54),
        ground_top=(94, 74, 72), ground_mid=(64, 52, 52), ground_bot=(40, 34, 36),
        glow_color=(255, 126, 48), star_alpha=0)),
]

VOLCANIC_CALDERA = BiomeSpec(
    name="Volcanic Caldera",
    note="Caldera-rim ridges around a crater notch; ash-charcoal terrain, smoky ember sky, lava glow at night.",
    keyframes=_VOLCANO_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.60, 0.82, 1.0), dither_amp=2.6, zenith_dark=0.08),
    ridges=[
        # Far rim wall with a broad central crater dip.
        RidgeParams(base_h=0.24, octaves=((0.006, 22), (0.016, 10)), parallax=0.06,
                    color_key='mtn_far', notch=0.50, seed=1),
        # Mid rim, deeper notch + a little jag for cinder texture.
        RidgeParams(base_h=0.30, octaves=((0.009, 26),), parallax=0.14,
                    color_key='mtn_mid', notch=0.55, jag=0.22, seed=3),
        # Near rim shoulders framing the crater foreground.
        RidgeParams(base_h=0.20, octaves=((0.012, 18),), parallax=0.26,
                    color_key='mtn_near', notch=0.42, jag=0.18, seed=5),
    ],
    signature=bm.draw_basalt_columns,
    foliage=None,
    atmosphere=bm.ember_haze,
    ground=GroundParams(),
)


# ── Biome 4 — Karst Watertown ─────────────────────────────────────────────────
# Misty vertical karst towers, soft jade/grey palette, heavy shan-shui mist.
# Humid, serene; stilt houses on a still-water inlet are the hero.
_KARST_KF = [
    (0.06, dict(  # morning — pearly jade haze
        sky_top=(150, 186, 196), sky_mid=(196, 216, 218), sky_bot=(224, 234, 230),
        horizon=(232, 238, 230),
        mtn_far=(150, 174, 174), mtn_mid=(120, 150, 150), mtn_near=(92, 124, 124),
        struct_light=(210, 218, 214), struct_mid=(150, 162, 158),
        struct_dark=(92, 108, 106), struct_accent=(176, 156, 130),
        foliage_top=(96, 158, 110), foliage_mid=(58, 118, 82), foliage_dark=(34, 78, 58),
        foliage_accent=(150, 196, 140),
        ground_top=(150, 168, 158), ground_mid=(112, 134, 126), ground_bot=(78, 100, 96),
        water_tint=(150, 178, 178), mist_tint=(216, 230, 226), star_alpha=0)),
    (0.18, dict(  # midday — clearest, soft teal sky
        sky_top=(128, 178, 196), sky_mid=(184, 212, 218), sky_bot=(218, 232, 230),
        horizon=(228, 236, 228),
        mtn_far=(146, 172, 172), mtn_mid=(116, 148, 148), mtn_near=(88, 122, 122),
        struct_light=(214, 222, 218), struct_mid=(152, 164, 160),
        struct_dark=(92, 108, 106), struct_accent=(180, 158, 132),
        foliage_top=(100, 162, 112), foliage_mid=(60, 122, 84), foliage_dark=(34, 80, 58),
        foliage_accent=(154, 200, 142),
        ground_top=(150, 170, 158), ground_mid=(112, 136, 126), ground_bot=(78, 102, 96),
        water_tint=(146, 180, 182), mist_tint=(212, 228, 224), star_alpha=0)),
    (0.40, dict(  # golden — warm gold sifting through the mist
        sky_top=(168, 184, 178), sky_mid=(236, 210, 168), sky_bot=(252, 226, 184),
        horizon=(252, 228, 184),
        mtn_far=(168, 174, 162), mtn_mid=(142, 144, 130), mtn_near=(112, 116, 104),
        struct_light=(228, 218, 198), struct_mid=(166, 158, 142),
        struct_dark=(102, 102, 94), struct_accent=(206, 168, 122),
        foliage_top=(120, 168, 104), foliage_mid=(76, 126, 76), foliage_dark=(44, 84, 54),
        foliage_accent=(178, 200, 132),
        ground_top=(166, 170, 146), ground_mid=(124, 132, 114), ground_bot=(86, 100, 92),
        water_tint=(176, 184, 162), mist_tint=(230, 224, 196), star_alpha=0)),
    (0.50, dict(  # sunset — rose-grey water mirror
        sky_top=(140, 130, 152), sky_mid=(226, 158, 150), sky_bot=(248, 188, 158),
        horizon=(250, 198, 162),
        mtn_far=(150, 138, 148), mtn_mid=(126, 112, 122), mtn_near=(98, 86, 98),
        struct_light=(214, 196, 196), struct_mid=(156, 140, 144),
        struct_dark=(96, 86, 94), struct_accent=(204, 152, 130),
        foliage_top=(98, 138, 96), foliage_mid=(60, 100, 68), foliage_dark=(36, 68, 50),
        foliage_accent=(150, 176, 122),
        ground_top=(154, 144, 144), ground_mid=(116, 110, 116), ground_bot=(82, 80, 92),
        water_tint=(168, 150, 152), mist_tint=(222, 200, 196), star_alpha=20)),
    (0.62, dict(  # dusk — cool blue mist, lit windows begin
        sky_top=(62, 70, 100), sky_mid=(112, 118, 142), sky_bot=(168, 158, 166),
        horizon=(208, 184, 176),
        mtn_far=(96, 106, 124), mtn_mid=(76, 86, 104), mtn_near=(56, 66, 84),
        struct_light=(176, 184, 196), struct_mid=(120, 128, 142),
        struct_dark=(74, 82, 98), struct_accent=(196, 158, 118),
        foliage_top=(60, 92, 76), foliage_mid=(38, 64, 56), foliage_dark=(24, 44, 42),
        foliage_accent=(96, 128, 98),
        ground_top=(102, 110, 120), ground_mid=(78, 86, 100), ground_bot=(56, 64, 82),
        water_tint=(112, 124, 138), mist_tint=(176, 188, 196), star_alpha=70)),
    (0.70, dict(  # night — black water, warm lantern windows, moonlit mist
        sky_top=(12, 18, 42), sky_mid=(26, 38, 70), sky_bot=(52, 66, 96),
        horizon=(118, 126, 142),
        mtn_far=(40, 52, 78), mtn_mid=(30, 42, 64), mtn_near=(22, 32, 50),
        struct_light=(132, 148, 168), struct_mid=(74, 88, 110),
        struct_dark=(40, 50, 70), struct_accent=(255, 188, 96),
        foliage_top=(40, 64, 60), foliage_mid=(26, 44, 44), foliage_dark=(16, 28, 30),
        foliage_accent=(60, 88, 76),
        ground_top=(52, 64, 84), ground_mid=(38, 48, 68), ground_bot=(26, 34, 52),
        water_tint=(46, 60, 84), mist_tint=(120, 136, 152), glow_color=(255, 200, 120),
        star_alpha=205)),
    (0.80, dict(  # predawn — grey-violet, mist heaviest
        sky_top=(30, 38, 70), sky_mid=(60, 70, 104), sky_bot=(120, 120, 144),
        horizon=(190, 172, 172),
        mtn_far=(70, 82, 104), mtn_mid=(54, 66, 88), mtn_near=(40, 50, 70),
        struct_light=(160, 168, 182), struct_mid=(108, 118, 134),
        struct_dark=(66, 76, 94), struct_accent=(200, 162, 120),
        foliage_top=(50, 80, 72), foliage_mid=(32, 56, 52), foliage_dark=(20, 36, 38),
        foliage_accent=(82, 116, 92),
        ground_top=(94, 104, 116), ground_mid=(72, 82, 100), ground_bot=(52, 62, 82),
        water_tint=(98, 112, 128), mist_tint=(176, 184, 192), star_alpha=110)),
    (0.94, dict(  # sunrise — apricot light flooding the inlet
        sky_top=(140, 172, 188), sky_mid=(248, 196, 168), sky_bot=(254, 222, 184),
        horizon=(254, 224, 184),
        mtn_far=(166, 168, 162), mtn_mid=(138, 134, 128), mtn_near=(108, 104, 102),
        struct_light=(226, 212, 198), struct_mid=(164, 152, 142),
        struct_dark=(100, 96, 92), struct_accent=(214, 164, 116),
        foliage_top=(112, 162, 104), foliage_mid=(68, 120, 78), foliage_dark=(40, 80, 56),
        foliage_accent=(166, 198, 134),
        ground_top=(160, 164, 148), ground_mid=(120, 128, 118), ground_bot=(84, 98, 94),
        water_tint=(176, 180, 166), mist_tint=(232, 220, 198), star_alpha=0)),
]

KARST_WATERTOWN = BiomeSpec(
    name="Karst Watertown",
    note="Misty vertical karst towers over a still-water inlet of stilt houses; soft jade/grey, humid and serene.",
    keyframes=_KARST_KF,
    sky=SkyParams(positions=(0.0, 0.32, 0.62, 0.84, 1.0), dither_amp=1.8, zenith_dark=0.04),
    ridges=[
        # Far towers: tall, narrow spikes, low-contrast (lost in mist).
        RidgeParams(base_h=0.20, octaves=((0.009, 14),), parallax=0.06,
                    color_key='mtn_far', spike=0.78, seed=2),
        # Mid towers: the iconic Guilin fingers.
        RidgeParams(base_h=0.18, octaves=((0.011, 12),), parallax=0.14,
                    color_key='mtn_mid', spike=0.86, seed=5),
        # Near towers: a couple of bold close fingers framing the inlet.
        RidgeParams(base_h=0.14, octaves=((0.014, 10),), parallax=0.26,
                    color_key='mtn_near', spike=0.72, seed=8),
    ],
    signature=bm.draw_stilt_houses,
    foliage=bm.draw_bamboo_fringe,
    atmosphere=bm.karst_mist,
    ground=GroundParams(),
)


# ── Biome 5 — Autumn Highlands ────────────────────────────────────────────────
# Rolling forested hills, fiery maple palette (reds/oranges/golds), warm light.
# Terrace wall + cairn way-marker on a glowing canopy hillside.
_AUTUMN_KF = [
    (0.06, dict(  # morning — soft amber light on turning leaves
        sky_top=(110, 160, 206), sky_mid=(190, 208, 214), sky_bot=(232, 224, 196),
        horizon=(248, 226, 186),
        mtn_far=(168, 150, 142), mtn_mid=(150, 118, 100), mtn_near=(124, 88, 72),
        struct_light=(206, 178, 142), struct_mid=(158, 124, 92),
        struct_dark=(100, 72, 52), struct_accent=(190, 132, 82),
        foliage_top=(232, 158, 64), foliage_mid=(196, 104, 48), foliage_dark=(132, 64, 40),
        foliage_accent=(248, 196, 96),
        ground_top=(178, 130, 80), ground_mid=(140, 98, 62), ground_bot=(96, 68, 46),
        star_alpha=0)),
    (0.18, dict(  # midday — clear warm sky over the canopy
        sky_top=(92, 152, 210), sky_mid=(178, 204, 216), sky_bot=(226, 222, 198),
        horizon=(244, 224, 188),
        mtn_far=(172, 154, 146), mtn_mid=(152, 120, 102), mtn_near=(126, 90, 74),
        struct_light=(210, 182, 146), struct_mid=(162, 128, 96),
        struct_dark=(102, 74, 54), struct_accent=(194, 136, 86),
        foliage_top=(236, 162, 66), foliage_mid=(200, 108, 50), foliage_dark=(136, 66, 42),
        foliage_accent=(252, 200, 100),
        ground_top=(180, 132, 82), ground_mid=(142, 100, 64), ground_bot=(98, 70, 48),
        star_alpha=0)),
    (0.40, dict(  # golden — peak fire, everything glows
        sky_top=(120, 148, 196), sky_mid=(244, 196, 132), sky_bot=(255, 214, 156),
        horizon=(255, 216, 148),
        mtn_far=(190, 158, 138), mtn_mid=(176, 122, 90), mtn_near=(146, 92, 64),
        struct_light=(228, 184, 132), struct_mid=(184, 132, 84),
        struct_dark=(116, 76, 50), struct_accent=(214, 138, 76),
        foliage_top=(248, 158, 56), foliage_mid=(214, 100, 42), foliage_dark=(146, 60, 36),
        foliage_accent=(255, 204, 96),
        ground_top=(196, 134, 78), ground_mid=(154, 100, 60), ground_bot=(104, 70, 46),
        star_alpha=0)),
    (0.50, dict(  # sunset — crimson sky, embered leaves
        sky_top=(112, 84, 122), sky_mid=(232, 120, 84), sky_bot=(255, 156, 92),
        horizon=(255, 178, 106),
        mtn_far=(160, 116, 122), mtn_mid=(152, 92, 84), mtn_near=(124, 72, 60),
        struct_light=(208, 150, 110), struct_mid=(166, 108, 76),
        struct_dark=(104, 62, 46), struct_accent=(206, 116, 66),
        foliage_top=(232, 124, 52), foliage_mid=(196, 80, 44), foliage_dark=(132, 50, 38),
        foliage_accent=(248, 168, 76),
        ground_top=(176, 110, 70), ground_mid=(138, 84, 56), ground_bot=(94, 60, 44),
        star_alpha=20)),
    (0.62, dict(  # dusk — purple sky, canopy deepening to wine
        sky_top=(46, 40, 86), sky_mid=(104, 64, 118), sky_bot=(192, 116, 110),
        horizon=(238, 154, 116),
        mtn_far=(104, 88, 116), mtn_mid=(92, 70, 88), mtn_near=(70, 52, 62),
        struct_light=(150, 116, 110), struct_mid=(116, 84, 80),
        struct_dark=(72, 50, 48), struct_accent=(160, 100, 70),
        foliage_top=(168, 86, 56), foliage_mid=(128, 58, 46), foliage_dark=(82, 40, 38),
        foliage_accent=(196, 120, 60),
        ground_top=(120, 82, 66), ground_mid=(92, 64, 54), ground_bot=(64, 48, 44),
        star_alpha=70)),
    (0.70, dict(  # night — deep blue, canopy a dark warm mass
        sky_top=(12, 16, 44), sky_mid=(26, 30, 68), sky_bot=(52, 50, 86),
        horizon=(128, 100, 110),
        mtn_far=(46, 46, 72), mtn_mid=(38, 36, 58), mtn_near=(28, 26, 44),
        struct_light=(110, 96, 100), struct_mid=(74, 60, 62),
        struct_dark=(44, 36, 40), struct_accent=(132, 86, 60),
        foliage_top=(96, 56, 46), foliage_mid=(66, 40, 40), foliage_dark=(40, 28, 32),
        foliage_accent=(120, 72, 46),
        ground_top=(64, 50, 48), ground_mid=(48, 38, 40), ground_bot=(32, 26, 30),
        glow_color=(255, 196, 130), star_alpha=205)),
    (0.80, dict(  # predawn — cool dawn-grey, warmth still smouldering
        sky_top=(30, 34, 76), sky_mid=(60, 56, 108), sky_bot=(124, 96, 122),
        horizon=(206, 150, 138),
        mtn_far=(78, 72, 102), mtn_mid=(64, 56, 82), mtn_near=(48, 42, 62),
        struct_light=(140, 110, 104), struct_mid=(104, 78, 74),
        struct_dark=(64, 46, 44), struct_accent=(150, 96, 64),
        foliage_top=(146, 84, 56), foliage_mid=(106, 56, 44), foliage_dark=(66, 36, 36),
        foliage_accent=(176, 110, 58),
        ground_top=(106, 80, 68), ground_mid=(82, 62, 56), ground_bot=(56, 44, 44),
        glow_color=(255, 188, 140), star_alpha=110)),
    (0.94, dict(  # sunrise — peach light setting the leaves alight
        sky_top=(104, 150, 200), sky_mid=(252, 192, 152), sky_bot=(255, 216, 174),
        horizon=(255, 222, 178),
        mtn_far=(186, 158, 144), mtn_mid=(172, 124, 96), mtn_near=(144, 94, 68),
        struct_light=(224, 184, 138), struct_mid=(182, 132, 90),
        struct_dark=(116, 78, 52), struct_accent=(210, 138, 80),
        foliage_top=(248, 156, 60), foliage_mid=(212, 102, 44), foliage_dark=(142, 60, 38),
        foliage_accent=(255, 202, 100),
        ground_top=(192, 138, 82), ground_mid=(150, 102, 62), ground_bot=(102, 72, 48),
        star_alpha=0)),
]

AUTUMN_HIGHLANDS = BiomeSpec(
    name="Autumn Highlands",
    note="Rolling forested hills under a fiery maple canopy; terrace wall + cairn way-marker, warm and cozy.",
    keyframes=_AUTUMN_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.60, 0.84, 1.0), dither_amp=2.2, zenith_dark=0.05),
    ridges=[
        # Rolling hills: smooth low-freq swells, only the near rank gets a touch
        # of jag so the closest ridge reads as rocky outcrop above the forest.
        RidgeParams(base_h=0.18, octaves=((0.006, 20), (0.013, 11)), parallax=0.06,
                    color_key='mtn_far', seed=2),
        RidgeParams(base_h=0.22, octaves=((0.008, 24), (0.016, 12)), parallax=0.14,
                    color_key='mtn_mid', seed=4),
        RidgeParams(base_h=0.16, octaves=((0.011, 18),), parallax=0.26,
                    color_key='mtn_near', jag=0.18, seed=6),
    ],
    signature=bm.draw_terrace_cairn,
    foliage=bm.draw_autumn_canopy,
    ground=GroundParams(),
)


# ── registry ──────────────────────────────────────────────────────────────────
BIOMES = {
    "desert_mesa": DESERT_MESA,
    "alpine_snowpeak": ALPINE_SNOWPEAK,
    "volcanic_caldera": VOLCANIC_CALDERA,
    "karst_watertown": KARST_WATERTOWN,
    "autumn_highlands": AUTUMN_HIGHLANDS,
}
GROUP_A = ["desert_mesa", "alpine_snowpeak", "volcanic_caldera",
           "karst_watertown", "autumn_highlands"]
GROUP_B = []
BIOME_NAMES = {k: v.name for k, v in BIOMES.items()}
BIOME_NOTES = {k: v.note for k, v in BIOMES.items()}
