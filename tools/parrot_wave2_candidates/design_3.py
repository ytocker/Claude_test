"""design_3 · CONSTELLATION MACAW — LEGENDARY wave-2 parrot exploration.

A celestial-globe Pip: a deep lapis-midnight body engraved with a GOLD
star-chart — hard metallic star-LINES joining hand-placed star-NODES across
back/wing/chest, ringed by a thin GOLD ORBITAL HALO behind the head (the
legendary tell), crowned by a hard GILDED CRESCENT-MOON crest rising past the
crown, and trailing a COMET TRAIL of gold star-nodes (big→small) where the
feather fan used to be. Every accent value is hard metallic gold — the
deliberate split from AURORA, whose cosmic read is soft teal/green RIBBONS.

Draw order matters: the orbital halo and the comet-node trail must paint BEHIND
the outlined body, so this can't use store_skins._make_skin's body-first
_compose. Mirroring AURORA's getter, this is a custom back-aura pass — an
ADDITIVE bloom buffer that twinkles the gold NODES on dark night skies, plus an
OPAQUE bright-detail buffer (halo band, comet nodes, node cores as solid gold
over a thin ink backing) so the chart ALSO survives a bright day sky where the
additive bloom washes out — then the lapis body, then the front overlay
(crescent crest, join-the-dots line-chart, wing rim, aviators), then the house
outline, then the per-(frame, 3°-bucket) rotation cache.

The two-pass trick mirrors AURORA exactly: gold NODES get an additive bloom so
the chart twinkles on night sky; the gold LINES stay OPAQUE so they survive day
sky. The whole chart is BAKED into each of the 4 wing frames (no runtime
particle hook): the halo glints and comet tail drift a touch with the wing beat
so the engraving still reads alive across the filmstrip. Exploration only —
NEVER registered in store_skins.BUILDERS.
"""
import math

import pygame

from game.parrot import _WING_ANGLES, _add_outline
from game.draw import blit_glow, lerp_color
from game.store_skins import (
    COMPOSITE_W, COMPOSITE_H, PARROT_DY, HX, HY, CROWN_Y,
)
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── palette (brief) ───────────────────────────────────────────────────────────
_LAPIS   = (21, 34, 74)           # #15224A lapis midnight body
_INDIGO  = (12, 20, 48)           # #0C1430 indigo shadow
_GOLD    = (232, 194, 90)         # #E8C25A star gold (the chart line/node value)
_GLINT   = (255, 243, 200)        # #FFF3C8 gold glint / white star
_SAPPH   = (58, 90, 168)          # #3A5AA8 sapphire mid
_INK     = (10, 16, 38)           # thin dark backing so gold survives bright sky

# Lapis re-plumage: a deep midnight-blue body kept dark enough that the gold
# engraving is the ONLY bright value, but lifted off pure black (sapphire mid in
# the chest/crown) so the body never reads as a flat void on a dark night sky.
# Lenses keep Pip's aviators but tint DEEP SAPPHIRE so the face stays in-key; the
# beak is cooled to a pale sapphire-grey so the macaw wedge still reads.
_CONSTELLATION_PAL = _pal(
    tail=[(12, 20, 46), (15, 25, 56), (20, 33, 72), (28, 44, 92)],
    tail_line=(9, 15, 36),
    body_shadow=(11, 18, 44),
    body_main=_LAPIS,
    body_chest=(34, 54, 110),
    body_belly=(17, 28, 64),
    sheen=(120, 150, 230, 70),
    wing_main=(19, 31, 70),
    wing_dark=(10, 17, 42),
    wing_tip=(46, 72, 138),
    wing_secondary=None,
    wing_highlight=(96, 128, 206),
    head_shadow=(11, 18, 44),
    head_main=(20, 33, 74),
    head_cheek=(40, 60, 116),
    head_crown=(34, 54, 108),
    lens_frame=(78, 104, 168),
    lens_body=(9, 14, 34),
    lens_tint=(46, 74, 150, 150),
    lens_glint=(220, 232, 255),
    beak_main=(150, 166, 206),
    beak_dark=(40, 56, 98),
    beak_gloss=(228, 238, 255),
    foot=(70, 92, 150),
)


def _constellation_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _CONSTELLATION_PAL)


# ── shared helpers ────────────────────────────────────────────────────────────

def _flap_phase(angle_deg):
    """0 on the down-stroke (wing 50°) → 1 on the up-stroke (-40°). The halo
    glints and the comet tail drift a touch on the up-beat so the baked
    engraving still reads alive across the 4 frames."""
    return 1.0 - (angle_deg + 40) / 90.0


