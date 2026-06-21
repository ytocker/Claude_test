"""COMET parcel cosmetic (PREMIUM — legendary/secret tier).

A captured shooting star: a hot rounded STAR/ORB core blazing a tapering TAIL of
light — a glowing comma/tadpole streak rather than an object. It is the only
parcel with NO container; it IS the light. At 22px it must read as a bright core
with a comet trail from any angle: the symmetric round core has no "up", and the
tail rotating with the bird's tilt becomes pure MOTION.

Built at 2× (44px) then smoothscaled to 22 so the core stays a tight bright
cluster and the tail keeps its smooth taper at the tiny read. The core is kept
the brightest pixel cluster by drawing soft layered glow halos UNDER it and a
small WHITE-HOT centre dot ON TOP — the halo can bloom but the heart never
washes to mush. NIGHT is the showpiece: warm additive halos bake a real bloom
against the dark sky.

Carry context: the parcel rides centred 12px below Pip, so the whole TOP half of
the sprite buries inside Pip's belly and only the bottom ~40% clears. The core +
tail root are therefore weighted to the BOTTOM of the sprite — the white-hot core
and the brightest tail mass sit in the lowest band where they read as a separate
light BELOW Pip, not a highlight ON him. The night bloom is sized so its halo
bleeds PAST Pip's edge even while the core is partly occluded — that escaping
aura is what announces 'legendary' at a glance. The tail trails up-and-back into
the occluded zone, so it reads as motion streaming off the visible head."""
import math
import pygame

from game.parrot import _aaellipse
from game.draw import lerp_color as _lerp_color

SIZE = 22
SS = 44  # 2× supersample; smoothscaled for a crisp tiny read

# DAY palette — white-gold core, amber body, warm-orange tail fading out.
CORE_HOT = (0xFF, 0xFF, 0xF4)    # white-hot centre dot (brightest cluster)
CORE = (0xFF, 0xF4, 0xD0)        # white-gold core
BODY = (0xFF, 0xC2, 0x4A)        # amber orb body
TAIL_HOT = (0xFF, 0xB0, 0x52)    # tail root, near the core
TAIL = (0xFF, 0x8A, 0x3C)        # tail mid — warm orange
KEYLINE = (0x6E, 0x3A, 0x10)     # faint dark sky-side edge (anti-washout on day)

# NIGHT showpiece — warm additive halos that bloom against the dark sky. Baked
# in every render (mode-agnostic) but only visually "ignites" on a dark bg.
HALO_HOT = (0xFF, 0xD6, 0x6A)    # inner warm-gold bloom
HALO_PLASMA = (0xFF, 0x7A, 0x55)  # plasma falloff at the bloom skirt


def _glow_halo(s, cx, cy, r, inner, outer, peak):
    """Soft additive radial bloom: many thin rings, faint at the rim and denser
    near the core, so the core stays a bright heart with a smooth skirt instead
    of a flat disc. Additive so it reads warm in day and BLOOMS on the night
    sky — the legendary spectacle of this parcel."""
    glow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for i in range(r, 0, -1):
        t = i / r                       # 1 at the rim, 0 at the core
        col = _lerp_color(inner, outer, t)
        a = int(peak * (1.0 - t) ** 2)  # quadratic falloff — soft skirt, hot heart
        pygame.draw.circle(glow, col + (a,), (r, r), i)
    s.blit(glow, (cx - r, cy - r), special_flags=pygame.BLEND_RGBA_ADD)


def _tail(s, tip, root_cx, root_cy, root_hw, length, spread):
    """Tapered gradient comet tail as a stack of shrinking translucent ellipses
    marching from the core toward `tip`. Built as a quad of ellipses rather than
    one polygon so the trail has a SMOOTH gradient (hot near the core, fading to
    transparent) and a soft feathered edge that survives rotation as motion."""
    tx, ty = tip
    steps = 26
    for i in range(steps, -1, -1):
        t = i / steps                       # 0 at core root, 1 at the wispy tip
        # Position marches from the core out to the tip.
        x = root_cx + (tx - root_cx) * t
        y = root_cy + (ty - root_cy) * t
        # Width tapers from the core radius to a point; a slight bulge near the
        # root makes the classic teardrop/comma comet head.
        bulge = 1.0 + 0.25 * math.sin((1.0 - t) * math.pi * 0.5)
        w = max(0.6, root_hw * (1.0 - t) ** 1.15 * bulge)
        # Colour hot at the root, cooling to plasma orange toward the tip.
        col = _lerp_color(TAIL_HOT, TAIL, min(1.0, t * 1.3))
        # Alpha fades to fully transparent at the tip; brightest near the core.
        a = int(210 * (1.0 - t) ** 1.4)
        if a <= 2:
            continue
        ell = pygame.Surface((int(w * 2) + 2, int(w * 2) + 2), pygame.SRCALPHA)
        _aaellipse(ell, col + (a,), (ell.get_width() / 2, ell.get_height() / 2),
                   w, w)
        s.blit(ell, (x - ell.get_width() / 2, y - ell.get_height() / 2))


