"""The 10 episodes. Usage (with Blender's Python / `bpy` module):

    python episodes.py --ep 3 --out frames/ep03 [--still 40] [--res 960x540] [--samples 20]
"""
import os
import sys
import math
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *          # noqa: E402,F401
import sets as S           # noqa: E402
import characters as C     # noqa: E402

N = EP_FRAMES


def kick_legs(ch, f0, f1, period=16, amp=18, phase=0):
    f = f0
    while f <= f1:
        a = amp * math.sin((f - f0) / period * 2 * math.pi + phase)
        ch.leg(f, "L", 90, 90 + a)
        ch.leg(f, "R", 90, 90 - a)
        f += period // 4


def seat(ch, frame, seat_h, rot_z=None):
    x, y, _ = ch.root.location
    z = seat_h + 0.05 - ch.L
    ch.at(frame, (x, y, z), rot_z)
    for s in "LR":
        ch.leg(frame, s, 90, 90)


def stool(loc, h=0.47):
    st = empty("stool", loc)
    cyl("stoolseat", 0.22, 0.06, mat("stool", "#e67e22", 0.5), (0, 0, h), st)
    cyl("stoolleg", 0.03, h, mat("desk_leg", "#333333", 0.4, 0.6), (0, 0, h / 2), st)
    return st


def screen_text(lid, body, size, color, f_on=1, f_off=None, z=0.14, name="scrtxt"):
    t = text(name, body, size, emissive("st_" + color, color, 6), (0, -0.006, z), lid, extrude=0.0)
    show_between(t, f_on, f_off)
    return t


def hard_hat(ch):
    R = 0.2 * ch.hs
    hat = empty("hardhat", (0, 0, 0.07 + R * 0.95 * 0.95 + R * 0.55), ch.head)
    yel = mat("hardhat", "#f1c40f", 0.35)
    sphere("dome", R * 1.12, yel, (0, 0, 0), hat, scale=(1.08, 1.0, 0.8), cut=lambda x, y, z: z < 0.0)
    cyl("brim", R * 1.28, 0.02, yel, (0, -0.03, 0.0), hat)
    box("ridge", (0.04, R * 2.0, 0.04), yel, (0, 0, R * 0.86), hat, bevel=0.015)
    return hat


def grad_cap(name, loc):
    g = empty(name, loc)
    blk = mat("capblack", "#111111", 0.5)
    box("board", (0.5, 0.5, 0.025), blk, (0, 0, 0), g, rot=(0, 0, 45))
    cyl("crown", 0.17, 0.12, blk, (0, 0, -0.07), g)
    gold = mat("tassel", "#f1c40f", 0.4)
    sphere("button", 0.025, gold, (0, 0, 0.02), g)
    cyl("tassel", 0.012, 0.22, gold, (0.24, -0.1, -0.1), g)
    return g


# =========================================================================== #
def ep01():
    """The Dream — three kids, three thought bubbles."""
    S.set_street()
    cam, tgt = camera((0.3, -6.0, 1.55), (0, 0, 1.3), lens=36)
    key(cam, 1, loc=(0.3, -6.0, 1.55)); key(cam, N, loc=(0, -5.0, 1.45))
    kids = {}
    for cid, x in (("gamer", -0.8), ("hacker", 0.0), ("gears", 0.8)):
        k = C.build(cid, "kid", (x, 0.02, 0))
        seat(k, 1, 0.34)
        kick_legs(k, 1, N, period=16 + int(x * 4), phase=x * 3)
        kids[cid] = k
    kids["gamer"].look(1, yaw=12); kids["gears"].look(1, yaw=-12)
    for cid, x, f, ic in (("gamer", -1.35, 12, S.icon_controller), ("gears", 1.35, 30, S.icon_gear),
                          ("hacker", 0.0, 50, S.icon_scales)):
        k = kids[cid]
        z = 2.2 if cid == "hacker" else 1.95
        b = S.bubble(f"bub_{cid}", (x, 0, z), (k.root.location.x, 0, 1.25), r=0.38)
        ic(b, 0.75)
        pop_in(b, f, 7)
        k.look(f - 2, yaw=0); k.look(f + 6, yaw=-10 if x > 0 else 10, pitch=-14)
        k.talk(f + 2, f + 14)
        k.blink(f + 30 if f + 30 < N else 8)
    gear = [o for o in bpy.data.objects if o.name.startswith("gear")][0]
    key(gear, 1, rot=(0, 0, 0)); key(gear, N, rot=(0, 400, 0))
    kids["hacker"].look(70, yaw=-15, pitch=-10); kids["hacker"].look(86, yaw=15, pitch=-10)


