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


# 1. Golden Hour — saturated amber-GOLD with a hot sun-kissed core, MODERATE band.
GOLDEN_HOUR = _spec(
    'Golden Hour',
    'A saturated amber-gold horizon (H44 S~0.55) with a hotter H30 sun-kissed core at the very band — reads true gold, not tan — kept low so the cyan mid still breathes. MODERATE.',
    {
        # sky_bot carries the amber-gold (H~44 S~0.55) and horizon holds a hotter,
        # higher-chroma H30 sun-kissed core, so the band reads gold not flat tan.
        0.40: dict(sky_top=(92, 150, 174), sky_mid=(182, 190, 168), sky_bot=(252, 192, 100), horizon=(255, 162, 56)),
        0.50: dict(sky_top=(82, 130, 160), sky_mid=(192, 182, 150), sky_bot=(255, 184, 80),  horizon=(255, 142, 40)),
        0.62: dict(sky_top=(38, 80, 118),  sky_mid=(100, 132, 154), sky_bot=(212, 172, 118), horizon=(252, 156, 70)),
        0.88: dict(sky_top=(80, 146, 174), sky_mid=(178, 192, 176), sky_bot=(246, 196, 128), horizon=(255, 172, 84)),
        0.94: dict(sky_top=(86, 156, 182), sky_mid=(168, 196, 186), sky_bot=(234, 202, 148), horizon=(253, 182, 110)),
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
    'A clear salmon-coral melting up from the horizon, sat lifted (~0.40) so it reads unmistakably coral; the mid stays a cool blush for a clean reef glow, the sunrise warmed off neutral. MODERATE.',
    {
        # sat lifted across the band so it reads salmon-coral not near-neutral; the
        # sunrise (0.88/0.94) warmed off grey into a clear pale coral.
        0.40: dict(sky_top=(92, 148, 174), sky_mid=(202, 170, 174), sky_bot=(255, 166, 138), horizon=(255, 128, 100)),
        0.50: dict(sky_top=(82, 128, 160), sky_mid=(208, 158, 164), sky_bot=(255, 150, 122), horizon=(255, 90, 64)),
        0.62: dict(sky_top=(38, 80, 118),  sky_mid=(116, 126, 150), sky_bot=(222, 150, 146), horizon=(252, 120, 102)),
        0.88: dict(sky_top=(80, 146, 174), sky_mid=(196, 176, 178), sky_bot=(252, 176, 152), horizon=(255, 140, 116)),
        0.94: dict(sky_top=(86, 156, 182), sky_mid=(176, 190, 188), sky_bot=(238, 192, 172), horizon=(252, 158, 134)),
    },
)


# 4. Crimson Fire — fiery red-orange, DRAMATIC.
CRIMSON_FIRE = _spec(
    'Crimson Fire',
    'A fiery red-into-scarlet-orange that floods the lower sky and washes the mid ember, cool cyan only at the very top. DRAMATIC.',
    {
        # horizon core nudged a hair redder (toward H8) to widen the gap from
        # Tangerine's orange core; the rest of the fiery ramp is unchanged.
        0.40: dict(sky_top=(90, 142, 168), sky_mid=(206, 156, 144), sky_bot=(248, 134, 90),  horizon=(242, 82, 52)),
        0.44: dict(sky_top=(86, 132, 162), sky_mid=(216, 144, 130), sky_bot=(250, 120, 78),  horizon=(236, 66, 44)),
        0.50: dict(sky_top=(78, 118, 152), sky_mid=(222, 130, 116), sky_bot=(250, 108, 70),  horizon=(228, 52, 38)),
        0.56: dict(sky_top=(58, 96, 138),  sky_mid=(204, 116, 110), sky_bot=(244, 106, 72),  horizon=(218, 50, 40)),
        0.62: dict(sky_top=(36, 76, 114),  sky_mid=(138, 102, 130), sky_bot=(224, 112, 86),  horizon=(214, 62, 50)),
        0.86: dict(sky_top=(40, 82, 120),  sky_mid=(166, 124, 138), sky_bot=(240, 138, 110), horizon=(238, 96, 78)),
        0.88: dict(sky_top=(78, 142, 170), sky_mid=(204, 158, 150), sky_bot=(246, 158, 126), horizon=(246, 116, 94)),
        0.90: dict(sky_top=(82, 150, 178), sky_mid=(190, 178, 168), sky_bot=(244, 176, 142), horizon=(250, 138, 112)),
        0.94: dict(sky_top=(86, 156, 182), sky_mid=(172, 192, 188), sky_bot=(228, 198, 166), horizon=(250, 158, 134)),
    },
)


# 5. Rose-Magenta — bright jewel rose H338, MODERATE.
ROSE_MAGENTA = _spec(
    'Rose-Magenta',
    'A bright jewel rose (H338, chroma ~0.45, higher value) rising from a vivid rose horizon into a quiet violet blush, cyan mid held above — clean and luminous, the brightest of the pink family. MODERATE.',
    {
        # rose pushed brighter/higher-chroma (H~338, ~0.45) and lighter in value so
        # it separates by HUE *and* value from the deeper Ember/Fuchsia pink rows.
        0.40: dict(sky_top=(94, 146, 176), sky_mid=(204, 162, 192), sky_bot=(255, 150, 192), horizon=(255, 96, 156)),
        0.50: dict(sky_top=(84, 124, 164), sky_mid=(210, 146, 190), sky_bot=(255, 124, 184), horizon=(255, 64, 140)),
        0.62: dict(sky_top=(38, 78, 118),  sky_mid=(124, 106, 156), sky_bot=(212, 124, 180), horizon=(244, 84, 148)),
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(198, 166, 196), sky_bot=(252, 160, 196), horizon=(255, 110, 166)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(172, 188, 198), sky_bot=(234, 184, 202), horizon=(252, 123, 176)),
    },
)


