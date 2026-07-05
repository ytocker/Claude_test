"""Shared PARROT-SKELETON anatomy for the skeleton costume v2 exploration.

The v1 winners (BONEWHITE / DEADMAN'S FLAG) read as a generic skull+ribcage
cluster, not a *parrot*. This module draws the corrected anatomy that every v2
design layers a theme onto, so the parrot read is identical across all five:

  • a big HOOKED BONE BEAK (down-curved upper mandible + scooped lower) — the
    single signature that says "parrot skeleton" at a glance,
  • a cranium with a large eye socket and a short S-curve cervical neck,
  • a ribcage + a vertebral spine that runs the whole body and KEEPS GOING into
  • a long BONY TAIL (pygostyle + splayed tail-feather bones) so the skeleton is
    long like a macaw, not stopped at the torso,
  • a radiating finger-bone wing (flaps with the 4 poses) and clawed leg bones.

Drawn in the 64×60 SPRITE space the prebuilt getters expect (head right at
~(46,17), tail left, beak tip ~x60). A design supplies a ``Pal`` palette plus
optional ``pre``/``post`` hooks (pre = behind the bones: glow aura, cutlass,
mantle; post = on top: bandana, paint, socket-fire, gold). Scratch only — never
registered in ``store_skins.BUILDERS``.
"""
import math
import pygame

from game.parrot import SPRITE_W, SPRITE_H, _aaellipse
from game.store_skins import _poly


class Pal:
    """Palette for one themed skeleton. ``bone`` is the brightest element; the
    body is the near-value floor the bone sits on; ``keyline`` is the dark rim
    that keeps bright bone legible against a bright day sky."""

    def __init__(self, bone, bone_sh, bone_deep, body, body_deep, keyline,
                 socket=(8, 8, 10), glint=(255, 255, 255), rib=None):
        self.bone = bone
        self.bone_sh = bone_sh          # cool under-edge for roundness
        self.bone_deep = bone_deep      # deepest bone shade / socket rim
        self.body = body                # dark "flesh" floor
        self.body_deep = body_deep
        self.keyline = keyline          # day-sky rim just outside the bone
        self.socket = socket            # hollow interior
        self.glint = glint
        self.rib = rib or bone          # rib stroke (themes may darken)


# Canonical clean-white palette; themes override what they need.
WHITE = Pal(
    bone=(255, 255, 255), bone_sh=(228, 231, 238), bone_deep=(120, 124, 134),
    body=(21, 22, 28), body_deep=(12, 13, 18), keyline=(58, 61, 71),
    socket=(8, 8, 11), glint=(255, 255, 255),
)


def _bone_line(surf, P, p0, p1, w=2, cap=True):
    """A keyline-rimmed bone strut: a fatter dark rim under a bright core so the
    bone survives on bright sky (the outline pass only edges the silhouette)."""
    pygame.draw.line(surf, P.keyline, p0, p1, w + 2)
    pygame.draw.line(surf, P.bone, p0, p1, w)
    if cap:
        pygame.draw.circle(surf, P.bone, p1, max(1, w - 1))


def _vertebra(surf, P, pts):
    """Bead column (spine tell) through the given path points."""
    for x, y in pts:
        pygame.draw.circle(surf, P.keyline, (x, y), 2, 1)
        pygame.draw.circle(surf, P.bone, (x, y), 2)
        pygame.draw.circle(surf, P.bone_sh, (x, y), 2, 1)


# ── TAIL — long bony macaw tail (the "skeleton goes all the way back") ────────
def tail(surf, P):
    """The macaw's long tail as ONE bold clean pygostyle bone sweeping back-and-
    down off the hips to a bright terminal — the second parrot tell. A single
    strong line reads at 40px where a splayed fan turns to noise; just two thin
    hint feather-bones near the root suggest the fan without cluttering. Drawn
    before the body so the body overlaps the root and it reads attached."""
    root = (18, 35)
    # Central pygostyle — long, lengthened past the old tip to the sprite edge.
    pyg = [(18, 35), (12, 39), (6, 43), (0, 49)]
    pygame.draw.lines(surf, P.keyline, False, pyg, 4)
    pygame.draw.lines(surf, P.bone, False, pyg, 2)
    pygame.draw.circle(surf, P.keyline, (0, 49), 3, 1)
    pygame.draw.circle(surf, P.bone, (0, 49), 2)        # bright terminal cap
    # Two thin hint feather-bones near the root (kept few + thin = no 40px noise).
    for tx, ty in ((2, 42), (3, 53)):
        pygame.draw.line(surf, P.keyline, root, (tx, ty), 3)
        pygame.draw.line(surf, P.bone, root, (tx, ty), 1)
    pygame.draw.circle(surf, P.bone, root, 2)


