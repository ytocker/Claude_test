"""Render docs/pillar_redesign/terracotta_buddha_reference_moodboard.png.

Single reference card sheet for the 10 canonical Terracotta Warrior +
Buddha statue subjects the design loop is targeting. Each card =
canonical name + period / origin + 5 iconographic markers + Wikipedia
URL. The bar the procedural designs must meet."""

from __future__ import annotations

import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = pathlib.Path(__file__).parent
_REPO = _HERE.parent.parent
sys.path.insert(0, str(_REPO))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

OUT = _REPO / "docs" / "pillar_redesign"
OUT.mkdir(parents=True, exist_ok=True)


# (name_en, name_zh, period_loc, family, [5 iconographic markers], wiki_url)
REFERENCES = [
    (
        "High Officer (General)",
        "高级军吏俑",
        "Qin dynasty, c. 246–210 BCE — Pit 1, Xi'an",
        "Terracotta",
        [
            "Double fish-tail rank crown (guan)",
            "Wide overlapping shoulder pauldrons",
            "Vermilion silk ribbon-knot on the chest",
            "Dense vertical-row leather scale armour",
            "Ceremonial polearm + twin battle pennants",
        ],
        "en.wikipedia.org/wiki/Terracotta_Army",
    ),
    (
        "Standing Light-Infantry Archer",
        "立射俑",
        "Qin dynasty, c. 246–210 BCE — Pit 2, Xi'an",
        "Terracotta",
        [
            "Side-bun hairstyle (right-of-centre)",
            "Vertical wooden bow stave + bowstring",
            "Calf-binding leggings with diagonal wraps",
            "Light unarmoured chest panel (front fighter)",
            "丁-stance: left foot angled forward",
        ],
        "en.wikipedia.org/wiki/Terracotta_Army",
    ),
    (
        "Kneeling Crossbowman",
        "跪射俑",
        "Qin dynasty, c. 246–210 BCE — Pit 2, Xi'an",
        "Terracotta",
        [
            "Left knee down + right foot under bent knee",
            "Dense 7×4 leather scale armour panel",
            "Rear-bun hairstyle pinned with chin strap",
            "Horizontal crossbow stock at right hip",
            "Hands clasped over chest holding the bow",
        ],
        "en.wikipedia.org/wiki/Terracotta_Army",
    ),
    (
        "Cavalryman + Saddled Horse",
        "骑兵俑 + 鞍马",
        "Qin dynasty, c. 246–210 BCE — Pit 2, Xi'an",
        "Terracotta",
        [
            "Rounded leather cavalry cap + chin strap",
            "Short tunic + light vest (no pauldrons)",
            "Northwestern horse: cropped mane, large nostril",
            "Vermilion saddle cloth + raised pommel/cantle",
            "Braided plait tail + twin belly bands (no stirrups)",
        ],
        "en.wikipedia.org/wiki/Terracotta_Army",
    ),
    (
        "Charioteer",
        "御手俑",
        "Qin dynasty, c. 246–210 BCE — Pit 1, Xi'an",
        "Terracotta",
        [
            "Tall trapezoidal cap with ochre+vermilion rank bands",
            "Both arms extended forward gripping reins",
            "Ceremonial sword on left hip, bronze pommel",
            "Forward-projecting chariot pole + bronze ferrule",
            "Pleated lower robe + wide waist sash",
        ],
        "en.wikipedia.org/wiki/Terracotta_Army",
    ),
    (
        "Leshan Giant Buddha",
        "乐山大佛 (Maitreya)",
        "Tang dynasty, 713–803 CE — Sichuan cliff face",
        "Buddha — Sandstone",
        [
            "Cliff niche carved into sedimentary strata",
            "Oversized head (1:6 head-to-body ratio)",
            "Snail-shell hair curls + ushnisha + wisdom flame",
            "Long pendulous ears + urna (forehead jewel)",
            "Dhyana mudra: both hands palm-up on the knees",
        ],
        "en.wikipedia.org/wiki/Leshan_Giant_Buddha",
    ),
    (
        "Tian Tan Big Buddha",
        "天坛大佛 (Sakyamuni)",
        "1993 CE — Lantau Island, Hong Kong",
        "Buddha — Patinated bronze",
        [
            "Three-tier circular Temple-of-Heaven altar base",
            "Lotus throne with 8 visible petals",
            "Right hand: abhaya mudra (palm forward, fingers UP)",
            "Left hand: varada mudra (palm-up on the knee)",
            "Halo with 12 radial petal-rays + central flame",
        ],
        "en.wikipedia.org/wiki/Tian_Tan_Buddha",
    ),
    (
        "Standing Maitreya / Budai",
        "彌勒 / 布袋和尚",
        "Traditional iconography, gilt-bronze treatments",
        "Buddha — Gilt-bronze",
        [
            "Round exposed belly + visible belly-button",
            "Smiling crescent eyes (laughing curve)",
            "Saffron diagonal sash + wide waist sash",
            "Symmetric arms-up welcome with raised fingers",
            "Bald + ushnisha + visible gilt-wear cracks",
        ],
        "en.wikipedia.org/wiki/Budai",
    ),
    (
        "Cliff-Niche Reclining Buddha",
        "涅槃像 / 龕窟",
        "Yungang Caves archetype — Northern Wei, 460–525 CE",
        "Buddha — Gold-leaf on sandstone niche",
        [
            "Full-height sandstone strata cliff column",
            "Horizontal arched niche carved into lower half",
            "Head RIGHT on pillow + bare-feet soles LEFT",
            "Diagonal saffron sash with gilt borders",
            "Halo glow behind head + wear cracks on gilt",
        ],
        "en.wikipedia.org/wiki/Yungang_Grottoes",
    ),
    (
        "Guanyin / Avalokiteśvara",
        "觀音 (Dehua porcelain)",
        "Ming-Qing Dehua kilns — Fujian, China",
        "Buddha — Blanc-de-chine porcelain",
        [
            "Flame-spire diadem with tiny Amitabha effigy",
            "Slender hourglass body with cool-white glaze",
            "Water-vase in LEFT hand at hip (water trickle)",
            "Willow branch in RIGHT hand raised overhead",
            "Flame-tipped aureole (12 tongues) + cobalt-fired eyes",
        ],
        "en.wikipedia.org/wiki/Dehua_porcelain",
    ),
]

