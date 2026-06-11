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
#   * DECOUPLED moments — the rule that drives this whole set: the SUNSET is the
#     magnificent, emotional half — bolder, deeper, more saturated, pushed for
#     grandeur. The SUNRISE is a genuinely DIFFERENT moment, never a softer
#     mirror of the same colour. It is EITHER:
#       [C] a CONTRASTING, cooler/quieter hue family from the sunset (dove-blue,
#           cyan-peach, pink-grey, soft gold, gentle peach), so dawn and dusk
#           read as plainly different times of day; OR
#       [S] the SAME hue family as the sunset but at a FRACTION of its chroma —
#           a low, restrained whisper, far quieter in saturation AND value, kept
#           to a thin near-horizon band so it never twins the sunset's bloom.
#     Either way the sunrise must read CALMER and lower-energy than that row's
#     sunset. (Real dawn skies are clearer, paler and cooler; dusk holds the
#     richer, weary, more saturated colour — the study leans into that truth.)


# 1. Molten Gold & Ember — grand blazing gold->ember sunset, DRAMATIC.
#    Dawn [S]: pale apricot whisper (same warm family, a fraction of the chroma).
MOLTEN_GOLD_EMBER = _spec(
    'Molten Gold & Ember',
    'SUNSET: a grand blazing gold (H46) sky_bot deepening to a molten ember-orange (H22) horizon, the fire climbing up through the mid to ~40% of the frame, widened dwell — the most opulent gold row. SUNRISE [S]: a pale apricot whisper, same warm family at a fraction of the chroma, kept to a thin low band. DRAMATIC.',
    {
        # SUNSET — gold sky_bot over an ember horizon, the warm bloom lifted high
        # into a buttery sky_mid so it reads sky-filling and magnificent, not a
        # low band; cyan retreats to the zenith only.
        0.40: dict(sky_top=(92, 148, 174), sky_mid=(214, 184, 138), sky_bot=(255, 192, 86),  horizon=(255, 150, 56)),
        0.44: dict(sky_top=(88, 140, 170), sky_mid=(226, 178, 120), sky_bot=(255, 184, 72),  horizon=(255, 134, 44)),
        0.50: dict(sky_top=(80, 126, 160), sky_mid=(234, 170, 104), sky_bot=(255, 176, 58),  horizon=(252, 116, 34)),
        0.56: dict(sky_top=(60, 102, 144), sky_mid=(220, 156, 104), sky_bot=(252, 162, 60),  horizon=(244, 104, 36)),
        0.62: dict(sky_top=(36, 78, 116),  sky_mid=(150, 130, 130), sky_bot=(230, 154, 86),  horizon=(238, 116, 50)),
        # SUNRISE [S] — same warm family, but a soft pale apricot kept low and pale:
        # far lower chroma than the sunset's molten gold, the mid barely tinted.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(176, 192, 188), sky_bot=(238, 204, 176), horizon=(252, 192, 152)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(166, 196, 196), sky_bot=(226, 206, 192), horizon=(248, 198, 170)),
    },
)


# 2. Volcanic Crimson — deep scarlet-red, sky-filling, DRAMATIC.
#    Dawn [C]: calm dove-blue / soft lilac (a contrasting cool, quiet hue).
VOLCANIC_CRIMSON = _spec(
    'Volcanic Crimson',
    'SUNSET: a deep volcanic scarlet-red (H4) flooding the lower sky and washing the mid a smouldering crimson, cyan only at the zenith — the most intense red of the set, widened dwell. SUNRISE [C]: a calm dove-blue mid melting into a soft lilac horizon, a cool contrasting hue clearly different from the fiery dusk. DRAMATIC.',
    {
        # SUNSET — scarlet horizon, the red bloom carried up through a hot-crimson
        # sky_bot into a dusky-red mid so the whole lower frame burns.
        0.40: dict(sky_top=(90, 140, 166), sky_mid=(206, 132, 132), sky_bot=(244, 96, 76),   horizon=(232, 50, 40)),
        0.44: dict(sky_top=(86, 130, 162), sky_mid=(214, 118, 116), sky_bot=(244, 80, 64),   horizon=(224, 40, 36)),
        0.50: dict(sky_top=(78, 116, 152), sky_mid=(218, 104, 102), sky_bot=(242, 66, 54),   horizon=(214, 32, 32)),
        0.56: dict(sky_top=(58, 96, 138),  sky_mid=(198, 96, 100),  sky_bot=(234, 64, 56),   horizon=(204, 34, 36)),
        0.62: dict(sky_top=(36, 76, 114),  sky_mid=(132, 90, 122),  sky_bot=(204, 78, 76),   horizon=(196, 46, 50)),
        # SUNRISE [C] — a cool, quiet dove-blue / lilac dawn: nothing red at all, so
        # the morning reads as an entirely different, calmer moment.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(168, 184, 204), sky_bot=(196, 192, 214), horizon=(214, 196, 216)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(160, 188, 206), sky_bot=(190, 196, 216), horizon=(206, 198, 216)),
    },
)


