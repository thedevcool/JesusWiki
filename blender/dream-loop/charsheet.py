"""Render the locked character model sheet (front + 3/4 views, kid + adult)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import characters as C

out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "/tmp/sheet.png"
res = (1600, 900)
reset()
world("#dfe6ee", 0.9)
plane("floor", (40, 40), mat("floor", "#c9d3dd", 0.9))
plane("wall", (40, 12), mat("wall", "#e9eef3", 0.9), (0, 4, 6), rot=(90, 0, 0))
sun((50, 10, 30), strength=2.5)
area((0, -6, 6), (50, 0, 0), size=8, power=900)
xs = [-3.6, -2.5, -0.7, 0.4, 2.2, 3.3]
for i, (cid, kidera, adultera) in enumerate([("gamer", "kid", "student"), ("hacker", "kid", "pro"),
                                             ("gears", "kid", "student")]):
    k = C.build(cid, kidera, (xs[2 * i], 0, 0), yaw=0)
    a = C.build(cid, adultera, (xs[2 * i + 1], 0, 0), yaw=-20)
    a.look(1, yaw=8)
    text(cid + "lbl", C.BIBLE[cid]["label"], 0.22, mat("ink", "#2c3e50"),
         ((xs[2*i] + xs[2*i+1]) / 2, -0.6, 0.02), rot=(0, 0, 0))
camera((0, -10.5, 1.6), (0, 0, 1.0), lens=38)
setup_render(os.path.dirname(out), res=res, samples=48)
bpy.context.scene.render.filepath = out
bpy.ops.render.render(write_still=True)
