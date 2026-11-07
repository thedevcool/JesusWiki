# The Dream Loop — a 10-episode Blender micro-series

A ~40-second animated loop (10 episodes × 4 s), modelled, lit, animated and
rendered entirely from Python with **Blender** (Cycles), no hand-made `.blend`
files. Episode 10 dives into a thought bubble that turns white, and episode 1
fades in from white, so the video loops back on itself.

| # | Title | Beat |
|---|-------|------|
| 1 | The Dream | Three kids on a bench: game dev 🎮, mechanical engineer ⚙️, lawyer ⚖️ |
| 2 | Plot Twist | "Lawyer? Nah, I'll be a **HACKER**!" (just for fun) |
| 3 | Friendly Terror | The game dev's screen: `HACKED :)` |
| 4 | Help Desk | The game dev is stuck, so the "hacker" fixes it: `BUG!` → `FIXED!` |
| 5 | The Grind | 6 years: calendar ticks, day/night, coffee mugs pile up |
| 6 | Backend Boss | Server room: **BACKEND DEVELOPER** |
| 7 | Still Studying | Computer Science & Mechanical Engineering, books stacking up |
| 8 | Sundays | 3 years on, the two meet at church |
| 9 | Almost There | Progress bars at ~95%; graduation caps hover, still learning |
| 10 | The Lead | Lead software engineer. Still not a hacker… yet → loop |

## Locked characters

`characters.py` is the **character bible**. Every physical trait (skin tone,
head shape, eye spacing/size, brow angle, nose, ears, hair style, height, build
and signature accessory) lives in one `BIBLE` dict and is reused by every
episode, so faces can't drift. Only outfits change with the era (kid → student
→ pro → lead), and those are defined in the bible too.

| Character | Locked look |
|-----------|-------------|
| **The Game Dev** | tall & slim, long head, high-top hair, green, *headphones always on* |
| **The Mech Engineer** | short & broad, wide head, buzz cut, orange, overalls (+ hard hat) |
| **The "Hacker"** | medium, oval head, side-part with swoop, black/purple, *glasses always on* |

Kids use the same head at 90% scale on a 64% body, so they're recognisably
the same people when they grow up.

![model sheet](character_sheet.png)

## Files

- `lib.py`: primitives (bmesh), materials, keyframe helpers, camera/lights, render settings
- `characters.py`: the locked character bible + builder + animation verbs (walk, sit, type, talk, wave…)
- `sets.py`: places (street & bench, bedrooms, grind desk, server room, library, church, campus, office) and props
- `episodes.py`: the 10 episodes
- `charsheet.py`: renders the model sheet
- `render_all.sh`: renders episodes to PNG frames
- `assemble.sh`: ffmpeg captions + episode badges → `dream_loop.mp4`

## Rebuild

```bash
pip install bpy==5.2.3           # Blender as a Python module (or use blender --background --python)
PY=python3 ./render_all.sh frames 960x540 10     # ~1 h on 4 CPU cores
./assemble.sh frames out                          # -> out/dream_loop.mp4
python3 charsheet.py --out character_sheet.png
```

Preview a single frame of an episode quickly:

```bash
python3 episodes.py --ep 3 --out /tmp/ep3 --still 1,48,90 --res 640x360 --samples 8
```