def ep02():
    """Plot twist — 'lawyer'... no, 'HACKER' (just for fun)."""
    S.set_street()
    cam, tgt = camera((0.0, -4.0, 1.5), (0, 0, 1.55), lens=36)
    key(cam, 1, loc=(0.0, -4.0, 1.5)); key(cam, N, loc=(0.0, -4.4, 1.55))
    kids = {}
    for cid, x in (("gamer", -0.8), ("hacker", 0.0), ("gears", 0.8)):
        k = C.build(cid, "kid", (x, 0.02, 0))
        seat(k, 1, 0.34)
        kids[cid] = k
    kick_legs(kids["hacker"], 1, 40, period=12)
    for cid, x, ic in (("gamer", -1.35, S.icon_controller), ("gears", 1.35, S.icon_gear)):
        b = S.bubble(f"bub_{cid}", (x, 0, 2.05), (kids[cid].root.location.x, 0, 1.25), r=0.38)
        ic(b, 0.75)
        if cid == "gears":
            g_ = [o for o in b.children_recursive if o.name.startswith("gear")][0]
            key(g_, 1, rot=(0, 0, 0)); key(g_, N, rot=(0, 400, 0))
    law = S.bubble("bub_law", (0, 0, 2.2), (0, 0, 1.25), r=0.38)
    S.icon_scales(law, 0.75)
    pop_out(law, 26, 6)
    hb = S.bubble("bub_hack", (0, 0, 2.2), (0, 0, 1.25), r=0.42, color="#14161c")
    S.icon_hacker(hb, 0.8)
    pop_in(hb, 32, 7)
    h, g, m = kids["hacker"], kids["gamer"], kids["gears"]
    h.look(10, yaw=-25); h.look(18, yaw=-28, pitch=-8); h.talk(12, 30)
    h.arm(12, "R", 6, 0, 8); h.arm(22, "R", 120, 20, 30); h.arm(40, "R", 6, 0, 8)
    for k, yaw in ((g, 30), (m, -30)):
        k.look(1, yaw=0); k.look(36, yaw=0); k.look(42, yaw=yaw, pitch=-5)
        k.surprise(42, 18)
        x, y, z = k.root.location
        key(k.root, 40, loc=(x, y, z)); key(k.root, 45, loc=(x, y, z + 0.18)); key(k.root, 51, loc=(x, y, z))
    # hacker cracks up
    h.look(50, yaw=0, pitch=0)
    for i, f in enumerate(range(54, N, 6)):
        h.look(f, yaw=4 * (-1) ** i, pitch=-12 if i % 2 else 4)
    h.talk(52, 90, rate=3)
    h.arm(52, "L", 30, 50, 90); h.arm(52, "R", 30, 50, 90)


