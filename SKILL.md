---
name: cadquery-ai-skill-archive
description: >-
  Archived: Early CadQuery AI skill prototype. For active CadQuery development, use the main
  'cadquery' skill from jmwright/cadquery-llm-skill.
---

# CadQuery AI Skill

CadQuery is an intuitive, easy-to-use Python module for building parametric 3D CAD models. This skill distills the essential API concepts and domain-specific rules required to write accurate CadQuery scripts.

## 1. Top-Level API & Topology
CadQuery wraps the OpenCASCADE (OCCT) geometry kernel. The primary topological concepts are:
- **Vertex**: A single point in space.
- **Edge**: A connection between two or more vertices along a curve.
- **Wire**: A collection of connected edges.
- **Face**: A set of edges/wires enclosing a surface.
- **Solid**: A collection of faces that enclose an interior volume.

The API is primarily interacted with via the **Fluent API** (the `Workplane` object). 

## 2. Coordinate Spaces & Orientation (CRITICAL)

### 2.1 Three spaces, one axis convention
Three coordinate spaces matter when designing a printed part:

| Space | What it is |
|---|---|
| **Build Space** | The coordinates the CadQuery script works in. |
| **User Space** | The part as it sits when in use (mounted on a wall, on a bench, etc.). |
| **Print Space** | The part as it sits on the print bed, rotated for strength and to need fewer supports. |

**Rules:**
1. All three spaces use the CAD standard: **+X = right, +Y = rear (away from the viewer), +Z = up.**
2. **Build Space and User Space are the same.** Model the part exactly as it will be used. Never model it lying in its print orientation.
3. **The rotation from Build Space to Print Space is the LAST operation in the script.** Never rotate partway through a build. Every selector, workplane and feature before that rotation means a user-space direction.

### 2.2 Shared vocabulary
Positional words always refer to User Space (= Build Space):

| Word | Direction | Face selector |
|---|---|---|
| right / left | +X / −X | `">X"` / `"<X"` |
| rear (back) / front | +Y / −Y | `">Y"` / `"<Y"` |
| top / bottom | +Z / −Z | `">Z"` / `"<Z"` |

Edges and corners combine these words. The **front-right edge** is the vertical edge at max X and min Y:
```python
body.edges("|Z and >X and <Y")   # front-right vertical edge
body.edges("|X and >Z and <Y")   # top-front horizontal edge
```

### 2.3 Workplane quirks
When defining a CadQuery workplane, always use positive forward cyclic loops ("XY", "YZ", "ZX"). Do NOT use "XZ", as the right-hand cross product ($X \times Z = -Y$) forces the normal (Local Z) to point in the negative global Y direction, causing extrusions and boolean cuts to travel backwards.

Verified local axes of the named planes:

| Plane | Local x | Local y | Normal (extrude direction) | Use |
|---|---|---|---|---|
| `"XY"` | +X | +Y | **+Z** | top/bottom sketches |
| `"YZ"` | +Y | +Z | **+X** | left/right side sketches |
| `"ZX"` | **+Z** | **+X** | **+Y** | front/rear sketches (**required** instead of `"XZ"`) |
| `"XZ"` | +X | +Z | **−Y** | **FORBIDDEN** |

> [!WARNING]
> **`"ZX"` swaps the 2D sketch axes.** On a `"ZX"` workplane, local x is global **Z** and local y is global **X**. So every 2D coordinate is written `(z, x)`:
> - `.center(z, x)`, `.moveTo(z, x)`, `.lineTo(z, x)`, `.pushPoints([(z, x), ...])`
> - `.rect(height_along_Z, width_along_X)`
>
> This cannot be avoided: no right-handed plane has local x = +X, local y = +Z and a +Y normal. Put a comment such as `# local (z, x)` on every `"ZX"` sketch line.

- `.workplane(offset=d)` moves the plane along its normal. On `"ZX"`, `offset=-10` puts the plane at y = −10 (the front face of a part 20 deep, centered on the origin).
- `.transformed(offset=...)` is in **local** coordinates. On `"ZX"` that means `(z, x, y)`.