# ── BODY — dark flesh floor the bright bone reads on ──────────────────────────
def body(surf, P):
    _aaellipse(surf, P.body_deep, (29, 34), 16, 12)
    _aaellipse(surf, P.body, (28, 33), 15, 11)
    _aaellipse(surf, P.body_deep, (24, 29), 8, 4)        # faint top sheen line


# ── RIBCAGE + spine through the torso ─────────────────────────────────────────
def ribcage(surf, P):
    """A bone sternum with paired rib arcs sweeping off it, sitting on the chest
    forward of the wing so the two never share pixels."""
    pygame.draw.line(surf, P.keyline, (34, 27), (24, 41), 4)     # sternum rim
    pygame.draw.line(surf, P.bone, (34, 28), (24, 40), 2)        # sternum
    for i, ty in enumerate((30, 35, 40)):
        sx = 33 - i * 3
        pygame.draw.arc(surf, P.rib, (sx - 12, ty - 5, 13, 12),
                        math.radians(20), math.radians(150), 2)
        pygame.draw.arc(surf, P.rib, (sx - 1, ty - 5, 13, 12),
                        math.radians(30), math.radians(160), 2)


def spine(surf, P):
    """Cervical S-curve from the skull base, continuing through the torso to the
    tail root — one unbroken vertebral line so the skeleton reads full-length.
    A continuous bone line is laid UNDER the vertebra beads so the eye traces an
    unbroken skull→tail backbone at 40px (beads alone read as scattered dots)."""
    path = [(41, 24), (37, 27), (33, 30), (28, 33), (23, 35), (18, 35)]
    pygame.draw.lines(surf, P.keyline, False, path, 3)
    pygame.draw.lines(surf, P.bone, False, path, 1)
    _vertebra(surf, P, path)


