"""
Sky COLOR-FIELD exploration — 5 high-end treatments of the pure atmosphere.

Scope: the sky's own color field only — the blue that grades to night and back.
NO objects (no clouds / sun / moon / stars / god-rays) and NO additive radial
glow — an additive blob over the sky clips to white and reads as a sun disc or
searchlight, which is forbidden. Any horizon warmth is BAKED INTO THE STOP RAMP
as a low wedge whose lightness never exceeds ~0.92 OKLab L, so it lifts the
horizon without ever blowing to white. Each treatment is judged purely on how
gorgeous the gradient itself reads across the full day cycle.

Every treatment is built on `game.sky_field` (OKLab perceptual interpolation +
non-uniform eased stops + Bayer dither) so they share the "stop looking like a
PowerPoint gradient" foundation and differ only in palette philosophy. Each
synthesizes its richer 5–7 stop ramp from the four existing biome anchors
(`sky_top / sky_mid / sky_bot / horizon`) via OKLab ops, so it renders against
the current keyframes with no biome.py edit.

Contract (consumed by render_field_variants.py and the design loop):
    draw_<name>(w, h, palette) -> opaque pygame.Surface of size (w, h)
    VARIANTS:      {name: func}
    VARIANT_NAMES: [name, ...]            # display order
    VARIANT_NOTES: {name: one-line intent}
"""
import pygame

from game.sky_field import (
    make_sky_field, oklab_lerp, srgb_to_oklab, oklab_to_srgb,
    with_value, shift_temperature,
)

# Hard ceiling on any baked horizon-warmth wedge. Above this the low band starts
# to blow toward paper-white and a red parrot silhouette stops reading against
# it; capping in OKLab L keeps warmth as glow-in-the-ramp, never a hot spot.
_WARM_L_CAP = 0.92


