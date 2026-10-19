"""Read generated binary STL files without Blender; no printability certification."""

import collections
import hashlib
import json
import math
import pathlib
import struct
import sys


def audit(path):
    raw = path.read_bytes()
    if len(raw) < 84 or len(raw) > 64 * 1024 * 1024:
        raise ValueError("Unexpected internal-probe STL size")
    count = struct.unpack_from("<I", raw, 80)[0]
    if len(raw) != 84 + count * 50:
        raise ValueError("Not a complete binary STL")
    ids, vertices, faces = {}, [], []
    edges = collections.Counter()
    directed = collections.Counter()
    zero_area = 0
    volume = 0.0
    for index in range(count):
        values = struct.unpack_from("<12fH", raw, 84 + index * 50)
        face = []
        points = []
        for offset in (3, 6, 9):
            point = tuple(values[offset:offset + 3])
            if not all(math.isfinite(v) for v in point):
                raise ValueError("Non-finite coordinate")
            if point not in ids:
                ids[point] = len(vertices)
                vertices.append(point)
            face.append(ids[point])
            points.append(point)
        a, b, c = points
        ab = tuple(b[i] - a[i] for i in range(3))
        ac = tuple(c[i] - a[i] for i in range(3))
        cross = (ab[1]*ac[2] - ab[2]*ac[1],
                 ab[2]*ac[0] - ab[0]*ac[2],
                 ab[0]*ac[1] - ab[1]*ac[0])
        zero_area += len(set(face)) < 3 or sum(v*v for v in cross) <= 1e-20
        volume += (a[0]*(b[1]*c[2] - b[2]*c[1])
                   + a[1]*(b[2]*c[0] - b[0]*c[2])
                   + a[2]*(b[0]*c[1] - b[1]*c[0])) / 6
        for u, v in zip(face, face[1:] + face[:1]):
            edges[tuple(sorted((u, v)))] += 1
            directed[(u, v)] += 1
        faces.append(tuple(face))
    adjacency = collections.defaultdict(set)
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    remaining = set(range(len(vertices)))
    components = 0
    while remaining:
        components += 1
        stack = [remaining.pop()]
        while stack:
            for neighbor in adjacency[stack.pop()]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
    minimum = [min(v[i] for v in vertices) for i in range(3)]
    maximum = [max(v[i] for v in vertices) for i in range(3)]
    radii = [math.hypot(v[0], v[1]) for v in vertices]
    boundary = sum(n == 1 for n in edges.values())
    nonmanifold = sum(n != 2 for n in edges.values())
    inconsistent = sum(directed[(u, v)] != directed[(v, u)] for u, v in edges)
    duplicate_faces = len(faces) - len({tuple(sorted(f)) for f in faces})
    return {
        "file": path.name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
        "coordinate_unit_convention": "mm; STL itself has no unit declaration",
        "triangles": count, "unique_vertices_exact_float32": len(vertices),
        "unique_edges": len(edges), "boundary_edges": boundary,
        "nonmanifold_edges": nonmanifold, "inconsistently_oriented_edges": inconsistent,
        "zero_area_or_repeated_vertex_triangles": zero_area,
        "duplicate_triangles": duplicate_faces, "connected_components": components,
        "euler_characteristic": len(vertices) - len(edges) + count,
        "signed_volume_mm3": volume, "bbox_min_mm": minimum, "bbox_max_mm": maximum,
        "bbox_dimensions_mm": [maximum[i] - minimum[i] for i in range(3)],
        "radial_coordinate_range_mm": [min(radii), max(radii)],
        "min_radius_above_inner_30mm_tolerance": min(r for r in radii if r > 30.001),
        "basic_mesh_invariants_pass": count > 0 and boundary == nonmanifold == inconsistent
            == zero_area == duplicate_faces == 0 and components == 1 and volume > 0,
        "not_proven_by_this_parser": ["arbitrary STL editing", "Boolean operation history", "self-intersection audit",
                       "slicer behavior", "physical print", "global minimum wall thickness"],
    }


if __name__ == "__main__":
    print(json.dumps([audit(pathlib.Path(p)) for p in sys.argv[1:]], indent=2))
