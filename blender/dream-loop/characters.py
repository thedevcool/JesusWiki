"""CHARACTER BIBLE — locked physiques.

Every episode builds its cast by calling `build(<id>, era)`. The face/body
numbers in `BIBLE` are the single source of truth, so a character's skin
tone, head shape, eye spacing, nose, brows, ears and hair can never drift
between episodes. Only the *outfit* changes with the era (kid → student →
pro → lead), and even outfits are defined here, not in episode code.

Do not tweak a character inside an episode. If a look must change, change it
here and every episode re-renders consistently.
"""
import math
from lib import (mat, sphere, box, cyl, torus, empty, key, key_axis)

# ---- LOCKED -------------------------------------------------------------- #
BIBLE = {
    # The Game Developer (later studies Computer Science)
    "gamer": dict(
        label="The Game Dev",
        height=1.06, build=0.90,
        skin="#8a5a3c", skin_shade="#6f452c",
        head_size=1.00, head_shape=(0.92, 0.95, 1.05),   # longer, narrow
        eye_gap=0.072, eye_size=1.00, brow_tilt=-6, nose=1.0, ear=1.0,
        hair="hightop", hair_color="#1b1410",
        signature="headphones",                          # always worn
        outfits={
            "kid":     dict(top="#2ecc71", pants="#3b5b92", shoes="#e74c3c"),
            "student": dict(top="#1f9e57", pants="#2c3e5c", shoes="#e74c3c", hood=True),
        },
    ),
    # The Mechanical Engineer
    "gears": dict(
        label="The Mech Engineer",
        height=0.96, build=1.22,
        skin="#6b4026", skin_shade="#55321e",
        head_size=1.04, head_shape=(1.06, 1.0, 0.95),    # wide, square-ish
        eye_gap=0.082, eye_size=0.92, brow_tilt=4, nose=1.25, ear=1.1,
        hair="buzz", hair_color="#120c09",
        signature="orange",
        outfits={
            "kid":     dict(top="#e67e22", pants="#6d4c33", shoes="#34495e"),
            "student": dict(top="#e67e22", pants="#24476b", shoes="#3d2b1f", overalls=True),
        },
    ),
    # The "Hacker" (wanted to be a lawyer, said 'hacker' for fun,
    # became a backend dev, then a lead software engineer)
    "hacker": dict(
        label="The 'Hacker'",
        height=1.00, build=1.00,
        skin="#7a4b30", skin_shade="#603a24",
        head_size=1.00, head_shape=(0.98, 0.98, 1.0),    # oval
        eye_gap=0.076, eye_size=1.05, brow_tilt=-2, nose=0.9, ear=0.95,
        hair="sidepart", hair_color="#16100c",
        signature="glasses",                             # always worn
        outfits={
            "kid":  dict(top="#2b2b33", pants="#3b3b48", shoes="#8e44ad", hood=True),
            "pro":  dict(top="#22222a", pants="#2f2f3a", shoes="#8e44ad", hood=True),
            "lead": dict(top="#3a3f4b", pants="#262a33", shoes="#1c1c1c", blazer="#8e44ad"),
        },
    ),
}
KID_BODY = 0.64     # kids: smaller body ...
KID_HEAD = 0.90     # ... but nearly the same head, so faces stay recognisable


