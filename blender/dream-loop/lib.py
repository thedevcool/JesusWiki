"""Low-level helpers: primitives, materials, keyframes, camera, lights, render setup.

Everything is built procedurally with bmesh so scenes are 100% reproducible
from code (no .blend files to drift out of sync).
"""
import math
import bpy
import bmesh
from mathutils import Matrix, Vector

FPS = 24
EP_FRAMES = 96  # 4 seconds per episode


# --------------------------------------------------------------------------- #
# Scene reset / render settings
# --------------------------------------------------------------------------- #
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _MATS.clear()
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, EP_FRAMES
    sc.render.fps = FPS
    return sc


def setup_render(out_dir, res=(960, 540), samples=24, pct=100):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    cy = sc.cycles
    cy.device = "CPU"
    cy.samples = samples
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.05
    cy.max_bounces = 4
    cy.diffuse_bounces = 2
    cy.glossy_bounces = 2
    cy.transmission_bounces = 2
    cy.transparent_max_bounces = 4
    cy.use_denoising = True
    try:
        cy.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = pct
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = out_dir.rstrip("/") + "/f_"
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Punchy"
    except Exception:
        pass


# --------------------------------------------------------------------------- #
# Colour + materials
# --------------------------------------------------------------------------- #
def srgb(h):
    """'#rrggbb' -> linear RGBA tuple."""
    h = h.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


_MATS = {}


def mat(name, color, rough=0.55, metal=0.0, emit=0.0, emit_color=None):
    key = name
    if key in _MATS:
        return _MATS[key]
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    p = m.node_tree.nodes.get("Principled BSDF")
    col = srgb(color) if isinstance(color, str) else color
    p.inputs["Base Color"].default_value = col
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if emit:
        ec = emit_color if emit_color is not None else col
        ec = srgb(ec) if isinstance(ec, str) else ec
        p.inputs["Emission Color"].default_value = ec
        p.inputs["Emission Strength"].default_value = emit
    m.diffuse_color = col
    _MATS[key] = m
    return m


def emissive(name, color, strength=3.0):
    return mat(name, color, rough=0.4, emit=strength, emit_color=color)


def key_mat_emission(m, frame, color=None, strength=None):
    p = m.node_tree.nodes.get("Principled BSDF")
    if color is not None:
        c = srgb(color) if isinstance(color, str) else color
        p.inputs["Emission Color"].default_value = c
        p.inputs["Emission Color"].keyframe_insert("default_value", frame=frame)
        p.inputs["Base Color"].default_value = c
        p.inputs["Base Color"].keyframe_insert("default_value", frame=frame)
    if strength is not None:
        p.inputs["Emission Strength"].default_value = strength
        p.inputs["Emission Strength"].keyframe_insert("default_value", frame=frame)


