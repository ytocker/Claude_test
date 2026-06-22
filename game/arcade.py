"""Arcade-corner content + logic: the Crystal Ball, the Vending Machine, and
Master Beakon (the elder-macaw sage).

Pure data + selection functions. Each picker takes an injected ``rng``
(random.Random) so outcomes are testable and reproducible; the Profile scene
owns the coin debits (store_data.try_spend) and persistence. Nothing here draws
or touches pygame. Tone: roast the play, never the player; the curios are a
coin-sink for flavor, never pay-to-win.
"""
from __future__ import annotations

VENDING_COST = 5
BEAKON_COST = 20
CRYSTAL_COST = 0   # the crystal ball is free; it only costs you your dignity


# ── Crystal Ball ──────────────────────────────────────────────────────────────
# Three flavors: it knows you (meta), profound nonsense, and ~1-in-5 a real tip
# disguised as prophecy. predicted_pillar (when set) lets the next run grade the
# prophecy and feed the running accuracy gloat.

_CRYSTAL_META = [
    "An early, confident death awaits. Around pillar {p}. The usual.",
    "A power-up will appear. You will panic and waste it.",
    "You will tap too much. You always tap too much.",
    "I see a wall. I see you. I see the wall again.",
]
_CRYSTAL_NONSENSE = [
    "The pillar you fear is the pillar you meet.",
    "To fly is merely to fall, slowly, with confidence.",
    "A coin saved is a coin you will ignore mid-air anyway.",
    "Gerald sends his regards.",
]
_CRYSTAL_REAL = [
    "The Ghost passes through stone. So should your worry.",
    "When time runs thick, the patient bird taps but once.",
    "Every fifteenth wall, the sky rains gold. Be ready to be greedy.",
]


def _typical_pillar(stats: dict, rng) -> int:
    """A plausible 'you'll die around here' pillar from the player's history —
    their median-ish death pillar, nudged so the prophecy feels specific."""
    hist = stats.get("death_pillar_histogram") or []
    total = sum(int(x) for x in hist)
    if total <= 0:
        return rng.randint(3, 9)
    half, run = total / 2.0, 0
    for i, n in enumerate(hist):
        run += int(n)
        if run >= half:
            return max(1, i + rng.randint(-1, 1))
    return rng.randint(3, 9)


def crystal_prediction(stats: dict, rng) -> dict:
    """Pick a prophecy for the next run. Returns ``{text, kind, predicted_pillar}``;
    predicted_pillar is None for non-numeric lines (only the meta pillar line and
    a fraction of others commit to a number the next run can grade)."""
    roll = rng.random()
    if roll < 0.20:
        return {"text": rng.choice(_CRYSTAL_REAL), "kind": "real",
                "predicted_pillar": None}
    if roll < 0.60:
        p = _typical_pillar(stats, rng)
        # Only the numeric "death around pillar {p}" line commits a number the
        # next run can grade; the other meta jabs stay unfalsifiable.
        if rng.random() < 0.5:
            return {"text": _CRYSTAL_META[0].format(p=p), "kind": "meta",
                    "predicted_pillar": p}
        return {"text": rng.choice(_CRYSTAL_META[1:]), "kind": "meta",
                "predicted_pillar": None}
    return {"text": rng.choice(_CRYSTAL_NONSENSE), "kind": "nonsense",
            "predicted_pillar": None}


def grade_prophecy(predicted_pillar: "int | None", actual_pillar: int) -> "bool | None":
    """Did the last numeric prophecy come true? Within ±1 pillar counts as a
    hit. None when the prophecy committed to no number (ungradable)."""
    if predicted_pillar is None:
        return None
    return abs(int(predicted_pillar) - int(actual_pillar)) <= 1


# ── Vending Machine ───────────────────────────────────────────────────────────
# 5 coins → a capsule of charming junk for the Junk Drawer, plus rare jackpots
# and joke outcomes. Outcome kinds: trinket / charm / jackpot / joke. A joke can
# return coins ("change"), keep them ("out_of_order"), or hand over a one-off
# collectible (the ultra-rare Gerald figurine).

_TRINKETS = [
    ("duck", "Rubber Duck", "It has seen things."),
    ("fry", "A Single Sad Fry", "Cold. Alone. Iconic."),
    ("eye", "Googly Eye", "It is looking at you. Only you."),
    ("clip", "Bent Paperclip", "Technically still a paperclip."),
    ("ribbon", "Participation Ribbon", "For showing up. Barely."),
]
_CHARMS = [
    ("acorn", "Tiny Acorn Charm", "Pin it to your parcel. Nature's keychain."),
    ("bell", "Tin Bell Charm", "Jingles with quiet disappointment."),
    ("star", "Foil Star Charm", "You tried. Here is a star."),
]

