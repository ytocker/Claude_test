"""
Alpine Haze sunset/sunrise study — 10 variants over ONE shared day/night spine.

The user loves the round-14 "Alpine Haze" look: a cool glacial-cyan day and a
clean cool-cyan blue-hour night. A later restyle pushed its sunrise/sunset too
brown/yellow and muddy. This module keeps the Alpine day + night arc EXACTLY
and varies ONLY the sunset and sunrise colour story, so each variant reads as a
different beautiful moment without disturbing the beloved spine.

Provably-identical spine: the Alpine keyframes are authored ONCE in
`_ALPINE_HAZE_KF`. Each design `_compose`s its BiomeSpec by CLONING that base
list and overriding ONLY the sunset/sunrise RGB at the named phases (plus any
optional hold/onset frames it inserts to widen dwell on the dramatic ones).
The day anchors (0.06 / 0.18 / 0.30), the deep-night (0.72) and predawn (0.80)
blue-hour frames, and EVERY frame's `star_alpha`, pass through untouched — so
day/night timing and star onset stay byte-for-byte identical across all 10.

Preview-only data. Nothing on the live render path imports this module — it is
reached solely through `tools/preview_sky_alpine_sunsets.py`. Pure-Pygame /
pygbag-safe (the keyframes are just colour tables; the OKLab bake lives in the
engine).
"""
from __future__ import annotations

from game.biome_sky import BiomeSpec, SkyParams


# ── the shared Alpine Haze spine (authored once) ──────────────────────────────
# Phase clock matches the calm sets so the preview columns line up:
#   morning 0.06 · midday 0.18 · afternoon 0.30 · golden 0.40 · sunset 0.50 ·
#   dusk 0.62 · deep-night 0.72 · predawn 0.80 · dawn 0.88 · sunrise 0.94
# `make_palette` wraps 0.94 -> 0.06 through 1.0 so the night side is continuous.
#
# Frames flagged SPINE below are KEPT byte-for-byte on every variant. Frames
# flagged VARY are the only ones a design overrides (golden 0.40, sunset 0.50,
# dusk 0.62 for the sunset cluster; dawn 0.88, sunrise 0.94 for the sunrise
# cluster), and designs may additionally INSERT hold/onset frames at 0.44/0.56
# (sunset) and 0.86/0.90 (sunrise) to widen the dwell on the dramatic ones.
_ALPINE_HAZE_KF = [
    (0.06, dict(sky_top=(86, 158, 186),  sky_mid=(150, 192, 202), sky_bot=(196, 212, 210), horizon=(214, 218, 212), star_alpha=0)),   # SPINE morning
    (0.18, dict(sky_top=(76, 168, 192),  sky_mid=(144, 198, 208), sky_bot=(196, 214, 212), horizon=(216, 220, 212), star_alpha=0)),   # SPINE midday
    (0.30, dict(sky_top=(86, 160, 188),  sky_mid=(152, 192, 204), sky_bot=(198, 212, 208), horizon=(216, 218, 210), star_alpha=0)),   # SPINE afternoon
    (0.40, dict(sky_top=(88, 152, 178),  sky_mid=(156, 186, 196), sky_bot=(202, 208, 202), horizon=(220, 214, 204), star_alpha=0)),   # VARY golden
    (0.50, dict(sky_top=(74, 126, 160),  sky_mid=(146, 168, 184), sky_bot=(202, 200, 196), horizon=(230, 204, 184), star_alpha=12)),  # VARY sunset
    (0.62, dict(sky_top=(34, 76, 116),   sky_mid=(76, 126, 160),  sky_bot=(134, 172, 186), horizon=(190, 204, 200), star_alpha=80)),  # VARY dusk
    (0.72, dict(sky_top=(8, 28, 62),     sky_mid=(16, 64, 104),   sky_bot=(34, 104, 136),  horizon=(70, 144, 164),  star_alpha=210)), # SPINE deep night
    (0.80, dict(sky_top=(12, 38, 78),    sky_mid=(26, 84, 124),   sky_bot=(54, 126, 156),  horizon=(108, 166, 186), star_alpha=130)), # SPINE predawn
    (0.88, dict(sky_top=(76, 146, 176),  sky_mid=(140, 186, 200), sky_bot=(190, 210, 208), horizon=(214, 218, 210), star_alpha=20)),  # VARY dawn
    (0.94, dict(sky_top=(84, 156, 184),  sky_mid=(148, 192, 202), sky_bot=(196, 212, 210), horizon=(214, 218, 212), star_alpha=0)),   # VARY sunrise
]

