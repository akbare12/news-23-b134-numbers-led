#!/usr/bin/env python3
"""news-23 b134 numbers-led: draw THE WORLD TODAY front page, 23 Nov 2026.

Layout: masthead + kicker + BIG number grid first (10 numbers) + region bar
+ 3 hero scenes + 10 cards + world map + ALSO list + DATE CHECK + footer.
1024x1024, PIL only. Run: python3 draw.py  ->  entry.png (same dir).
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (247, 243, 232)
INK = (20, 20, 20)
GRAY = (110, 108, 100)
RED = (165, 18, 30)
DARKRED = (140, 12, 24)
NAVY = (16, 32, 86)
GOLD = (176, 138, 30)
GREEN = (46, 125, 50)
TEAL = (0, 121, 107)
PURPLE = (106, 27, 154)
MAPGREEN = (178, 205, 158)
MAPEDGE = (140, 175, 120)

FD = "/usr/share/fonts/truetype/dejavu"


def f(path, size):
    return ImageFont.truetype(path, size)


SERIF = f(f"{FD}/DejaVuSerif-Bold.ttf", 52)
BOLD = lambda s: f(f"{FD}/DejaVuSans-Bold.ttf", s)  # noqa: E731
REG = lambda s: f(f"{FD}/DejaVuSans.ttf", s)  # noqa: E731


def wrap(d, text, font, max_w):
    """Wrap text into lines fitting max_w pixels."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def chip(d, x_right, y, label, fill):
    """Right-aligned chip; returns left edge."""
    font = BOLD(10)
    tw = d.textlength(label, font=font)
    w = int(tw) + 12
    h = 15
    d.rounded_rectangle([x_right - w, y, x_right, y + h], radius=3, fill=fill)
    d.text((x_right - w + 6, y + 2), label, font=font, fill=(255, 255, 255))
    return x_right - w