# 6. Violet Twilight — purple-violet + pink, DRAMATIC.
VIOLET_TWILIGHT = _spec(
    'Violet Twilight',
    'Deep purple-violet blooming HIGH into the mid over a hot-pink horizon band — the dreamiest of the dramatic rows, colour reaching ~40% of the frame, cyan retreating to the zenith. DRAMATIC.',
    {
        # bloom pushed HIGH: the violet now saturates the mid (~40% of frame) with
        # a hotter pink horizon, so it reads clearly more dramatic than the moderate
        # magenta rows below it; cyan retreats to the zenith only.
        0.40: dict(sky_top=(94, 144, 176), sky_mid=(152, 130, 198), sky_bot=(190, 116, 194), horizon=(236, 108, 172)),
        0.44: dict(sky_top=(84, 130, 172), sky_mid=(140, 114, 198), sky_bot=(182, 102, 192), horizon=(236, 92, 166)),
        0.50: dict(sky_top=(70, 110, 160), sky_mid=(128, 96, 196),  sky_bot=(174, 88, 190),  horizon=(232, 74, 158)),
        0.56: dict(sky_top=(52, 90, 144),  sky_mid=(108, 84, 186),  sky_bot=(162, 86, 186),  horizon=(224, 72, 154)),
        0.62: dict(sky_top=(34, 72, 114),  sky_mid=(82, 78, 162),   sky_bot=(144, 90, 180),  horizon=(212, 78, 150)),
        0.86: dict(sky_top=(42, 82, 122),  sky_mid=(120, 98, 178),  sky_bot=(184, 112, 190), horizon=(232, 94, 164)),
        0.88: dict(sky_top=(80, 142, 172), sky_mid=(160, 138, 200), sky_bot=(202, 138, 200), horizon=(238, 112, 172)),
        0.90: dict(sky_top=(82, 150, 178), sky_mid=(166, 158, 204), sky_bot=(206, 152, 204), horizon=(240, 128, 180)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(162, 186, 204), sky_bot=(206, 184, 206), horizon=(240, 146, 186)),
    },
)


# 7. Fuchsia-Cyan — true fuchsia band under a held Alpine-cyan sliver, MODERATE.
FUCHSIA_CYAN = _spec(
    'Fuchsia-Cyan',
    'The duotone clash IS the feature: a true hot-fuchsia (H320) horizon band held cleanly beneath a kept Alpine-cyan sliver in the mid — magenta-below / cyan-above, vivid and intentional. MODERATE.',
    {
        # The cyan retention is the SIGNATURE: sky_mid stays strongly Alpine-cyan
        # while sky_bot/horizon push to true fuchsia (H~320, S0.55+), so the duotone
        # clash is sharp and intentional rather than a washed blend.
        0.40: dict(sky_top=(90, 152, 180), sky_mid=(136, 192, 204), sky_bot=(232, 120, 190), horizon=(252, 76, 166)),
        0.50: dict(sky_top=(80, 132, 166), sky_mid=(124, 184, 202), sky_bot=(240, 92, 182),  horizon=(250, 44, 148)),
        0.62: dict(sky_top=(38, 80, 118),  sky_mid=(76, 138, 172),  sky_bot=(190, 94, 174),  horizon=(234, 58, 146)),
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(134, 194, 206), sky_bot=(234, 132, 194), horizon=(252, 86, 170)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(140, 198, 206), sky_bot=(220, 174, 202), horizon=(248, 116, 180)),
    },
)