# Shared bake params for all 10 — keeps the grade placement identical too.
_ALPINE_SKY = SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.14)

# star_alpha for any INSERTED hold/onset frame, interpolated from the Alpine
# neighbours so star timing never shifts (0.40->0.50 and 0.50->0.62 spans on
# the sunset side; 0.80->0.88 and 0.88->0.94 spans on the sunrise side).
_INSERT_STAR_ALPHA = {
    0.44: 5,    # between golden 0.40 (0) and sunset 0.50 (12)
    0.56: 30,   # between sunset 0.50 (12) and dusk 0.62 (80)
    0.86: 48,   # between predawn 0.80 (130) and dawn 0.88 (20) -> closer to dawn
    0.90: 13,   # between dawn 0.88 (20) and sunrise 0.94 (0)
}

# Phases a design is ALLOWED to override (anything else stays spine).
_VARY_PHASES = {0.40, 0.50, 0.62, 0.88, 0.94}
_INSERT_PHASES = {0.44, 0.56, 0.86, 0.90}


def _compose(overrides: dict) -> list:
    """Clone the Alpine spine and apply a design's sunset/sunrise overrides.

    `overrides` maps phase -> dict(sky_top/mid/bot/horizon). For a VARY phase
    we replace only those four RGB keys, preserving the spine's star_alpha. For
    an INSERT phase we add a brand-new frame, giving it the interpolated
    star_alpha so the star arc is unchanged. Any phase NOT listed (the day
    anchors, deep night, predawn) is copied verbatim — this is what guarantees
    the spine is identical with zero hand-transcription."""
    by_phase = {ph: dict(d) for ph, d in _ALPINE_HAZE_KF}
    for ph, rgb in overrides.items():
        assert ph in _VARY_PHASES or ph in _INSERT_PHASES, f"phase {ph} is not overridable"
        frame = dict(rgb)
        if ph in by_phase:
            # VARY: keep the spine star_alpha, swap only the four sky colours.
            frame['star_alpha'] = by_phase[ph]['star_alpha']
        else:
            # INSERT: new dwell frame gets the interpolated star_alpha.
            frame['star_alpha'] = _INSERT_STAR_ALPHA[ph]
        by_phase[ph] = frame
    return [(ph, by_phase[ph]) for ph in sorted(by_phase)]


def _spec(name, note, overrides):
    return BiomeSpec(name=name, note=note, keyframes=_compose(overrides), sky=_ALPINE_SKY)


# ── the 10 sunset/sunrise stories (Alpine day + night under every one) ─────────
# Authoring discipline shared by all rows:
#   * The TOP ~25-30% (sky_top) stays cool Alpine cyan even on the dramatic
#     rows, so white/gold HUD text and the scarlet bird keep reading — warmth
#     is pushed into mid/bot/horizon, never the zenith.
#   * Clean, saturated hues only. No muddy brown/olive (the round-17 failure).
#   * DRAMATIC: colour climbs from the horizon up THROUGH sky_bot into sky_mid,
#     and the dwell is widened with 0.44/0.56 (sunset) + 0.86/0.90 (sunrise).
#   * MODERATE/NATURAL: rich colour kept to a horizon-to-low band; the mid stays
#     closer to Alpine cool so the moment reads as a clean horizon glow.
#   * The sunrise is a softer take on the SAME family as the sunset, so both
#     moments read as that design's signature colour.


# 1. Golden Hour — clean amber -> yellow-orange, MODERATE band.
GOLDEN_HOUR = _spec(
    'Golden Hour',
    'Clean amber-into-yellow-orange horizon band — a warm classic kept low and tidy so the cyan mid still breathes. MODERATE.',
    {
        0.40: dict(sky_top=(92, 150, 174), sky_mid=(168, 186, 184), sky_bot=(232, 200, 150), horizon=(252, 198, 116)),
        0.50: dict(sky_top=(82, 130, 160), sky_mid=(176, 180, 168), sky_bot=(248, 198, 132), horizon=(255, 184, 92)),
        0.62: dict(sky_top=(38, 80, 118),  sky_mid=(96, 132, 156),  sky_bot=(196, 178, 152), horizon=(244, 178, 116)),
        0.88: dict(sky_top=(80, 146, 174), sky_mid=(168, 190, 188), sky_bot=(228, 206, 168), horizon=(250, 204, 138)),
        0.94: dict(sky_top=(86, 156, 182), sky_mid=(160, 196, 198), sky_bot=(214, 212, 188), horizon=(244, 208, 162)),
    },
)