def _arc(cx, cy, r, a0, a1, steps=18):
    """Point list along a circular arc (radians a0→a1) — the spine of the gold
    orbital halo, sampled fine enough to draw as a thick smooth band that
    survives the 40px downscale."""
    return [(cx + math.cos(a0 + (a1 - a0) * i / steps) * r,
             cy + math.sin(a0 + (a1 - a0) * i / steps) * r)
            for i in range(steps + 1)]


# Orbital halo geometry: a WIDE arc wrapping the head from the left flank, over
# the top-rear, down the right flank, sized larger than the skull (r=20) so the
# clean gold band clears OUTSIDE the silhouette on the sides — the part that
# reads as a halo separating bird from sky. The crescent crest sits up off the
# top, so the halo leans to wrap the rear/flanks rather than the very top.
_HALO_CX, _HALO_CY, _HALO_R = HX - 2, HY - 1, 20


def _halo_spine():
    return _arc(_HALO_CX, _HALO_CY, _HALO_R, math.radians(190), math.radians(350))


# Halo star-glints pinned ON the ring (fixed positions, stable across frames) —
# a few bright nodes that read as stars caught on the orbit.
def _halo_glints():
    spine = _halo_spine()
    return [spine[1], spine[6], spine[12], spine[len(spine) - 2]]


def _comet_nodes(phase):
    """Comet trail replacing the feather fan: a tapering line of gold star-nodes
    (big→small) streaming DOWN-BACK into open sky past the body's back edge
    (body back ≈ x13), brightest node at the ROOT. A fixed hand-placed line (NOT
    random) so the 4 frames stay stable; the tail end drifts 1px with the flap so
    the comet feels like it's streaming. Each entry: (x, y, radius)."""
    drift = (phase - 0.5) * 2.0
    # Root sits at the upper tail join; the line sweeps down-and-back so the
    # nodes clearly clear the silhouette into open sky. Big root → small tip.
    return [
        (15,            HY + 6,             3),   # brightest root node
        (11,            HY + 11,            3),
        (7,             HY + 16 + drift,    2),
        (3,             HY + 21 + drift,    2),
        (0,             HY + 26 + drift * 2, 1),  # faint tail tip
    ]


# ── back layer: orbital halo + comet-node trail (two-pass) ────────────────────

def _constellation_back(surf, angle_deg):
    """Every behind-body element lives here, BEHIND the outlined bird, so the
    house outline (grown from the bird's alpha mask) never boxes a gold node into
    a dark-rimmed island. Two passes, both un-outlined, the AURORA trick exactly:

      1. an ADDITIVE bloom buffer — soft gold stamps under every halo glint and
         comet node, so the chart TWINKLES on dark night skies where additive
         emission shines.
      2. an OPAQUE bright-detail buffer alpha-blitted ON TOP — the orbital halo
         band (clean 2px gold over a faint ink backing) + the comet-node line as
         solid gold over a thin ink backing, so the halo and comet ALSO survive a
         bright day sky where additive washes to nothing. A legendary reads on
         both skies."""
    phase = _flap_phase(angle_deg)
    halo = _halo_spine()
    glints = _halo_glints()
    nodes = _comet_nodes(phase)

    # ── pass 1: additive bloom (night twinkle) ───────────────────────────────
    glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    # Faint gold wash along the whole orbit so the ring reads as lit on dark sky.
    for i, (gx, gy) in enumerate(halo):
        if i % 3 == 0:
            blit_glow(glow, int(gx), int(gy), 5, _GOLD, alpha=55)
    # Brighter blooms under the pinned halo glints — these are the twinkles.
    for gx, gy in glints:
        blit_glow(glow, int(gx), int(gy), 6, _GLINT, alpha=120)
        blit_glow(glow, int(gx), int(gy), 3, (255, 255, 255), alpha=150)
    # Comet nodes bloom big→small, brightest at the root — the aft light-source.
    for nx, ny, r in nodes:
        blit_glow(glow, int(nx), int(ny), 4 + r, _GOLD, alpha=110)
        blit_glow(glow, int(nx), int(ny), r + 1, _GLINT, alpha=140)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

    # ── pass 2: opaque bright detail (day + night) ───────────────────────────
    det = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)

    # ORBITAL HALO — the legendary tell: a clean 2px gold band over a 4px faint
    # ink backing (so it survives a bright sky), with the pinned star-glints as
    # bright gold/white dots. Thin and precise so it reads as a struck gold ring,
    # not a glow.
    pygame.draw.lines(det, _INK, False, halo, 4)
    pygame.draw.lines(det, _GOLD, False, halo, 2)
    # A hair of brighter gold along the top-rear of the arc for a struck sheen.
    sheen = _arc(_HALO_CX, _HALO_CY, _HALO_R, math.radians(210), math.radians(300))
    pygame.draw.lines(det, _GLINT, False, sheen, 1)
    for gx, gy in glints:
        pygame.draw.circle(det, _INK, (int(gx), int(gy)), 3)
        pygame.draw.circle(det, _GLINT, (int(gx), int(gy)), 2)
        pygame.draw.circle(det, (255, 255, 255), (int(gx), int(gy)), 1)

    # COMET TRAIL — the aft silhouette-breaker. A thin gold line threading the
    # nodes (over an ink backing for day contrast), then each node as a struck
    # gold disc (ink ring → gold → white-hot core) big→small, brightest at the
    # root. The line + tapering nodes read unmistakably as a comet streaming
    # down-back, not a feather fan.
    line = [(x, y) for x, y, _ in nodes]
    pygame.draw.lines(det, _INK, False, line, 3)
    pygame.draw.lines(det, _GOLD, False, line, 1)
    for nx, ny, r in nodes:
        pygame.draw.circle(det, _INK, (int(nx), int(ny)), r + 1)
        pygame.draw.circle(det, _GOLD, (int(nx), int(ny)), r)
        pygame.draw.circle(det, _GLINT, (int(nx), int(ny)), max(1, r - 1))

    surf.blit(det, (0, 0))


