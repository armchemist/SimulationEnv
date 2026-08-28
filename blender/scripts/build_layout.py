"""Rebuild the lab-bench prop layout in Blender.

Idempotent: re-running deletes and recreates the waste bucket, then snaps
every prop back to the coordinates below. Nothing else in the scene is
touched.

    blender lab_bench.blend --background --python blender/scripts/build_layout.py --save

or, with the scene open, from the Scripting workspace:

    exec(open(r"<repo>/blender/scripts/build_layout.py").read())

Bench surface is Z = 0, the display floor spans X -700..700 and
Y -194.6..405.4 mm. Props are laid out left to right in four zones:

    ① waste bucket  ② beaker x2  ③ cylinder holder x2  ④ reagent x5

Zone gaps are 48 | 96 | 96 | 96 | 48 mm and total exactly 1400 mm.
"""

import bpy
from mathutils import Vector

PROP_COLLECTION = "lab_scene"

# name -> (x, y, z) in metres
LAYOUT = {
    # ① 폐기통
    "Waste_Bucket":            (-0.5735, 0.320, 0.0),
    # ② 비커 x2, 피치 90 mm
    "beaker_01":               (-0.3640, 0.330, 0.0),
    "beaker_02":               (-0.2740, 0.330, 0.0),
    # ③ 실린더 홀더 x2, 피치 180 mm (틈 15 mm)
    "rack_01":                 (-0.0605, 0.330, 0.0),
    "rack_02":                 ( 0.1195, 0.330, 0.0),
    # ④ 시약 x5, 열 피치 70 mm, 지그재그 앞 3 / 뒤 2
    "Chemical_Bottle_H2O2":    ( 0.3355, 0.295, 0.0),
    "Chemical_Bottle_ETHANOL": ( 0.4055, 0.365, 0.0),
    "Chemical_Bottle_SOLVENT": ( 0.4755, 0.295, 0.0),
    "Chemical_Bottle_ACID":    ( 0.5455, 0.365, 0.0),
    "Chemical_Bottle_NAOH":    ( 0.6155, 0.295, 0.0),
}

BUCKET_PARTS = ("Waste_Bucket", "Waste_Bucket_Body",
                "Waste_Bucket_Opening", "Waste_Bucket_Rim")


def build_waste_bucket():
    """Tapered bucket, ⌀130 (bottom) -> ⌀150 (top), H200, red rim."""
    coll = bpy.data.collections[PROP_COLLECTION]
    for n in BUCKET_PARTS:
        o = bpy.data.objects.get(n)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)

    def relink(o):
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)

    root = bpy.data.objects.new("Waste_Bucket", None)
    root.empty_display_size = 0.05
    coll.objects.link(root)

    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=0.065, radius2=0.075,
                                    depth=0.20, location=(0, 0, 0.10))
    body = bpy.context.active_object
    body.name = "Waste_Bucket_Body"
    relink(body)

    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.068, depth=0.004,
                                        location=(0, 0, 0.199))
    opening = bpy.context.active_object
    opening.name = "Waste_Bucket_Opening"
    relink(opening)

    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=10,
                                     major_radius=0.0745, minor_radius=0.004,
                                     location=(0, 0, 0.200))
    rim = bpy.context.active_object
    rim.name = "Waste_Bucket_Rim"
    relink(rim)

    for ob, mat in ((body, "Mat_Lab_White_Plastic"),
                    (opening, "Mat_Lab_Dark_Plastic"),
                    (rim, "Mat_Lab_Label_Red")):
        ob.data.materials.clear()
        ob.data.materials.append(bpy.data.materials[mat])
        ob.parent = root
        ob.matrix_parent_inverse.identity()
    return root


def apply_layout():
    for name, loc in LAYOUT.items():
        bpy.data.objects[name].location = loc
    bpy.context.view_layer.update()


def report():
    def bbox(o):
        obs = [o] + list(o.children_recursive) if o.type == "EMPTY" else [o]
        pts = [ob.matrix_world @ Vector(c)
               for ob in obs if ob.type == "MESH" for c in ob.bound_box]
        return (min(p.x for p in pts) * 1000, max(p.x for p in pts) * 1000)

    zones = [("① waste",   ["Waste_Bucket"]),
             ("② beaker",  ["beaker_01", "beaker_02"]),
             ("③ holder",  ["rack_01", "rack_02"]),
             ("④ reagent", [n for n in LAYOUT if n.startswith("Chemical")])]
    prev = -700.0
    for label, names in zones:
        spans = [bbox(bpy.data.objects[n]) for n in names]
        lo = min(s[0] for s in spans)
        hi = max(s[1] for s in spans)
        print("%-11s X %8.1f ~ %8.1f   span %6.1f   gap %5.1f"
              % (label, lo, hi, hi - lo, lo - prev))
        prev = hi
    print("%-11s                              gap %5.1f" % ("right edge", 700.0 - prev))


if __name__ == "__main__" or True:
    build_waste_bucket()
    apply_layout()
    report()