# 2. Tangerine Blaze — vivid orange, DRAMATIC sky-filling.
TANGERINE_BLAZE = _spec(
    'Tangerine Blaze',
    'A vivid tangerine that climbs from the horizon through the whole lower-mid frame, cyan held only at the zenith — sky-filling, widened dwell. DRAMATIC.',
    {
        0.40: dict(sky_top=(92, 146, 172), sky_mid=(214, 168, 138), sky_bot=(250, 168, 92),  horizon=(255, 148, 64)),
        0.44: dict(sky_top=(88, 138, 168), sky_mid=(224, 158, 120), sky_bot=(255, 156, 78),  horizon=(255, 134, 52)),
        0.50: dict(sky_top=(80, 124, 158), sky_mid=(228, 146, 108), sky_bot=(255, 146, 70),  horizon=(255, 120, 46)),
        0.56: dict(sky_top=(60, 100, 142), sky_mid=(210, 130, 104), sky_bot=(252, 138, 72),  horizon=(252, 112, 48)),
        0.62: dict(sky_top=(36, 78, 116),  sky_mid=(140, 116, 138), sky_bot=(228, 138, 92),  horizon=(248, 124, 62)),
        0.86: dict(sky_top=(40, 84, 122),  sky_mid=(166, 134, 142), sky_bot=(244, 160, 110), horizon=(255, 144, 76)),
        0.88: dict(sky_top=(78, 142, 172), sky_mid=(206, 168, 152), sky_bot=(250, 176, 120), horizon=(255, 158, 92)),
        0.90: dict(sky_top=(82, 150, 178), sky_mid=(190, 184, 170), sky_bot=(246, 190, 142), horizon=(255, 170, 110)),
        0.94: dict(sky_top=(86, 156, 182), sky_mid=(172, 192, 188), sky_bot=(230, 202, 162), horizon=(252, 184, 128)),
    },
)


# 3. Coral Reef — coral-pink -> salmon, MODERATE.
CORAL_REEF = _spec(
    'Coral Reef',
    'Soft coral-pink melting into salmon along the horizon, the mid kept a cool blush so it reads as a clean reef glow. MODERATE.',
    {
        0.40: dict(sky_top=(92, 148, 174), sky_mid=(186, 178, 184), sky_bot=(244, 184, 168), horizon=(255, 162, 142)),
        0.50: dict(sky_top=(82, 128, 160), sky_mid=(192, 170, 178), sky_bot=(250, 174, 156), horizon=(255, 146, 124)),
        0.62: dict(sky_top=(38, 80, 118),  sky_mid=(106, 130, 156), sky_bot=(208, 168, 168), horizon=(248, 154, 140)),
        0.88: dict(sky_top=(80, 146, 174), sky_mid=(182, 182, 188), sky_bot=(240, 192, 180), horizon=(254, 172, 156)),
        0.94: dict(sky_top=(86, 156, 182), sky_mid=(166, 194, 196), sky_bot=(222, 206, 196), horizon=(250, 186, 174)),
    },
)


# 4. Crimson Fire — fiery red-orange, DRAMATIC.
CRIMSON_FIRE = _spec(
    'Crimson Fire',
    'A fiery red-into-scarlet-orange that floods the lower sky and washes the mid ember, cool cyan only at the very top. DRAMATIC.',
    {
        0.40: dict(sky_top=(90, 142, 168), sky_mid=(206, 156, 144), sky_bot=(248, 138, 96),  horizon=(244, 96, 64)),
        0.44: dict(sky_top=(86, 132, 162), sky_mid=(216, 144, 130), sky_bot=(250, 124, 84),  horizon=(238, 80, 56)),
        0.50: dict(sky_top=(78, 118, 152), sky_mid=(222, 130, 116), sky_bot=(250, 112, 76),  horizon=(230, 66, 50)),
        0.56: dict(sky_top=(58, 96, 138),  sky_mid=(204, 116, 110), sky_bot=(244, 110, 78),  horizon=(220, 62, 52)),
        0.62: dict(sky_top=(36, 76, 114),  sky_mid=(138, 102, 130), sky_bot=(224, 116, 92),  horizon=(216, 74, 62)),
        0.86: dict(sky_top=(40, 82, 120),  sky_mid=(166, 124, 138), sky_bot=(240, 138, 110), horizon=(238, 96, 78)),
        0.88: dict(sky_top=(78, 142, 170), sky_mid=(204, 158, 150), sky_bot=(246, 158, 126), horizon=(246, 116, 94)),
        0.90: dict(sky_top=(82, 150, 178), sky_mid=(190, 178, 168), sky_bot=(244, 176, 142), horizon=(250, 138, 112)),
        0.94: dict(sky_top=(86, 156, 182), sky_mid=(172, 192, 188), sky_bot=(228, 198, 166), horizon=(250, 158, 134)),
    },
)


