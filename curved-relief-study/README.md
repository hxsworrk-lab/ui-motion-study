# Contour-constrained curved relief — Blender study

**Hx Works · Self-initiated · Synthetic geometry · AI-assisted scripting**

A small raised cross on a cylindrical patch, generated from original analytic geometry. The study compares a regular grid with a contour-constrained planar triangulation mapped onto the same cylinder. It is not a customer design or a complete can holder.

[Inspect the binary STL](raised.stl) · [Recorded source and fresh-import checks](report.json) · [Blender source](probe.py) · [Independent binary-STL auditor](audit_stl.py)

## What was checked

The recorded Blender 5.2.1 LTS run produced 4,466 vertices and 8,928 triangles. The source and a fresh native STL import had zero boundary, non-manifold, inconsistent-direction or degenerate edges/triangles under the included checks, one connected component, and positive signed volume. All 434 input contour segments were covered. The fresh-import bounding-box coordinate difference was zero in that run.

Numeric coordinates use millimetres by convention; STL contains no unit declaration. The base outer radius is 32 mm, inner radius 30 mm and raised height 0.8 mm. The radial gap is measured against the known analytic cylinder; it is not a global minimum wall-thickness guarantee.

## Reproduce in an isolated Blender process

With an existing Blender 5.2.1 installation, download this folder and run from it:

```sh
blender --background --factory-startup --python probe.py
blender --background --factory-startup --python probe.py -- --verify
python audit_stl.py raised.stl
```

The first command creates the mesh, overwrites `raised.stl` and `report.json`, and renders a regular-grid/constrained-contour comparison. The second imports that STL into a fresh process and records basic mesh checks. `baseline_helpers.py` contains the selected unchanged baseline, metrics and render helpers needed by the original script. No customer asset, dependency download, account or network request is used. Rendered pixels and floating-point results may vary by Blender version and platform.

## Evidence limits

This is a bounded geometry example, not proof of arbitrary STL repair, pattern extraction, editing an existing customer surface, recessed artwork, complex typography, self-intersection freedom, slicer behaviour, toolpaths, material suitability, physical print quality or can fit. The contour is aligned in the triangulation; this does not promise flawless appearance on every shape. No smooth-shading modifier is used to hide geometry.

The earlier closed-cutter Boolean approach produced degenerate triangles and was rejected. The published mesh instead maps a constrained triangulation directly onto an analytic cylinder; it does not demonstrate robust Boolean repair.

Before any production work, the actual source, modification rights, permitted tools, required dimensions, acceptance checks, revisions, fee and payment must be agreed. Keep confidential files back until the permitted material workflow is confirmed.

The Blender source and its extracted helpers retain their GPL-3.0-or-later notice. This page adds no separate licence grant for other files or third-party materials. No client or exclusive-rights claim is made.
