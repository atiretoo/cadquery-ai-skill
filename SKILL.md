---
name: CadQuery Maintainer
description: Core syntax, patterns, and coordinate system rules for generating precise CadQuery 3D models.
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

## 2. Coordinate System Quirks (CRITICAL)

When defining a CadQuery workplane, always use positive forward cyclic loops ("XY", "YZ", "ZX"). Do NOT use "XZ", as the right-hand cross product ($X \times Z = -Y$) forces the normal (Local Z) to point in the negative global Y direction, causing extrusions and boolean cuts to travel backwards.

- **XY**: Normal is +Z
- **YZ**: Normal is +X
- **ZX**: Normal is +Y (Use this instead of "XZ")

Offsets applied to a workplane (e.g., `.workplane(offset=10)`) move the plane along its normal axis.

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

CadQuery's power comes from string-based selectors used to pick faces, edges, and vertices for subsequent operations.

- `>Z`: Selects faces/edges whose normal/direction points most in the +Z direction (Top).
- `<Z`: Selects faces/edges in the -Z direction (Bottom).
- `>Y` / `<Y`: Right / Left.
- `>X` / `<X`: Front / Back.
- `%Plane`: Selects entities that are planar to the specified plane.
- `[Z`: Selects edges parallel to the Z axis.
- `|Z`: Selects faces parallel to the Z axis (e.g. cylinder sides).

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

## 6. Exporting

Models can be exported to standard formats for 3D printing (STL) or generic CAD (STEP).
```python
cq.exporters.export(result, "my_part.step")
cq.exporters.export(result, "my_part.stl")
```
