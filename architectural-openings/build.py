"""Original conceptual plan fixture; no client plan, survey or construction use."""
import bpy, pathlib, sys, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out=pathlib.Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
model=bpy.data.collections.new('01 Editable model - meters');scene.collection.children.link(model)
presentation=bpy.data.collections.new('02 Presentation cutaway only');scene.collection.children.link(presentation)
def mat(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.72
 return m
wallmat=mat('Warm mineral wall',(.69,.65,.56));floormat=mat('Floor',(.28,.24,.19));blue=mat('Opening notation',(.06,.27,.44));white=mat('Ground',(.38,.43,.47))
objects=[];walls=[]
def box(name,x0,x1,y0,y1,z0,z1,material=wallmat,wall=True,collection=model):
 assert x1>x0 and y1>y0 and z1>z0
 bpy.ops.mesh.primitive_cube_add(size=1,location=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
 ob=bpy.context.object;ob.name=name;ob.dimensions=(x1-x0,y1-y0,z1-z0)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for col in list(ob.users_collection):col.objects.unlink(ob)
 collection.objects.link(ob);ob.data.materials.append(material)
 if collection==model:objects.append(ob)
 if wall:walls.append(ob)
 return ob
box('Floor slab',-4,4,-2.5,2.5,-.15,0,floormat,False)
box('West wall',-4,-3.8,-2.3,2.3,0,2.8)
box('East wall',3.8,4,-2.3,2.3,0,2.8)
for a,b in [(-4,-2.45),(-1.55,4)]:box('South wall',a,b,-2.5,-2.3,0,2.8)
box('Entrance lintel',-2.45,-1.55,-2.5,-2.3,2.1,2.8)
for a,b in [(-4,-2.8),(-1.2,1.6),(2.8,4)]:box('North wall',a,b,2.3,2.5,0,2.8)
for i,(a,b) in enumerate([(-2.8,-1.2),(1.6,2.8)],1):
 box('Window '+str(i)+' sill wall',a,b,2.3,2.5,0,.9)
 box('Window '+str(i)+' lintel',a,b,2.3,2.5,2.1,2.8)
for a,b in [(-2.3,-1.35),(-.45,2.3)]:box('Partition wall',.94,1.06,a,b,0,2.8)
box('Partition door lintel',.94,1.06,-1.35,-.45,2.1,2.8)

# Test actual wall polygons with rays; do not infer clear space from input labels.
verts=[];faces=[]
for ob in walls:
 start=len(verts);verts.extend(ob.matrix_world @ v.co for v in ob.data.vertices)
 faces.extend(tuple(start+i for i in p.vertices) for p in ob.data.polygons)
bvh=BVHTree.FromPolygons(verts,faces)
tests=[]
def ray(name,origin,direction,distance,clear):
 hit=bvh.ray_cast(Vector(origin),Vector(direction),distance)[0] is not None
 tests.append({'name':name,'origin':origin,'direction':direction,'distance':distance,'expected_clear':clear,'observed_clear':not hit,'passed':hit != clear})
for offset,clear in [(-.44,True),(.44,True),(-.46,False),(.46,False)]:
 ray('Entrance lateral '+str(offset),(-2+offset,-3,1),(0,1,0),1,clear)
for z,clear in [(2.09,True),(2.11,False)]:ray('Entrance head '+str(z),(-2,-3,z),(0,1,0),1,clear)
for y,clear in [(-1.34,True),(-.46,True),(-1.36,False),(-.44,False)]:ray('Partition clearance '+str(y),(.5,y,1),(1,0,0),1,clear)
for z,clear in [(.91,True),(2.09,True),(.89,False),(2.11,False)]:ray('North window height '+str(z),(-2,3,z),(0,-1,0),1,clear)
assert all(t['passed'] for t in tests),tests
assert all(len(ob.data.vertices)==8 and len(ob.data.polygons)==6 for ob in objects)
dimensions={ob.name:[round(v,6) for v in ob.dimensions] for ob in objects}
source={'classification':'Self-initiated fictional conceptual geometry, not client work or construction documents',
 'units':'meters','outer_dimensions':[8,5],'wall_height':2.8,'external_wall_thickness':.2,'partition_thickness':.12,
 'entrance_clear_width':.9,'door_clear_height':2.1,'window_sill':.9,'window_head':2.1,
 'assumptions':['No survey or code-compliance claim.','Open roof is a presentation choice.','Wall elements are individually closed editable cuboids; no continuous welded building mesh claimed.','No BIM/MEP/structural/detailing deliverable.']}
(out/'plan-specification.json').write_text(json.dumps(source,indent=2),encoding='utf-8')
(out/'geometry-checks.json').write_text(json.dumps({'objects':len(objects),'dimensions':dimensions,'actual_polygon_rays':tests,'passed':True},indent=2),encoding='utf-8')
bpy.ops.object.select_all(action='DESELECT')
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.export_scene.gltf(filepath=str(out/'editable-room-study.glb'),export_format='GLB',use_selection=True,export_animations=False)

# Keep full-height source walls; render-only proxies disclose the cutaway.
for ob in list(walls):
 if ob.name.startswith(('South wall','Entrance lintel','West wall')):
  ob.hide_render=True
  lo=ob.location-ob.dimensions/2;hi=ob.location+ob.dimensions/2
  if lo.z<.5:box('Cutaway proxy '+ob.name,lo.x,hi.x,lo.y,hi.y,0,min(.5,hi.z),wallmat,False,presentation)
def floor_label(text,pos,size=.22):
 bpy.ops.object.text_add(location=pos);ob=bpy.context.object;ob.data.body=text;ob.data.size=size;ob.data.align_x='CENTER';ob.data.materials.append(blue)
 for col in list(ob.users_collection):col.objects.unlink(ob)
 presentation.objects.link(ob)
floor_label('CONCEPT / METERS',(-1.4,-.2,.015),.22)
floor_label('8.00 x 5.00 m',(0,-3.1,.015),.25)
floor_label('0.90 m',(-2,-2.5,.018),.15)
floor_label('0.90 m',(1,-.9,.018),.14)
for a,b in [((-2.45,-2.75,.02),(-1.55,-2.75,.02)),((.7,-1.35,.02),(.7,-.45,.02))]:
 curve=bpy.data.curves.new('Opening dimension line','CURVE');curve.dimensions='3D';curve.bevel_depth=.015
 sp=curve.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1)
 ob=bpy.data.objects.new('Opening dimension line',curve);presentation.objects.link(ob);ob.data.materials.append(blue)
box('Studio ground',-200,200,-200,200,-.22,-.20,white,False,presentation)
bpy.ops.object.camera_add(location=(-9,-11,12));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.4))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=14.5;scene.camera=cam
for loc,power,size in [((-3,-4,10),1800,7),((5,3,8),1300,6)]:
 bpy.ops.object.light_add(type='AREA',location=loc);ob=bpy.context.object;ob.data.energy=power;ob.data.size=size;ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
scene.world.color=(.2,.2,.2);scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.resolution_x=1500;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.filepath=str(out/'model-and-openings.png')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'editable-room-study.blend'))
bpy.ops.render.render(write_still=True)
print(json.dumps({'runtime':bpy.app.version_string,'ray_checks':len(tests),'all_pass':all(t['passed'] for t in tests),'objects':len(objects),'units':'meters'}))
