# Isaac Sim / USD — running notes & glossary

Our growing reference for what the code actually *means*. Add to it as we hit new things.

## The core idea: USD, the "scene document"

Isaac Sim's 3D world is a **USD stage**. USD (Universal Scene Description, from Pixar) is
basically a document format for 3D scenes — think of it like the HTML/DOM of a webpage, but for
a 3D world. Everything you build (cameras, lights, the turret, joints) is a node in that document.

## Vocabulary (learn these 5 words and the file unlocks)

- **Stage** — the whole scene document. The tree of every object in the world. `world.stage`.
- **Prim** (primitive) — ONE node in that tree: a cube, a light, a joint, a grouping transform.
  Everything on the stage is a prim. Each has a **path** like `/World/Turret/base` (just like a
  file path — parent/child structure).
- **Schema** — a "type" or "interface" that says what data a prim carries. Two flavors:
  - **Typed schema** = WHAT a prim *is*. `UsdGeom.Cube`, `UsdPhysics.RevoluteJoint`. You make one
    with `.Define(stage, path)`.
  - **API schema** = a capability you *bolt onto* an existing prim. `UsdPhysics.RigidBodyAPI`,
    `UsdPhysics.CollisionAPI`. You add it with `.Apply(prim)`. You can stack several on one prim.
- **Attribute** — a piece of data on a prim (radius, position, mass, stiffness). Set with
  `.CreateXxxAttr(value)`.
- **Relationship** (`...Rel`) — a typed *pointer* from one prim to another. A joint points at the
  two bodies it connects. Set with `.CreateXxxRel().SetTargets([path])`.

## The 4 repeating patterns (this IS the API)

| You see... | It means... |
|---|---|
| `SomeType.Define(stage, "/path")` | create a prim of that type at that path |
| `SomeAPI.Apply(prim)` | bolt an extra capability onto an existing prim |
| `prim.CreateXxxAttr(value)` | set a data attribute (radius, mass, axis, …) |
| `prim.CreateXxxRel().SetTargets([p])` | make this prim point at another prim `p` |

Read almost any line in our scene scripts through this table and it becomes a sentence.

## Worked example — decoding real lines from phase1_step1_pan.py

```python
base = UsdGeom.Cylinder.Define(stage, "/World/Turret/base")
```
"Create a **cylinder** prim named `base` under `/World/Turret`." (Define = make a typed prim.)

```python
UsdPhysics.RigidBodyAPI.Apply(base.GetPrim())
```
"**Bolt on** the rigid-body capability, so physics now treats this cylinder as a solid movable
mass." (Apply = add an API schema. `.GetPrim()` hands the raw prim to the API.)

```python
revolute.CreateBody0Rel().SetTargets([base.GetPrim().GetPath()])
```
"This joint's **body0 pointer** targets the `base` prim." (A relationship: joint -> body it hinges.)

```python
revolute.CreateAxisAttr("Z")
```
"Set this joint's **axis attribute** to Z." (An attribute: the hinge spins about Z.)

## Physics capabilities — two you bolt onto a body

Both are API schemas you `.Apply(...)`. They're different and often used together:
- **`UsdPhysics.RigidBodyAPI`** — "this is a movable mass": has weight/momentum, obeys forces.
- **`UsdPhysics.CollisionAPI`** — "this has a solid surface": can bump/rest against other bodies
  instead of passing through them.
A solid object usually gets both. A pure viewpoint (a camera) may get neither.

Also note: `UsdPhysics` and `UsdGeom` are **libraries** (boxes of many schemas), not single
schemas. `UsdGeom.Cube`, `UsdPhysics.CollisionAPI` etc. are the individual schemas inside them.

## Transform ops — how a prim gets positioned/scaled

- A prim that can be moved is **`Xformable`**. `UsdGeom.Xformable(prim)` wraps it so you can add
  transforms.
- `.AddTranslateOp().Set((x, y, z))` — place it (position, in meters).
- `.AddScaleOp().Set((sx, sy, sz))` — stretch it (e.g. turn a unit cube into a thin bar).

## Python bits we've met

- **Assignment** `NAME = value` — store a value under a name.
- **Constant convention** — `UPPER_CASE` names mean "treat as constant" (Python doesn't enforce it).
- **Tuple** `(a, b)` — an ordered, immutable pair, e.g. `(min, max)` or `(width, height)`.
- **int vs float** — `1280` (whole count) vs `180.0` (continuous). Different types; some APIs care.
- **f-string** `f"x = {value}"` — a string with `{...}` slots filled by variables at runtime.
- **Line continuation** — a line can wrap freely inside `(`, `[`, `{`. Use that to stay under 80.