def _luma(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def _nightf(palette):
    """Continuous night-ness in [0,1] from zenith luminance — 1 at deep night,
    0 by full day. Lets a treatment morph smoothly across the cross-faded
    buckets instead of switching on a hard phase gate."""
    lum = _luma(palette['sky_top'])
    return max(0.0, min(1.0, (95.0 - lum) / 75.0))


def _twilightf(nf):
    """Peaks (≈1) at the dawn/dusk crossover, ≈0 at full day and deep night —
    the window where ember/belt warmth should be strongest."""
    return 1.0 - abs(nf - 0.5) * 2.0


def _cap_L(rgb, cap=_WARM_L_CAP):
    """Clamp a color's OKLab lightness so a warm wedge can never blow to white."""
    L, a, b = srgb_to_oklab(rgb)
    if L > cap:
        return oklab_to_srgb((cap, a, b))
    return rgb


def _desat(rgb, amt):
    """Pull chroma toward neutral by `amt` (0..1) in OKLab — used to bleed the
    magenta/red out of sunset mids so Skybit's RED hero parrot stays legible."""
    L, a, b = srgb_to_oklab(rgb)
    return oklab_to_srgb((L, a * (1.0 - amt), b * (1.0 - amt)))


def _pastelize(rgb, amt):
    """Lift toward a soft tint: raise OKLab lightness, ease chroma down."""
    L, a, b = srgb_to_oklab(rgb)
    return oklab_to_srgb((min(1.0, L + 0.10 * amt),
                          a * (1 - 0.35 * amt), b * (1 - 0.35 * amt)))


# ── 1. Deep-Space Night-led — jaw-dropping night, calm by day ────────────────
def draw_deep_space(w, h, palette):
    top, mid, bot, hor = (palette['sky_top'], palette['sky_mid'],
                          palette['sky_bot'], palette['horizon'])
    nf = _nightf(palette)
    tw = _twilightf(nf)
    # Authored around night: a graded navy depth with a faint milky temperature
    # band drifting LOW through the sky (a subtle hue shift, NOT stars). The
    # night zenith is lifted and pushed cooler-blue so the very top of frame
    # always reads as *sky*, never void — the gameplay layer below is already
    # dark, so a near-black top would read as dead.
    navy = shift_temperature(with_value(top, 0.07 * nf), -0.5 * nf)
    # Milky band: a whisper, not a line. The visible hard upper edge is killed by
    # (a) a weaker lerp toward the pale target (0.13 vs 0.20), (b) darkening the
    # milky peak ~15% L so it no longer pops, and (c) — in the stops below —
    # sliding it lower and widening the gap above it so the top fades in over a
    # long span instead of stepping in at a seam.
    milky = shift_temperature(oklab_lerp(mid, (190, 200, 225), 0.13 * nf),
                              0.15 * nf)
    milky = with_value(milky, -0.15 * nf)
    # Twilight plum→peach lives only in the low wedge, capped so it never blooms.
    plum = shift_temperature(oklab_lerp(bot, (150, 105, 140), 0.22 * tw), 0.10)
    peach = _cap_L(shift_temperature(oklab_lerp(hor, (250, 200, 175),
                                                0.30 * tw), 0.30))
    # Keep the lowest band a half-step deeper than the horizon anchor by day so
    # the white HUD score + pillar tops in the bottom ~15% hold contrast.
    low = with_value(peach, -0.03 * (1 - nf))
    # Lift the upper blend stop higher (0.28) and slide the milky peak lower
    # (0.70) to widen the inter-stop span to ~0.42 of frame — the milky drift
    # now eases in over a long gradient instead of arriving at a defined edge.
    stops = [
        (0.00, navy),
        (0.28, oklab_lerp(navy, mid, 0.55)),
        (0.70, milky),
        (0.84, oklab_lerp(milky, plum, 0.6)),
        (0.93, plum),
        (1.00, low),
    ]
    return make_sky_field(w, h, stops, dither_amp=2.4)


# ── 2. Hiroshige Bokashi — ukiyo-e graded Prussian-blue band ─────────────────
def draw_hiroshige_bokashi(w, h, palette):
    top, mid, bot, hor = (palette['sky_top'], palette['sky_mid'],
                          palette['sky_bot'], palette['horizon'])
    nf = _nightf(palette)
    # Prussian-blue lineage: cool the zenith, fade to a pale band low, hold the
    # warm horizon as the futa-iro second ink. Most of the grade lives in the
    # bottom third like a hand-pulled ichimonji bokashi.
    # At night, deepen the zenith and keep it cool so the indigo stays Prussian
    # ink rather than slumping to a flat washed grey-navy.
    deep = shift_temperature(with_value(top, -0.03 - 0.05 * nf), -0.5 - 0.2 * nf)
    deep = with_value(deep, 0.06 * nf)  # but never pure void at the very top
    # Pale low band: warmed slightly at night so the futa-iro ink survives
    # instead of going dead grey.
    pale = oklab_lerp(bot, (245, 245, 235), 0.30)
    pale = shift_temperature(pale, 0.12 * nf)
    # Pull ~10% chroma out of the mid so a sunset/dusk sky never goes hot-magenta
    # and swallow the red parrot silhouette.
    mid_q = _desat(mid, 0.10)
    horizon = _cap_L(hor)
    # At golden/sunset the cool ink was bleeding too high and the upper-mid went
    # neutral-grey before the warm second ink arrived. Raise the warm-ink onset
    # ~8% higher into frame (day-weighted, so night — already perfect — is left
    # untouched): the warm/pale transition stops move up and the cool mid_q stop
    # comes with them, keeping the mid juicy instead of grey.
    g = 1 - nf
    warm_lift = 0.08 * g
    stops = [
        (0.00, deep),
        (0.42, oklab_lerp(deep, mid_q, 0.7)),
        (0.66 - warm_lift, mid_q),
        (0.82 - warm_lift, oklab_lerp(mid_q, pale, 0.6)),
        (0.93 - warm_lift * 0.5, with_value(pale, -0.02)),
        (1.00, horizon),
    ]
    # Slightly stronger dither for the printed-ink tooth.
    return make_sky_field(w, h, stops, dither_amp=2.6)


# ── 3. Belt-of-Venus Twilight — counter-change + horizon ember ───────────────
def draw_belt_of_venus(w, h, palette):
    top, mid, bot, hor = (palette['sky_top'], palette['sky_mid'],
                          palette['sky_bot'], palette['horizon'])
    nf = _nightf(palette)
    bv = 0.5 + 0.5 * _twilightf(nf)  # ember intensity peaks at twilight
    # The signature is a real horizontal VALUE EVENT: a luminous ember band with
    # a measurably DARKER strip just below it, so counter-change reads as a true
    # belt rather than a soft fade. The ember sits higher than before (≈0.72) so
    # it floats clear of the horizon instead of merging into it.
    ember = _cap_L(shift_temperature(oklab_lerp(hor, (255, 190, 200),
                                                0.45 * bv), 0.3))
    # Faint COOL ember survives at night, but as a barely-there LIFT, not a
    # glowing stripe behind the lower pillar: pull the target toward a duller
    # blue, halve the mix, then darken (~19% L) + desaturate (~25%) so it can't
    # read as a bright horizontal seam.
    night = nf > 0.5
    if night:
        ember = _cap_L(shift_temperature(oklab_lerp(hor, (110, 120, 160),
                                                    0.20), -0.15))
        ember = _desat(with_value(ember, -0.19), 0.25)
    # Darker counter-change strip immediately below the ember (−7% L). At night
    # the counter-change is unwanted (it re-creates the stripe), so flatten it
    # to a near-flush shelf.
    shelf = with_value(ember, -0.02 if night else -0.07)
    # Day gets a faint warm horizon wedge so the row never reads as plain blue.
    day_warm = _cap_L(shift_temperature(oklab_lerp(hor, (250, 215, 185),
                                                   0.18 * (1 - nf)), 0.18))
    horizon = _cap_L(oklab_lerp(hor, day_warm, 1 - nf))
    # Desaturate the mid ~10% (red-parrot legibility).
    mid_q = _desat(shift_temperature(mid, -0.15), 0.10)
    # Keep the day/twilight ember high (≈0.72) where it floats as the hero belt.
    # At night ONLY, slide ember+shelf lower (0.74 / 0.86) and widen the gap so
    # the transition is feathered, leaving no hard edge behind the lower pillar.
    ember_pos = 0.74 if night else 0.72
    shelf_pos = 0.86 if night else 0.80
    stops = [
        (0.00, shift_temperature(with_value(top, -0.03 + 0.06 * nf), -0.4)),
        (0.40, mid_q),
        (0.62, oklab_lerp(mid_q, bot, 0.5)),
        (ember_pos, ember),
        (shelf_pos, shelf),
        (1.00, horizon),
    ]
    return make_sky_field(w, h, stops)


# ── 4. Alto Plum — bright, dreamy pastel daydream ────────────────────────────
def draw_alto_plum(w, h, palette):
    top, mid, bot, hor = (palette['sky_top'], palette['sky_mid'],
                          palette['sky_bot'], palette['horizon'])
    nf = _nightf(palette)
    # Deliberately the BRIGHT, airy, low-saturation counterpart to deep_space:
    # pushed further to rose/lilac, the whole value range LIFTED, chroma pulled
    # down so every phase reads unmistakably lighter and more pastel. This is the
    # daydream sky; deep_space is the rich deep one.
    # Heavier pastelization + an explicit lightness lift at each stop.
    def air(c, amt, lift):
        return with_value(_pastelize(c, amt), lift)
    rose = shift_temperature(oklab_lerp(top, (175, 130, 175), 0.40 * (1 - nf)),
                             0.12)
    lilac = oklab_lerp(mid, (185, 165, 200), 0.30 * (1 - nf))
    # Keep night lifted and cool-blue so the top never voids out.
    night_lift = 0.07 * nf
    # Widen the day/sunset value spread: deepen the two MID stops ~9% L (only at
    # day, faded out by night where the row is already lifted) so the red parrot
    # + green pillars get a value gap to read against. Pure value — no chroma.
    mid_dip = -0.09 * (1 - nf)
    stops = [
        (0.00, air(rose, 0.45 * (1 - nf) + 0.25, 0.05 + night_lift)),
        (0.38, with_value(air(lilac, 0.55 * (1 - nf) + 0.20, 0.06), mid_dip)),
        (0.66, with_value(
            air(oklab_lerp(lilac, bot, 0.45), 0.55 * (1 - nf) + 0.20, 0.05),
            mid_dip)),
        (0.86, air(_desat(bot, 0.15), 0.55 * (1 - nf) + 0.15, 0.04)),
        # Low wedge stays pastel-warm but capped and a half-step deeper by day so
        # white HUD text holds in the bottom ~15%.
        (1.00, with_value(_cap_L(air(hor, 0.40 * (1 - nf) + 0.15, 0.05)),
                          -0.03 * (1 - nf))),
    ]
    return make_sky_field(w, h, stops)


# ── 5. Atmospheric True — physical Rayleigh/Mie realism (no glow) ─────────────
def draw_atmospheric_true(w, h, palette):
    top, mid, bot, hor = (palette['sky_top'], palette['sky_mid'],
                          palette['sky_bot'], palette['horizon'])
    nf = _nightf(palette)
    tw = _twilightf(nf)
    # Physical structure: deepest, most-saturated value at the zenith; the change
    # compresses toward the horizon where you look through the most air. The Mie
    # forward-scatter warmth is baked as a SOFT PALE WEDGE low in the ramp —
    # capped at ≤0.92 L so it never blows to white — distinct from belt_of_venus's
    # stylized saturated ember.
    zenith = with_value(top, -0.05 + 0.07 * nf)  # deep, but lifted at night
    if nf > 0.0:
        zenith = shift_temperature(zenith, -0.2 * nf)
    # Pale Mie haze just above the horizon: a desaturated warm-white wedge, not a
    # bright bloom. Fades out at night.
    g = 1 - nf
    haze = _cap_L(_desat(oklab_lerp(bot, (235, 228, 215), 0.30 * g), 0.10))
    # Warm horizon wedge — soft and pale, chroma kept low and L capped.
    warm = _cap_L(_desat(shift_temperature(hor, 0.30 * g), 0.12))
    # Keep the very bottom a half-step deeper by day for HUD contrast.
    low = with_value(warm, -0.03 * g)
    stops = [
        (0.00, zenith),
        (0.28, top),
        # Extra ~5% chroma off the mid at SUNSET only (twilight-weighted, day/
        # golden/night left as-is) for even cleaner red-hero separation.
        (0.54, _desat(mid, 0.06 + 0.05 * tw)),
        (0.76, oklab_lerp(mid, bot, 0.55)),
        (0.90, haze),
        (1.00, low),
    ]
    return make_sky_field(w, h, stops)


VARIANTS = {
    "deep_space":        draw_deep_space,
    "hiroshige_bokashi": draw_hiroshige_bokashi,
    "belt_of_venus":     draw_belt_of_venus,
    "alto_plum":         draw_alto_plum,
    "atmospheric_true":  draw_atmospheric_true,
}
VARIANT_NAMES = list(VARIANTS.keys())
VARIANT_NOTES = {
    "deep_space":        "Night-led graded navy, lifted cool zenith + low milky drift; twilight plum→peach baked low",
    "hiroshige_bokashi": "Ukiyo-e Prussian-blue ichimonji bokashi, deepened night ink, desaturated mid",
    "belt_of_venus":     "Counter-change: luminous ember high (≈0.72) over a darker shelf; night ember is a faint cool lift, not a stripe",
    "alto_plum":         "Bright dreamy pastel rose/lilac — lifted value, low chroma at every phase",
    "atmospheric_true":  "Rayleigh/Mie realism: deep zenith, pale Mie haze + soft capped warm horizon wedge",
}