def pin(d, x, y, n):
    r = 9
    d.ellipse([x - r, y - r, x + r, y + r], fill=RED, outline=(255, 255, 255), width=1)
    font = BOLD(10)
    t = str(n)
    tw = d.textlength(t, font=font)
    d.text((x - tw / 2, y - 7), t, font=font, fill=(255, 255, 255))


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # ---------- masthead ----------
    d.text((24, 6), "THE WORLD TODAY", font=SERIF, fill=INK)
    date_font = BOLD(20)
    dt = "MONDAY 23 NOVEMBER 2026"
    d.text((W - 24 - d.textlength(dt, font=date_font), 22), dt, font=date_font, fill=GOLD)

    # ---------- kicker ----------
    d.rectangle([0, 64, W, 86], fill=RED)
    d.text((24, 69), "AI rout hits Asia  ·  UN chief urges AI rules  ·  US lead over China at record low  ·  Anthropic IPO $107.3B",
           font=BOLD(15), fill=(255, 255, 255))

    # ---------- BIG number grid (2 rows x 5 cols) ----------
    numbers = [
        ("-3.3%", "KOSPI"),
        ("5.3", "US-CHINA POWER GAP"),
        ("11,762", "EBOLA CASES, DRC"),
        ("10T won", "SEOUL STABILISATION FUND"),
        ("2%", "BILLIONAIRE TAX IN PARIS"),
        ("$450M", "SKUBAL DEAL"),
        ("165", "RUSSIAN MISSILES/WEEK"),
        ("12,000", "CLEARED IN MANCHESTER"),
        ("264 kg", "EXPLOSIVES SEIZED"),
        ("$107.3B", "ANTHROPIC IPO"),
    ]
    gx, gy = 8, 90
    cw, rh = 203, 50
    for i, (val, lab) in enumerate(numbers):
        col, row = i % 5, i // 5
        x = gx + col * cw
        y = gy + row * rh
        d.text((x + 8, y + 2), val, font=BOLD(26), fill=INK)
        d.text((x + 8, y + 31), lab, font=BOLD(10), fill=GRAY)
        if col < 4:
            d.line([(x + cw - 2, y + 6), (x + cw - 2, y + rh - 8)], fill=(210, 205, 190), width=1)
    d.line([(8, gy + rh), (W - 8, gy + rh)], fill=(210, 205, 190), width=1)

    # ---------- region bar ----------
    regions = [
        ("ASIA-PACIFIC 7", NAVY, 230),
        ("AMERICAS 8", RED, 262),
        ("MIDDLE EAST 6", PURPLE, 196),
        ("EUROPE 5", TEAL, 164),
        ("AFRICA 3", GREEN, 98),
        ("WORLD 2", GOLD, 74),
    ]
    rx, ry, rh2 = 0, 192, 19
    for name, color, wseg in regions:
        d.rectangle([rx, ry, rx + wseg, ry + rh2], fill=color)
        font = BOLD(11)
        tw = d.textlength(name, font=font)
        d.text((rx + (wseg - tw) / 2, ry + 4), name, font=font, fill=(255, 255, 255))
        rx += wseg

    # ---------- UTC strip ----------
    d.text((24, 215), "THE DAY IN UTC   ~00:00 Kospi dives   ~05:30 Guterres opens   ~09:00 Power Index   ~12:00 Paris 2% tax   ~15:00 Kyiv missiles",
           font=REG(11), fill=GRAY)
    d.text((W - 24 - d.textlength("~ APPROX", font=REG(11)), 215), "~ APPROX", font=REG(11), fill=GRAY)

    # ---------- heroes ----------
    hx = [8, 346, 684]
    hw = 330
    sy, sh = 230, 108  # scene top/height
    heroes = [
        ("AI ROUT HITS ASIA",
         "Kospi closes -3.3% to 4,708.54, sheds 161 pts; intraday -5.8%. Samsung -3.1%, SK Hynix -2.5%.",
         "KOREA EXCHANGE"),
        ("GUTERRES: REGULATE AI BEFORE IT'S TOO LATE",
         "UN chief urges global AI safety rules at the Bridgetown summit; 150 back a risk framework.",
         "UNITED NATIONS"),
        ("US LEAD OVER CHINA AT RECORD LOW",
         "Asia Power Index 2026: US 78.9, China 73.6 — gap 5.3, narrowest since 2018. India third at 40.5.",
         "LOWY INSTITUTE"),
    ]
    for i, (head, body, src) in enumerate(heroes):
        x = hx[i]
        if i == 0:
            # Kospi scene: navy sky, lit skyline, falling orange chart
            d.rectangle([x, sy, x + hw, sy + sh], fill=NAVY)
            for bx, bw, bh in [(10, 34, 62), (50, 26, 78), (82, 40, 55), (128, 30, 84),
                               (164, 36, 66), (206, 28, 80), (240, 34, 58), (280, 30, 72)]:
                d.rectangle([x + bx, sy + sh - bh - 16, x + bx + bw, sy + sh - 16], fill=(8, 18, 55))
                for wy in range(sy + sh - bh - 12, sy + sh - 20, 9):
                    for wx in range(x + bx + 5, x + bx + bw - 4, 9):
                        d.rectangle([wx, wy, wx + 3, wy + 3], fill=(255, 214, 90))
            d.text((x + 10, sy + 6), "-3.3%", font=BOLD(30), fill=(255, 255, 255))
            pts = [(x + 130, sy + 52), (x + 165, sy + 58), (x + 200, sy + 55),
                   (x + 235, sy + 66), (x + 270, sy + 62), (x + 305, sy + 78)]
            d.line(pts, fill=(255, 140, 0), width=3)
            for px, py in pts:
                d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 255, 255))
            d.rectangle([x, sy + sh - 16, x + hw, sy + sh], fill=(0, 0, 0))
            d.text((x + 8, sy + sh - 14), "KOSPI 4,708.54  ·  -161 PTS", font=BOLD(10), fill=(255, 214, 90))
        elif i == 1:
            # Guterres scene: green, gold text + globe
            d.rectangle([x, sy, x + hw, sy + sh], fill=(27, 94, 32))
            d.text((x + 12, sy + 8), "150", font=BOLD(40), fill=(255, 214, 90))
            for j, ln in enumerate(["DELEGATES", "BACK A RISK", "FRAMEWORK"]):
                d.text((x + 12, sy + 52 + j * 17), ln, font=BOLD(16), fill=(255, 214, 90))
            cx, cy, cr = x + 262, sy + 52, 44
            d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(200, 230, 190),
                      outline=(255, 255, 255), width=2)
            d.ellipse([cx - 20, cy - cr, cx + 20, cy + cr], outline=(120, 160, 110), width=1)
            d.line([(cx - cr, cy - 18), (cx + cr, cy - 18)], fill=(120, 160, 110), width=1)
            d.line([(cx - cr, cy + 18), (cx + cr, cy + 18)], fill=(120, 160, 110), width=1)
            d.rectangle([x, sy + sh - 16, x + hw, sy + sh], fill=(0, 0, 0))
            d.text((x + 8, sy + sh - 14), "BRIDGETOWN SUMMIT, BARBADOS", font=BOLD(10), fill=(255, 214, 90))
        else:
            # Power Index scene: bars
            d.rectangle([x, sy, x + hw, sy + sh], fill=(238, 232, 214))
            d.text((x + 10, sy + 6), "NARROWEST SINCE 2018", font=BOLD(13), fill=INK)
            d.text((x + hw - 10 - d.textlength("GAP 5.3", font=BOLD(13)), sy + 6), "GAP 5.3",
                   font=BOLD(13), fill=RED)
            bars = [("78.9", "US", NAVY, 0.789), ("73.6", "CHINA", RED, 0.736), ("40.5", "INDIA", GOLD, 0.405)]
            for j, (val, lab, col, frac) in enumerate(bars):
                by = sy + 32 + j * 24
                d.text((x + 10, by), val, font=BOLD(13), fill=INK)
                bx0 = x + 62
                bw = int(240 * frac)
                d.rectangle([bx0, by + 1, bx0 + bw, by + 15], fill=col)
                d.text((bx0 + bw + 6, by + 1), lab, font=BOLD(12), fill=INK)
        # headline / body / source+chip (below scene, clear of the black strip above)
        hy = sy + sh + 6
        hl = wrap(d, head, BOLD(17), hw)
        for j, ln in enumerate(hl[:2]):
            d.text((x, hy + j * 20), ln, font=BOLD(17), fill=INK)
        by = hy + len(hl[:2]) * 20 + 2
        bl = wrap(d, body, REG(12), hw)
        for j, ln in enumerate(bl[:2]):
            d.text((x, by + j * 15), ln, font=REG(12), fill=(60, 58, 52))
        cy = by + len(bl[:2]) * 15 + 4
        d.text((x, cy + 1), src, font=REG(10), fill=GRAY)
        chip(d, x + hw, cy, "REPORTED", NAVY)

    # ---------- cards bar ----------
    d.rectangle([0, 434, W, 454], fill=INK)
    d.text((24, 439), "MORE OF THE DAY  —  10 STORIES", font=BOLD(14), fill=(255, 255, 255))

    cards = [
        ("1", "AMERICAS", "BESSENT: NVIDIA ANSWERS", "Treasury wants answers.", "WSJ", "REPORTED"),
        ("2", "AMERICAS", "FBI PROBES NCIC HACK", "NCIC database hacked.", "AP", "REPORTED"),
        ("3", "WHITE HOUSE", "IRAN STRIKES MAY RESUME", "May resume in New Year.", "Reuters", "REPORTED"),
        ("4", "MARKETS", "US FUTURES JUMP 3%", "Holiday rally lifts 3%.", "Bloomberg", "REPORTED"),
        ("5", "SPORT", "SKUBAL'S $450M METS DEAL", "Nine-year, largest ever.", "AP", "REPORTED"),
        ("6", "SPORT", "TOM JACKSON DIES AT 75", "Broncos LB, ESPN voice.", "ESPN", "REPORTED"),
        ("7", "LEGAL", "STATES SUE SPACEX", "Ten states sue over AI.", "AP", "REPORTED"),
        ("8", "TECH", "ANTHROPIC IPO: $107.3B", "Raised $83; closes $97.17.", "WSJ", "REPORTED"),
        ("9", "EUROPE", "3 MISSILES CROSSED AIRSPACE", "Kyiv: 3 Kh-101s crossed.", "AP", "CLAIM"),
        ("10", "SPACE", "RUSSIAN NUCLEAR SATELLITE", "May carry a nuke.", "Reuters", "CLAIM"),
    ]
    cx0, cy0 = 8, 458
    cw2, ch2 = 203, 63
    for i, (num, cat, head, body, src, tag) in enumerate(cards):
        col, row = i % 5, i // 5
        x = cx0 + col * cw2
        y = cy0 + row * ch2
        nfont = BOLD(13)
        d.text((x + 4, y), num, font=nfont, fill=RED)
        nw = d.textlength(num, font=nfont)
        d.text((x + 4 + nw + 6, y + 2), cat, font=BOLD(10), fill=RED)
        hl = wrap(d, head, BOLD(11), cw2 - 8)
        for j, ln in enumerate(hl[:2]):
            d.text((x + 4, y + 14 + j * 12), ln, font=BOLD(11), fill=INK)
        d.text((x + 4, y + 39), body, font=REG(10), fill=(60, 58, 52))
        # source + chip share the bottom row (y+49..y+63), clear of the body line
        d.text((x + 4, y + 50), src, font=REG(9), fill=GRAY)
        chip(d, x + cw2 - 6, y + 48, tag, NAVY if tag == "REPORTED" else RED)
        if col < 4:
            d.line([(x + cw2 - 2, y + 4), (x + cw2 - 2, y + ch2 - 6)], fill=(210, 205, 190), width=1)

    # ---------- map bar ----------
    d.rectangle([0, 586, W, 606], fill=INK)
    d.text((24, 591), "WHERE IT HAPPENED", font=BOLD(14), fill=(255, 255, 255))

    # map blobs (absolute coordinates)
    mx, my = 8, 612
    d.polygon([(18, 632), (98, 616), (158, 626), (148, 702), (98, 762), (48, 742), (14, 692)],
              fill=MAPGREEN, outline=MAPEDGE)
    d.polygon([(178, 622), (258, 614), (308, 642), (288, 722), (228, 752), (183, 702)],
              fill=MAPGREEN, outline=MAPEDGE)
    d.polygon([(318, 632), (388, 620), (423, 662), (398, 732), (338, 742), (313, 682)],
              fill=MAPGREEN, outline=MAPEDGE)
    pins = [(360, 650, 1), (95, 745, 2), (395, 655, 3), (75, 690, 4), (110, 660, 5),
            (250, 650, 6), (215, 665, 7), (200, 640, 8), (260, 675, 9), (225, 630, 10),
            (280, 695, 11), (270, 720, 12), (245, 735, 13)]
    for px, py, n in pins:
        pin(d, px, py, n)
    # legend under map (short lines, kept inside the 422px map width)
    ly = my + 168
    d.text((mx, ly), "Pins 1–13: 1 Seoul · 2 Bridgetown · 3 Beijing · 4 Washington",
           font=REG(10), fill=INK)
    d.text((mx, ly + 14), "5 New York · 6 Kyiv · 7 Paris · 8 London · 9 Warsaw · 10 Manchester",
           font=REG(10), fill=INK)
    d.text((mx, ly + 28), "11 Beirut · 12 Gaza · 13 Khartoum", font=REG(10), fill=INK)

    # ALSO list (right of map)
    ax = 448
    d.text((ax, 610), "ALSO ON MONDAY", font=BOLD(13), fill=INK)
    also = [
        "14. Paris: 100+ back 2% billionaire tax",
        "15. Manchester: 12,000 cleared",
        "16. Zelenskyy: 165 missiles in a week",
        "17. COP31: Antalya pact rejected",
        "18. Israel unity talks resume",
        "19. Gaza: two killed in Israeli strike",
        "20. West Bank settler attacks",
        "21. Iran war: no deal in sight",
        "22. Lebanon seizes 264 kg explosives",
        "23. Bahrain: strike hits plant, 2 hurt",
        "24. Benghazi: UN demands probe [CLAIM]",
        "25. Sudan: defences down drones [CLAIM]",
        "26. DRC: fighting traps Ebola teams",
        "27. Bangladesh: Hasina jailed if she returns",
        "28. Seoul minister quits over AI exam row",
        "29. SK Telecom -7.3% as hype cools",
        "30. China eases margin rules",
        "31. Seoul readies 10T-won fund",
    ]
    for i, item in enumerate(also):
        col = i // 9
        row = i % 9
        x = ax + col * 288
        y = 632 + row * 20
        if "[CLAIM]" in item:
            base, _ = item.split(" [CLAIM]")
            d.text((x, y), base, font=REG(11), fill=INK)
            cw_ = d.textlength(base, font=REG(11))
            d.text((x + cw_ + 4, y), "[CLAIM]", font=BOLD(11), fill=RED)
        else:
            d.text((x, y), item, font=REG(11), fill=INK)

    # ---------- DATE CHECK ----------
    dx, dy, dw, dh = 8, 824, W - 16, 76
    d.rectangle([dx, dy, dx + dw, dy + dh], outline=RED, width=2)
    d.text((dx + 10, dy + 6), "DATE CHECK  —  READ 23 NOV 2026, 23:59 UTC  ·  STORIES DATED 23 NOV ONLY",
           font=BOLD(13), fill=RED)
    d.text((dx + 10, dy + 26), "LEFT OUT — NOT 23 NOV:  Dems reach 258 (22 Nov)  ·  Sparta II fire (22 Nov)  ·  El Chapo Isidro captured (22 Nov)",
           font=REG(11), fill=INK)
    d.text((dx + 10, dy + 42), "EU–Indonesia pact (21 Nov)  ·  Nigeria boat (21 Nov)  ·  ICJ Myanmar ruling (19 Nov)",
           font=REG(11), fill=INK)
    d.text((dx + 10, dy + 58), "NOT YET — Dymer search continues (14 missing)  ·  4 House races uncalled  ·  COP32 venue not set  ·  WHO evacuating trapped Ebola staff",
           font=REG(11), fill=INK)

    # ---------- footer ----------
    fy = 908
    d.text((24, fy), "Sources: Reuters · AP · Bloomberg · AFP · Yonhap · BBC · WSJ · ESPN · Lowy Institute (Asia Power Index 2026).",
           font=REG(10), fill=GRAY)
    d.text((24, fy + 15), "CHIPS: REPORTED = confirmed by wires · CLAIM = one side's claim, independently unconfirmed · ONGOING = still developing.",
           font=REG(10), fill=GRAY)
    d.text((24, fy + 30), "All times UTC. Figures as reported 23 Nov 2026. Scenes are drawn illustrations, not photographs.",
           font=REG(10), fill=GRAY)
    d.line([(24, 1000), (W - 24, 1000)], fill=GOLD, width=2)
    foot = "THE WORLD TODAY  ·  Monday 23 November 2026  ·  31 stories  ·  6 regions"
    d.text(((W - d.textlength(foot, font=BOLD(12))) / 2, 1006), foot, font=BOLD(12), fill=GOLD)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