# (kind, weight) — weights are relative, normalized in vend().
_VEND_TABLE = [
    ("trinket", 52),
    ("charm", 22),
    ("jackpot", 8),
    ("change", 9),
    ("out_of_order", 7),
    ("moth", 1.5),
    ("gerald", 0.5),
]

JACKPOT_COINS = 25


def vend(rng) -> dict:
    """Roll one capsule. Returns a dict describing the prize:
    ``{kind, id, name, flavor, coins_back}``. coins_back is the gross coins the
    machine returns (jackpot / change); the caller has already paid VENDING_COST.
    """
    total = sum(w for _k, w in _VEND_TABLE)
    r = rng.random() * total
    kind = _VEND_TABLE[-1][0]
    for k, w in _VEND_TABLE:
        if r < w:
            kind = k
            break
        r -= w

    if kind == "trinket":
        tid, name, flavor = rng.choice(_TRINKETS)
        return {"kind": "trinket", "id": tid, "name": name, "flavor": flavor,
                "coins_back": 0}
    if kind == "charm":
        cid, name, flavor = rng.choice(_CHARMS)
        return {"kind": "charm", "id": cid, "name": name, "flavor": flavor,
                "coins_back": 0}
    if kind == "jackpot":
        return {"kind": "jackpot", "id": "jackpot", "name": "JACKPOT",
                "flavor": "The machine respects you. Briefly.",
                "coins_back": JACKPOT_COINS}
    if kind == "change":
        return {"kind": "change", "id": "change", "name": "Your Change",
                "flavor": "Here's your change.", "coins_back": 1}
    if kind == "out_of_order":
        return {"kind": "out_of_order", "id": "receipt", "name": "OUT OF ORDER",
                "flavor": "Prints a receipt that says only: thank you.",
                "coins_back": 0}
    if kind == "moth":
        return {"kind": "moth", "id": "moth", "name": "Moth (escaped)",
                "flavor": "A moth flies out. That was the prize.",
                "coins_back": 0}
    return {"kind": "gerald", "id": "gerald_figurine", "name": "Gerald Figurine",
            "flavor": "Now you can lose to him at home, too.", "coins_back": 0}


# ── Master Beakon ─────────────────────────────────────────────────────────────
# 20 coins → one Tip for Life, saved to the Scroll of Wisdom. Three flavors
# (meta roast / profound nonsense / ~1-in-5 a real tip), with escalating sass as
# the player keeps paying; a true addict eventually gets a refund.

_BEAKON_META = [
    "Do not pay for things you do not understand.",
    "A fool and his coins enjoy a brief friendship.",
    "The wise bird hoards its coins. You are here.",
    "This tip cost twenty coins. Let that be the lesson.",
]
_BEAKON_NONSENSE = [
    "The pillar you fear is the pillar you meet.",
    "To fly is merely to fall, slowly, with confidence.",
    "Gerald is not your enemy. Gravity is.",
    "A coin saved is a coin you will ignore mid-air anyway.",
]
_BEAKON_REAL = [
    "The Ghost passes through stone. So should your worry.",
    "When time runs thick, the patient bird taps but once.",
    "Every fifteenth wall, the sky rains gold. Be ready.",
]

# Visit-count thresholds at which Beakon's framing curdles.
_SASS_REGULAR = 8
_SASS_ADDICT = 20


def beakon_tip(rng, visit_count: int) -> dict:
    """Pick a Tip for Life. Returns ``{text, kind, refund}``. At very high visit
    counts Beakon gives up and refunds the 20 coins (refund=True), because there
    is nothing left to teach you."""
    if visit_count >= _SASS_ADDICT and rng.random() < 0.5:
        return {"text": "Keep your coins. This one is free. You clearly need it "
                        "more than I.", "kind": "refund", "refund": True}
    roll = rng.random()
    if roll < 0.20:
        text, kind = rng.choice(_BEAKON_REAL), "real"
    elif roll < 0.60:
        text, kind = rng.choice(_BEAKON_META), "meta"
    else:
        text, kind = rng.choice(_BEAKON_NONSENSE), "nonsense"
    if visit_count >= _SASS_REGULAR and rng.random() < 0.4:
        text = "You again. " + text
    return {"text": text, "kind": kind, "refund": False}
