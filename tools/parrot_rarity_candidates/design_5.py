"""design_5 · SOLAR QUETZAL — LEGENDARY parrot rarity-spectrum exploration.

The apex of the tab: a radiant sun-god macaw, the warm/day counterpart to
design_4 Aurora's cool/night. FULL legendary treatment — a blazing SUN-DISC
HALO behind the head (a near-solid warm-gold disc with soft additive falloff,
painted BEHIND the body so the head sits ON it, ringed by 6 long evenly-spaced
spokes pushed OUTSIDE the rim like a sunburst), a SEPARATE smaller feathered
gold crown-crest fanning up past the crown, and long luminous quetzal
tail-streamers (gold core, warm-yellow-emerald edge) trailing well below the
body. Pip keeps his aviators, tinted gold-luminous.

The legendary tell is the sun-disc halo PLUS the silhouette-breaking streamers.
Distinctness from Aurora: the disc is PURE gold (never orange-red, so it can't
tip into the Phoenix), and the streamer edge is biased warm/yellow toward gold
(not aurora-green) so it reads as a golden sun-streamer, not a cool ribbon.

Draw order mirrors design_4 Aurora: the soft additive halo/disc must NOT live
inside the masked layer or the house outline would box the bloom into a
dark-rimmed island. So the OPAQUE bird (body + front crest + streamer cores +
rim) is outlined alone with a warm-amber keyline so the gold silhouette holds
on pale day sky, and the soft back-disc + emerald streamer edges are laid
UNDER it on a padded aura surface — then the shared per-(frame, 3°-bucket)
rotation cache.

Scratch only — never registered in store_skins.BUILDERS.
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _add_outline
from game.draw import blit_glow
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.store_skins import HX, HY, CROWN_Y, COMPOSITE_W, COMPOSITE_H, PARROT_DY


# ── palette ───────────────────────────────────────────────────────────────────
_GOLD      = (255, 210, 74)         # #FFD24A radiant gold
_SUN_WHITE = (255, 243, 192)        # #FFF3C0 sun white
_AMBER     = (255, 154, 46)         # #FF9A2E warm amber
# Streamer edge biased WARM/yellow toward gold (#3FB97A→gold) so it reads as a
# golden sun-streamer, NOT Aurora's cool emerald-green ribbon — the distinctness
# lock against design_4.
_SUN_EMER  = (63, 185, 122)         # #3FB97A warm sun-emerald
_EMER_DEEP = (40, 132, 64)          # warmer/yellower deep edge for the keyline
_CORE      = (255, 255, 255)        # #FFFFFF core glow
_AMBER_DK  = (150, 78, 18)          # warm keyline so the gold body holds on sky
# Disc held to PURE warm gold (no orange-red) so the halo never tips into the
# Phoenix's fire — the value contrast against the body comes from the white core.
_DISC_RIM  = (255, 196, 70)
_DISC_CORE = (255, 236, 168)


# Radiant-gold re-plumage. The hero body resolves to THREE discrete value bands
# (sun-white chest core → radiant gold → amber shadow) instead of a smear, with
# emerald quetzal accents in the wing/tail and the deepest amber doing the line
# work so the bright plumage keeps crisp feather structure at $3500-apex detail.
# Aviators kept, tinted warm so Pip stays recognisable under the sun-god skin.
P_SOLAR = _pal(
    tail=[(196, 122, 28), (224, 158, 44), (250, 196, 70), (255, 224, 120)],
    tail_line=(150, 86, 22),
    body_shadow=(210, 132, 30),         # amber shadow band (deepest body value)
    body_main=_GOLD,                    # radiant gold band (mid value)
    body_chest=_SUN_WHITE,              # sun-white chest core (brightest band)
    body_belly=(255, 226, 130),
    sheen=(255, 255, 255, 150),
    wing_main=(238, 176, 50),
    wing_dark=(168, 96, 22),            # darker so the wing leading edge is clean
    wing_tip=_SUN_EMER,                 # warm-emerald quetzal accent on the wingtip
    wing_secondary=(150, 214, 150),
    wing_highlight=_SUN_WHITE,
    head_shadow=(206, 128, 28),
    head_main=_GOLD,
    head_cheek=(255, 232, 150),
    head_crown=(255, 226, 120),
    # Gold-luminous aviators — Pip's signature stays, tinted to the sun-god.
    lens_frame=_SUN_WHITE,
    lens_body=(46, 28, 10),
    lens_tint=(255, 196, 90, 130),
    lens_glint=(255, 255, 255),
    beak_main=(58, 38, 16),
    beak_dark=(32, 20, 8),
    beak_gloss=(150, 110, 60),
    foot=(150, 96, 34),
)


# Disc geometry — radius ~head-height, centred just behind/above the head so the
# face sits ON it. Spokes are pushed OUTSIDE the rim for a clean sunburst ring.
_DCX, _DCY = HX - 2, HY - 4
_DISC_R = 17


def _sun_disc_back(surf):
    # The missing legendary tell, now a real BACK-LAYER sun-disc. A near-solid
    # warm-gold disc (radius ~head-height) with soft additive falloff, painted
    # BEFORE the body so the head sits ON it like a sun-god. Held to PURE gold
    # (no orange-red) so it can't be mistaken for the Phoenix's fire; its read
    # against the gold body comes from the bright core + ringed spokes, not hue.
    #
    # Two passes mirror Aurora's back-aura: an additive bloom (shines on night
    # sky) plus an opaque-ish disc body with a dark-gold rim so the disc ALSO
    # holds as a solid sun on a bright day sky where additive washes out.
    cx, cy = _DCX, _DCY

    # ── additive corona bloom (night) ───────────────────────────────────────
    glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    blit_glow(glow, cx, cy, _DISC_R + 12, (255, 168, 56), alpha=110)
    blit_glow(glow, cx, cy, _DISC_R + 3, (255, 214, 110), alpha=130)
    blit_glow(glow, cx, cy, _DISC_R - 6, (255, 244, 190), alpha=150)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── opaque disc body (day) ──────────────────────────────────────────────
    # A solid-ish gold disc so the head reads as sitting ON a sun, with a soft
    # 3-step value falloff (rim → gold → bright core) and a thin amber rim line
    # so it never dissolves into a bright sky.
    det = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.circle(det, (*_AMBER, 235), (cx, cy), _DISC_R + 1)
    pygame.draw.circle(det, (*_DISC_RIM, 225), (cx, cy), _DISC_R)
    pygame.draw.circle(det, (*_GOLD, 230), (cx, cy), _DISC_R - 4)
    pygame.draw.circle(det, (*_DISC_CORE, 235), (cx, cy), _DISC_R - 9)

    # 6 LONG evenly-spaced spokes pushed OUTSIDE the rim — a radially symmetric
    # sunburst ring behind the head, NOT short dense spikes on top. Each spoke:
    # amber base → gold core → a white tip spark, tapering as it reaches out.
    n = 6
    for i in range(n):
        a = (i / n) * math.tau + 0.26          # offset so no spoke hits the crest
        ca, sa = math.cos(a), math.sin(a)
        r0 = _DISC_R + 1
        r1 = _DISC_R + 12
        x0, y0 = cx + ca * r0, cy + sa * r0
        x1, y1 = cx + ca * r1, cy + sa * r1
        xm, ym = cx + ca * (r0 + 4), cy + sa * (r0 + 4)
        pygame.draw.line(det, _AMBER, (x0, y0), (x1, y1), 4)
        pygame.draw.line(det, _GOLD, (x0, y0), (xm, ym), 2)
        pygame.draw.circle(det, _SUN_WHITE, (int(x1), int(y1)), 1)

    surf.blit(det, (0, 0))


def _streamer(surf, root, pts, *, core_first):
    # A single quetzal tail-streamer: a flowing gold-cored band edged warm-
    # emerald. Two passes around the body — the warm-emerald edge + deep keyline
    # go BEHIND the body (core_first=False) so the roots tuck under the tail, and
    # the bright GOLD core goes ON TOP afterwards (core_first=True) so the
    # luminous centre always reads. The edge is biased warm/yellow so it never
    # reads as Aurora's cool ribbon. A continuous deep keyline keeps it crisp on
    # pale day sky.
    path = [root] + pts
    if not core_first:
        pygame.draw.lines(surf, _EMER_DEEP, False, path, 6)
        pygame.draw.lines(surf, _SUN_EMER, False, path, 4)
    else:
        pygame.draw.lines(surf, _AMBER, False, path, 3)
        pygame.draw.lines(surf, _GOLD, False, path, 2)
        pygame.draw.lines(surf, _SUN_WHITE, False, path[:2], 1)
        tip = path[-1]
        # A small emerald spade-tip — the resplendent-quetzal tell at the end.
        pygame.draw.circle(surf, _EMER_DEEP, tip, 3)
        pygame.draw.circle(surf, _SUN_EMER, tip, 2)
        pygame.draw.circle(surf, _CORE, (tip[0], tip[1] - 1), 1)


# Two streamer paths swept down-back below the body, well past the tail, so the
# lower silhouette is unmistakably a quetzal trailing light. Shared by the back
# (emerald edge) and front (gold core) passes so the two layers register.
_STREAM_ROOT = (16, 30 + PARROT_DY)
_STREAM_A = [(10, 44 + PARROT_DY), (16, 58 + PARROT_DY), (10, 72 + PARROT_DY)]
_STREAM_B = [(6, 40 + PARROT_DY), (4, 54 + PARROT_DY), (12, 66 + PARROT_DY)]


def _streamers_back(surf):
    _streamer(surf, _STREAM_ROOT, _STREAM_A, core_first=False)
    _streamer(surf, _STREAM_ROOT, _STREAM_B, core_first=False)


def _streamers_front(surf):
    _streamer(surf, _STREAM_ROOT, _STREAM_A, core_first=True)
    _streamer(surf, _STREAM_ROOT, _STREAM_B, core_first=True)


def _paint_front(surf, wing_angle_deg):
    # Bright gold streamer cores on top of the body so the luminous centre wins.
    _streamers_front(surf)

    # Warm-shadow band directly under the crest so the HEAD silhouette separates
    # from the crest spikes at 40px — without it the crest + skull fuse into one
    # orange blob. A short amber arc tracing the crown line, darkest where the
    # crest roots meet the skull, restores head/beak/face contrast.
    pygame.draw.lines(surf, _AMBER_DK, False,
                      [(HX - 9, CROWN_Y + 5), (HX - 3, CROWN_Y + 3),
                       (HX + 4, CROWN_Y + 4), (HX + 10, CROWN_Y + 7)], 2)

    # Clean wing leading edge — a crisp sun-white highlight tracing the back/
    # underside that faces open sky, so the radiant mass keeps a hard glowing
    # edge (crisp feather structure, not a horizontal-streak blur).
    pygame.draw.lines(surf, _AMBER_DK, False,
                      [(14, 41), (22, 45), (30, 48), (40, 47), (48, 42)], 2)
    pygame.draw.lines(surf, _SUN_WHITE, False,
                      [(15, 40), (22, 44), (30, 47), (40, 46), (47, 41)], 1)

    # Feathered gold crown-crest — a SEPARATE, smaller crown element kept clear
    # of the disc rim so disc and crest don't merge. Three plumes leaning
    # outward, centre tallest, each: amber keyline root → gold body → emerald
    # fleck tip → white spark, so it reads as a feathered crown at 40px, not the
    # disc's spokes. Smaller reach than R1 so it stays a crown, not a second fan.
    base_y = CROWN_Y + 3
    for dx, h, lean in ((-4, 12, -4), (-1, 17, 1), (4, 13, 6)):
        x = HX + dx
        root = (x, base_y + 2)
        mid = (x + lean // 2, base_y - h // 2)
        tip = (x + lean, base_y - h)
        pygame.draw.line(surf, _AMBER_DK, root, mid, 5)
        pygame.draw.line(surf, _AMBER, root, mid, 4)
        pygame.draw.line(surf, _GOLD, mid, tip, 3)
        pygame.draw.circle(surf, _SUN_EMER, tip, 2)       # emerald quetzal fleck
        pygame.draw.circle(surf, _CORE, (tip[0], tip[1] - 1), 1)

    # A few emerald quetzal accent-flecks on the chest + a sun-spark off the
    # back, the small jewels that say "resplendent" up close without muddying
    # the 40px read.
    for fx, fy in ((30, 50), (36, 54), (26, 46)):
        pygame.draw.circle(surf, _SUN_EMER, (fx, fy), 2)
        pygame.draw.circle(surf, (150, 214, 150), (fx, fy - 1), 1)
    pygame.draw.circle(surf, _SUN_WHITE, (HX + 13, HY + 6), 2)
    pygame.draw.circle(surf, _CORE, (HX + 13, HY + 5), 1)

    # Aviator read at 40px — a 2px gold-luminous rim + a single bright glint pixel
    # + a dark frame bridge, painted over the recoloured lenses so the aviators
    # survive the navy store card. Pip-without-readable-aviators isn't Pip.
    lx, rx, ly = HX - 4, HX + 6, HY - 1
    pygame.draw.circle(surf, _SUN_WHITE, (lx, ly), 4, 2)        # gold-lum rim
    pygame.draw.circle(surf, _SUN_WHITE, (rx, ly), 4, 2)
    pygame.draw.line(surf, (38, 24, 10), (lx + 3, ly - 1), (rx - 3, ly - 1), 2)  # dark bridge
    pygame.draw.circle(surf, _CORE, (lx - 1, ly - 1), 1)       # single glint pixel
    pygame.draw.circle(surf, _CORE, (rx - 1, ly - 1), 1)


def _solar_getter():
    # Mirrors design_4 Aurora's compose: the house outline is grown from the
    # alpha mask, so the soft additive sun-disc + emerald streamer edges must NOT
    # be part of the masked layer — else the dark rim would box the bloom into a
    # dark-rimmed island and kill the halo. So the OPAQUE bird (body + front
    # crest/streamer-cores/rim/aviators) is outlined ALONE with a warm-amber
    # keyline (not the house near-black) so the gold silhouette holds on pale day
    # sky, and the back disc + streamer edges are laid UNDER it on a padded aura
    # surface, then the shared per-(frame, 3°-bucket) rotation cache.
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        bird = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        bird.blit(_build_parrot_with_palette(wing_angle, P_SOLAR), (0, PARROT_DY))
        _paint_front(bird, wing_angle)
        bird = _add_outline(bird, outline_color=(80, 44, 12, 235))

        aura = pygame.Surface(bird.get_size(), pygame.SRCALPHA)
        pad = (bird.get_width() - COMPOSITE_W) // 2
        back = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _sun_disc_back(back)
        _streamers_back(back)
        aura.blit(back, (pad, pad))
        aura.blit(bird, (0, 0))
        return aura

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_flat(a) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


build = _solar_getter()
