# SPDX-License-Identifier: GPL-3.0-or-later
"""Original synthetic patch only: constrain 2D contour BEFORE cylindrical mapping.
No customer data, arbitrary STL editing, Boolean, whole holder or print claim.
"""
import ast, bpy, json, math, sys, time
from pathlib import Path
from collections import Counter, defaultdict
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

ROOT = Path(__file__).resolve().parent
OLD = ROOT / 'baseline_helpers.py'
START = time.time()
# Reuse frozen metric/closedness and display functions WITHOUT executing old builds.
tree = ast.parse(OLD.read_text(encoding='utf8'))
keep = {'geometry', 'relief', 'clamp', 'statistics', 'assert_closed', 'mesh_stats', 'material', 'look'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in keep], type_ignores=[]), str(OLD), 'exec'))
NU, NZ = 100, 110

def save(data):
    data.update(seconds=time.time()-START, blender=bpy.app.version_string,
                limits=['Synthetic analytic raised cross patch only.',
                        'Not buyer STL/pattern processing, arbitrary mesh repair, print or fit validation.',
                        'Radial coordinate gap is not global minimum physical thickness.'])
    (ROOT/'report.json').write_text(json.dumps(data, indent=2), encoding='utf8')

def mapped_mesh():
    coords, edges, lookup = [], [], {}
    def vertex(p):
        k=tuple(round(c,8) for c in p)
        if k not in lookup:
            lookup[k]=len(coords); coords.append(Vector(k))
        return lookup[k]
    def loop(poly):
        for a,b in zip(poly,poly[1:]+poly[:1]):
            steps=math.ceil(math.dist(a,b)/.4)
            ids=[vertex((a[0]+(b[0]-a[0])*i/steps,a[1]+(b[1]-a[1])*i/steps)) for i in range(steps+1)]
            edges.extend(zip(ids,ids[1:]))
    loop([(-10,-11),(10,-11),(10,11),(-10,11)])
    def cross(x,y,w):
        return [(-x,-w),(-w,-w),(-w,-y),(w,-y),(w,-w),(x,-w),(x,w),(w,w),(w,y),(-w,y),(-w,w),(-x,w)]
    loop(cross(5,6.4,1.2))
    loop(cross(4.6,6,.8))
    for iz in range(45):
        for ix in range(41): vertex((-10+ix*.5,-11+iz*.5))
    uv, out_edges, tris, _, edge_ids, _=delaunay_2d_cdt(coords,edges,[],0,1e-6,True)
    assert all(len(t)==3 for t in tris)
    covered={i for ids in edge_ids for i in ids if i<len(edges)}
    assert covered==set(range(len(edges))), 'Lost input contour segment'
    # UV CCW maps to negative radial; reverse for the OUTER surface.
    outer_faces=[]
    for a,b,c in tris:
        signed=(uv[b].x-uv[a].x)*(uv[c].y-uv[a].y)-(uv[b].y-uv[a].y)*(uv[c].x-uv[a].x)
        assert abs(signed)>1e-10
        outer_faces.append((a,c,b) if signed>0 else (a,b,c))
    outer, inner=[],[]
    for u,z in uv:
        d=min(max(abs(u)-5,abs(z)-1.2),max(abs(u)-1.2,abs(z)-6.4))
        t=max(0,min(1,-d/.4)); h=.8*t*t*(3-2*t)
        theta=u/32
        outer.append(((32+h)*math.sin(theta),(32+h)*math.cos(theta),z))
        inner.append((30*math.sin(theta),30*math.cos(theta),z))
    n=len(outer); faces=list(outer_faces)+[(a+n,c+n,b+n) for a,b,c in outer_faces]
    counts=Counter(tuple(sorted((a,b))) for f in outer_faces for a,b in zip(f,f[1:]+f[:1]))
    for f in outer_faces:
        for a,b in zip(f,f[1:]+f[:1]):
            if counts[tuple(sorted((a,b)))]==1: faces.extend([(b,a,a+n),(b,a+n,b+n)])
    return outer+inner,faces,{'input_constrained_segments':len(edges),'covered_segments':len(covered),'uv_vertices':len(uv),'uv_triangles':len(tris),'epsilon_mm':1e-6,'grid_mm':.5,'maximum_input_contour_segment_mm':.4,'raised_height_mm':.8,'ramp_mm':.4}

try:
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    if '--verify' in sys.argv:
        bpy.ops.wm.stl_import(filepath=str(ROOT/'raised.stl'),global_scale=1,use_scene_unit=False)
        ob=[o for o in bpy.context.scene.objects if o.type=='MESH'][0]
        stats=mesh_stats(ob); assert_closed(stats)
        report=json.loads((ROOT/'report.json').read_text())
        deviation=max(abs(stats['bbox_mm'][a][b]-report['statistics']['bbox_mm'][a][b]) for a in range(3) for b in range(2))
        assert deviation<.0001
        report['fresh_native_stl_import']={'statistics':stats,'max_bbox_coordinate_deviation_mm':deviation}
        save(report)
    else:
        vertices,faces,cdt=mapped_mesh(); stats=statistics(vertices,faces); assert_closed(stats)
        assert abs(stats['conservative_radial_material_gap_mm']-2)<1e-5
        mesh=bpy.data.meshes.new('Constrained analytic surface');mesh.from_pydata(vertices,[],faces);mesh.update()
        ob=bpy.data.objects.new('Contour-constrained raised cross',mesh);bpy.context.collection.objects.link(ob)
        ob.select_set(True);bpy.context.view_layer.objects.active=ob
        bpy.ops.wm.stl_export(filepath=str(ROOT/'raised.stl'),export_selected_objects=True,global_scale=1,use_scene_unit=False,ascii_format=False)
        old_v,old_f=geometry('raised'); old_mesh=bpy.data.meshes.new('Original regular grid');old_mesh.from_pydata(old_v,[],old_f);old_mesh.update()
        old_ob=bpy.data.objects.new('Previous regular-grid cross',old_mesh);bpy.context.collection.objects.link(old_ob)
        # Presentation transforms only AFTER origin-centred export.
        for item,x,color in [(old_ob,-12,(.18,.35,.48)),(ob,12,(.18,.35,.48))]:
            item.location=(x,-31,0);item.data.materials.append(material(item.name,color))
        scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001
        bpy.ops.object.camera_add(location=(18,65,28));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=52;look(cam,(0,0,0));scene.camera=cam
        for loc,energy,size in [((-20,18,30),22000,18),((30,15,10),7000,22)]:
            bpy.ops.object.light_add(type='AREA',location=loc);lamp=bpy.context.object;lamp.data.energy=energy;lamp.data.size=size;look(lamp,(0,0,0))
        scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
        scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=True
        scene.render.resolution_x=1100;scene.render.resolution_y=700;scene.render.resolution_percentage=100
        scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/'comparison.png')
        save({'passed':True,'statistics':stats,'cdt':cdt,'comparison':'left previous regular-grid / right constrained contour; both same material; no smooth-shading modifier'})
        bpy.ops.render.render(write_still=True)
except Exception as exc:
    save({'passed':False,'error':repr(exc)});raise
