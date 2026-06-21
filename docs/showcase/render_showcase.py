"""Render the Skybit Store visual showcase under docs/showcase/.

Emits, headless:
  * 15 store-menu page screenshots  (img/store_<group>_p<N>.png)
  * 140 gameplay screenshots        (img/play_<id>_{full,zoom}.png) — the parrot
                                     wearing every one of the 70 looks, in a
                                     single staged daytime scene so only the
                                     cosmetic changes frame to frame
  * 7 markdown pages                (README.md + one per category)

The gameplay scene mirrors tools/biome_snapshots.py: a real World() is stepped
so a pillar sits on the right, then the bird is snapped to a fixed flattering
pose. The background + world entities are rendered ONCE; each look just swaps
bird.equipped_skin and redraws the bird on a copy, so the staging is identical
across all 70 figures.

Run:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python docs/showcase/render_showcase.py
"""
import os, sys, pathlib, math, random, tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))   # needed for fonts / image.save

from game.config import W, H, GROUND_Y, BIRD_X
from game.world import World
from game.entities import Coin
from game import biome as _biome
from game import store_catalog, store_data
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)

HERE = pathlib.Path(__file__).parent
IMG = HERE / "img"
IMG.mkdir(parents=True, exist_ok=True)

# Tabs in store order; (group key, display label).
GROUPS = [
    ("costume", "COSTUMES"), ("parrot", "PARROTS"), ("animal", "ANIMALS"),
    ("shoes", "SHOES"), ("hats", "HATS"), ("shades", "SHADES"),
    ("parcels", "PARCELS"),
]

CYCLE = _biome.CYCLE_SECONDS
SCENE_SEED = 7        # one pillar lands at x≈300 (right side) — bird stays clear
SCENE_TICKS = 162
SCENE_PHASE = 0.0     # bright daytime so every cosmetic shows its true colours


def _phase_to_time(phase: float) -> float:
    # phase_for_time adds a 0.04 morning offset; invert it (as biome_snapshots).
    return ((phase - 0.04) % 1.0) * CYCLE


def _tab_order(group: str) -> list[str]:
    """The exact card order the live store shows for a tab: cheapest-first,
    with the free DEFAULT card fronting PARROTS and SHADES. Secret items are
    omitted from this gameplay-gallery order so the committed docs don't spoil
    them — the store-page render still shows them, masked as ???, since it draws
    a real StoreScene whose throwaway wallet owns nothing."""
    ids = sorted(store_catalog.ids_of_group(group), key=store_catalog.cost)
    ids = [i for i in ids if not store_catalog.is_secret(i)]
    if group in ("parrot", "shades"):
        ids = [store_catalog.BASE_SKIN] + ids
    elif group == "parcels":
        ids = [store_catalog.PARCEL_BASE] + ids
    return ids


# ── gameplay scene ───────────────────────────────────────────────────────────