def _star_core(s, cx, cy, r):
    """Bright rounded star/orb core: amber body orb under a white-gold cap and a
    tiny white-hot heart. A faint dark keyline on the SKY-SIDE (upper) edge keeps
    it from washing out on bright day. Four short specular spikes hint 'star'
    without breaking the round read that survives rotation."""
    # Sky-side keyline crescent — drawn first, slightly up/left, so the core's
    # upper rim has a dark anchor on bright day skies.
    _aaellipse(s, KEYLINE + (200,), (cx, cy - 0.6), r + 1.4, r + 1.4)

    # Amber body orb.
    _aaellipse(s, BODY + (255,), (cx, cy), r, r)
    # White-gold inner core, offset slightly toward the lit lower-left.
    _aaellipse(s, CORE + (255,), (cx - 0.6, cy + 0.6), r * 0.62, r * 0.62)

    # Four short star spikes (additive) — subtle so the silhouette stays round.
    spike = pygame.Surface((SS, SS), pygame.SRCALPHA)
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        ex, ey = cx + math.cos(a) * r * 1.7, cy + math.sin(a) * r * 1.7
        pa = math.radians(ang + 90)
        bw = r * 0.32
        pts = [(cx + math.cos(pa) * bw, cy + math.sin(pa) * bw),
               (ex, ey),
               (cx - math.cos(pa) * bw, cy - math.sin(pa) * bw)]
        pygame.draw.polygon(spike, CORE_HOT + (120,), pts)
    s.blit(spike, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # White-hot heart — the single brightest cluster, drawn last so nothing
    # blooms over it. Kept tight so the core never mushes out.
    _aaellipse(s, CORE_HOT + (255,), (cx - 0.6, cy + 0.6), r * 0.34, r * 0.34)


def build(mode="normal"):  # mode ignored — parcel is mode-agnostic, one surface
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)

    # The parcel rides centred 12px below Pip, whose body radius exceeds that
    # offset — so the sprite centre buries inside his belly and only the LOWEST
    # rows clear him. The core is shoved to the bottom band (≈0.84 down) and
    # grown a touch, so the whole white-hot heart and the tail root sit clearly
    # BELOW his silhouette and read as a separate light, not a highlight on him.
    core_cx = SS * 0.55
    core_cy = SS * 0.84
    core_r = 8.2

    # Tail tip up-and-back, climbing into the zone Pip occludes — the visible
    # head streams a trail UP toward his belly. As the parcel banks with the
    # bird this comma swings to read as MOTION.
    tip = (SS * 0.12, SS * 0.34)

    # ---- NIGHT bloom halos, baked UNDER the core so the comet emits light. Pip
    # eats almost the whole sprite, so the bloom's job is to ESCAPE — three
    # stacked halos, the widest reaching far enough that its skirt spills well
    # past Pip's lower edge as a soft aura, the mid carrying the warm body, the
    # inner keeping the heart bright. Brighter peaks so the escaping glow still
    # reads against both the dark night sky and Pip's red.
    _glow_halo(s, core_cx, core_cy, 21, HALO_HOT, HALO_PLASMA, 104)
    _glow_halo(s, core_cx, core_cy, 33, HALO_PLASMA, HALO_PLASMA, 72)
    _glow_halo(s, core_cx, core_cy, 14, CORE, HALO_HOT, 155)

    # ---- TAIL under the core so the head sits crisply over its own root. A
    # touch more root mass now that the bottom band has room.
    _tail(s, tip, core_cx, core_cy, core_r * 1.05, None, None)

    # ---- STAR/ORB CORE on top — the brightest cluster, the legendary heart.
    _star_core(s, core_cx, core_cy, core_r)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
