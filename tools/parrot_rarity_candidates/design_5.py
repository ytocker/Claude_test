"""design_5 · SOLAR QUETZAL — LEGENDARY parrot rarity-spectrum exploration.

The apex of the tab: a radiant sun-god macaw, the warm/day counterpart to
design_4 Aurora's cool/night. FULL legendary treatment — a sun-disc halo
blazing BEHIND the head with short radiating rays (hotter/brighter than
Aurora's soft ring), a feathered gold crown-crest fanning up past the crown,
and long luminous quetzal tail-streamers (gold core, emerald edge) trailing
well below the body to break the lower silhouette. Pip keeps his aviators,
tinted gold-luminous.

The 40px truth-read is carried by the halo+streamer pair: the sun-disc is the
single brightest mass on either sky, and the two streamers are the silhouette
break no epic in the set has. The big risk is the bright-gold body washing out
on pale day sky, so — like the astronaut's white — the whole bird is wrapped in
a continuous warm-amber keyline (a darker outline colour) so the silhouette
holds against the sky instead of dissolving into it.

The halo, rays and streamer roots paint BEHIND the body, so the body-first
order in _make_skin can't be used — this uses its own compose (back halo/rays
+ streamers → radiant body → front crest + streamer cores + rim) mirroring
_make_skin's lazy flat-build + per-(frame, 3°-bucket) rotation cache.

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
_EMERALD   = (47, 185, 138)         # #2FB98A quetzal emerald
_EMER_DEEP = (24, 120, 92)          # deeper emerald for streamer edge keying
_CORE      = (255, 255, 255)        # #FFFFFF core glow
_AMBER_DK  = (150, 78, 18)          # warm keyline so the gold body holds on sky

# Radiant-gold re-plumage: a luminous gold body with a sun-white chest, emerald
# quetzal accents in the wing/tail, and the deepest amber doing the line work so
# the bright plumage still has internal structure. Aviators kept, tinted warm so
# Pip stays recognisable under the sun-god treatment.
P_SOLAR = _pal(
    tail=[(196, 122, 28), (224, 158, 44), (250, 196, 70), (255, 224, 120)],
    tail_line=(150, 86, 22),
    body_shadow=(214, 142, 36),
    body_main=_GOLD,
    body_chest=_SUN_WHITE,
    body_belly=(255, 226, 130),
    sheen=(255, 255, 255, 130),
    wing_main=(238, 176, 50),
    wing_dark=(176, 104, 26),
    wing_tip=_EMERALD,                  # emerald quetzal accent on the wingtip
    wing_secondary=(120, 210, 168),
    wing_highlight=_SUN_WHITE,
    head_shadow=(214, 142, 36),
    head_main=_GOLD,
    head_cheek=(255, 232, 150),
    head_crown=(255, 226, 120),
    # Gold-luminous aviators — Pip's signature stays, tinted to the sun-god.
    lens_frame=_SUN_WHITE,
    lens_body=(60, 36, 12),
    lens_tint=(255, 196, 90, 130),
    lens_glint=(255, 255, 255),
    beak_main=(60, 40, 18),
    beak_dark=(34, 22, 10),
    beak_gloss=(150, 110, 60),
    foot=(150, 96, 34),
)


def _sun_disc(surf):
    # The legendary tell: a blazing sun-disc halo behind the head, painted FIRST
    # under the body so the head sits ON the disc like a sun-god. Built as
    # additive glow layers (hottest at the core) plus short radiating rays, so it
    # reads as a hot sun, not a flat ring — brighter/harder than Aurora's soft
    # halo. Held to a warm gold so it never competes with the body's value.
    cx, cy = HX - 2, HY - 3
    # Outer soft corona → inner hot core, stacked for depth.
    blit_glow(surf, cx, cy, 26, (255, 150, 40), alpha=120)
    blit_glow(surf, cx, cy, 19, (255, 200, 80), alpha=140)
    blit_glow(surf, cx, cy, 12, (255, 244, 180), alpha=150)

    # Short radiating rays: a ring of tapered gold spokes reaching just past the
    # head so the disc clearly breaks the silhouette as a sun, each tipped white.
    n = 12
    for i in range(n):
        a = (i / n) * math.tau + 0.13
        ca, sa = math.cos(a), math.sin(a)
        r0, r1 = 16, 25
        x0, y0 = cx + ca * r0, cy + sa * r0
        x1, y1 = cx + ca * r1, cy + sa * r1
        # Alternate long/short rays so the corona reads as sun-spikes, not a gear.
        if i % 2:
            x1, y1 = cx + ca * (r1 - 4), cy + sa * (r1 - 4)
        pygame.draw.line(surf, _AMBER, (x0, y0), (x1, y1), 3)
        pygame.draw.line(surf, _GOLD, (x0, y0), (x1, y1), 1)
        pygame.draw.circle(surf, _SUN_WHITE, (int(x1), int(y1)), 1)


def _streamer(surf, root, pts, *, core_first):
    # A single quetzal tail-streamer: a flowing gold-cored band edged emerald.
    # Drawn in two passes around the body — the EMERALD edge + deep keyline go
    # BEHIND the body (core_first=False) so the streamer roots tuck under the
    # tail, and the bright GOLD core goes on TOP afterwards (core_first=True) so
    # the luminous centre always reads. A continuous deep-emerald keyline keeps
    # the streamer crisp where it crosses pale day sky.
    path = [root] + pts
    if not core_first:
        pygame.draw.lines(surf, _EMER_DEEP, False, path, 6)
        pygame.draw.lines(surf, _EMERALD, False, path, 4)
    else:
        pygame.draw.lines(surf, _AMBER, False, path, 3)
        pygame.draw.lines(surf, _GOLD, False, path, 2)
        pygame.draw.lines(surf, _SUN_WHITE, False, path[:2], 1)
        tip = path[-1]
        # A small emerald spade-tip — the resplendent-quetzal tell at the end.
        pygame.draw.circle(surf, _EMER_DEEP, tip, 3)
        pygame.draw.circle(surf, _EMERALD, tip, 2)
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

    # White-gold core-glow rim tracing the back/underside that faces open sky, so
    # the radiant mass keeps a crisp glowing edge on night sky.
    pygame.draw.lines(surf, _SUN_WHITE, False,
                      [(15, 40), (22, 44), (30, 47), (40, 46), (47, 41)], 1)

    # Feathered gold crown-crest fanning UP past CROWN_Y — three plumes leaning
    # outward, the centre tallest so the crest clearly breaks the crown. Each
    # plume: an amber keyline root, gold body, emerald-flecked tip and a white
    # spark, so it reads as a sun-god's feathered crown at 40px, not a single
    # blob. Mirrors the cockatoo-crest idiom but richer for the legendary tier.
    base_y = CROWN_Y + 4
    for dx, h, lean in ((-5, 16, -5), (-1, 23, 1), (4, 18, 7)):
        x = HX + dx
        root = (x, base_y + 2)
        mid = (x + lean // 2, base_y - h // 2)
        tip = (x + lean, base_y - h)
        pygame.draw.line(surf, _AMBER_DK, root, mid, 5)
        pygame.draw.line(surf, _AMBER, root, mid, 4)
        pygame.draw.line(surf, _GOLD, mid, tip, 3)
        pygame.draw.circle(surf, _EMERALD, tip, 2)        # emerald quetzal fleck
        pygame.draw.circle(surf, _CORE, (tip[0], tip[1] - 1), 1)

    # A few emerald quetzal accent-flecks on the chest + a sun-spark off the
    # back, the small jewels that say "resplendent" up close without muddying
    # the 40px read.
    for fx, fy in ((30, 50), (36, 54), (26, 46)):
        pygame.draw.circle(surf, _EMERALD, (fx, fy), 2)
        pygame.draw.circle(surf, (120, 210, 168), (fx, fy - 1), 1)
    pygame.draw.circle(surf, _SUN_WHITE, (HX + 13, HY + 6), 2)
    pygame.draw.circle(surf, _CORE, (HX + 13, HY + 5), 1)


def _solar_getter():
    # The sun-disc/rays and the emerald streamer edges must sit BEHIND the body,
    # so the body-first order in _make_skin can't be used: halo+rays + streamer
    # edges -> radiant body -> front crest + gold streamer cores + rim -> outline.
    # The outline uses a warm amber keyline (not the house near-black) so the
    # bright-gold silhouette holds on pale day sky like the astronaut's white.
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        comp = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _sun_disc(comp)
        _streamers_back(comp)
        comp.blit(_build_parrot_with_palette(wing_angle, P_SOLAR), (0, PARROT_DY))
        _paint_front(comp, wing_angle)
        return _add_outline(comp, outline_color=(80, 44, 12, 235))

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