### 2.4 Canonical script structure
```python
import cadquery as cq

# ===== Build Space (== User Space): +X right, +Y rear, +Z up =====
body = cq.Workplane("XY").box(40, 20, 30)          # 40 wide (X), 20 deep (Y), 30 tall (Z)

# Front-face pocket: sketch on "ZX" at the front face and extrude toward +Y (into the part)
pocket = (
    cq.Workplane("ZX")
    .workplane(offset=-10)   # plane at y = -10 (front face)
    .center(5, 0)            # local (z, x): z = 5, x = 0
    .rect(10, 6)             # 10 along Z, 6 along X
    .extrude(5)              # +Y: y = -10 -> -5
)
body = body.cut(pocket)
body = body.edges("|Z and >X and <Y").fillet(2)    # front-right vertical edge

# ===== LAST STEP: Build Space -> Print Space =====
printable = body.rotate((0, 0, 0), (0, 1, 0), 90)  # right-down
cq.exporters.export(printable, "part.stl")
```
Keep `body` (Build/User Space) for previews, assemblies and STEP export. Only the print file gets rotated.

### 2.5 Print orientations (verified)
Each rotation is about the origin, applied once at the end of the script:

| Orientation | Face on the bed | Rotation |
|---|---|---|
| right-down | right (+X) | `.rotate((0,0,0), (0,1,0), 90)` |
| left-down | left (−X) | `.rotate((0,0,0), (0,1,0), -90)` |
| front-down | front (−Y) | `.rotate((0,0,0), (1,0,0), 90)` |
| rear-down | rear (+Y) | `.rotate((0,0,0), (1,0,0), -90)` |
| top-down (flipped) | top (+Z) | `.rotate((0,0,0), (0,1,0), 180)` |
| as-used | bottom (−Z) | none |

After rotating, the part may sit below or off the bed origin. Slicers normally drop the part onto the bed. If you need it there in the file, add a `.translate(...)` right after the rotation.

## 3. The Fluent API (`Workplane`)

A `Workplane` represents a 2D modeling context in a 3D space. Most CadQuery operations are chained from it.

### Creating and Moving Workplanes
- `cq.Workplane("XY")`: Start a base plane.
- `.workplane(offset=X)`: Create a new workplane parallel to the current one, offset by `X`.
- `.transformed(offset=(x, y, z), rotate=(rx, ry, rz))`: Transform the workplane coordinates.
- `.center(x, y)`: Shift the local center of the current workplane by `x` and `y`.

### 2D Sketching Operations
- `.rect(x, y)`: Draw a rectangle of width `x` and height `y`.
- `.circle(r)`: Draw a circle of radius `r`.
- `.lineTo(x, y)` / `.move(x, y)`: Draw lines or move the cursor.
- `.polygon(n, d)`: Draw an n-sided regular polygon.
- `.slot2D(length, width)`: Draw a 2D slot.

### 3D Operations
- `.extrude(distance)`: Extrudes a 2D sketch into a 3D solid.
- `.cutBlind(distance)`: Cuts into a solid by `distance`.
- `.cutThruAll()`: Cuts all the way through the object.
- `.loft(ruled=False)`: Creates a solid by lofting between 2 or more sketches.
- `.revolve(angle=360)`: Revolves a sketch around an axis.

## 4. Selectors and Filtering

CadQuery's power comes from string-based selectors used to pick faces, edges, and vertices for subsequent operations. Directions follow Section 2 (+X right, +Y rear, +Z up).

- `>Z` / `<Z`: Object farthest in +Z / −Z (top / bottom).
- `>X` / `<X`: Right / left.
- `>Y` / `<Y`: Rear / front.
- `|Z`: **Edges** parallel to Z (vertical edges), or **faces whose normal** is parallel to Z (horizontal faces such as top and bottom, *not* walls).
- `#Z`: Edges perpendicular to Z, or faces whose normal is perpendicular to Z (vertical walls).
- `+Z` / `-Z`: Faces whose normal points in +Z / −Z.
- `%Plane`, `%Cylinder`, `%Line`, `%Circle`: Select by geometry type.
- `>Z[1]` / `>>Z[-2]`: Nth selection by direction / by center position (indexing).
- Combine with `and`, `or`, `not`, `exc`, e.g. `"|Z and >X and <Y"`.
- Non-linear edges are only matched by type (`%`) and center (`>>`/`<<`) selectors.

