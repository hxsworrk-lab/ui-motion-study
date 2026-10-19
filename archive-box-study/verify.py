import bpy,json,math
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(p/'archive-box.glb'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
points=[o.matrix_world @ Vector(v) for o in meshes for v in o.bound_box]
r={'blender':bpy.app.version_string,'mesh_objects':len(meshes),'triangles':sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in meshes),'used_materials':sorted({m.name for o in meshes for m in o.data.materials}),'bounds_min':[min(v[i] for v in points) for i in range(3)],'bounds_max':[max(v[i] for v in points) for i in range(3)],'finite_vertices':all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co),'no_camera_or_light':not any(o.type in ['CAMERA','LIGHT'] for o in bpy.context.scene.objects),'limits':'Native GLB parse and bounded structure check only; no Unity, LOD, collision, UV/texture or production approval.'}
assert r['mesh_objects']==29 and r['triangles']==2212 and len(r['used_materials'])==7 and r['finite_vertices'] and r['no_camera_or_light'],r
p.joinpath('glb-import-check.json').write_text(json.dumps(r,indent=2)+'\n')
print('HX_NATIVE_GLB_CHECK '+json.dumps(r))
