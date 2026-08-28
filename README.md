# SimulationEnv

Chemistry lab bench simulation environment: a 1 m lead-screw linear rail with
a prismatic carriage, two OpenMANIPULATOR-X mounts, and the bench props
(waste bucket, beakers, cylinder holders, five reagent bottles).

The Blender scene is the single source of truth for geometry and layout;
the Gazebo models are generated from it.

![top view](drawings/bench_topview_dimensioned.png)

## Layout

Four zones, left to right, on a 1400 × 600 mm bench:

**① 폐기통 → ② 비커 ×2 → ③ 실린더 홀더 ×2 → ④ 시약 ×5**

Reagents are staggered: 3 in the front row, 2 in the rear.
Full coordinate tables are in [`docs/layout.md`](docs/layout.md).

World frame: **+X right, +Y back, +Z up**, metres, and **Z = 0 is the bench
surface**. Blender and Gazebo share the frame exactly — no axis conversion
anywhere in the pipeline.

## Repository

```
blender/
  lab_bench.blend              source scene
  scripts/build_layout.py      rebuild props + snap the layout (idempotent)
  scripts/render_topview.py    orthographic top render, 2 px/mm
  scripts/export_gazebo.py     scene -> gazebo/ models, meshes and world
drawings/
  draw_topview.py              dimensioned drawing from the top render
  topview.png                  top render (transparent background)
  bench_topview_dimensioned.png
gazebo/
  models/<name>/model.sdf      one model per prop / assembly
  models/<name>/meshes/*.obj   visual meshes (+ .mtl)
  worlds/lab_bench.world       the assembled bench
ros2/
  simulation_env_bringup/      launch + ros_gz_bridge config
docs/layout.md
```

## Running it

Tested against **Gazebo Sim (Harmonic)** with **ROS 2** and `ros_gz`.

### Gazebo on its own

```bash
export GZ_SIM_RESOURCE_PATH=$PWD/gazebo/models:$GZ_SIM_RESOURCE_PATH
gz sim -r gazebo/worlds/lab_bench.world
```

### With ROS 2

```bash
mkdir -p ~/ws/src && cd ~/ws/src
git clone https://github.com/armchemist/SimulationEnv.git
cd ~/ws
colcon build --packages-select simulation_env_bringup
source install/setup.bash
ros2 launch simulation_env_bringup lab_bench.launch.py
```

Drive the carriage (metres, ±0.42 from the rail centre):

```bash
ros2 topic pub --once /rail_axis/carriage_slide/cmd_pos \
    std_msgs/msg/Float64 "{data: 0.30}"
ros2 topic echo /rail_axis/joint_states
```

## Regenerating from Blender

```bash
# rebuild the props and snap the layout
blender blender/lab_bench.blend --background --python blender/scripts/build_layout.py

# re-export every Gazebo model, mesh and the world file
SIMENV_REPO=$PWD blender blender/lab_bench.blend --background \
    --python blender/scripts/export_gazebo.py

# redraw the dimensioned top view
blender blender/lab_bench.blend --background --python blender/scripts/render_topview.py
python drawings/draw_topview.py
```

`export_gazebo.py` writes visuals from the exported meshes but keeps
**collisions as primitives** (box / cylinder from the measured bounding
boxes) — mesh collisions are slow and unstable for small props. Masses and
inertias are analytic for those primitives; they are plausible, not weighed.

## Models

| Model | Collision | Mass (kg) | Notes |
|---|---|---:|---|
| `waste_bucket` | cylinder ⌀157 × 204 | 0.45 | |
| `beaker` | cylinder ⌀70 × 95 | 0.15 | spawned twice |
| `cylinder_holder` | box 165 × 50 × 80 | 0.25 | spawned twice, 6 slots |
| `reagent_bottle_h2o2` | box 75 × 58 × 172 | 0.55 | amber |
| `reagent_bottle_ethanol` | box 75 × 58 × 172 | 0.55 | amber |
| `reagent_bottle_solvent` | box 70 × 54 × 179 | 0.52 | dark |
| `reagent_bottle_acid` | box 73 × 56 × 187 | 0.60 | white |
| `reagent_bottle_naoh` | box 73 × 56 × 187 | 0.60 | white |
| `rail_axis` | composite | 6.8 | rail + carriage, prismatic X, ±0.42 m |
| `linear_rail` | box 1000 × 56 × 73 | 6.0 | mesh source for `rail_axis` |
| `rail_carriage` | box 80 × 60 × 62 | 0.8 | mesh source for `rail_axis` |
| `omx_mounting_plate` | box 395 × 140 × 6 | 1.2 | static |
| `omx_module` | box 150 × 375 × 277 | 1.5 | static visual placeholder |

`linear_rail` and `rail_carriage` are not placed in the world directly —
`rail_axis` references their meshes and adds the joint — but their model
directories must stay on `GZ_SIM_RESOURCE_PATH`.

## The arm

`omx_module` is a **single fused, decimated mesh (26k triangles)**. It is a
visual placeholder: it does not articulate and has no joints. For real
manipulation, drop the official OpenMANIPULATOR-X description in and delete
the two `omx_module` includes from `gazebo/worlds/lab_bench.world`. Mount
poses to reuse:

| | X | Y | Z |
|---|---:|---:|---:|
| left | −0.116527 | 0.074456 | 0.0735 |
| right | 0.108469 | 0.075270 | 0.0735 |

Z is the top face of `omx_mounting_plate`.

## License

Apache-2.0.