# 5. Rose-Magenta — red-purple, MODERATE.
ROSE_MAGENTA = _spec(
    'Rose-Magenta',
    'A jewel red-purple: rose-magenta horizon rising into a quiet violet blush, cyan mid held above — a clean magenta moment, not a full-sky flood. MODERATE.',
    {
        0.40: dict(sky_top=(94, 146, 176), sky_mid=(180, 168, 192), sky_bot=(228, 158, 184), horizon=(238, 120, 156)),
        0.50: dict(sky_top=(84, 124, 164), sky_mid=(184, 154, 188), sky_bot=(232, 138, 176), horizon=(232, 96, 142)),
        0.62: dict(sky_top=(38, 78, 118),  sky_mid=(112, 110, 156), sky_bot=(186, 134, 174), horizon=(220, 104, 148)),
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(176, 172, 196), sky_bot=(226, 168, 190), horizon=(238, 130, 164)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(160, 190, 200), sky_bot=(214, 192, 200), horizon=(236, 152, 180)),
    },
)


# 6. Violet Twilight — purple-violet + pink, DRAMATIC.
VIOLET_TWILIGHT = _spec(
    'Violet Twilight',
    'Deep purple-violet rising through the mid with a hot-pink horizon band — a dramatic dreamy twilight, cyan retreating to the zenith. DRAMATIC.',
    {
        0.40: dict(sky_top=(94, 144, 176), sky_mid=(170, 152, 192), sky_bot=(202, 142, 190), horizon=(232, 130, 174)),
        0.44: dict(sky_top=(88, 134, 172), sky_mid=(166, 140, 192), sky_bot=(198, 128, 188), horizon=(232, 116, 168)),
        0.50: dict(sky_top=(78, 118, 162), sky_mid=(156, 124, 190), sky_bot=(192, 116, 186), horizon=(228, 100, 160)),
        0.56: dict(sky_top=(60, 98, 148),  sky_mid=(134, 110, 180), sky_bot=(182, 110, 182), horizon=(220, 96, 156)),
        0.62: dict(sky_top=(38, 76, 118),  sky_mid=(98, 96, 158),   sky_bot=(160, 110, 176), horizon=(208, 100, 152)),
        0.86: dict(sky_top=(42, 82, 122),  sky_mid=(136, 116, 172), sky_bot=(196, 130, 186), horizon=(228, 116, 166)),
        0.88: dict(sky_top=(80, 142, 172), sky_mid=(174, 154, 196), sky_bot=(212, 156, 196), horizon=(234, 132, 174)),
        0.90: dict(sky_top=(82, 150, 178), sky_mid=(176, 170, 200), sky_bot=(216, 168, 200), horizon=(236, 148, 182)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(164, 188, 202), sky_bot=(210, 190, 204), horizon=(236, 162, 188)),
    },
)


# 7. Fuchsia-Cyan — magenta bloom that keeps an Alpine cyan band (tropical), MODERATE.
FUCHSIA_CYAN = _spec(
    'Fuchsia-Cyan',
    'Tropical contrast: a hot fuchsia horizon glow under a band of retained Alpine cyan in the mid — magenta-below / cyan-above, vivid but clean. MODERATE.',
    {
        0.40: dict(sky_top=(90, 152, 180), sky_mid=(150, 188, 200), sky_bot=(220, 158, 192), horizon=(244, 112, 170)),
        0.50: dict(sky_top=(80, 132, 166), sky_mid=(140, 178, 196), sky_bot=(224, 138, 186), horizon=(240, 84, 156)),
        0.62: dict(sky_top=(38, 80, 118),  sky_mid=(86, 134, 168),  sky_bot=(178, 128, 180), horizon=(224, 92, 154)),
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(148, 190, 202), sky_bot=(220, 168, 196), horizon=(244, 122, 174)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(152, 194, 202), sky_bot=(208, 194, 204), horizon=(240, 146, 186)),
    },
)