class Char:
    """Handle to a rigged-by-hierarchy character with simple animation verbs."""

    def __init__(self, cid, era):
        self.cid, self.era = cid, era
        self.parts = {}

    # ---- animation verbs ---- #
    def at(self, frame, loc=None, rot_z=None):
        if loc is not None:
            key(self.root, frame, loc=loc)
        if rot_z is not None:
            key_axis(self.root, frame, "rotation_euler", 2, rot_z, deg=True)

    def look(self, frame, yaw=0, pitch=0):
        key(self.head, frame, rot=(pitch, 0, yaw))

    def arm(self, frame, side, raise_=0, fwd=0, elbow=0, twist=0):
        """side: 'L' (+x... character's left is -x) | 'R'. Angles in degrees."""
        sh, el = self.parts["sh" + side], self.parts["el" + side]
        s = 1 if side == "R" else -1      # R arm sits at +x
        key(sh, frame, rot=(-fwd, -s * raise_, twist))
        key(el, frame, rot=(-elbow, 0, 0))

    def arms_rest(self, frame):
        self.arm(frame, "L", 6, 0, 8)
        self.arm(frame, "R", 6, 0, 8)

    def leg(self, frame, side, hip=0, knee=0):
        key(self.parts["hip" + side], frame, rot=(-hip, 0, 0))
        key(self.parts["knee" + side], frame, rot=(knee, 0, 0))

    def sit(self, frame, seat_h):
        z = seat_h - self.L
        loc = tuple(self.root.location)
        key(self.root, frame, loc=(loc[0], loc[1], z))
        for s in "LR":
            self.leg(frame, s, 90, 90)

    def stand_legs(self, frame):
        for s in "LR":
            self.leg(frame, s, 0, 0)

    def talk(self, f0, f1, rate=4):
        m = self.parts["mouth"]
        f = f0
        while f < f1:
            key(m, f, scale=(1, 1, 1))
            key(m, f + rate // 2, scale=(1.05, 1, 2.3))
            f += rate
        key(m, f1, scale=(1, 1, 1))

    def surprise(self, frame, hold=14):
        for b in self.parts["brows"]:
            z = b.location.z
            key(b, frame - 1, loc=(b.location.x, b.location.y, z))
            key(b, frame + 2, loc=(b.location.x, b.location.y, z + 0.03 * self.hs))
            key(b, frame + hold, loc=(b.location.x, b.location.y, z + 0.03 * self.hs))
            key(b, frame + hold + 4, loc=(b.location.x, b.location.y, z))
        m = self.parts["mouth"]
        key(m, frame - 1, scale=(1, 1, 1))
        key(m, frame + 2, scale=(0.6, 1, 3.2))
        key(m, frame + hold, scale=(0.6, 1, 3.2))
        key(m, frame + hold + 4, scale=(1, 1, 1))

    def blink(self, frame):
        for e in self.parts["eyes"]:
            key(e, frame - 1, scale=(1, 1, 1))
            key(e, frame + 1, scale=(1, 1, 0.1))
            key(e, frame + 3, scale=(1, 1, 1))

    def jump(self, frame, h=0.25, dur=10):
        x, y, z = self.root.location
        key(self.root, frame, loc=(x, y, z))
        key(self.root, frame + dur // 2, loc=(x, y, z + h))
        key(self.root, frame + dur, loc=(x, y, z))

    def bob(self, f0, f1, amp=0.015, period=24):
        x, y, z = self.root.location
        f = f0
        while f <= f1:
            ph = (f - f0) / period * 2 * math.pi
            key(self.torso_pivot, f, loc=(0, 0, self.L + amp * math.sin(ph)))
            f += period // 4

    def walk(self, f0, f1, start, end, step=8):
        key(self.root, f0, loc=start)
        key(self.root, f1, loc=end)
        f, sgn = f0, 1
        while f < f1:
            self.leg(f, "L", 25 * sgn, 10)
            self.leg(f, "R", -25 * sgn, 10)
            self.arm(f, "L", 6, -20 * sgn, 15)
            self.arm(f, "R", 6, 20 * sgn, 15)
            f += step
            sgn = -sgn
        self.stand_legs(f1)
        self.arms_rest(f1)

    def type_(self, f0, f1, rate=4):
        f, t = f0, 0
        while f <= f1:
            a = 4 if t % 2 else -4
            self.arm(f, "L", 10, 55 + a, 55)
            self.arm(f, "R", 10, 55 - a, 55)
            f += rate
            t += 1


def _surf_y(x, z, rx, ry, rz):
    """Front surface (−y) of an ellipsoid at (x, z)."""
    v = 1 - (x / rx) ** 2 - (z / rz) ** 2
    return -ry * math.sqrt(max(v, 0.0))


def build(cid, era, loc=(0, 0, 0), yaw=0):
    spec = BIBLE[cid]
    kid = era == "kid"
    outfit = spec["outfits"].get(era) or spec["outfits"][list(spec["outfits"])[-1]]
    c = Char(cid, era)
    P = c.parts
    pre = f"{cid}_"

    bf = spec["height"] * (KID_BODY if kid else 1.0)
    b = spec["build"] * (0.85 if kid else 1.0)
    hs = spec["head_size"] * (KID_HEAD if kid else 1.0)
    c.hs = hs

    L = 0.80 * bf          # leg length
    T = 0.62 * bf          # torso length
    W = 0.44 * b           # torso width
    D = 0.26 * b           # torso depth
    A = 0.62 * bf          # arm length
    lr, ar = 0.072 * b, 0.058 * b
    c.L = L

    skin = mat(pre + "skin", spec["skin"], rough=0.5)
    skin2 = mat(pre + "skin2", spec["skin_shade"], rough=0.5)
    top = mat(pre + era + "_top", outfit["top"], rough=0.7)
    pants = mat(pre + era + "_pants", outfit["pants"], rough=0.75)
    shoes = mat(pre + era + "_shoes", outfit["shoes"], rough=0.45)
    hair = mat(pre + "hair", spec["hair_color"], rough=0.9)
    white = mat("eye_white", "#f4f1ea", rough=0.25)
    black = mat("pupil", "#0d0d10", rough=0.15)
    lip = mat(pre + "lip", "#3a1d14", rough=0.4)

    root = empty(pre + "ROOT", loc)
    root.rotation_euler[2] = math.radians(yaw)
    c.root = root
    tp = empty(pre + "torso_pivot", (0, 0, L), root)
    c.torso_pivot = tp

    # ---- legs (hip -> knee) ---- #
    for s, sx in (("L", -1), ("R", 1)):
        hip = empty(pre + "hip" + s, (sx * W * 0.24, 0, L), root)
        cyl(pre + "thigh" + s, lr, L / 2 + 0.02, pants, (0, 0, -L / 4), hip)
        knee = empty(pre + "knee" + s, (0, 0, -L / 2), hip)
        cyl(pre + "shin" + s, lr * 0.92, L / 2 - 0.04, pants, (0, 0, -L / 4 + 0.01), knee)
        box(pre + "shoe" + s, (0.13 * b, 0.25 * max(bf, 0.8), 0.075), shoes,
            (0, -0.05, -L / 2 + 0.035), knee, bevel=0.03)
        P["hip" + s], P["knee" + s] = hip, knee

    # ---- torso ---- #
    box(pre + "torso", (W, D, T), top, (0, 0, T / 2), tp, bevel=0.07 * b)
    box(pre + "waist", (W * 1.01, D * 1.01, 0.13 * bf), pants, (0, 0, 0.05 * bf), tp, bevel=0.05)
    if outfit.get("hood"):
        torus(pre + "hood", W * 0.32, 0.055 * b, top, (0, 0.04, T - 0.01), tp, rot=(-12, 0, 0))
        for s in (-1, 1):  # drawstrings
            cyl(pre + "string", 0.008, 0.14 * bf, mat("string", "#eeeeee"),
                (s * 0.04, -D / 2 - 0.005, T - 0.12 * bf), tp)
    if outfit.get("overalls"):
        box(pre + "bib", (W * 0.62, 0.02, T * 0.45), pants, (0, -D / 2, T * 0.32), tp, bevel=0.01)
        for s in (-1, 1):
            box(pre + "strap", (0.05, D * 1.04, 0.03), pants, (s * W * 0.25, 0, T - 0.02), tp)
            box(pre + "strapF", (0.05, 0.02, T * 0.38), pants, (s * W * 0.25, -D / 2, T * 0.72), tp)
            sphere(pre + "button", 0.018, mat("brass", "#d4a017", 0.3, 0.8),
                   (s * W * 0.25, -D / 2 - 0.02, T * 0.53), tp)
    if outfit.get("blazer"):
        shirt = mat(pre + "shirt", outfit["blazer"], rough=0.6)
        box(pre + "shirtV", (W * 0.22, 0.02, T * 0.6), shirt, (0, -D / 2 - 0.01, T * 0.68), tp)
        for s in (-1, 1):
            box(pre + "lapel", (0.05, 0.02, T * 0.5), mat(pre + "lapel", "#2b2f38"),
                (s * W * 0.15, -D / 2 - 0.02, T * 0.7), tp, rot=(0, s * 15, 0))
        box(pre + "badge", (0.07, 0.01, 0.05), mat("badge", "#f1c40f", 0.3),
            (-W * 0.3, -D / 2 - 0.02, T * 0.72), tp)

    # ---- arms (shoulder -> elbow) ---- #
    for s, sx in (("L", -1), ("R", 1)):
        sh = empty(pre + "sh" + s, (sx * (W / 2 + ar * 0.7), 0, T - 0.07 * bf), tp)
        sphere(pre + "shoulder" + s, ar * 1.08, top, (0, 0, 0), sh)
        cyl(pre + "uarm" + s, ar, A / 2 + 0.02, top, (0, 0, -A / 4), sh)
        el = empty(pre + "el" + s, (0, 0, -A / 2), sh)
        cyl(pre + "farm" + s, ar * 0.92, A / 2, top, (0, 0, -A / 4), el)
        sphere(pre + "hand" + s, ar * 1.3, skin, (0, 0, -A / 2 - 0.02), el)
        P["sh" + s], P["el" + s] = sh, el
        sh.rotation_euler = (0, math.radians(-sx * 6), 0)

    # ---- head (all features in head-pivot space, from the locked spec) ---- #
    head = empty(pre + "head", (0, 0, T), tp)
    c.head = head
    R = 0.20 * hs
    rx, ry, rz = (R * k for k in spec["head_shape"])
    hz = 0.07 + rz * 0.95
    cyl(pre + "neck", 0.055 * b, 0.12, skin, (0, 0, 0.04), head)
    sphere(pre + "skull", R, skin, (0, 0, hz), head, scale=spec["head_shape"], seg=40)

    eg, es = spec["eye_gap"] * hs, 0.040 * spec["eye_size"] * hs
    eyes, brows = [], []
    for sx in (-1, 1):
        ex, ez = sx * eg, 0.015 * hs
        ey = _surf_y(ex, ez, rx, ry, rz)
        ep = empty(pre + "eye", (ex, ey + es * 0.45, hz + ez), head)
        sphere(pre + "eyeW", es, white, (0, 0, 0), ep, scale=(1, 0.6, 1.1))
        sphere(pre + "pupil", es * 0.52, black, (0, -es * 0.42, -es * 0.05), ep, scale=(1, 0.5, 1))
        sphere(pre + "glint", es * 0.15, mat("glint", "#ffffff", emit=2.0),
               (es * 0.18, -es * 0.66, es * 0.22), ep)
        eyes.append(ep)
        bz = ez + 0.062 * hs
        by = _surf_y(ex, bz, rx, ry, rz)
        br = box(pre + "brow", (0.075 * hs, 0.02, 0.018 * hs), hair, (ex, by + 0.004, hz + bz), head,
                 rot=(0, sx * spec["brow_tilt"], 0), bevel=0.006)
        brows.append(br)
        # ears
        sphere(pre + "ear", 0.045 * hs * spec["ear"], skin, (sx * rx * 0.98, 0.0, hz), head,
               scale=(0.45, 0.8, 1.15))
    P["eyes"], P["brows"] = eyes, brows

    nz = -0.035 * hs
    sphere(pre + "nose", 0.03 * hs * spec["nose"], skin2,
           (0, _surf_y(0, nz, rx, ry, rz) + 0.008, hz + nz), head, scale=(1.15, 0.9, 0.95))
    mz = -0.10 * hs
    mouth = empty(pre + "mouth", (0, _surf_y(0, mz, rx, ry, rz) + 0.006, hz + mz), head)
    torus(pre + "smile", 0.045 * hs, 0.009 * hs, lip, (0, 0, 0.03 * hs), mouth,
          rot=(90, 0, 0), arc=(200, 340), seg=16, rseg=8)
    P["mouth"] = mouth

    # ---- hair (locked style) ---- #
    style = spec["hair"]
    hsc = tuple(k * 1.05 for k in spec["head_shape"])
    if style == "hightop":
        sphere(pre + "hair", R, hair, (0, 0.006, hz + 0.01), head, scale=hsc, seg=40,
               cut=lambda x, y, z: z < -0.05 or (y < -0.15 and z < 0.5))
        cyl(pre + "hightop", rx * 0.82, 0.16 * hs, hair, (0, 0.01, hz + rz * 0.9), head,
            r2=rx * 0.86, seg=28)
        sphere(pre + "htcap", rx * 0.86, hair, (0, 0.01, hz + rz * 0.9 + 0.08 * hs), head,
               scale=(1, 0.95, 0.25))
    elif style == "buzz":
        sphere(pre + "hair", R, hair, (0, 0.004, hz + 0.004), head,
               scale=tuple(k * 1.025 for k in spec["head_shape"]), seg=40,
               cut=lambda x, y, z: z < -0.15 or (y < -0.2 and z < 0.58))
    elif style == "sidepart":
        sphere(pre + "hair", R, hair, (0, 0.006, hz + 0.012), head, scale=hsc, seg=40,
               cut=lambda x, y, z: z < -0.1 or (y < -0.2 and z < 0.42))
        sphere(pre + "swoop", R * 0.55, hair, (-rx * 0.35, -ry * 0.55, hz + rz * 0.62), head,
               scale=(1.3, 0.7, 0.45), rot=(0, 15, 0))
        box(pre + "part", (0.006, ry * 1.2, 0.02), mat("part", "#3a2a20"),
            (rx * 0.32, 0, hz + rz * 0.93), head, rot=(0, 20, 0))

    # ---- signature accessories (locked) ---- #
    sig = spec["signature"]
    if sig == "headphones":
        hp = mat("headphones", "#111111", 0.3)
        hpa = mat("headphones_accent", "#2ecc71", 0.3, emit=1.5)
        torus(pre + "hp_band", W * 0.36, 0.02, hp, (0, -0.02, 0.02), head, rot=(-10, 0, 0))
        for sx in (-1, 1):
            cyl(pre + "hp_cup", 0.05, 0.04, hp, (sx * W * 0.34, -0.09, 0.0), head, rot=(0, 90, 0))
            cyl(pre + "hp_ring", 0.03, 0.045, hpa, (sx * W * 0.34, -0.09, 0.0), head, rot=(0, 90, 0))
    if sig == "glasses":
        gm = mat("glasses", "#0b0b0b", 0.2, 0.5)
        lens = mat("lens", "#9fd3ff", 0.05, emit=0.15)
        for e in eyes:
            ex, ey, ez = e.location
            torus(pre + "rim", es * 1.45, 0.006, gm, (ex, ey - es * 0.75, ez), head,
                  rot=(90, 45, 0), seg=4, rseg=6)
            cyl(pre + "lens", es * 1.4, 0.003, lens, (ex, ey - es * 0.75, ez), head,
                rot=(90, 45, 0), seg=4)
            sx = 1 if ex > 0 else -1
            box(pre + "temple", (0.008, ry * 0.9, 0.008), gm, (sx * (abs(ex) + es * 1.4), ey * 0.45, ez), head)
        e0 = eyes[0].location
        box(pre + "bridge", (eg * 2 - es * 2.8, 0.008, 0.008), gm, (0, e0.y - es * 0.75, e0.z + 0.01), head)

    c.arms_rest(1)
    return c
