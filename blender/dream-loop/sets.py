"""Locations ("places"), each carved from primitives. Characters face −Y, camera sits at −Y."""
import math
import random
from lib import (mat, emissive, sphere, box, cyl, torus, plane, text, empty, sun, area, point,
                 world, key, key_mat_emission)


# ---------------------------------------------------------------- props ---- #
def bench(loc=(0, 0, 0), width=2.6, seat_h=0.34):
    wood = mat("bench_wood", "#a0522d", 0.6)
    iron = mat("bench_iron", "#2d2d2d", 0.4, 0.6)
    b = empty("bench", loc)
    for i in range(3):
        box("slat", (width, 0.11, 0.04), wood, (0, -0.13 + i * 0.13, seat_h), b, bevel=0.01)
    for i in range(2):
        box("back", (width, 0.04, 0.1), wood, (0, 0.24, seat_h + 0.22 + i * 0.16), b, rot=(-8, 0, 0), bevel=0.01)
    for sx in (-1, 1):
        box("leg", (0.06, 0.4, seat_h), iron, (sx * width * 0.44, 0.02, seat_h / 2), b)
        box("legb", (0.05, 0.05, 0.5), iron, (sx * width * 0.44, 0.24, seat_h + 0.22), b)
    return b


def tree(loc, s=1.0):
    t = empty("tree", loc)
    cyl("trunk", 0.14 * s, 2.2 * s, mat("bark", "#6b4423", 0.9), (0, 0, 1.1 * s), t)
    leaf = mat("leaf", "#3f8f3a", 0.8)
    for dx, dy, dz, r in ((0, 0, 2.5, 0.9), (0.6, 0.1, 2.2, 0.65), (-0.6, -0.1, 2.25, 0.7), (0.1, 0.3, 3.0, 0.6)):
        sphere("leaves", r * s, leaf, (dx * s, dy * s, dz * s), t, seg=16)
    return t


def streetlight(loc, on=True):
    s = empty("lamp", loc)
    iron = mat("bench_iron", "#2d2d2d", 0.4, 0.6)
    cyl("pole", 0.05, 3.0, iron, (0, 0, 1.5), s)
    sphere("bulb", 0.16, emissive("lampglow", "#ffd27a", 8 if on else 0.2), (0, 0, 3.05), s)
    if on:
        point((loc[0], loc[1] - 0.2, 2.9), "#ffcf87", 120, 0.3)
    return s


def house(loc, w, h, color, roof="#8e3b2f"):
    hh = empty("house", loc)
    box("walls", (w, 2.0, h), mat("house_" + color, color, 0.85), (0, 0, h / 2), hh)
    r = cyl("roof", w * 0.75, 2.1, mat("roof_" + roof, roof, 0.7), (0, 0, h + w * 0.18), hh,
            rot=(90, 0, 0), seg=3)
    r.scale = (1, 0.5, 1)
    win = emissive("window_warm", "#ffd58a", 2.5)
    for dx in (-w * 0.25, w * 0.25):
        box("win", (w * 0.2, 0.05, h * 0.22), win, (dx, -1.0, h * 0.6), hh)
    box("door", (w * 0.18, 0.05, h * 0.42), mat("door", "#5a3a22"), (0, -1.0, h * 0.21), hh)
    return hh


def laptop(loc, parent=None, screen_color="#2f80ed", rot=(0, 0, 0), name="laptop"):
    lp = empty(name, loc, parent, rot)
    alu = mat("alu", "#b8bec7", 0.3, 0.7)
    box("base", (0.42, 0.3, 0.02), alu, (0, 0, 0.01), lp, bevel=0.005)
    lid = empty("lid", (0, 0.15, 0.02), lp, rot=(-15, 0, 0))
    box("lidshell", (0.42, 0.015, 0.28), alu, (0, 0.008, 0.14), lid, bevel=0.005)
    scr = emissive(name + "_screen", screen_color, 2.5)
    box("screen", (0.38, 0.004, 0.24), scr, (0, -0.002, 0.14), lid)
    return lp, lid, scr