# Sheet layout — 2 columns × 5 rows for readable card density
COLS = 2
ROWS = 5
CARD_W = 940
CARD_H = 460
GAP = 24
PAD = 28
TITLE_H = 80

SHEET_W = PAD * 2 + COLS * CARD_W + (COLS - 1) * GAP
SHEET_H = TITLE_H + PAD * 2 + ROWS * CARD_H + (ROWS - 1) * GAP

# Palette — neutral parchment + dark ink, evokes museum catalogue
BG = (28, 28, 34)
CARD_BG = (242, 236, 224)
CARD_BORDER_TERRACOTTA = (168, 96, 60)
CARD_BORDER_BUDDHA = (130, 96, 168)
HEADER_BG_TERRACOTTA = (228, 196, 168)
HEADER_BG_BUDDHA = (212, 198, 232)
NAME_INK = (40, 28, 24)
ZH_INK = (96, 40, 28)
META_INK = (96, 80, 64)
FAMILY_TAG_INK = (255, 248, 232)
BULLET_INK = (52, 36, 28)
BULLET_DOT = (148, 108, 76)
URL_INK = (76, 116, 156)
TITLE_INK = (245, 240, 228)

font_title = pygame.font.SysFont("Liberation Serif,Times New Roman,serif", 38, bold=True)
font_subtitle = pygame.font.SysFont("Liberation Serif,Times New Roman,serif", 18, italic=True)
font_name = pygame.font.SysFont("Liberation Serif,Times New Roman,serif", 28, bold=True)
font_zh = pygame.font.SysFont(
    "Noto Sans CJK SC,Noto Sans CJK,WenQuanYi Zen Hei,SimSun,sans-serif",
    24, bold=True,
)
font_meta = pygame.font.SysFont("Liberation Sans,Arial,sans-serif", 16, italic=True)
font_family_tag = pygame.font.SysFont("Liberation Sans,Arial,sans-serif", 14, bold=True)
font_bullet = pygame.font.SysFont("Liberation Sans,Arial,sans-serif", 18)
font_url = pygame.font.SysFont("DejaVu Sans Mono,Liberation Mono,Consolas,monospace", 14)