# 8. Lavender-Peach — soft lilac -> peach, GENTLE/NATURAL.
LAVENDER_PEACH = _spec(
    'Lavender-Peach',
    'The quietest of the set, but now two readable hues: a soft lilac (H285 S~0.30) upper-warm band melting through a clean blend into a pale peach (H28 S~0.40) horizon. Kept gentle by LOW value contrast, sky mostly cyan — not by killing saturation. NATURAL.',
    {
        # two committed hues — lilac (H~285) in the warm band, peach (H~28) at the
        # horizon — kept gentle via low VALUE contrast and a low natural band, so
        # the sky stays mostly cyan rather than washing to grey.
        0.40: dict(sky_top=(92, 150, 176), sky_mid=(200, 168, 210), sky_bot=(236, 192, 178), horizon=(252, 178, 138)),
        0.50: dict(sky_top=(82, 130, 162), sky_mid=(202, 158, 212), sky_bot=(240, 182, 168), horizon=(254, 159, 111)),
        0.62: dict(sky_top=(38, 80, 118),  sky_mid=(120, 116, 164), sky_bot=(200, 152, 168), horizon=(240, 156, 128)),
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(196, 174, 210), sky_bot=(234, 194, 182), horizon=(252, 184, 146)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(174, 188, 206), sky_bot=(224, 198, 188), horizon=(250, 190, 158)),
    },
)


# 9. Ember Red-Purple — deep red -> purple, DRAMATIC.
EMBER_RED_PURPLE = _spec(
    'Ember Red-Purple',
    'A moody deep ember-red horizon bleeding up through a higher-value magenta mid-step into a smouldering purple mid — the darkest, most cinematic of the dramatic rows, the colour bloom now reaching ~40% of the frame. The magenta hand-off keeps the red->purple meeting from greying out. DRAMATIC.',
    {
        # The red->purple hand-off is routed through a brighter MAGENTA sky_bot so
        # the meeting doesn't grey out; sky_mid stays deep purple, horizon deep red,
        # and the bloom is lifted higher (~40%) to read as one of the dramatic rows.
        0.40: dict(sky_top=(90, 142, 170), sky_mid=(166, 116, 178), sky_bot=(224, 110, 162), horizon=(230, 74, 96)),
        0.44: dict(sky_top=(82, 130, 166), sky_mid=(156, 100, 176), sky_bot=(224, 92, 156),  horizon=(224, 58, 84)),
        0.50: dict(sky_top=(72, 112, 154), sky_mid=(142, 84, 172),  sky_bot=(222, 76, 150),  horizon=(216, 46, 76)),
        0.56: dict(sky_top=(54, 92, 140),  sky_mid=(120, 74, 162),  sky_bot=(208, 74, 148),  horizon=(206, 46, 78)),
        0.62: dict(sky_top=(34, 74, 112),  sky_mid=(86, 66, 146),   sky_bot=(178, 80, 146),  horizon=(196, 56, 86)),
        0.86: dict(sky_top=(40, 82, 120),  sky_mid=(124, 92, 166),  sky_bot=(206, 104, 156), horizon=(222, 76, 98)),
        0.88: dict(sky_top=(80, 142, 170), sky_mid=(160, 132, 184), sky_bot=(214, 128, 170), horizon=(228, 94, 112)),
        0.90: dict(sky_top=(82, 150, 178), sky_mid=(164, 152, 192), sky_bot=(216, 142, 176), horizon=(230, 110, 126)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(160, 184, 198), sky_bot=(212, 178, 194), horizon=(230, 134, 146)),
    },
)


# 10. Pink-Gold — explicit pink -> gold DUOTONE, MODERATE.
PINK_GOLD = _spec(
    'Pink-Gold',
    'An explicit duotone: a visible hot-pink mid-band (H335 S~0.45) sitting over a gold horizon (H40) — pink-above / gold-below, celebratory and clearly distinct from the single-story Golden Hour. Cool cyan kept up top. MODERATE.',
    {
        # explicit two-tone: sky_bot/mid carry a hot-pink band (H~335) while the
        # horizon holds a gold core (H~40), so it reads as a pink->gold duotone and
        # not a second Golden Hour.
        0.40: dict(sky_top=(92, 148, 174), sky_mid=(216, 158, 184), sky_bot=(250, 132, 168), horizon=(255, 178, 86)),
        0.50: dict(sky_top=(82, 128, 160), sky_mid=(220, 144, 180), sky_bot=(252, 110, 158), horizon=(255, 162, 66)),
        0.62: dict(sky_top=(38, 80, 118),  sky_mid=(120, 122, 158), sky_bot=(214, 118, 156), horizon=(250, 158, 90)),
        0.88: dict(sky_top=(80, 146, 174), sky_mid=(212, 162, 186), sky_bot=(248, 142, 172), horizon=(255, 184, 102)),
        0.94: dict(sky_top=(86, 156, 182), sky_mid=(186, 184, 196), sky_bot=(234, 168, 186), horizon=(253, 192, 128)),
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