def desk(loc, w=1.6, d=0.75, h=0.74, color="#c8a27a"):
    dk = empty("desk", loc)
    top = mat("desk_" + color, color, 0.5)
    box("top", (w, d, 0.05), top, (0, 0, h), dk, bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl("leg", 0.03, h, mat("desk_leg", "#333333", 0.4, 0.6), (sx * (w / 2 - 0.08), sy * (d / 2 - 0.08), h / 2), dk)
    return dk


def chair(loc, rot_z=0, color="#34495e"):
    ch = empty("chair", loc, rot=(0, 0, rot_z))
    m = mat("chair_" + color, color, 0.6)
    box("seat", (0.5, 0.48, 0.07), m, (0, 0, 0.47), ch, bevel=0.02)
    box("back", (0.5, 0.06, 0.55), m, (0, 0.24, 0.78), ch, bevel=0.02)
    cyl("stem", 0.03, 0.42, mat("desk_leg", "#333333", 0.4, 0.6), (0, 0, 0.22), ch)
    return ch


def monitor(loc, parent=None, name="mon", color="#0f1720", w=0.62, h=0.38):
    m = empty(name, loc, parent)
    box("bezel", (w, 0.03, h), mat("bezel", "#15151a", 0.3), (0, 0, 0.2 + h / 2), m, bevel=0.008)
    scr = emissive(name + "_scr", color, 1.2)
    box("panel", (w - 0.04, 0.004, h - 0.04), scr, (0, -0.017, 0.2 + h / 2), m)
    box("stand", (0.05, 0.05, 0.2), mat("bezel", "#15151a"), (0, 0.03, 0.1), m)
    box("foot", (0.22, 0.16, 0.015), mat("bezel", "#15151a"), (0, 0.03, 0.007), m)
    return m, scr


def code_lines(parent, w, h, y, z0, seed=1, rows=10, colors=("#7ee787", "#79c0ff", "#ff7b72", "#d2a8ff")):
    rnd = random.Random(seed)
    grp = empty("code", (0, y, z0), parent)
    lh = h / rows
    for i in range(rows * 2):
        ln = rnd.uniform(0.2, 0.9) * w
        ind = rnd.choice((0, 0, 1, 2)) * 0.04
        box("ln", (ln, 0.002, lh * 0.35), emissive("code_" + colors[i % len(colors)], colors[i % len(colors)], 4),
            (-w / 2 + ind + ln / 2, 0, h / 2 - i * lh), grp)
    return grp


def bubble(name, loc, anchor, r=0.55, color="#ffffff", parent=None):
    """Thought bubble: big puff + two trailing dots towards anchor."""
    m = mat("bubble_" + color, color, 0.35)
    b = empty(name, loc, parent)
    sphere("puff", r, m, (0, 0, 0), b, scale=(1.25, 0.35, 1.0), seg=24)
    for k, (dx, dz) in enumerate(((0.65, -0.35), (-0.7, -0.25), (0.0, 0.48), (0.6, 0.35), (-0.55, 0.35))):
        sphere("puff", r * 0.5, m, (dx * r, 0.02, dz * r), b, scale=(1, 0.5, 1), seg=16)
    ax, ay, az = anchor
    for i, t in enumerate((0.45, 0.72)):
        p = (ax + (loc[0] - ax) * t - loc[0], 0, az + (loc[2] - az) * t - loc[2])
        sphere("dot", r * (0.16 - i * 0.05), m, p, b, seg=12)
    return b


# ---------------------------------------------------------------- icons ---- #
def icon_controller(parent, s=1.0):
    g = empty("controller", (0, -0.25, 0), parent)
    body = mat("ctrl", "#2c2c34", 0.35)
    box("cbody", (0.5 * s, 0.12 * s, 0.24 * s), body, (0, 0, 0), g, bevel=0.08 * s)
    for sx in (-1, 1):
        sphere("grip", 0.13 * s, body, (sx * 0.2 * s, 0, -0.1 * s), g)
    dp = mat("dpad", "#dddddd")
    box("dpad1", (0.1 * s, 0.03, 0.03 * s), dp, (-0.14 * s, -0.07 * s, 0.02 * s), g)
    box("dpad2", (0.03 * s, 0.03, 0.1 * s), dp, (-0.14 * s, -0.07 * s, 0.02 * s), g)
    for (dx, dz, c) in ((0.13, 0.05, "#e74c3c"), (0.18, 0.0, "#3498db"), (0.13, -0.05, "#2ecc71"), (0.08, 0.0, "#f1c40f")):
        sphere("btn", 0.022 * s, emissive("btn" + c, c, 1.5), (dx * s, -0.07 * s, (dz + 0.02) * s), g)
    return g


def icon_gear(parent, s=1.0, name="gear"):
    g = empty(name, (0, -0.25, 0), parent)
    m = mat("steel", "#9aa4ad", 0.3, 0.9)
    cyl("gbody", 0.22 * s, 0.08 * s, m, (0, 0, 0), g, rot=(90, 0, 0), seg=32)
    for i in range(10):
        a = i * 36
        box("tooth", (0.07 * s, 0.08 * s, 0.07 * s), m,
            (math.cos(math.radians(a)) * 0.25 * s, 0, math.sin(math.radians(a)) * 0.25 * s), g, rot=(0, -a, 0))
    cyl("hole", 0.07 * s, 0.1 * s, mat("hole", "#2c3e50"), (0, 0, 0), g, rot=(90, 0, 0))
    return g


def icon_scales(parent, s=1.0):
    g = empty("scales", (0, -0.25, 0), parent)
    m = mat("gold", "#d4a017", 0.25, 0.9)
    cyl("post", 0.02 * s, 0.45 * s, m, (0, 0, 0), g)
    box("beam", (0.5 * s, 0.025 * s, 0.025 * s), m, (0, 0, 0.2 * s), g)
    for sx in (-1, 1):
        cyl("chain", 0.006, 0.18 * s, m, (sx * 0.24 * s, 0, 0.1 * s), g)
        cyl("pan", 0.1 * s, 0.02 * s, m, (sx * 0.24 * s, 0, 0.0), g, r2=0.07 * s)
    cyl("base", 0.12 * s, 0.03 * s, m, (0, 0, -0.22 * s), g)
    return g


def icon_hacker(parent, s=1.0):
    g = empty("hackicon", (0, -0.22, 0), parent)
    text("code_glyph", "</>", 0.34 * s, emissive("hackgreen", "#39ff14", 6), (0, 0, 0.07 * s), g)
    text("hacker_word", "HACKER", 0.14 * s, emissive("hackgreen", "#39ff14", 6), (0, 0, -0.17 * s), g)
    return g


# ---------------------------------------------------------------- sets ----- #
def set_street(dusk=1.0):
    """Neighbourhood bench at sunset — where the dream started."""
    world("#f2a65a", 0.6)
    sun((72, 0, -35), "#ffb36b", 3.2, angle=8)
    area((0, -5, 4), (55, 0, 0), size=6, color="#ffd9b0", power=500)
    plane("grass", (60, 60), mat("grass", "#5c9e45", 0.9))
    box("path", (60, 1.6, 0.02), mat("path", "#c9b79c", 0.9), (0, -1.6, 0.01))
    plane("sky", (80, 30), emissive("skyglow", "#ffb070", 1.0), (0, 22, 10), rot=(90, 0, 0))
    sphere("sunball", 1.6, emissive("sunball", "#fff1c1", 6), (5, 21, 3.2))
    bench((0, 0, 0))
    tree((3.2, 1.8, 0), 1.1)
    tree((-4.5, 3.5, 0), 0.9)
    streetlight((-2.4, 0.6, 0))
    for x, w, h, c in ((-6, 3, 2.6, "#e8d6b0"), (-2.2, 2.6, 3.0, "#cfe3e8"), (1.6, 3.2, 2.4, "#f0c9b4"), (5.6, 2.8, 2.8, "#d9d2ea")):
        house((x, 8, 0), w, h, c)


def set_room(wall="#9ec5e8", floor="#b98b5e", poster="#2ecc71"):
    """A teen's bedroom/study corner."""
    world("#20242c", 0.3)
    plane("floor", (14, 14), mat("floor_" + floor, floor, 0.6))
    plane("backwall", (14, 6), mat("wall_" + wall, wall, 0.9), (0, 2.2, 3), rot=(90, 0, 0))
    plane("sidewall", (14, 6), mat("wall_" + wall, wall, 0.9), (-3.6, 0, 3), rot=(90, 0, 90))
    box("window", (1.4, 0.05, 1.0), emissive("win_day", "#bfe6ff", 2.0), (1.6, 2.17, 1.9))
    box("winframe", (1.5, 0.04, 0.06), mat("white", "#f5f5f5"), (1.6, 2.13, 1.9))
    box("poster", (0.7, 0.03, 0.95), mat("poster_" + poster, poster, 0.6), (-1.6, 2.17, 1.9))
    text("posterTxt", "LEVEL UP", 0.12, mat("white", "#f5f5f5"), (-1.6, 2.14, 2.2), extrude=0.005)
    sphere("posterIcon", 0.15, mat("white", "#f5f5f5"), (-1.6, 2.14, 1.8), scale=(1, 0.2, 1))
    area((0.5, -2.5, 3.2), (50, 0, 0), size=5, color="#fff2dd", power=650)
    area((1.6, 1.6, 2.2), (-90, 0, 0), size=1.4, color="#cfe9ff", power=120)


def set_grind():
    """Night-and-day desk where 6 years of grinding happen."""
    world("#101418", 0.25)
    plane("floor", (14, 14), mat("floor_dark", "#4a3b31", 0.7))
    plane("backwall", (14, 6), mat("wall_grind", "#3d4a5c", 0.9), (0, 2.0, 3), rot=(90, 0, 0))
    sky = emissive("grind_sky", "#8ecbff", 2.0)
    box("window", (1.6, 0.05, 1.1), sky, (-1.9, 1.97, 1.9))
    box("winbar", (0.05, 0.03, 1.1), mat("white", "#f5f5f5"), (-1.9, 1.94, 1.9))
    lamp = area((0, -2.4, 3.0), (50, 0, 0), size=4, color="#fff0d6", power=500)
    desk((0, 0.6, 0), w=2.0)
    mons = []
    for i, x in enumerate((-0.38, 0.38)):
        m, scr = monitor((x, 0.78, 0.765), name=f"mon{i}", color="#0d1117")
        mons.append(m)
    return sky, lamp, mons


def set_server_room():
    world("#05070d", 0.2)
    plane("floor", (30, 30), mat("tile", "#1b2130", 0.35, 0.3))
    plane("ceil", (30, 30), mat("ceil", "#0b0f18", 0.8), (0, 0, 3.4), rot=(180, 0, 0))
    leds = []
    rack = mat("rack", "#12151c", 0.35, 0.6)
    for side in (-1, 1):
        for i in range(6):
            x, y = side * 1.9, -1.0 + i * 1.1
            box("rack", (0.9, 0.95, 2.4), rack, (x, y, 1.2), bevel=0.02)
            for row in range(10):
                c = ("#00e5ff", "#39ff14", "#8e44ad")[(row + i) % 3]
                led = box("led", (0.02, 0.6, 0.025), emissive(f"led{side}{i}{row}", c, 5),
                          (x - side * 0.46, y, 0.35 + row * 0.2))
                leds.append(led)
    for k, y in enumerate((-1, 1.5, 4)):
        box("ceilLight", (0.3, 1.2, 0.04), emissive("ceilLight", "#cfe8ff", 6), (0, y, 3.38))
    area((0, -3, 2.8), (60, 0, 0), size=3, color="#9fd6ff", power=350)
    point((0, 0.5, 2.6), "#00e5ff", 80, 0.5)
    return leds


def set_library():
    world("#2a2118", 0.3)
    plane("floor", (16, 16), mat("floor_lib", "#7a5232", 0.55))
    plane("backwall", (16, 6), mat("wall_lib", "#e9dcc3", 0.9), (0, 2.6, 3), rot=(90, 0, 0))
    rnd = random.Random(7)
    wood = mat("shelfwood", "#5b3a21", 0.6)
    for sx in (-2.6, 2.6):
        box("shelf", (1.6, 0.4, 2.6), wood, (sx, 2.35, 1.3))
        for r in range(4):
            x = sx - 0.7
            while x < sx + 0.68:
                bw = rnd.uniform(0.05, 0.1)
                bh = rnd.uniform(0.38, 0.5)
                c = rnd.choice(("#c0392b", "#2980b9", "#27ae60", "#8e44ad", "#f39c12", "#16a085", "#ecf0f1"))
                box("book", (bw, 0.28, bh), mat("book" + c, c, 0.6), (x + bw / 2, 2.15, 0.2 + r * 0.62 + bh / 2))
                x += bw + 0.008
    board = empty("board", (0, 2.55, 1.85))
    box("chalk", (2.2, 0.04, 1.1), mat("chalkboard", "#1f3b2d", 0.85), (0, 0, 0), board)
    box("chalkframe", (2.3, 0.03, 1.2), mat("shelfwood", "#5b3a21"), (0, 0.02, 0), board)
    chalk = mat("chalkline", "#f2f2f2", 0.9, emit=0.6)
    text("cs", "O(n log n)", 0.15, chalk, (-0.55, -0.03, 0.25), board)
    text("me", "F = ma", 0.17, chalk, (0.55, -0.03, 0.25), board)
    text("cs2", "if (learning) keep_going();", 0.07, chalk, (-0.2, -0.03, -0.25), board)
    text("me2", "torque = r x F", 0.09, chalk, (0.6, -0.03, -0.05), board)
    desk((0, 0.3, 0), w=2.4, d=0.9, h=0.74, color="#8a5a35")
    area((0, -2.6, 3.3), (50, 0, 0), size=5, color="#ffe6c4", power=600)
    point((0, 0.3, 2.3), "#ffd08a", 60, 0.4)


def set_church():
    world("#1b1410", 0.3)
    plane("floor", (20, 30), mat("church_floor", "#8c6a4f", 0.5))
    box("aisle", (1.1, 30, 0.01), mat("carpet", "#8b1e2d", 0.85), (0, 0, 0.005))
    stone = mat("church_wall", "#efe6d6", 0.9)
    plane("altarwall", (20, 9), stone, (0, 6.5, 4.5), rot=(90, 0, 0))
    for sx in (-1, 1):
        plane("sidewall", (30, 9), stone, (sx * 4.5, 0, 4.5), rot=(90, 0, 90))
        for i, y in enumerate((-2, 1, 4)):
            cols = ("#e74c3c", "#3498db", "#f1c40f", "#27ae60", "#9b59b6")
            for k in range(3):
                box("glass", (0.04, 0.35, 0.7), emissive(f"sg{(i + k) % 5}", cols[(i + k) % 5], 3.5),
                    (sx * 4.47, y - 0.36 + k * 0.36, 2.9))
            sphere("glasstop", 0.52, emissive("sgtop", "#f39c12", 3), (sx * 4.47, y, 3.3), scale=(0.05, 1, 0.6))
    # altar + cross
    box("altarstep", (4, 1.4, 0.25), mat("altarwood", "#6e4426", 0.5), (0, 5.4, 0.125))
    box("altar", (1.6, 0.6, 0.95), mat("altarcloth", "#f7f3ea", 0.7), (0, 5.4, 0.72))
    gold = mat("crossgold", "#f0c35a", 0.25, 0.9, emit=1.2, emit_color="#ffd37a")
    box("crossV", (0.16, 0.12, 1.7), gold, (0, 6.4, 3.0))
    box("crossH", (0.95, 0.12, 0.16), gold, (0, 6.4, 3.35))
    point((0, 5.9, 3.1), "#ffd9a0", 260, 0.6)
    # pews
    pew = mat("pew", "#5a361e", 0.55)
    for sx in (-1, 1):
        for i in range(5):
            y = 0.2 + i * 1.0
            box("pewseat", (2.6, 0.45, 0.08), pew, (sx * 1.95, y, 0.45), bevel=0.02)
            box("pewback", (2.6, 0.08, 0.6), pew, (sx * 1.95, y + 0.24, 0.75), bevel=0.02)
            box("pewend", (0.08, 0.55, 0.9), pew, (sx * 0.62, y + 0.05, 0.45), bevel=0.02)
    area((0, -3, 4.5), (45, 0, 0), size=6, color="#ffe9c9", power=700)
    area((0, 3, 6.0), (0, 0, 0), size=6, color="#ffd9a0", power=300)


def set_campus():
    world("#9fd0ff", 0.9)
    sun((55, 0, 25), "#fff4df", 3.5)
    plane("lawn", (60, 60), mat("lawn", "#6bb04f", 0.9))
    box("plaza", (8, 5, 0.03), mat("plaza", "#d8d2c4", 0.8), (0, 0.5, 0.015))
    marble = mat("marble", "#f1ede4", 0.5)
    box("hall", (9, 3, 3.6), marble, (0, 6.5, 1.8))
    box("steps", (6, 1.2, 0.3), marble, (0, 4.7, 0.15))
    box("pediment", (6.6, 0.8, 0.4), marble, (0, 4.8, 3.3))
    roof = cyl("tri", 3.7, 0.7, marble, (0, 4.9, 3.7), rot=(90, 0, 0), seg=3)
    roof.rotation_euler[1] = math.radians(90)
    roof.scale = (0.35, 1, 1)
    for i in range(6):
        cyl("column", 0.17, 3.0, marble, (-2.6 + i * 1.04, 4.9, 1.65), seg=16)
    text("hallname", "UNIVERSITY", 0.32, mat("ink", "#2c3e50"), (0, 4.38, 3.32), extrude=0.02)
    tree((-4.8, 3, 0), 1.0)
    tree((4.8, 3, 0), 1.0)
    area((0, -5, 4), (55, 0, 0), size=6, power=400)


def set_lead_office():
    world("#c9d6e2", 0.3)
    plane("floor", (20, 20), mat("office_floor", "#b9b2a8", 0.4))
    plane("backwall", (20, 8), mat("office_wall", "#dfe3e8", 0.9), (0, 2.6, 4), rot=(90, 0, 0))
    for i in range(4):
        box("glass", (1.5, 0.04, 2.6), mat("cityglass", "#5d8fb5", 0.1, emit=0.35, emit_color="#7fb3d5"),
            (-4.5 + i * 1.6, 2.55, 1.6))
    wb = empty("whiteboard", (1.1, 2.45, 1.65))
    box("wbboard", (2.2, 0.05, 1.25), mat("whiteboard", "#ffffff", 0.2), (0, 0, 0), wb)
    ink = mat("marker", "#2c3e50", 0.4)
    blue = mat("marker_blue", "#2471a3", 0.4)
    nodes = [(-0.75, 0.3, "API"), (0.0, 0.3, "AUTH"), (0.75, 0.3, "QUEUE"), (-0.4, -0.3, "DB"), (0.4, -0.3, "CACHE")]
    for x, z, lbl in nodes:
        box("node", (0.46, 0.01, 0.22), mat("nodefill", "#d6eaf8", 0.4), (x, -0.03, z), wb)
        text("nodeTxt", lbl, 0.08, ink, (x, -0.045, z), wb, extrude=0.002)
    for (x0, z0, x1, z1) in ((-0.52, 0.3, -0.23, 0.3), (0.23, 0.3, 0.52, 0.3), (-0.6, 0.18, -0.45, -0.18), (0.6, 0.18, 0.45, -0.18)):
        ln = math.hypot(x1 - x0, z1 - z0)
        ang = math.degrees(math.atan2(z1 - z0, x1 - x0))
        box("arrow", (ln, 0.005, 0.012), blue, ((x0 + x1) / 2, -0.04, (z0 + z1) / 2), wb, rot=(0, -ang, 0))
    sign = empty("sign", (-2.9, 2.5, 2.2))
    box("signbg", (2.0, 0.04, 0.42), mat("signbg", "#22222a", 0.4), (0, 0, 0), sign)
    text("signTxt", "ENGINEERING", 0.17, emissive("signglow", "#c39bd3", 4), (0, -0.03, 0), sign)
    desk((-1.6, 0.9, 0), w=1.6, color="#e5e7e9")
    monitor((-1.6, 1.0, 0.765), name="leadmon", color="#1e2a38")
    cyl("plant_pot", 0.18, 0.4, mat("pot", "#ffffff", 0.3), (2.9, 1.9, 0.2))
    sphere("plant", 0.42, mat("leaf", "#3f8f3a", 0.8), (2.9, 1.9, 0.75), seg=16)
    area((0, -3.5, 4.5), (45, 0, 0), size=7, color="#fff4e6", power=550)
    return wb