# ── WING — radiating finger-bones (flaps with the pose) ───────────────────────
def finger_wing(angle_deg, P):
    w = pygame.Surface((56, 56), pygame.SRCALPHA)
    wrist = (22, 30)
    tips = [(54, 12), (52, 30), (38, 48)]
    for tip in tips:
        pygame.draw.line(w, P.keyline, wrist, tip, 4)
        pygame.draw.circle(w, P.keyline, tip, 3, 1)
    pygame.draw.circle(w, P.keyline, wrist, 4)
    for i, tip in enumerate(tips):
        col = P.bone if i < 2 else P.bone_sh
        pygame.draw.line(w, col, wrist, tip, 2)
        pygame.draw.circle(w, P.bone, tip, 2)
        mid = ((wrist[0] + tip[0]) // 2, (wrist[1] + tip[1]) // 2)
        pygame.draw.circle(w, P.bone_sh, mid, 1)
    pygame.draw.circle(w, P.bone, wrist, 3)
    pygame.draw.circle(w, P.body_deep, wrist, 1)
    return pygame.transform.rotate(w, angle_deg)


def wing(surf, P, angle_deg, center=(28, 21)):
    img = finger_wing(angle_deg, P)
    surf.blit(img, img.get_rect(center=center).topleft)


# ── LEGS — bone leg-pair with clawed feet ─────────────────────────────────────
def legs(surf, P):
    for hx, fx in ((27, 26), (33, 34)):
        knee = (hx, 45)
        foot = (fx, 49)
        pygame.draw.line(surf, P.keyline, (hx, 40), knee, 4)
        pygame.draw.line(surf, P.keyline, knee, foot, 4)
        pygame.draw.line(surf, P.bone, (hx, 41), knee, 2)
        pygame.draw.circle(surf, P.bone, knee, 2)
        pygame.draw.line(surf, P.bone, knee, foot, 2)
        for dx in (-2, 0, 2):
            pygame.draw.line(surf, P.bone_sh, foot, (foot[0] + dx, foot[1] + 3), 2)


# ── SKULL + the signature HOOKED BONE BEAK ────────────────────────────────────
def skull(surf, P, socket_fill=None, draw_socket=True):
    """Rounded macaw cranium with a large hollow eye socket. ``socket_fill``
    lets a theme put fire/gold in the socket; default is a dark hollow."""
    sf = socket_fill if socket_fill is not None else P.socket
    # Keyline dome first so the bright cranium never touches the sky. Cranium
    # kept a hair smaller (rx 10→9) so the hooked beak wins the head silhouette
    # rather than reading as a big mammal skull with a stub.
    _aaellipse(surf, P.keyline,   (46, 17), 10, 9)
    _aaellipse(surf, P.bone,      (46, 17), 9, 8)         # cranium
    _aaellipse(surf, P.bone_sh,   (46, 21), 8, 5)         # under-edge shade
    _aaellipse(surf, P.bone,      (47, 21), 8, 5)         # cheek / jaw front
    # A 1px dark notch under the beak base so the forward beak bone doesn't weld
    # to the cheek.
    pygame.draw.line(surf, P.body_deep, (50, 18), (51, 21), 1)
    if draw_socket:
        # One big round eye socket set forward near the cere (parrot eye), nudged
        # toward the beak so the head reads parrot, not mammal.
        pygame.draw.circle(surf, P.bone_deep, (46, 17), 4)
        pygame.draw.circle(surf, sf, (46, 17), 3)
        pygame.draw.circle(surf, P.glint, (48, 15), 1)   # life glint


def beak(surf, P):
    """The PARROT tell: a SHORT, DEEP, DOWN-CURVED hooked bone beak — the macaw
    'comma'. The upper mandible is a deep wedge off the skull front that bulges
    only modestly forward (to ~x60) then curls HARD DOWN to a hooked tip that
    hangs BELOW the short scooped lower mandible, pointing back at the throat. A
    dark notch parts the beak base from the cranium so it reads as a separate
    forward bone, and a curved dark gape defines the hook. Keyline-wrapped so it
    survives the 40px read. (v1 cut it long+horizontal and it read as a raptor
    snout — the down-hook is what says 'parrot'.)"""
    # Upper mandible — deep comma: tall base on the skull front, short forward
    # bulge, then a hard down-curl to a tip that drops CLEARLY below the lower
    # jaw (the overhang — not the length — is the parrot tell at 40px).
    upper = [(50, 9), (56, 10), (59, 14), (60, 19), (58, 26),
             (55, 32), (52, 31), (51, 24), (50, 18), (48, 13)]
    _poly(surf, P.keyline, [(x + 1, y) for x, y in upper])        # dark rim
    _poly(surf, P.bone, upper)
    _poly(surf, P.bone_sh, [(58, 26), (55, 32), (53, 28), (56, 22)])  # hook shade
    pygame.draw.line(surf, P.bone_sh, (51, 11), (58, 16), 1)      # ridge highlight
    pygame.draw.circle(surf, P.bone, (53, 31), 1)                 # bright hook nub
    # Cere/nostril hollow at the beak base.
    pygame.draw.circle(surf, P.bone_deep, (52, 13), 1)
    # Dark notch parting the beak base from the cranium (beak reads forward) —
    # a full 1px-wide vertical break so the hook detaches from the cranium mass.
    pygame.draw.line(surf, P.body_deep, (49, 11), (49, 20), 2)
    # Curved dark gape between the mandibles — this shadow IS the hook read;
    # 3px and run the full length so the two mandibles never clot into a ball.
    pygame.draw.lines(surf, P.body_deep, False, [(50, 19), (54, 23), (56, 27)], 3)
    # Lower mandible — a short bone scoop pulled IN so the upper hook overhangs
    # below it (tip y27 sits above the hook tip y32).
    lower = [(50, 20), (55, 23), (54, 27), (51, 26)]
    _poly(surf, P.keyline, [(x, y + 1) for x, y in lower])
    _poly(surf, P.bone, lower)
    _poly(surf, P.bone_sh, [(51, 24), (54, 27), (51, 26)])


# ── full assembly ─────────────────────────────────────────────────────────────
def build_skeleton(wing_angle_deg, P, *, pre=None, post=None,
                   socket_fill=None, draw_socket=True, draw_wing=True):
    """Assemble the parrot skeleton for one wing angle. ``pre(surf, angle, P)``
    draws behind the bones (aura / cutlass / mantle); ``post(surf, angle, P)``
    draws on top (bandana / paint / socket-fire / gold)."""
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    if pre:
        pre(surf, wing_angle_deg, P)
    tail(surf, P)
    body(surf, P)
    ribcage(surf, P)
    spine(surf, P)
    if draw_wing:
        wing(surf, P, wing_angle_deg)
    legs(surf, P)
    skull(surf, P, socket_fill=socket_fill, draw_socket=draw_socket)
    beak(surf, P)
    if post:
        post(surf, wing_angle_deg, P)
    return surf