def build_scene():
    """Step a real world into a clean daytime frame, stage the bird pose, and
    pre-render the background + entities (everything EXCEPT the bird) once.
    Returns (world, base_surface); world.bird is reused to draw each look."""
    random.seed(SCENE_SEED)
    world = World()
    world.ready_t = 0.0
    dt = 1 / 60
    for tick in range(SCENE_TICKS):
        if tick % 22 == 0:
            world.bird.flap()
        world.update(dt)

    # Restore biome time so the palette is the daytime keyframe.
    world.biome_time = _phase_to_time(SCENE_PHASE)

    # A short coin arc between the bird and the pillar — gameplay flavour that
    # never overlaps the bird body (so the cosmetic is always unobstructed).
    world.coins = []
    world.powerups.clear()
    for i, dx in enumerate((78, 120, 162)):
        world.coins.append(Coin(BIRD_X + dx, H * 0.42 - 26 + math.sin(i * 0.9) * 18))

    # Fixed flattering pose: open sky, slight upward "just-flapped" tilt.
    bird = world.bird
    bird.alive = True
    bird.x = BIRD_X
    bird.y = H * 0.42
    bird.vy = -120
    bird.frame_t = 1.0      # a mid-flap wing frame, same for every look

    palette = world.biome_palette
    surf = pygame.Surface((W, H))

    # Sky with bucket interpolation (matches scenes._draw_background).
    buckets = _biome.PHASE_BUCKETS
    bf = (world.biome_phase % 1.0) * buckets
    a = int(bf) % buckets
    b = (a + 1) % buckets
    t = bf - int(bf)
    pal_a = _biome.palette_for_phase(a / buckets)
    pal_b = _biome.palette_for_phase(b / buckets)
    sky_a = get_sky_surface_biome(W, H, GROUND_Y, pal_a, a)
    sky_a.set_alpha(None)
    surf.blit(sky_a, (0, 0))
    if t > 0:
        sky_b = get_sky_surface_biome(W, H, GROUND_Y, pal_b, b)
        sky_b.set_alpha(int(t * 255))
        surf.blit(sky_b, (0, 0))
        sky_b.set_alpha(None)

    scroll = world.bg_scroll
    cloud_phase = 1.5
    for i, (bx, by, sc, variant) in enumerate((
            (20, 90, 0.9, 0), (180, 140, 1.1, 2),
            (60, 220, 0.8, 3), (230, 60, 0.7, 1),
            (320, 180, 0.9, 4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(cloud_phase * 0.3 + i) * 3,
                   sc, variant=variant)
    draw_mountains(surf, scroll, GROUND_Y, W, palette['mtn_far'], palette['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))

    for p in world.pipes:
        p.draw(surf, palette)
    for c in world.coins:
        c.draw(surf)

    return world, surf


_ZOOM_BOX = 150
_ZOOM_SCALE = 2.5


def render_look(world, base, skin_id):
    """Return (full_surface, zoom_surface) of the bird wearing skin_id."""
    world.bird.equipped_skin = skin_id
    full = base.copy()
    world.bird.draw(full, 0, 0)

    cx, cy = BIRD_X, int(H * 0.42)
    half = _ZOOM_BOX // 2
    x0 = max(0, min(W - _ZOOM_BOX, cx - half))
    y0 = max(0, min(H - _ZOOM_BOX, cy - half))
    crop = full.subsurface(pygame.Rect(x0, y0, _ZOOM_BOX, _ZOOM_BOX)).copy()
    zoom = pygame.transform.smoothscale(
        crop, (int(_ZOOM_BOX * _ZOOM_SCALE), int(_ZOOM_BOX * _ZOOM_SCALE)))
    return full, zoom


# ── store pages ──────────────────────────────────────────────────────────────

def render_store_pages():
    """Return {group: n_pages}, saving img/store_<group>_p<N>.png for every page
    of every tab. Uses a throwaway wallet so the player's real save is untouched."""
    store_data.STORE_FILE = tempfile.mktemp(suffix="_showcase.json")
    store_data._reset_for_test()
    store_data.add_coins(999999)   # clean active BUY chips with prices

    from game.store import StoreScene, _TABS

    store = StoreScene()
    pages = {}
    for tab_i, (label, g) in enumerate(_TABS):
        store.tab = tab_i
        store.page = 0
        store.t = 0.0
        warm = pygame.Surface((W, H))
        store.render(warm)                 # populates tab-strip widths
        store._scroll_tab_into_view(tab_i)  # bring this tab's pill into view
        n = store.n_pages
        pages[g] = n
        for p in range(n):
            store.page = p
            surf = pygame.Surface((W, H))
            store.render(surf)
            pygame.image.save(surf, IMG / f"store_{g}_p{p + 1}.png")
    return pages


# ── markdown ─────────────────────────────────────────────────────────────────

def _disp(skin_id):
    if skin_id == store_catalog.BASE_SKIN:
        return "DEFAULT", "FREE"
    return store_catalog.name(skin_id), str(store_catalog.cost(skin_id))


def write_category_md(group, label, store_n_pages, cols=4):
    ids = _tab_order(group)
    lines = [f"# {label} — {len(ids)} looks", ""]
    lines.append("[← back to the showcase index](README.md)")
    lines.append("")
    lines.append("## In the store")
    lines.append("")
    lines.append(f"How the **{label}** tab looks in the shop"
                 + (f" ({store_n_pages} pages)" if store_n_pages > 1 else "") + ":")
    lines.append("")
    for p in range(store_n_pages):
        lines.append(f'<img src="img/store_{group}_p{p + 1}.png" width="280">')
    lines.append("")
    lines.append("## In gameplay")
    lines.append("")
    lines.append("Pip wearing every item, mid-flight in the same daytime scene "
                 "(only the cosmetic changes). Click any frame for the full screen.")
    lines.append("")
    lines.append("<table>")
    for i, sid in enumerate(ids):
        if i % cols == 0:
            lines.append("  <tr>")
        name, cost = _disp(sid)
        cell = (f'    <td align="center" valign="top">'
                f'<a href="img/play_{sid}_full.png">'
                f'<img src="img/play_{sid}_zoom.png" width="180"></a><br>'
                f'<b>{name}</b><br>{cost}</td>')
        lines.append(cell)
        if i % cols == cols - 1 or i == len(ids) - 1:
            lines.append("  </tr>")
    lines.append("</table>")
    lines.append("")
    (HERE / f"{group}.md").write_text("\n".join(lines), encoding="utf-8")


def write_index():
    total = len(store_catalog.skin_ids())
    lines = [
        "# Skybit Store — visual showcase", "",
        f"Every cosmetic in the coin Store, **category by category**: how each tab "
        f"looks in the shop, and the parrot **Pip wearing every one of the "
        f"{total} looks** (+ the free DEFAULT) in real gameplay. All art is "
        f"procedural (drawn from code).", "",
        "Each gameplay frame is staged in the same daytime scene so the looks "
        "compare cleanly; click any thumbnail for the full 360×640 screen.", "",
        "## Categories", "",
    ]
    for group, label in GROUPS:
        n = len(_tab_order(group))
        lines.append(f"- [**{label}** — {n} looks]({group}.md)")
    lines += [
        "", "---", "",
        "See also the single-figure contact sheet of every item: "
        "[`docs/store/all_items.png`](../store/all_items.png).", "",
        "Regenerate this whole showcase:", "", "```sh",
        "SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \\",
        "  python docs/showcase/render_showcase.py", "```", "",
    ]
    (HERE / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    # Wipe any stale figures so removed items don't linger.
    for old in IMG.glob("*.png"):
        old.unlink()

    print("Rendering store pages…")
    store_pages = render_store_pages()
    n_store = sum(store_pages.values())
    print(f"  {n_store} store page PNGs across {len(store_pages)} tabs")

    print("Staging gameplay scene…")
    world, base = build_scene()

    # Every unique look across all tabs (skin_base shared by parrot+shades).
    all_ids = []
    for group, _ in GROUPS:
        for sid in _tab_order(group):
            if sid not in all_ids:
                all_ids.append(sid)
    print(f"Rendering {len(all_ids)} looks × (full+zoom)…")
    for sid in all_ids:
        full, zoom = render_look(world, base, sid)
        pygame.image.save(full, IMG / f"play_{sid}_full.png")
        pygame.image.save(zoom, IMG / f"play_{sid}_zoom.png")

    print("Writing markdown…")
    for group, label in GROUPS:
        write_category_md(group, label, store_pages[group])
    write_index()

    n_play = len(all_ids) * 2
    print(f"Done: {n_store} store + {n_play} gameplay = {n_store + n_play} PNGs, "
          f"{len(GROUPS) + 1} markdown files.")


if __name__ == "__main__":
    main()
