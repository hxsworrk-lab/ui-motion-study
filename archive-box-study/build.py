# Hx Works: self-initiated original study, AI-assisted scripting; no client asset.
import bpy, math, json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
asset=[]
def mat(name, rgb, metal=0, rough=.58):
 m=bpy.data.materials.new(name);m.use_nodes=True
 n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*rgb,1);n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough
 return m
jade=mat('Paint - faded jade',(.125,.29,.265),.12)
lidmat=mat('Paint - warm bone',(.61,.57,.39),.10)
ink=mat('Ink enamel',(.023,.040,.044),.15)
red=mat('Seal - vermilion',(.63,.075,.045))
paper=mat('Paper - cream',(.85,.73,.47),0,.88)
brass=mat('Hardware - aged brass',(.55,.34,.11),.55,.35)
eyemat=mat('Eyes - muted amber',(.96,.53,.10),.05,.32)
root=bpy.data.objects.new('HX_Misfiled_Archive_Box',None);bpy.context.collection.objects.link(root)
def box(name,loc,size,material,bevel=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(material)
 if bevel:
  b=o.modifiers.new('Low polygon edge chamfer','BEVEL');b.width=bevel;b.segments=1
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name)
 o.parent=root;asset.append(o);return o
box('closed body block',(0,0,.48),(1.30,.86,.78),jade,.035)
box('lid', (0,0,.925),(1.39,.94,.15),lidmat,.025)
box('dark lid reveal',(0,0,.842),(1.34,.90,.035),ink,.006)
for x in [-.49,.49]:
 for y in [-.27,.27]:box('foot',(x,y,.065),(.17,.19,.11),ink,.02)
# Two side hinges and front rim; all original primitive construction.
for x in [-.43,.43]:
 box('lid hinge',(x,.447,.88),(.20,.06,.12),brass,.012)
box('label plate',(0,-.444,.53),(.70,.025,.31),brass,.018)
box('paper label',(0,-.462,.53),(.62,.016,.25),paper,.009)
# A narrow peephole gives the otherwise mundane archive box an odd character.
box('peephole',(0,-.476,.575),(.48,.015,.093),ink,.015)
for x in [-.125,.125]:
 box('amber eye',(x,-.488,.577),(.072,.014,.043),eyemat,.013)
 box('vertical pupil',(x,-.498,.577),(.012,.007,.038),ink,.003)
# An unlettered red paper seal: abstract marks, not claimed Chinese writing.
box('red paper seal',(.43,-.473,.765),(.145,.025,.43),red,.008)
for z in [.64,.71,.78,.85]:
 a=box('abstract seal mark',(.43,-.490,z),(.080,.007,.010),paper,.002);a.rotation_euler[1]=.24 if z<.76 else -.24
# Folded paper tab, partially tucked under the lid.
box('folded paper tab',(-.39,-.22,1.018),(.27,.34,.025),paper,.006)
box('tab fold',(-.39,-.071,1.046),(.27,.045,.074),paper,.004)
# Small plate serial. Built-in Blender font; converted into editable mesh.
bpy.ops.object.text_add(location=(-.118,-.479,.455),rotation=(math.pi/2,0,0))
t=bpy.context.object;t.name='serial 013';t.data.body='013';t.data.size=.086;t.data.extrude=.0005;t.data.materials.append(ink)
bpy.ops.object.convert(target='MESH');t.parent=root;asset.append(t)
# Modest handle, modelled rather than texture-painted.
for x in [-.18,.18]:box('handle mount',(x,-.447,.245),(.09,.045,.08),brass,.011)
box('handle left',(-.18,-.512,.23),(.045,.10,.045),brass,.009)
box('handle right',(.18,-.512,.23),(.045,.10,.045),brass,.009)
box('handle grip',(0,-.56,.23),(.39,.045,.045),brass,.009)
# Inspectable, bounded mesh metrics. Not watertight union / print / engine proof.
triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in asset)
vertices=sum(len(o.data.vertices) for o in asset)
for o in bpy.context.selected_objects:o.select_set(False)
root.select_set(True)
for o in asset:o.select_set(True)
bpy.context.view_layer.objects.active=asset[0]
bpy.ops.export_scene.gltf(filepath=str(OUT/'archive-box.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=False)
report={'blender':bpy.app.version_string,'mesh_objects':len(asset),'vertices':vertices,'triangles':triangles,'materials':len({m.name for o in asset for m in o.data.materials}),'basis':'Original primitives and converted built-in-font serial, no client/third-party asset','limits':['Closed stylized prop, not a functional hinged/hollow container','No UV texture painting, LOD, collider or Unity import/runtime validation','Separate intersecting component meshes, not printable watertight union','Not commissioned artwork, not proof of game production or professional years']}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
# Studio scene objects are not included in the GLB export.
floormat=mat('Studio floor',(.19,.235,.245),0,.9)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,0));bpy.context.object.data.materials.append(floormat)
world=bpy.data.worlds.new('Studio World');bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.19,.24,.28,1);world.node_tree.nodes['Background'].inputs[1].default_value=.35
for name,loc,power,size,color in [('key',(-3,-4,5),430,4,(1,.83,.66)),('fill',(4,-1,2.6),220,3,(.63,.82,1)),('rim',(1,3,4),500,3,(.80,1,.91))]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=color;o.rotation_euler=(Vector((0,0,.55))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2.6,-3.9,2.3));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.51))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.40
sc=bpy.context.scene;sc.camera=cam;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True;sc.render.resolution_x=1100;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(OUT/'preview.png');sc.view_settings.view_transform='AgX';sc.render.film_transparent=False
for prop in sc.render.bl_rna.properties:
 if prop.identifier.startswith('use_stamp_') and prop.type == 'BOOLEAN': setattr(sc.render,prop.identifier,False)
sc.render.use_stamp=False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'archive-box.blend'))
bpy.ops.render.render(write_still=True)
print('HX_ARCHIVE_STUDY_REPORT '+json.dumps(report))
