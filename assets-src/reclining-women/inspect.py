import bpy,json
from mathutils import Vector
from pathlib import Path
p=str(Path(__file__).resolve().parent)+'/';bpy.ops.wm.open_mainfile(filepath=p+'reclining-women.blend');bpy.context.scene.frame_set(1);deps=bpy.context.evaluated_depsgraph_get();out={}
for rig in [o for o in bpy.data.objects if o.type=='ARMATURE']:
 points=[]
 for ob in rig.children:
  if ob.type=='MESH':
   e=ob.evaluated_get(deps);points +=[ob.matrix_world@v.co for v in e.to_mesh().vertices];e.to_mesh_clear()
 out[rig.name]={'blenderMin':[min(v[i] for v in points) for i in range(3)],'blenderMax':[max(v[i] for v in points) for i in range(3)]}
print('BOUNDS',json.dumps(out));open(p+'bounds.json','w').write(json.dumps(out,indent=2))
# Human-scale face inspection from just above the shoulders.
bpy.ops.object.camera_add(location=(3,-2.5,4.0));cam=bpy.context.object;cam.rotation_euler=(Vector((1.25,-.1,.43))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.25;bpy.context.scene.camera=cam
for loc,power,size in [((2,-2,4),180,3),((0,2,3),80,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);ob=bpy.context.object;ob.data.energy=power;ob.data.size=size;ob.rotation_euler=(Vector((1,0,.3))-ob.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.render.resolution_x=1200;scene.render.resolution_y=950;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=p+'face-inspection.png';scene.world.color=(.08,.08,.08);bpy.ops.render.render(write_still=True)