# ── front overlay: crescent crest + star-line chart + rim + aviators ──────────

def _constellation_front(surf, angle_deg):
    """Painted OVER the body and INSIDE the masked layer, so only crisp opaque
    gold belongs here (soft bloom lives in _constellation_back to dodge the
    outline). The job: the crescent-moon crest (silhouette-break #1), the
    join-the-dots star-chart over the plumage, the gold wing rim, a re-asserted
    macaw face, and the deep-sapphire aviators with a gold top-rim glint.

    All chart LINES are opaque gold so the engraving survives the 40px day read;
    the NODES get their twinkle from the additive back-pass plus an opaque gold
    core here so they read on both skies."""

    # 1. GILDED CRESCENT-MOON CREST (silhouette-break #1) — a hard gold sliver
    #    rising past CROWN_Y: a fuller outer gold disc with a lapis disc bitten
    #    out of it, leaving a thick crescent. A pale inner rim catches light, and
    #    one white star sits tucked in the crescent's hollow. The crescent tilts
    #    so its horns point up-and-back, clearly a moon over the brow.
    mcx, mcy = HX - 1, CROWN_Y - 7        # moon centre, well past the crown
    mr = 9
    pygame.draw.circle(surf, _INK, (mcx, mcy), mr + 1)        # backing
    pygame.draw.circle(surf, _GOLD, (mcx, mcy), mr)           # full gold disc
    pygame.draw.circle(surf, _GLINT, (mcx, mcy), mr, 1)       # pale struck rim
    # Bite a lapis disc out, offset down-right, to leave a crescent with horns up.
    bcx, bcy = mcx + 4, mcy + 2
    pygame.draw.circle(surf, _INDIGO, (bcx, bcy), mr - 1)
    # Re-strike a thin gold inner edge along the bitten curve so the crescent's
    # inner lip reads as metal, not a hole.
    inner = _arc(bcx, bcy, mr - 1, math.radians(150), math.radians(300), steps=10)
    pygame.draw.lines(surf, _GOLD, False, inner, 1)
    # White star in the crescent hollow.
    sx, sy = bcx - 1, bcy
    pygame.draw.circle(surf, (255, 255, 255), (sx, sy), 1)
    pygame.draw.line(surf, (*_GLINT, 200), (sx - 2, sy), (sx + 2, sy), 1)
    pygame.draw.line(surf, (*_GLINT, 200), (sx, sy - 2), (sx, sy + 2), 1)

    # 2. JOIN-THE-DOTS STAR-CHART over the plumage — a FIXED hand-placed pattern
    #    (NOT random) of gold star-NODES on back/wing/chest connected by thin
    #    gold LINES, so the whole bird reads as an engraved celestial chart. The
    #    nodes are chosen to suggest a wing-spread bird-constellation across the
    #    body. Lines are opaque gold over a faint ink channel so they survive the
    #    40px day read; nodes get a gold disc + white core.
    nodes = (
        (24, 47, 2),   # back-shoulder (brightest, near the chart's "head")
        (30, 44, 2),   # upper back
        (37, 46, 2),   # chest-top, toward the wing
        (44, 49, 2),   # wing leading shoulder
        (33, 53, 1),   # chest centre
        (27, 56, 1),   # lower belly
        (40, 56, 1),   # lower chest, toward tail-side
        (21, 52, 1),   # rear flank, toward the comet root
    )
    # Edge list joining the nodes into one connected constellation figure.
    edges = (
        (0, 1), (1, 2), (2, 3),       # the spread "wing-bar" across the top
        (1, 4), (4, 5),               # spine down into the belly
        (4, 6), (2, 6),               # a triangle toward the tail
        (0, 7), (7, 5),               # rear flank link toward the comet
    )
    for a, b in edges:
        ax, ay, _ = nodes[a]
        bx, by, _ = nodes[b]
        pygame.draw.line(surf, _INK, (ax, ay), (bx, by), 2)
        pygame.draw.line(surf, _GOLD, (ax, ay), (bx, by), 1)
    for nx, ny, r in nodes:
        pygame.draw.circle(surf, _INK, (nx, ny), r + 1)
        pygame.draw.circle(surf, _GOLD, (nx, ny), r)
        pygame.draw.circle(surf, _GLINT, (nx, ny), max(1, r - 1))
    # The two brightest nodes get a twinkle cross so the chart sparkles at 40px.
    for nx, ny, r in (nodes[0], nodes[3]):
        pygame.draw.line(surf, (*_GLINT, 200), (nx - 3, ny), (nx + 3, ny), 1)
        pygame.draw.line(surf, (*_GLINT, 200), (nx, ny - 3), (nx, ny + 3), 1)

    # 3. WING LEADING-EDGE GOLD RIM — one bright gold rim along the wing's top
    #    edge so the wing carves off the dark body as a struck-gold plane and the
    #    flap stays legible. Ink channel under a 2px gold core for the 40px read.
    wing_rim = [(36, 41), (42, 44), (47, 48)]
    pygame.draw.lines(surf, _INK, False, wing_rim, 3)
    pygame.draw.lines(surf, _GOLD, False, wing_rim, 2)

    # 4. BACK/CROWN GOLD RIM — a thin gold edge along the head crown + upper back
    #    so the lapis head reads as a distinct lit dome on top of the body, the
    #    single break that restores the macaw silhouette at 40px.
    crown_rim = [(HX - 12, CROWN_Y + 4), (HX - 5, CROWN_Y), (HX + 4, CROWN_Y + 1),
                 (HX + 11, HY - 4)]
    pygame.draw.lines(surf, _INK, False, crown_rim, 3)
    pygame.draw.lines(surf, _GOLD, False, crown_rim, 2)

    # 5. Re-assert Pip's macaw FACE at 40px — a bright gold glint on the near lens
    #    and a sharpened beak top edge so the identity survives the downscale.
    pygame.draw.circle(surf, _GLINT, (HX + 6, HY - 4), 2)        # near-lens top glint
    pygame.draw.line(surf, _GLINT, (HX + 8, HY + 1), (HX + 13, HY + 4), 2)  # beak top edge


# ── custom compose + getter (halo + comet need a back layer) ──────────────────

def _constellation_getter():
    """back aura (orbital halo + comet-node trail, two-pass) → lapis body → front
    crescent/star-chart/rim/aviators overlay → house outline, then the
    per-(frame, 3°-bucket) rotation cache shared by every store skin.

    The outline is grown from the bird's alpha mask, so the faint additive halo +
    comet bloom must NOT join the masked layer (a dark rim would wrap the glow and
    kill it). So outline the OPAQUE bird (body + front overlay) alone, then lay
    the soft back-aura UNDER it, padded to match the outline's grow so the bird
    stays centred for the rotation maths."""
    state = {"frames": None, "rot": {}}

    def _flat(wing_angle):
        bird = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        bird.blit(_constellation_base(wing_angle), (0, PARROT_DY))
        _constellation_front(bird, wing_angle)
        bird = _add_outline(bird)

        aura = pygame.Surface(bird.get_size(), pygame.SRCALPHA)
        pad = (bird.get_width() - COMPOSITE_W) // 2
        back = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        _constellation_back(back, wing_angle)
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


build = _constellation_getter()