# 8. Lavender-Peach — soft lilac -> peach, GENTLE/NATURAL.
LAVENDER_PEACH = _spec(
    'Lavender-Peach',
    'The quietest of the set: a soft lilac mid melting into a pale peach horizon — a gentle, natural pastel dusk that barely lifts off the band. NATURAL.',
    {
        0.40: dict(sky_top=(92, 150, 176), sky_mid=(176, 176, 196), sky_bot=(222, 198, 192), horizon=(244, 196, 168)),
        0.50: dict(sky_top=(82, 130, 162), sky_mid=(176, 166, 192), sky_bot=(226, 188, 188), horizon=(248, 186, 156)),
        0.62: dict(sky_top=(38, 80, 118),  sky_mid=(104, 122, 158), sky_bot=(184, 158, 178), horizon=(228, 168, 158)),
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(174, 180, 200), sky_bot=(220, 200, 196), horizon=(244, 200, 176)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(160, 192, 200), sky_bot=(212, 204, 200), horizon=(242, 198, 184)),
    },
)


# 9. Ember Red-Purple — deep red -> purple, DRAMATIC.
EMBER_RED_PURPLE = _spec(
    'Ember Red-Purple',
    'A moody deep ember-red horizon bleeding up into a smouldering purple mid — the darkest, most cinematic of the dramatic rows. DRAMATIC.',
    {
        0.40: dict(sky_top=(90, 142, 170), sky_mid=(176, 148, 178), sky_bot=(216, 130, 156), horizon=(228, 96, 110)),
        0.44: dict(sky_top=(84, 132, 166), sky_mid=(172, 134, 176), sky_bot=(214, 116, 148), horizon=(222, 82, 98)),
        0.50: dict(sky_top=(76, 116, 156), sky_mid=(162, 118, 172), sky_bot=(210, 102, 140), horizon=(214, 68, 88)),
        0.56: dict(sky_top=(58, 96, 142),  sky_mid=(140, 104, 162), sky_bot=(198, 98, 138),  horizon=(204, 64, 90)),
        0.62: dict(sky_top=(36, 76, 114),  sky_mid=(100, 88, 146),  sky_bot=(170, 98, 142),  horizon=(196, 72, 96)),
        0.86: dict(sky_top=(40, 82, 120),  sky_mid=(132, 108, 162), sky_bot=(198, 118, 152), horizon=(220, 92, 108)),
        0.88: dict(sky_top=(80, 142, 170), sky_mid=(170, 146, 182), sky_bot=(210, 142, 168), horizon=(226, 108, 122)),
        0.90: dict(sky_top=(82, 150, 178), sky_mid=(170, 162, 190), sky_bot=(212, 152, 174), horizon=(228, 124, 136)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(162, 186, 198), sky_bot=(208, 184, 192), horizon=(228, 146, 154)),
    },
)


# 10. Pink-Gold — hot pink -> gold, MODERATE.
PINK_GOLD = _spec(
    'Pink-Gold',
    'A hot-pink horizon warming up into gold through the lower sky — a celebratory dual-tone glow, cool cyan kept up top. MODERATE.',
    {
        0.40: dict(sky_top=(92, 148, 174), sky_mid=(190, 178, 178), sky_bot=(246, 188, 154), horizon=(250, 142, 152)),
        0.50: dict(sky_top=(82, 128, 160), sky_mid=(196, 168, 172), sky_bot=(252, 178, 138), horizon=(248, 120, 138)),
        0.62: dict(sky_top=(38, 80, 118),  sky_mid=(110, 128, 156), sky_bot=(214, 166, 154), horizon=(238, 122, 134)),
        0.88: dict(sky_top=(80, 146, 174), sky_mid=(188, 182, 184), sky_bot=(242, 196, 164), horizon=(250, 152, 158)),
        0.94: dict(sky_top=(86, 156, 182), sky_mid=(168, 194, 196), sky_bot=(224, 204, 184), horizon=(248, 170, 174)),
    },
)


# Sheet order matches the 10 curated directions in the brief.
CONCEPTS = [
    ('golden_hour', GOLDEN_HOUR),
    ('tangerine_blaze', TANGERINE_BLAZE),
    ('coral_reef', CORAL_REEF),
    ('crimson_fire', CRIMSON_FIRE),
    ('rose_magenta', ROSE_MAGENTA),
    ('violet_twilight', VIOLET_TWILIGHT),
    ('fuchsia_cyan', FUCHSIA_CYAN),
    ('lavender_peach', LAVENDER_PEACH),
    ('ember_red_purple', EMBER_RED_PURPLE),
    ('pink_gold', PINK_GOLD),
]
