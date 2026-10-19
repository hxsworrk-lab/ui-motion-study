import bpy, pathlib, sys, json
root=pathlib.Path(sys.argv[sys.argv.index('--')+1]).resolve()
for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(root/'editable-room-study.glb'))
meshes=[o for o in bpy.data.objects if o.type=='MESH']
points=[o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
lo=[min(p[i] for p in points) for i in range(3)]
hi=[max(p[i] for p in points) for i in range(3)]
error=max(abs(a-b) for a,b in zip(lo+hi,[-4,-2.5,-.15,4,2.5,2.8]))
result={'imported_meshes':len(meshes),'world_min':lo,'world_max':hi,'max_expected_bounds_error_m':error,
        'passed':len(meshes)==16 and error<1e-5,
        'scope':'Fresh Blender GLB import, overall geometry scale only. No BIM/engine/code-compliance claim.'}
(root/'reimport-checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result));assert result['passed'],result
