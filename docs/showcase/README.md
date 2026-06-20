# Skybit Store — visual showcase

Every cosmetic in the coin Store, **category by category**: how each tab looks in the shop, and the parrot **Pip wearing every one of the 69 looks** (+ the free DEFAULT) in real gameplay. All art is procedural (drawn from code).

Each gameplay frame is staged in the same daytime scene so the looks compare cleanly; click any thumbnail for the full 360×640 screen.

## Categories

- [**COSTUMES** — 15 looks](costume.md)
- [**PARROTS** — 7 looks](parrot.md)
- [**ANIMALS** — 9 looks](animal.md)
- [**SHOES** — 10 looks](shoes.md)
- [**HATS** — 17 looks](hats.md)
- [**SHADES** — 13 looks](shades.md)

---

See also the single-figure contact sheet of every item: [`docs/store/all_items.png`](../store/all_items.png).

Regenerate this whole showcase:

```sh
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  python docs/showcase/render_showcase.py
```