# --------------------------------------------------------------------------- #
# Objects
# --------------------------------------------------------------------------- #
def _link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def empty(name, loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    o = bpy.data.objects.new(name, None)
    o.empty_display_size = 0.1
    _link(o)
    place(o, loc, parent, rot)
    return o


def place(o, loc=(0, 0, 0), parent=None, rot=(0, 0, 0), scale=None):
    if parent is not None:
        o.parent = parent
        o.matrix_parent_inverse = Matrix.Identity(4)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    if scale is not None:
        o.scale = scale if hasattr(scale, "__len__") else (scale,) * 3
    return o


def _mesh_obj(name, bm, material, smooth=True):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    o = bpy.data.objects.new(name, me)
    if material is not None:
        o.data.materials.append(material)
    return _link(o)


def sphere(name, r, material, loc=(0, 0, 0), parent=None, scale=None, rot=(0, 0, 0), seg=24,
           cut=None):
    """UV sphere. `cut(x,y,z)->bool` on unit-sphere coords deletes verts (for hair caps)."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(8, seg // 2), radius=r)
    if cut:
        dead = [v for v in bm.verts if cut(v.co.x / r, v.co.y / r, v.co.z / r)]
        bmesh.ops.delete(bm, geom=dead, context="VERTS")
    o = _mesh_obj(name, bm, material)
    return place(o, loc, parent, rot, scale)


def box(name, size, material, loc=(0, 0, 0), parent=None, rot=(0, 0, 0), bevel=0.0, smooth=False):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    o = _mesh_obj(name, bm, material, smooth=smooth)
    if bevel:
        md = o.modifiers.new("bev", "BEVEL")
        md.width = bevel
        md.segments = 3
        md.limit_method = "NONE"
        if smooth is False:
            for poly in o.data.polygons:
                poly.use_smooth = True
    return place(o, loc, parent, rot)


def cyl(name, r, depth, material, loc=(0, 0, 0), parent=None, rot=(0, 0, 0), r2=None, seg=20,
        smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r,
                          radius2=r if r2 is None else r2, depth=depth)
    o = _mesh_obj(name, bm, material, smooth=smooth)
    if smooth:
        o.data.polygons.foreach_set("use_smooth", [True] * len(o.data.polygons))
    return place(o, loc, parent, rot)


def torus(name, R, r, material, loc=(0, 0, 0), parent=None, rot=(0, 0, 0), seg=32, rseg=10,
          arc=(0.0, 360.0)):
    """Torus (or arc of one) in the XY plane."""
    bm = bmesh.new()
    a0, a1 = map(math.radians, arc)
    full = abs(a1 - a0) >= 2 * math.pi - 1e-6
    n = seg if full else seg + 1
    rings = []
    for i in range(n):
        u = a0 + (a1 - a0) * i / seg
        ring = []
        for j in range(rseg):
            w = 2 * math.pi * j / rseg
            x = (R + r * math.cos(w)) * math.cos(u)
            y = (R + r * math.cos(w)) * math.sin(u)
            z = r * math.sin(w)
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)
    pairs = [(i, (i + 1) % n) for i in range(n if full else n - 1)]
    for i, k in pairs:
        for j in range(rseg):
            jj = (j + 1) % rseg
            bm.faces.new((rings[i][j], rings[k][j], rings[k][jj], rings[i][jj]))
    if not full:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    o = _mesh_obj(name, bm, material)
    return place(o, loc, parent, rot)


def plane(name, size, material, loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    bm = bmesh.new()
    sx, sy = size
    vs = [bm.verts.new((x * sx / 2, y * sy / 2, 0)) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    bm.faces.new(vs)
    o = _mesh_obj(name, bm, material, smooth=False)
    return place(o, loc, parent, rot)


def text(name, body, size, material, loc=(0, 0, 0), parent=None, rot=(90, 0, 0), extrude=0.01,
         align="CENTER"):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.align_x = align
    cu.align_y = "CENTER"
    o = bpy.data.objects.new(name, cu)
    o.data.materials.append(material)
    _link(o)
    return place(o, loc, parent, rot)


# --------------------------------------------------------------------------- #
# Keyframes
# --------------------------------------------------------------------------- #
def key(o, frame, loc=None, rot=None, scale=None):
    if loc is not None:
        o.location = loc
        o.keyframe_insert("location", frame=frame)
    if rot is not None:
        o.rotation_euler = [math.radians(a) for a in rot]
        o.keyframe_insert("rotation_euler", frame=frame)
    if scale is not None:
        o.scale = scale if hasattr(scale, "__len__") else (scale,) * 3
        o.keyframe_insert("scale", frame=frame)


def key_axis(o, frame, path, idx, value, deg=False):
    getattr(o, path)[idx] = math.radians(value) if deg else value
    o.keyframe_insert(path, index=idx, frame=frame)


def show_between(objs, f_on, f_off=None):
    """Visible only in [f_on, f_off). Applies to whole hierarchy."""
    if not isinstance(objs, (list, tuple)):
        objs = [objs]
    allo = []
    for o in objs:
        allo.append(o)
        allo.extend(o.children_recursive)
    for o in allo:
        for f, hidden in ((1, f_on > 1), (f_on, False)):
            o.hide_render = hidden
            o.keyframe_insert("hide_render", frame=f)
        if f_off is not None:
            o.hide_render = True
            o.keyframe_insert("hide_render", frame=f_off)


def pop_in(o, frame, dur=6, final=1.0):
    s = final if hasattr(final, "__len__") else (final,) * 3
    key(o, 1, scale=(0.001,) * 3)
    key(o, frame, scale=(0.001,) * 3)
    key(o, frame + dur, scale=tuple(v * 1.15 for v in s))
    key(o, frame + dur + 3, scale=s)


def pop_out(o, frame, dur=5, final=1.0):
    s = final if hasattr(final, "__len__") else (final,) * 3
    key(o, frame, scale=s)
    key(o, frame + 2, scale=tuple(v * 1.15 for v in s))
    key(o, frame + dur, scale=(0.001,) * 3)


# --------------------------------------------------------------------------- #
# Camera, lights, world
# --------------------------------------------------------------------------- #
def camera(loc, target, lens=40):
    cd = bpy.data.cameras.new("Cam")
    cd.lens = lens
    cam = bpy.data.objects.new("Cam", cd)
    _link(cam)
    cam.location = loc
    tgt = empty("CamTarget", target)
    c = cam.constraints.new("TRACK_TO")
    c.target = tgt
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    bpy.context.scene.camera = cam
    return cam, tgt


def sun(rot, color="#ffffff", strength=3.0, angle=5):
    ld = bpy.data.lights.new("Sun", "SUN")
    ld.energy = strength
    ld.color = srgb(color)[:3]
    ld.angle = math.radians(angle)
    o = bpy.data.objects.new("Sun", ld)
    _link(o)
    o.rotation_euler = [math.radians(a) for a in rot]
    return o


def area(loc, rot, size=4, color="#ffffff", power=300):
    ld = bpy.data.lights.new("Area", "AREA")
    ld.energy = power
    ld.size = size
    ld.color = srgb(color)[:3]
    o = bpy.data.objects.new("Area", ld)
    _link(o)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    return o


def point(loc, color="#ffffff", power=100, radius=0.2):
    ld = bpy.data.lights.new("Point", "POINT")
    ld.energy = power
    ld.color = srgb(color)[:3]
    ld.shadow_soft_size = radius
    o = bpy.data.objects.new("Point", ld)
    _link(o)
    o.location = loc
    return o


def world(color, strength=1.0):
    w = bpy.data.worlds.new("World")
    try:
        w.use_nodes = True
    except Exception:
        pass
    bg = w.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = srgb(color) if isinstance(color, str) else color
    bg.inputs["Strength"].default_value = strength
    bpy.context.scene.world = w
    return w
