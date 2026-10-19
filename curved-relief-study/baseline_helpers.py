# SPDX-License-Identifier: GPL-3.0-or-later
"""Unchanged metric, baseline geometry and presentation functions from the original self-initiated study."""
import bpy, math
from collections import Counter, defaultdict
from mathutils import Vector
NU, NZ = 100, 110

def clamp(x):
    return min(1.0, max(0.0, x))

def relief(u, z, kind):
    if kind == 'raised':
        # Union of two synthetic rectangles, with a 0.4 mm inward ramp.
        d = min(max(abs(u)-5.0, abs(z)-1.2), max(abs(u)-1.2, abs(z)-6.4))
        return .8 * clamp(-d/.4)
    # One synthetic diamond, with a narrow inward ramp before its plateau.
    q = abs(u)/5.4 + abs(z)/7.2
    return -.6 * clamp((1-q)/.12)

def geometry(kind):
    outer, inner = [], []
    for iz in range(NZ+1):
        z = -11 + 22*iz/NZ
        for iu in range(NU+1):
            u = -10 + 20*iu/NU
            theta = u/32
            r = 32 + relief(u, z, kind)
            outer.append((r*math.sin(theta), r*math.cos(theta), z))
            inner.append((30*math.sin(theta), 30*math.cos(theta), z))
    n = len(outer)
    outer_faces = []
    for iz in range(NZ):
        for iu in range(NU):
            a = iz*(NU+1)+iu
            b, d = a+1, a+(NU+1)
            c = d+1
            # v then u gives the outward (+radial) normal for x=r sin(theta).
            outer_faces.extend([(a,d,c), (a,c,b)])
    faces = list(outer_faces)
    faces += [(a+n,c+n,b+n) for a,b,c in outer_faces]
    count = Counter(tuple(sorted((a,b))) for f in outer_faces for a,b in zip(f, f[1:]+f[:1]))
    boundary = [(a,b) for f in outer_faces for a,b in zip(f, f[1:]+f[:1]) if count[tuple(sorted((a,b)))] == 1]
    for a,b in boundary:
        faces.extend([(b,a,a+n), (b,a+n,b+n)])
    return outer+inner, faces

def statistics(vertices, triangles):
    vs = [Vector(v) for v in vertices]
    edge_count = Counter()
    directed = Counter()
    adj = defaultdict(set)
    degenerates = 0
    area = volume = 0.0
    for a,b,c in triangles:
        cross = (vs[b]-vs[a]).cross(vs[c]-vs[a])
        tri_area = cross.length/2
        area += tri_area
        degenerates += int(tri_area <= 1e-10 or len({a,b,c}) != 3)
        volume += vs[a].dot(vs[b].cross(vs[c]))/6
        for p,q in ((a,b),(b,c),(c,a)):
            edge_count[tuple(sorted((p,q)))] += 1
            directed[(p,q)] += 1
            adj[p].add(q)
            adj[q].add(p)
    unseen = set(range(len(vs)))
    components = 0
    while unseen:
        components += 1
        stack = [unseen.pop()]
        while stack:
            for q in adj[stack.pop()]:
                if q in unseen:
                    unseen.remove(q)
                    stack.append(q)
    bounds = [[min(v[k] for v in vs), max(v[k] for v in vs)] for k in range(3)]
    radii = [math.hypot(v.x,v.y) for v in vs]
    inner = [r for r in radii if r < 30.1]
    outer = [r for r in radii if r > 31.2]
    return {
        'vertex_count':len(vs), 'triangle_count':len(triangles),
        'boundary_edge_count':sum(n==1 for n in edge_count.values()),
        'non_manifold_edge_count':sum(n!=2 for n in edge_count.values()),
        'inconsistent_directed_edge_count':sum(directed[(a,b)]!=directed[(b,a)] for a,b in edge_count),
        'degenerate_triangle_count':degenerates,
        'finite_coordinates':all(math.isfinite(c) for v in vs for c in v),
        'signed_volume_mm3':volume, 'surface_area_mm2':area,
        'connected_components':components, 'bbox_mm':bounds,
        'bbox_dimensions_mm':[b-a for a,b in bounds],
        'measured_inner_radius_range_mm':[min(inner),max(inner)],
        'measured_outer_radius_range_mm':[min(outer),max(outer)],
        'conservative_radial_material_gap_mm':min(outer)-max(inner),
        'radial_gap_is_global_thinnest_distance':False}

def assert_closed(s):
    assert s['boundary_edge_count']==s['non_manifold_edge_count']==s['inconsistent_directed_edge_count']==s['degenerate_triangle_count']==0, s
    assert s['finite_coordinates'] and s['signed_volume_mm3']>0 and s['connected_components']==1, s

def mesh_stats(ob):
    ob.data.calc_loop_triangles()
    return statistics([tuple(v.co) for v in ob.data.vertices], [tuple(t.vertices) for t in ob.data.loop_triangles])

def material(name,color):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=.78
    return m

def look(ob,target):
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
