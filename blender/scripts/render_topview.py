"""Render an orthographic top view of the bench, on a transparent background.

The output is the underlay for drawings/draw_topview.py. The camera covers
exactly the display floor: X -700..700, Y -194.6..405.4 mm, rendered at
2800 x 1200 px, i.e. 2 px/mm — so image pixels map to millimetres exactly.

    blender lab_bench.blend --background --python blender/scripts/render_topview.py

Scene settings (camera, engine, resolution, hidden objects) are restored
afterwards, so this is safe to run against a scene you are working in.
"""

import bpy
import os

OUT = os.environ.get(
    "SIMENV_TOPVIEW",
    os.path.join(os.path.dirname(bpy.data.filepath) or ".",
                 "..", "drawings", "topview.png"))

# display floor extents, metres
X0, X1 = -0.700, 0.700
Y0, Y1 = -0.1946, 0.4054
PX_PER_M = 2000.0                       # 2 px per mm

HIDE = ["Rail_Display_Floor", "wall_front", "wall_right", "wall_right.001"]
HIDE_COLLECTION = "Top_View_Blueprint"


def main():
    sc = bpy.context.scene
    saved = dict(cam=sc.camera, engine=sc.render.engine, fp=sc.render.filepath,
                 rx=sc.render.resolution_x, ry=sc.render.resolution_y,
                 pct=sc.render.resolution_percentage,
                 ff=sc.render.image_settings.file_format,
                 cm=sc.render.image_settings.color_mode,
                 film=sc.render.film_transparent)

    cam_data = bpy.data.cameras.new("TMP_TopOrtho")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = X1 - X0
    cam = bpy.data.objects.new("TMP_TopOrtho", cam_data)
    sc.collection.objects.link(cam)
    cam.location = ((X0 + X1) / 2, (Y0 + Y1) / 2, 3.0)
    cam.rotation_euler = (0.0, 0.0, 0.0)
    sc.camera = cam

    hidden = []
    for n in HIDE:
        o = bpy.data.objects.get(n)
        if o:
            hidden.append((o, o.hide_render))
            o.hide_render = True
    lc = bpy.context.view_layer.layer_collection.children.get(HIDE_COLLECTION)
    lc_saved = lc.exclude if lc else None
    if lc:
        lc.exclude = True

    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh_saved = (sh.light, sh.color_type, sh.show_cavity, sh.show_object_outline)
    sh.light = "STUDIO"
    sh.color_type = "MATERIAL"
    sh.show_cavity = True
    sh.show_object_outline = True
    sc.display.render_aa = "32"
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.resolution_x = int(round((X1 - X0) * PX_PER_M))
    sc.render.resolution_y = int(round((Y1 - Y0) * PX_PER_M))
    sc.render.resolution_percentage = 100
    sc.render.filepath = os.path.abspath(OUT)
    bpy.ops.render.render(write_still=True)

    sh.light, sh.color_type, sh.show_cavity, sh.show_object_outline = sh_saved
    for o, v in hidden:
        o.hide_render = v
    if lc:
        lc.exclude = lc_saved
    sc.camera = saved["cam"]
    sc.render.engine = saved["engine"]
    sc.render.filepath = saved["fp"]
    sc.render.resolution_x, sc.render.resolution_y = saved["rx"], saved["ry"]
    sc.render.resolution_percentage = saved["pct"]
    sc.render.image_settings.file_format = saved["ff"]
    sc.render.image_settings.color_mode = saved["cm"]
    sc.render.film_transparent = saved["film"]
    bpy.data.objects.remove(cam, do_unlink=True)
    bpy.data.cameras.remove(cam_data)

    print("rendered", sc.render.resolution_x, "x", sc.render.resolution_y,
          "->", os.path.abspath(OUT))


main()