# 3. Magenta Storm — intense magenta->purple, DRAMATIC.
#    Dawn [S]: a low mauve mist (same family, far quieter).
MAGENTA_STORM = _spec(
    'Magenta Storm',
    'SUNSET: an intense storm-magenta (H322) horizon blooming up through a hot-magenta sky_bot into a brooding purple mid (~40% of the frame), widened dwell — electric and tempestuous. SUNRISE [S]: a low mauve mist, the same magenta family bled down to a pale whisper kept near the horizon. DRAMATIC.',
    {
        # SUNSET — the magenta climbs high; sky_mid goes deep storm-purple while the
        # horizon stays the hottest magenta, the meeting routed through a bright
        # sky_bot so it never greys out.
        0.40: dict(sky_top=(92, 142, 172), sky_mid=(168, 110, 184), sky_bot=(228, 92, 184),  horizon=(244, 56, 152)),
        0.44: dict(sky_top=(84, 130, 168), sky_mid=(156, 94, 184),  sky_bot=(230, 74, 178),  horizon=(244, 40, 144)),
        0.50: dict(sky_top=(74, 114, 158), sky_mid=(142, 80, 182),  sky_bot=(230, 58, 172),  horizon=(240, 28, 134)),
        0.56: dict(sky_top=(54, 94, 142),  sky_mid=(120, 72, 168),  sky_bot=(216, 60, 166),  horizon=(228, 32, 132)),
        0.62: dict(sky_top=(34, 74, 112),  sky_mid=(86, 66, 146),   sky_bot=(184, 70, 158),  horizon=(214, 44, 130)),
        # SUNRISE [S] — same magenta family but a soft, low mauve mist: chroma
        # dropped hard, value lifted, kept to a thin near-horizon band.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(182, 178, 202), sky_bot=(216, 178, 204), horizon=(232, 172, 200)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(174, 186, 204), sky_bot=(212, 184, 204), horizon=(226, 178, 200)),
    },
)


# 4. Tropical Fuchsia-Cyan — bold fuchsia under a kept Alpine-cyan band, MODERATE.
#    Dawn [C]: clean pale cyan-peach (a cool contrasting hue).
TROPICAL_FUCHSIA_CYAN = _spec(
    'Tropical Fuchsia-Cyan',
    'SUNSET: the duotone clash IS the feature — a bold hot-fuchsia (H322) horizon band held cleanly beneath a KEPT Alpine-cyan sliver in the mid: magenta-below / cyan-above, vivid and intentional. SUNRISE [C]: a clean pale cyan-peach dawn — cool cyan mid warming to the faintest peach horizon, a different and calmer hue than the dusk. MODERATE.',
    {
        # SUNSET — the cyan retention is the signature: sky_mid stays strongly
        # Alpine-cyan while sky_bot/horizon push to true fuchsia, so the clash is
        # sharp and deliberate, kept to a horizon-to-low band (MODERATE).
        0.40: dict(sky_top=(90, 152, 180), sky_mid=(136, 192, 204), sky_bot=(232, 116, 188), horizon=(252, 70, 162)),
        0.50: dict(sky_top=(80, 132, 166), sky_mid=(124, 184, 202), sky_bot=(240, 86, 180),  horizon=(250, 38, 144)),
        0.62: dict(sky_top=(38, 80, 118),  sky_mid=(76, 138, 172),  sky_bot=(190, 90, 172),  horizon=(232, 52, 142)),
        # SUNRISE [C] — cyan-peach: the mid keeps a cool cyan while the horizon warms
        # only to a pale peach, so dawn is clearly cooler and quieter than the dusk.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(150, 196, 204), sky_bot=(212, 204, 196), horizon=(244, 198, 168)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(152, 198, 204), sky_bot=(206, 206, 200), horizon=(240, 200, 176)),
    },
)