def ep03():
    """Friendly terror — the game dev gets 'hacked' :)"""
    S.set_room()
    cam, tgt = camera((1.5, -2.3, 1.6), (0.15, 0.55, 0.9), lens=34)
    key(cam, 1, loc=(1.5, -2.3, 1.6)); key(cam, N, loc=(1.25, -2.0, 1.45))
    dk = S.desk((0, 0.95, 0), w=1.4, d=0.65, h=0.62)
    stool((0, 0.25, 0), 0.4)
    lp, lid, scr = S.laptop((0, 0.88, 0.645), name="glaptop")
    screen_text(lid, "MY GAME v0.1", 0.04, "#ffffff", 1, 44, z=0.17)
    sprite = box("sprite", (0.05, 0.005, 0.05), emissive("sprite", "#f1c40f", 4), (-0.08, -0.006, 0.09), lid)
    show_between(sprite, 1, 44)
    for f in range(1, 44, 6):
        key(sprite, f, loc=(-0.12 + (f % 24) / 100, -0.006, 0.09 + 0.02 * ((f // 6) % 2)))
    screen_text(lid, "HACKED :)", 0.06, "#39ff14", 44, z=0.15)
    screen_text(lid, "- your friendly hacker", 0.022, "#39ff14", 44, z=0.09)
    key_mat_emission(scr, 43, color="#2f80ed", strength=2.5)
    key_mat_emission(scr, 44, color="#1a0000", strength=2.5)
    for f in range(44, N, 4):
        key_mat_emission(scr, f, color="#3a0000" if (f // 4) % 2 else "#100000", strength=3)
    g = C.build("gamer", "kid", (0, 0.25, 0), yaw=180)
    seat(g, 1, 0.4)
    g.type_(1, 42)
    g.look(1, yaw=0, pitch=-8)
    g.surprise(46, 30)
    g.look(46, yaw=0, pitch=12); g.look(52, yaw=-140, pitch=5)
    g.arm(46, "L", 140, 20, 20); g.arm(46, "R", 140, 20, 20)
    g.arm(60, "L", 120, 60, 120); g.arm(60, "R", 120, 60, 120)   # hands on head
    x, y, z = g.root.location
    key(g.root, 44, loc=(x, y, z)); key(g.root, 48, loc=(x, y, z + 0.15)); key(g.root, 53, loc=(x, y, z))
    h = C.build("hacker", "kid", (3.2, 0.6, 0), yaw=40)
    h.walk(48, 64, (3.2, 0.6, 0), (1.35, 0.55, 0), step=6)
    h.look(64, yaw=-20); h.talk(64, N, 3)
    for i, f in enumerate(range(66, N, 6)):
        h.look(f, yaw=-20, pitch=-14 if i % 2 else 6)
    h.arm(66, "R", 80, 30, 10)     # pointing & laughing
    h.arm(66, "L", 30, 50, 100)


def ep04():
    """Help desk — whenever the game dev is stuck, he knows who to call."""
    S.set_room(wall="#cbbde8", floor="#9c7a5a", poster="#8e44ad")
    cam, tgt = camera((0.9, -2.7, 1.45), (-0.15, 0.4, 0.9), lens=32)
    S.desk((0.4, 0.95, 0), w=1.3, d=0.65, h=0.62)
    stool((0.4, 0.25, 0), 0.4)
    lp, lid, scr = S.laptop((0.4, 0.88, 0.645), name="hlaptop", screen_color="#0d1117")
    S.code_lines(lid, 0.3, 0.18, -0.006, 0.14, seed=4, rows=6)
    h = C.build("hacker", "kid", (0.4, 0.25, 0), yaw=180)
    seat(h, 1, 0.4)
    h.type_(1, 26)
    h.look(30, yaw=-110); h.at(30, rot_z=180); h.at(38, rot_z=150)
    h.type_(50, 70, rate=3)
    h.look(50, yaw=-60, pitch=-10); h.look(70, yaw=-60, pitch=-10)
    h.look(74, yaw=-130); h.talk(74, 86)
    g = C.build("gamer", "kid", (-2.8, 0.1, 0), yaw=70)
    g.walk(1, 28, (-2.8, 0.1, 0), (-0.75, 0.15, 0), step=7)
    glp, glid, gscr = S.laptop((0, -0.3, 0.12), parent=g.torso_pivot, name="glap",
                               screen_color="#4a0000", rot=(10, 0, -60))
    screen_text(glid, "BUG!", 0.07, "#ff5c5c", 1, 72, z=0.15)
    screen_text(glid, "FIXED!", 0.07, "#39ff14", 72, z=0.15)
    key_mat_emission(gscr, 71, color="#4a0000"); key_mat_emission(gscr, 72, color="#003a10")
    for f in (1, 28):
        g.arm(f, "L", 10, 70, 40); g.arm(f, "R", 10, 70, 40)
    g.look(30, yaw=40); g.talk(30, 46); g.surprise(30, 10)
    g.look(50, yaw=30, pitch=-15)
    g.arm(74, "L", 10, 70, 40); g.arm(78, "L", 150, 10, 10)    # celebrate
    g.jump(76, 0.22, 10); g.look(78, yaw=-10, pitch=8); g.talk(78, N, 3)
    h.arm(80, "R", 6, 0, 8); h.arm(86, "R", 130, 10, 10)        # thumbs up / high five


def ep05():
    """The grind — 6 years, day & night."""
    sky, lamp, mons = S.set_grind()
    cam, tgt = camera((1.9, -1.6, 1.75), (0.0, 0.55, 1.1), lens=32)
    key(cam, 1, loc=(1.9, -1.6, 1.75)); key(cam, N, loc=(1.55, -1.25, 1.6))
    S.chair((0, -0.05, 0), rot_z=180)
    h = C.build("hacker", "pro", (0, 0.05, 0), yaw=180)
    seat(h, 1, 0.5)
    h.type_(1, N, rate=3)
    h.look(1, yaw=-6, pitch=-4)
    for i, f in enumerate(range(8, N, 16)):
        h.look(f, yaw=8 if i % 2 else -10, pitch=-4)
    for mi, m in enumerate(mons):
        cg = S.code_lines(m, 0.52, 0.28, -0.022, 0.39, seed=mi + 10, rows=10)
        lines = list(cg.children)
        for j, ln in enumerate(lines):
            f = 1 + int(j * (N - 10) / len(lines))
            sx = ln.scale.copy()
            key(ln, 1, scale=(0.001, 1, 1)); key(ln, f, scale=(0.001, 1, 1)); key(ln, f + 3, scale=(1, 1, 1))
    cal = empty("calendar", (1.2, 1.96, 1.95))
    box("calpage", (0.5, 0.02, 0.6), mat("white", "#f5f5f5"), (0, 0, 0), cal)
    box("calhead", (0.5, 0.025, 0.14), mat("calred", "#c0392b"), (0, -0.002, 0.23), cal)
    for yr in range(6):
        t = text(f"yr{yr}", f"YEAR\n{yr + 1}", 0.11, mat("ink", "#2c3e50"), (0, -0.02, -0.06), cal, extrude=0.004)
        show_between(t, 1 + yr * 16, 1 + (yr + 1) * 16 if yr < 5 else None)
    for yr in range(6):    # day/night cycle per year
        f = 1 + yr * 16
        key_mat_emission(sky, f, color="#8ecbff", strength=2.2)
        key_mat_emission(sky, f + 7, color="#ffb36b", strength=1.6)
        key_mat_emission(sky, f + 10, color="#0b1030", strength=0.6)
        key_mat_emission(sky, f + 15, color="#0b1030", strength=0.6)
        lamp.data.energy = 500; lamp.data.keyframe_insert("energy", frame=f)
        lamp.data.energy = 180; lamp.data.keyframe_insert("energy", frame=f + 10)
    mug = mat("mug", "#ecf0f1", 0.3)
    for i in range(6):
        mg = cyl(f"mug{i}", 0.04, 0.1, mug, (-0.85 + (i % 3) * 0.1, 0.45 + (i // 3) * 0.12, 0.815), seg=16)
        pop_in(mg, 6 + i * 16, 4)


def ep06():
    """Backend boss."""
    leds = S.set_server_room()
    cam, tgt = camera((-0.9, -4.2, 1.3), (0, 1.0, 1.35), lens=32)
    key(cam, 1, loc=(-0.9, -4.2, 1.3)); key(cam, N, loc=(0.7, -3.3, 1.2))
    rnd = random.Random(3)
    for led in leds:
        m = led.data.materials[0]
        for f in range(1, N + 1, 8):
            key_mat_emission(m, f + rnd.randint(0, 6), strength=rnd.choice((0.3, 6, 6)))
    h = C.build("hacker", "pro", (0, 1.0, 0))
    h.look(1, yaw=0, pitch=-8); h.look(14, yaw=0, pitch=6); h.look(20, yaw=0, pitch=-2)
    h.arms_rest(20)
    h.arm(30, "L", 20, 55, 105); h.arm(30, "R", 25, 60, 100)   # arms crossed
    h.blink(60)
    holo = empty("holo", (0, 1.0, 2.55))
    glow = emissive("holo", "#00e5ff", 6)
    text("holoTxt", "BACKEND DEVELOPER", 0.22, glow, (0, 0, 0), holo, extrude=0.0)
    text("holoSub", "APIs  ·  DATABASES  ·  CLOUD", 0.08, emissive("holo2", "#9fd6ff", 4), (0, 0, -0.2), holo, extrude=0.0)
    pop_in(holo, 22, 8)
    key(holo, 32, loc=(0, 1.0, 2.55)); key(holo, N, loc=(0, 1.0, 2.62))
    ring = empty("orbit", (0, 1.0, 1.2))
    for i in range(6):
        a = i * 60
        cube = box("packet", (0.09, 0.09, 0.09), emissive("pkt" + str(i % 3), ("#00e5ff", "#39ff14", "#c39bd3")[i % 3], 5),
                   (math.cos(math.radians(a)) * 0.85, math.sin(math.radians(a)) * 0.85, 0.15 * math.sin(a)), ring,
                   bevel=0.015)
        key(cube, 1, rot=(0, 0, 0)); key(cube, N, rot=(180, 360, 0))
    key(ring, 1, rot=(0, 0, 0)); key(ring, N, rot=(0, 0, 240))


def ep07():
    """Still studying — Computer Science & Mechanical Engineering."""
    S.set_library()
    cam, tgt = camera((0, -3.6, 1.45), (0, 0.6, 1.05), lens=36)
    key(cam, 1, loc=(0.3, -3.8, 1.5)); key(cam, N, loc=(-0.2, -3.2, 1.4))
    g = C.build("gamer", "student", (-0.62, 0.95, 0))
    m = C.build("gears", "student", (0.62, 0.95, 0))
    hard_hat(m)
    for ch in (g, m):
        S.chair((ch.root.location.x, ch.root.location.y + 0.05, 0))
        seat(ch, 1, 0.5)
        ch.arm(1, "L", 12, 55, 35); ch.arm(1, "R", 12, 55, 35)
        bk = empty("openbook", (0, -0.42, 0.22), ch.torso_pivot, rot=(-55, 0, 0))
        page = mat("page", "#fbf7ee", 0.8)
        cover = mat("cover_" + ch.cid, "#2980b9" if ch.cid == "gamer" else "#c0392b", 0.6)
        for s in (-1, 1):
            box("page", (0.15, 0.2, 0.02), page, (s * 0.075, 0, 0), bk, rot=(0, s * 10, 0))
            box("cover", (0.16, 0.21, 0.01), cover, (s * 0.078, 0, -0.012), bk, rot=(0, s * 10, 0))
    for i, f in enumerate(range(1, N, 12)):
        g.look(f, yaw=0, pitch=-18 if i % 2 else -10)
        m.look(f + 6, yaw=0, pitch=-16 if i % 2 else -9)
    g.look(56, yaw=30, pitch=0); m.look(58, yaw=-30, pitch=0)
    g.talk(58, 70, 3); m.talk(60, 72, 3)
    g.look(76, yaw=0, pitch=-15); m.look(78, yaw=0, pitch=-15)
    rnd = random.Random(11)
    for side, cx in ((-1, -1.05), (1, 1.05)):
        for i in range(7):
            c = rnd.choice(("#c0392b", "#2980b9", "#27ae60", "#8e44ad", "#f39c12", "#16a085"))
            bk = box("stackbook", (0.3, 0.22, 0.06), mat("book" + c, c, 0.6),
                     (cx + rnd.uniform(-0.03, 0.03), 0.25, 0.795 + i * 0.062), rot=(0, 0, rnd.uniform(-8, 8)))
            pop_in(bk, 4 + i * 11 + (side + 1) * 3, 4)
    glp, glid, _ = S.laptop((-0.15, 0.1, 0.765), name="studylap", screen_color="#0d1117", rot=(0, 0, 200))
    S.code_lines(glid, 0.3, 0.18, -0.006, 0.14, seed=21, rows=6)


def ep08():
    """Sundays — after 3 years, they always meet at church."""
    S.set_church()
    cam, tgt = camera((0, -5.0, 1.7), (0, 1.5, 1.3), lens=30)
    key(cam, 1, loc=(0, -5.2, 1.75)); key(cam, N, loc=(0, -4.0, 1.6))
    g = C.build("gamer", "student", (-3.4, -0.9, 0), yaw=90)
    m = C.build("gears", "student", (3.4, -0.9, 0), yaw=-90)
    g.walk(1, 34, (-3.4, -0.9, 0), (-0.42, -0.9, 0))
    m.walk(1, 34, (3.4, -0.9, 0), (0.45, -0.9, 0))
    for ch, yaw in ((g, 90), (m, -90)):
        ch.at(1, rot_z=yaw); ch.at(34, rot_z=yaw); ch.at(40, rot_z=yaw * 0.6)
        ch.look(36, yaw=0); ch.talk(38, 52, 3)
        ch.arm(38, "R", 140, 0, 20); ch.arm(42, "R", 150, 0, -10); ch.arm(46, "R", 140, 0, 20)
        ch.arm(50, "R", 6, 0, 8)
    # hug
    for ch, x in ((g, -0.27), (m, 0.3)):
        ch.at(52, (-0.42 if ch is g else 0.45, -0.9, 0))
        ch.at(58, (x, -0.9, 0))
        ch.at(54, rot_z=90 if ch is g else -90)
        ch.arm(54, "L", 35, 80, 20); ch.arm(54, "R", 35, 80, 20)
        ch.arm(66, "L", 35, 80, 20); ch.arm(66, "R", 35, 80, 20)
        ch.arms_rest(70)
        ch.at(66, (x, -0.9, 0))
        ch.at(70, rot_z=180); ch.look(70, yaw=0, pitch=8)
    g.walk(72, N, (-0.27, -0.9, 0), (-0.3, 0.3, 0), step=8)
    m.walk(72, N, (0.3, -0.9, 0), (0.33, 0.3, 0), step=8)
    for ch in (g, m):
        ch.at(N, rot_z=180)


def ep09():
    """Almost there… but still learning."""
    S.set_campus()
    cam, tgt = camera((0, -4.8, 1.6), (0, 0, 1.75), lens=34)
    key(cam, 1, loc=(0.4, -5.0, 1.55)); key(cam, N, loc=(0, -4.4, 1.65))
    g = C.build("gamer", "student", (-0.6, 0, 0), yaw=8)
    m = C.build("gears", "student", (0.6, 0, 0), yaw=-8)
    for i, (ch, lbl, pct, x) in enumerate(((g, "COMPUTER SCIENCE", 0.93, -0.75), (m, "MECH ENGINEERING", 0.95, 0.75))):
        bar = empty("bar" + ch.cid, (x, -0.1, 2.62))
        box("frame", (1.0, 0.04, 0.14), mat("barframe", "#2c3e50", 0.5), (0, 0.02, 0), bar, bevel=0.02)
        piv = empty("fillpiv", (-0.47, -0.01, 0), bar)
        box("fill", (0.94, 0.03, 0.09), emissive("barfill" + ch.cid, "#2ecc71" if i == 0 else "#e67e22", 3),
            (0.47, 0, 0), piv)
        text("barlbl", lbl, 0.085, mat("ink", "#2c3e50"), (0, 0, 0.16), bar, extrude=0.005)
        key(piv, 1, scale=(0.15, 1, 1)); key(piv, 40, scale=(pct - 0.04, 1, 1)); key(piv, 60, scale=(pct, 1, 1))
        key(piv, 75, scale=(pct + 0.005, 1, 1)); key(piv, N, scale=(pct + 0.01, 1, 1))
        cap = grad_cap("cap" + ch.cid, (ch.root.location.x, 0, 4.2))
        top = {"gamer": 2.12, "gears": 1.84}[ch.cid]
        key(cap, 1, loc=(ch.root.location.x, 0, 4.2)); key(cap, 30, loc=(ch.root.location.x, 0, 4.2))
        key(cap, 55, loc=(ch.root.location.x, 0, top + 0.22)); key(cap, 60, loc=(ch.root.location.x, 0, top + 0.28))
        key(cap, N, loc=(ch.root.location.x, 0, top + 0.26))
        key(cap, 55, rot=(0, 0, 0)); key(cap, N, rot=(0, 0, 25 * (-1) ** i))
        ch.look(1, yaw=0, pitch=-15); ch.look(42, yaw=0, pitch=-15); ch.look(52, yaw=0, pitch=-30)
        ch.look(64, yaw=(-1) ** i * 25, pitch=0)
        ch.talk(66, 80, 3)
        ch.blink(20 + i * 6)
    # out come the books: still learning
    for ch in (g, m):
        bk = empty("book_" + ch.cid, (0, -0.42, 0.42), ch.torso_pivot, rot=(-60, 0, 0))
        box("bkbody", (0.28, 0.2, 0.05), mat("bk_" + ch.cid, "#2980b9" if ch is g else "#c0392b", 0.6), (0, 0, 0), bk,
            bevel=0.005)
        pop_in(bk, 78, 5)
        ch.arm(76, "L", 8, 0, 8); ch.arm(80, "L", 12, 55, 35)
        ch.arm(76, "R", 8, 0, 8); ch.arm(80, "R", 12, 55, 35)
        ch.look(84, yaw=0, pitch=-20)


def ep10():
    """The lead — still not a hacker… yet. Fly into the bubble → loop to ep1."""
    S.set_lead_office()
    cam, tgt = camera((0, -3.3, 1.55), (0.3, 1.4, 1.35), lens=32)
    h = C.build("hacker", "lead", (0.0, 1.5, 0), yaw=-15)
    h.arm(1, "R", 75, 10, 10); h.look(1, yaw=40); h.talk(4, 26, 4)
    h.arm(14, "R", 70, 15, 20); h.arm(24, "R", 75, 10, 10)
    h.arms_rest(32); h.look(32, yaw=-15)
    plate = empty("plate", (0.2, 1.3, 2.62))
    text("plateTxt", "LEAD SOFTWARE ENGINEER", 0.17, emissive("plate", "#c39bd3", 5), (0, 0, 0), plate, extrude=0.0)
    pop_in(plate, 28, 7)
    pop_out(plate, 60, 5)
    b = S.bubble("bub_dream", (-0.9, 1.5, 2.45), (-0.1, 1.5, 2.0), r=0.36)
    S.icon_hacker(b, 0.7)
    text("q", "?", 0.3, emissive("hackgreen", "#39ff14", 6), (0.3, -0.22, 0.05), b, extrude=0.0)
    pop_in(b, 44, 7)
    h.look(44, yaw=-15); h.look(52, yaw=-35, pitch=-15)
    h.arm(58, "L", 40, 40, 100); h.arm(58, "R", 40, 40, 100)       # shrug
    h.look(60, yaw=0, pitch=5); h.talk(60, 72, 3)
    h.arm(70, "L", 40, 40, 100); h.arm(70, "R", 40, 40, 100)
    h.arms_rest(76)
    # fly into the dream bubble — it fills the frame white, ep01 fades in from white
    key(tgt, 1, loc=(0.3, 1.4, 1.35)); key(tgt, 64, loc=(0.1, 1.4, 1.6)); key(tgt, 78, loc=(-0.9, 1.5, 2.45))
    key(cam, 1, loc=(0, -3.3, 1.55)); key(cam, 68, loc=(-0.2, -3.0, 1.7)); key(cam, N, loc=(-0.9, 1.2, 2.45))
    key(b, 74, scale=(1, 1, 1)); key(b, N, scale=(2.2, 2.2, 2.2))


EPISODES = {i + 1: f for i, f in enumerate((ep01, ep02, ep03, ep04, ep05, ep06, ep07, ep08, ep09, ep10))}


def main():
    a = sys.argv
    ep = int(a[a.index("--ep") + 1])
    out = a[a.index("--out") + 1]
    res = tuple(int(v) for v in (a[a.index("--res") + 1] if "--res" in a else "960x540").split("x"))
    samples = int(a[a.index("--samples") + 1]) if "--samples" in a else 20
    reset()
    EPISODES[ep]()
    setup_render(out, res=res, samples=samples)
    sc = bpy.context.scene
    sc.render.use_persistent_data = True
    os.makedirs(out, exist_ok=True)
    if "--still" in a:
        for f in a[a.index("--still") + 1].split(","):
            sc.frame_set(int(f))
            sc.render.filepath = os.path.join(out, f"still_{int(f):03d}.png")
            bpy.ops.render.render(write_still=True)
    else:
        if "--frames" in a:
            s, e = a[a.index("--frames") + 1].split("-")
            sc.frame_start, sc.frame_end = int(s), int(e)
        bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()