**Usage Example:**
```python
# Fillet all vertical edges
result = cq.Workplane("XY").box(10, 10, 10).edges("|Z").fillet(2)

# Select the top face and sketch a hole
result = result.faces(">Z").workplane().circle(3).cutThruAll()
```

## 5. Assemblies

Assemblies allow combining multiple `Workplane` shapes into a single hierarchical structure.

```python
import cadquery as cq

part1 = cq.Workplane("XY").box(10, 10, 10)
part2 = cq.Workplane("XY").cylinder(10, 5)

assy = (
    cq.Assembly(part1, name="base", loc=cq.Location(cq.Vector(0, 0, 0)))
    .add(part2, name="peg", color=cq.Color("red"))
    .constrain("base@faces@>Z", "peg@faces@<Z", "Axis")
    .solve()
)
```

Constraints like `Axis`, `Point`, and `Plane` can automatically position geometry without explicit vector math.

### 5.1 Multi-Piece Woodworking & Assembly Rules

When modeling projects that involve woodworking, cabinetry, or multi-board timber structures:

- **Distinct Components:** Do **NOT** fuse touching wooden boards into a single boolean `union()`. Model each board, stringer, slat, or cleat as an individual solid and assemble them using `cq.Assembly()` or `cq.Compound.makeCompound()`. This preserves individual board geometry, bill-of-materials cut lists, and realistic part separation.
- **Visual Seam Chamfers:** In visual renders with `show_hidden: false`, touching coplanar faces of identical color will blend seamlessly, making individual boards indistinguishable. Add a small (**0.5 mm to 1.0 mm**) chamfer to the edges of each board before assembling. Where two boards butt together, the chamfers form a clean V-groove shadow line that clearly delineates individual components in renders.

```python
# Example: Creating a wooden board with a subtle shadow-line chamfer
board = cq.Workplane("XY").box(300, 90, 19).edges().chamfer(0.8)
```

## 6. Exporting

Models can be exported to standard formats for 3D printing (STL) or generic CAD (STEP).
```python
cq.exporters.export(result, "my_part.step")
cq.exporters.export(result, "my_part.stl")
```

## 7. CadQuery MCP Server & Verification Best Practices

When using the `cadquery` MCP server (`render`, `inspect`, `export`) to visualize and verify models, adhere to the following rules:

### 7.1 Visual Verification Protocol (`render`)
The MCP `render` tool executes Python code and returns headless visual renders directly into the agent's multimodal context:
- **Hide cluttered wireframes:** Always pass `show_hidden: false` to remove internal wireframe clutter.
- **Multi-view verification:** Always pass `multi_view: true` to generate 4 perspectives simultaneously (**Isometric, Front, Top, Right**) for thorough visual validation.
- **Output assignment:** Always assign the target geometry to `result` (e.g. `result = cq.Workplane(...)...`) or call `show_object(shape)`.
- **Recommended dimensions:** `width: 1024`, `height: 768`.

### 7.2 Geometric Inspection (`inspect`)
Visual renders alone can obscure sub-millimeter alignment errors or tolerance mismatches. Use the `inspect` tool to confirm:
- Bounding box dimensions (`xmin..xmax`, `ymin..ymax`, `zmin..zmax`) and overall spans (`xlen`, `ylen`, `zlen`).
- Model symmetry, volume, surface area, and center of mass.

### 7.3 Isolated MCP Environment & Imports
The MCP server runs in its own isolated Python environment. Whenever executing script snippets that import packages or modules from the current repository, prepend:
```python
import sys
sys.path.insert(0, ".")  # or absolute workspace path
```

### 7.4 Stdio Protocol Rule (CRITICAL: Never Use `print`)
> [!CAUTION]
> **NEVER include `print(...)` statements in CadQuery scripts executed through the MCP server.**
> The MCP server communicates with Antigravity via standard I/O (`stdio`) using JSON-RPC. Any raw stdout output emitted by user code corrupts the JSON-RPC stream, causing the tool call to fail or time out.

### 7.5 Parametric Design & Unit Testing
- Ensure all models are fully parametric, with dimensions parameterized at the top of the script or function.
- Test models with unit tests validating critical dimensions, tolerances, and bounding boxes.