# 5. Amethyst & Rose — luxe violet->rose, MODERATE.
#    Dawn [S]: subtle lavender haze (same family, far quieter).
AMETHYST_ROSE = _spec(
    'Amethyst & Rose',
    'SUNSET: a luxe amethyst-violet (H280) sky_bot melting into a jewel-rose (H338) horizon — a rich violet-to-rose duotone kept to a horizon-to-low band, the cyan mid breathing above. SUNRISE [S]: a subtle lavender haze, the same violet family pared to a pale low whisper. MODERATE.',
    {
        # SUNSET — amethyst above, rose at the horizon; MODERATE, so the colour is
        # rich but held low and the sky_mid stays nearer the Alpine cool.
        0.40: dict(sky_top=(94, 146, 176), sky_mid=(180, 156, 202), sky_bot=(204, 130, 198), horizon=(248, 110, 158)),
        0.50: dict(sky_top=(84, 126, 164), sky_mid=(178, 142, 202), sky_bot=(206, 110, 196), horizon=(250, 82, 146)),
        0.62: dict(sky_top=(38, 78, 118),  sky_mid=(116, 110, 162), sky_bot=(176, 110, 182), horizon=(232, 92, 144)),
        # SUNRISE [S] — same violet family, a pale lavender haze: chroma far lower,
        # value lifted, only a faint low band.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(184, 180, 204), sky_bot=(208, 184, 208), horizon=(224, 178, 204)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(176, 188, 204), sky_bot=(204, 188, 208), horizon=(218, 182, 204)),
    },
)


# 6. Tangerine Inferno — vivid sky-filling orange, DRAMATIC.
#    Dawn [C]: cool pink-grey calm (a contrasting muted cool hue).
TANGERINE_INFERNO = _spec(
    'Tangerine Inferno',
    'SUNSET: a vivid tangerine (H26) that climbs from the horizon through the whole lower-mid frame, cyan held only at the zenith — a sky-filling inferno, widened dwell. SUNRISE [C]: a cool pink-grey calm — a desaturated dove-pink mid over a faint grey-pink horizon, plainly quieter and cooler than the blazing dusk. DRAMATIC.',
    {
        # SUNSET — tangerine floods the lower frame and washes the mid warm; the
        # bloom reaches ~40% of the frame for a true inferno.
        0.40: dict(sky_top=(92, 146, 172), sky_mid=(218, 166, 130), sky_bot=(252, 158, 80),  horizon=(255, 134, 52)),
        0.44: dict(sky_top=(88, 138, 168), sky_mid=(228, 154, 112), sky_bot=(255, 146, 68),  horizon=(255, 120, 44)),
        0.50: dict(sky_top=(80, 124, 158), sky_mid=(232, 142, 98),  sky_bot=(255, 136, 58),  horizon=(255, 106, 38)),
        0.56: dict(sky_top=(60, 100, 142), sky_mid=(214, 128, 98),  sky_bot=(252, 128, 60),  horizon=(252, 100, 40)),
        0.62: dict(sky_top=(36, 78, 116),  sky_mid=(144, 114, 134), sky_bot=(230, 128, 78),  horizon=(248, 112, 52)),
        # SUNRISE [C] — cool pink-grey: a muted dove-pink mid and a soft grey-pink
        # horizon, low chroma, no orange — a calm, cool counterpoint to the inferno.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(184, 186, 198), sky_bot=(208, 188, 198), horizon=(222, 188, 198)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(178, 190, 200), sky_bot=(204, 192, 200), horizon=(216, 190, 198)),
    },
)