def render_text(text: str, font: pygame.font.Font, color, max_width=None) -> pygame.Surface:
    if max_width is None:
        return font.render(text, True, color)
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        if font.size(test)[0] > max_width and line:
            lines.append(line)
            line = w
        else:
            line = test
    if line:
        lines.append(line)
    line_h = font.get_linesize()
    surf = pygame.Surface((max_width, line_h * len(lines)), pygame.SRCALPHA)
    for i, ln in enumerate(lines):
        surf.blit(font.render(ln, True, color), (0, i * line_h))
    return surf


def draw_card(sheet, x, y, ref):
    name_en, name_zh, period, family, markers, url = ref
    is_terracotta = family.startswith("Terracotta")
    border = CARD_BORDER_TERRACOTTA if is_terracotta else CARD_BORDER_BUDDHA
    header_bg = HEADER_BG_TERRACOTTA if is_terracotta else HEADER_BG_BUDDHA

    pygame.draw.rect(sheet, CARD_BG, (x, y, CARD_W, CARD_H), border_radius=12)
    pygame.draw.rect(sheet, border, (x, y, CARD_W, CARD_H), width=3, border_radius=12)

    header_h = 100
    header_rect = pygame.Rect(x + 3, y + 3, CARD_W - 6, header_h)
    pygame.draw.rect(sheet, header_bg, header_rect,
                     border_top_left_radius=10, border_top_right_radius=10)

    pad = 24
    sheet.blit(font_name.render(name_en, True, NAME_INK), (x + pad, y + 14))
    sheet.blit(font_zh.render(name_zh, True, ZH_INK), (x + pad, y + 48))
    sheet.blit(font_meta.render(period, True, META_INK), (x + pad, y + 78))

    tag_text = family.upper()
    tag_surf = font_family_tag.render(tag_text, True, FAMILY_TAG_INK)
    tag_pad_x, tag_pad_y = 12, 6
    tag_w = tag_surf.get_width() + tag_pad_x * 2
    tag_h = tag_surf.get_height() + tag_pad_y * 2
    tag_x = x + CARD_W - tag_w - pad
    tag_y = y + 14
    pygame.draw.rect(sheet, border, (tag_x, tag_y, tag_w, tag_h), border_radius=4)
    sheet.blit(tag_surf, (tag_x + tag_pad_x, tag_y + tag_pad_y))

    markers_y = y + header_h + 20
    markers_label = font_meta.render("Five iconographic markers:", True, META_INK)
    sheet.blit(markers_label, (x + pad, markers_y))
    markers_y += markers_label.get_height() + 8

    bullet_x = x + pad
    text_x = x + pad + 24
    text_max_w = CARD_W - pad * 2 - 24
    for marker in markers:
        pygame.draw.circle(sheet, BULLET_DOT, (bullet_x + 8, markers_y + 11), 4)
        marker_surf = render_text(marker, font_bullet, BULLET_INK, max_width=text_max_w)
        sheet.blit(marker_surf, (text_x, markers_y))
        markers_y += marker_surf.get_height() + 8

    url_y = y + CARD_H - 36
    pygame.draw.line(sheet, border, (x + pad, url_y - 8),
                     (x + CARD_W - pad, url_y - 8), 1)
    sheet.blit(font_url.render(url, True, URL_INK), (x + pad, url_y))


def main():
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill(BG)

    title = font_title.render(
        "TERRACOTTA WARRIORS + BUDDHA STATUES — REFERENCE MOODBOARD",
        True, TITLE_INK,
    )
    subtitle = font_subtitle.render(
        "The canonical references the procedural pillar designs are targeting. "
        "Each card lists the five iconographic markers a culturally-informed viewer "
        "should recognise at thumbnail.",
        True, (200, 196, 188),
    )
    sheet.blit(title, ((SHEET_W - title.get_width()) // 2, 20))
    sheet.blit(subtitle, ((SHEET_W - subtitle.get_width()) // 2, 62))

    for idx, ref in enumerate(REFERENCES):
        col = idx % COLS
        row = idx // COLS
        x = PAD + col * (CARD_W + GAP)
        y = TITLE_H + PAD + row * (CARD_H + GAP)
        draw_card(sheet, x, y, ref)

    out = OUT / "terracotta_buddha_reference_moodboard.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