# 7. Coral Blaze — warm coral->salmon, MODERATE.
#    Dawn [S]: soft blush whisper (same coral family, far quieter).
CORAL_BLAZE = _spec(
    'Coral Blaze',
    'SUNSET: a warm coral (H14) melting up from a salmon-red horizon, sat lifted so it reads unmistakably coral; the mid stays a cool blush for a clean reef glow, kept to a horizon-to-low band. SUNRISE [S]: a soft blush whisper, the same coral family pared to a pale low band. MODERATE.',
    {
        # SUNSET — salmon-coral; MODERATE, so the rich coral is held low while the
        # sky_mid keeps a cool blush rather than blooming high.
        0.40: dict(sky_top=(92, 148, 174), sky_mid=(204, 168, 172), sky_bot=(255, 162, 132), horizon=(255, 118, 92)),
        0.50: dict(sky_top=(82, 128, 160), sky_mid=(210, 156, 162), sky_bot=(255, 144, 116), horizon=(255, 82, 60)),
        0.62: dict(sky_top=(38, 80, 118),  sky_mid=(118, 124, 150), sky_bot=(222, 144, 142), horizon=(252, 112, 96)),
        # SUNRISE [S] — same coral family, a soft blush: chroma dropped, value up,
        # only a faint warm band near the horizon.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(190, 184, 192), sky_bot=(236, 196, 188), horizon=(252, 184, 168)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(180, 190, 196), sky_bot=(230, 198, 192), horizon=(248, 188, 176)),
    },
)


# 8. Indigo & Fire — fiery red-orange horizon under a DEEP INDIGO sky, DRAMATIC.
#    Dawn [C]: soft gold whisper (a quiet warm contrast to the indigo dusk).
INDIGO_FIRE = _spec(
    'Indigo & Fire',
    'SUNSET: the high-contrast jewel of the set — a fiery red-orange (H18) horizon burning beneath a DEEP INDIGO (H250) sky_bot/mid, the cool indigo pressing down on the flame within a single sky, widened dwell. SUNRISE [C]: a soft gold whisper, a quiet warm glow that contrasts the indigo dusk and reads far calmer. DRAMATIC.',
    {
        # SUNSET — the drama is the COLLISION inside one sky: indigo dominates the
        # mid/bot while the horizon holds a thin, fierce red-orange flame. Route the
        # indigo->flame meeting through a violet sky_bot so it doesn't grey out.
        0.40: dict(sky_top=(86, 132, 168), sky_mid=(96, 96, 168),   sky_bot=(150, 92, 152),  horizon=(248, 120, 64)),
        0.44: dict(sky_top=(78, 120, 162), sky_mid=(82, 84, 164),   sky_bot=(146, 80, 142),  horizon=(250, 104, 52)),
        0.50: dict(sky_top=(66, 104, 152), sky_mid=(68, 72, 158),   sky_bot=(142, 70, 132),  horizon=(250, 88, 44)),
        0.56: dict(sky_top=(50, 86, 138),  sky_mid=(58, 66, 146),   sky_bot=(134, 70, 128),  horizon=(244, 84, 46)),
        0.62: dict(sky_top=(32, 70, 112),  sky_mid=(48, 60, 128),   sky_bot=(120, 72, 122),  horizon=(232, 92, 56)),
        # SUNRISE [C] — a soft gold whisper: a pale warm glow, low chroma, kept low,
        # a calm and entirely different mood from the indigo-and-flame dusk.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(178, 190, 184), sky_bot=(232, 202, 168), horizon=(250, 196, 146)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(170, 194, 192), sky_bot=(224, 204, 180), horizon=(246, 200, 164)),
    },
)


# 9. Rose-Gold Royale — opulent hot-pink->gold duotone, MODERATE.
#    Dawn [S]: quiet rose-gold haze (same family, far quieter).
ROSE_GOLD_ROYALE = _spec(
    'Rose-Gold Royale',
    'SUNSET: an opulent duotone — a hot-pink (H335) mid-band sitting over a rich gold (H42) horizon, pink-above / gold-below, celebratory and regal, kept to a horizon-to-low band. SUNRISE [S]: a quiet rose-gold haze, the same pink-gold family pared to a pale low whisper. MODERATE.',
    {
        # SUNSET — explicit two-tone: a hot-pink sky_bot/mid band over a gold
        # horizon core; MODERATE, held low so it reads as a clean rose-gold glow.
        0.40: dict(sky_top=(92, 148, 174), sky_mid=(218, 156, 184), sky_bot=(252, 126, 164), horizon=(255, 174, 80)),
        0.50: dict(sky_top=(82, 128, 160), sky_mid=(222, 140, 178), sky_bot=(252, 102, 152), horizon=(255, 156, 58)),
        0.62: dict(sky_top=(38, 80, 118),  sky_mid=(120, 120, 158), sky_bot=(214, 112, 152), horizon=(250, 152, 84)),
        # SUNRISE [S] — same rose-gold family, a quiet haze: chroma dropped, value
        # lifted, only a faint pink-warm low band.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(196, 180, 192), sky_bot=(236, 188, 184), horizon=(252, 196, 158)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(182, 188, 196), sky_bot=(230, 192, 190), horizon=(248, 198, 170)),
    },
)


# 10. Aurora Teal-Magenta — bold teal<->magenta "electric" aurora sky, DRAMATIC.
#     Dawn [C]: gentle peach calm (a warm, quiet contrast to the electric dusk).
AURORA_TEAL_MAGENTA = _spec(
    'Aurora Teal-Magenta',
    'SUNSET: an electric aurora sky — a bold magenta (H320) horizon arcing up into a luminous TEAL (H180) mid that ties to the Alpine cyan, a teal<->magenta charge filling the lower-mid frame, widened dwell. SUNRISE [C]: a gentle peach calm, a soft warm low glow that reads quiet and different from the electric dusk. DRAMATIC.',
    {
        # SUNSET — the aurora charge: a hot magenta horizon meeting a glowing teal
        # mid (the teal is on-brand with the Alpine cyan), the bloom lifted high so
        # the electric clash fills the lower-mid frame.
        0.40: dict(sky_top=(88, 152, 182), sky_mid=(80, 188, 184),  sky_bot=(196, 132, 196), horizon=(244, 78, 168)),
        0.44: dict(sky_top=(82, 146, 180), sky_mid=(66, 188, 182),  sky_bot=(202, 116, 194), horizon=(246, 60, 162)),
        0.50: dict(sky_top=(72, 134, 174), sky_mid=(54, 186, 180),  sky_bot=(208, 100, 192), horizon=(246, 44, 154)),
        0.56: dict(sky_top=(54, 110, 158), sky_mid=(52, 168, 174),  sky_bot=(198, 96, 184),  horizon=(236, 48, 152)),
        0.62: dict(sky_top=(34, 78, 120),  sky_mid=(52, 130, 158),  sky_bot=(172, 92, 174),  horizon=(222, 58, 146)),
        # SUNRISE [C] — gentle peach: a soft, low, warm glow, low chroma, no teal or
        # magenta — a calm, plainly different counterpoint to the electric dusk.
        0.88: dict(sky_top=(80, 146, 176), sky_mid=(184, 190, 190), sky_bot=(238, 200, 180), horizon=(252, 192, 160)),
        0.94: dict(sky_top=(86, 156, 184), sky_mid=(176, 192, 196), sky_bot=(230, 202, 188), horizon=(248, 196, 174)),
    },
)


# Sheet order matches the 10 fresh directions in the brief.
CONCEPTS = [
    ('molten_gold_ember', MOLTEN_GOLD_EMBER),
    ('volcanic_crimson', VOLCANIC_CRIMSON),
    ('magenta_storm', MAGENTA_STORM),
    ('tropical_fuchsia_cyan', TROPICAL_FUCHSIA_CYAN),
    ('amethyst_rose', AMETHYST_ROSE),
    ('tangerine_inferno', TANGERINE_INFERNO),
    ('coral_blaze', CORAL_BLAZE),
    ('indigo_fire', INDIGO_FIRE),
    ('rose_gold_royale', ROSE_GOLD_ROYALE),
    ('aurora_teal_magenta', AURORA_TEAL_MAGENTA),
]
