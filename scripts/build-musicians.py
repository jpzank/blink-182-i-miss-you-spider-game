"""Build skinned, animated musicians from CC0 MakeHuman anatomy and garments.
Run: blender -b --python scripts/build-musicians.py
"""
import bpy, json, math, os, random
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'assets-src/makehuman'; SYSTEM=SRC/'system'
bpy.ops.wm.read_factory_settings(use_empty=True) # no startup-file brush or UI references

def objdata(path):
 vs=[];uv=[];faces=[];group='';groups={}
 for ln in Path(path).read_text().splitlines():
  t=ln.split()
  if not t:continue
  if t[0]=='v':vs.append(Vector(map(float,t[1:4])))
  elif t[0]=='vt':uv.append(tuple(map(float,t[1:3])))
  elif t[0]=='g':group=t[1]
  elif t[0]=='f':
   f=[(int(p.split('/')[0])-1,int(p.split('/')[1])-1 if '/' in p and p.split('/')[1] else 0) for p in t[1:]];faces.append((group,f));groups.setdefault(group,set()).update(a for a,b in f)
 return vs,uv,faces,groups
base,uv,faces,groups=objdata(SRC/'base.obj');morphed=[v.copy() for v in base]
for target in ['male.target','caucasian.target']:
 for ln in (SRC/target).read_text().splitlines():
  t=ln.split()
  if len(t)==4 and t[0].isdigit():morphed[int(t[0])]+=Vector(map(float,t[1:]))
body_ids=groups['body'];foot=min(morphed[i].y for i in body_ids);top=max(morphed[i].y for i in body_ids);S=3.9/(top-foot)
anatomy=[v.copy() for v in morphed]
def conv(v):return Vector((v.x*S,-v.z*S,(v.y-foot)*S))
def center(group):return sum((morphed[i] for i in groups[group]),Vector())/len(groups[group])
rigdata=json.load(open(SRC/'default.mhskel'));weights=json.load(open(SRC/'default_weights.mhw'))['weights'];vw={}
for name,pairs in weights.items():
 for i,w in pairs:vw.setdefault(i,{})[name]=w

def proxy(path):
 mapping=[];delete=set();scales=[1,1,1];mode='';ranges=[]
 for ln in Path(path).read_text().splitlines():
  t=ln.split()
  if not t or t[0].startswith('#'):continue
  if t[0] in ['x_scale','y_scale','z_scale']:
   axis={'x_scale':0,'y_scale':1,'z_scale':2}[t[0]];a,b=int(t[1]),int(t[2]);scales[axis]=abs(morphed[a][axis]-morphed[b][axis])/float(t[3]);continue
  if t[0]=='verts':mode='verts';continue
  if t[0]=='delete_verts':mode='delete';continue
  if not (t[0][0].isdigit() or t[0][0]=='-'):mode='';continue
  if mode=='verts':
   if len(t)==1:mapping.append(([int(t[0])],[1.0],Vector((0,0,0))))
   elif len(t)==9:mapping.append((list(map(int,t[:3])),list(map(float,t[3:6])),Vector(map(float,t[6:9]))))
  elif mode=='delete':
   j=0
   while j<len(t):
    if j+2<len(t) and t[j+1]=='-':delete.update(range(int(t[j]),int(t[j+2])+1));j+=3
    else:delete.add(int(t[j]));j+=1
 out=[];outweights=[]
 for inds,ws,offset in mapping:
  p=sum((morphed[i]*w for i,w in zip(inds,ws)),Vector())+Vector(tuple(offset[i]*scales[i] for i in range(3)));out.append(p);d={}
  for i,ww in zip(inds,ws):
   for n,w in vw.get(i,{}).items():d[n]=d.get(n,0)+w*ww
  d={n:max(0,w) for n,w in d.items() if w>.005};outweights.append(d)
 return out,outweights,delete

materials={}
def material(name,texture=None,color=(.2,.2,.2,1),rough=.8,alpha=False):
 if name in materials:return materials[name]
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=color;p.inputs['Roughness'].default_value=rough
 if texture:
  tex=n.new('ShaderNodeTexImage');im=bpy.data.images.load(str(texture),check_existing=True)
  if im.size[0]>1536:im.scale(1536,1536)
  tex.image=im;m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
  if alpha:m.node_tree.links.new(tex.outputs['Alpha'],p.inputs['Alpha']);m.surface_render_method='DITHERED'
 if name=='Skin':p.inputs['Subsurface Weight'].default_value=.09
 materials[name]=m;return m
skin=material('Skin',SYSTEM/'skins/young_caucasian_male/young_lightskinned_male_diffuse.png',rough=.58)
suit=material('Wool suit',SYSTEM/'clothes/male_elegantsuit01/male_elegantsuit01_diffuse.png',rough=.95)
shoe=material('Leather shoes',SYSTEM/'clothes/shoes01/shoes01_diffuse.png',rough=.4)
eye=material('Eyes',SRC/'brown_eye.png',rough=.16)

allrigs=[]
def rig_for(role,offset):
 arm=bpy.data.armatures.new(role+'Skeleton');rig=bpy.data.objects.new(role,arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 joints={n:sum((morphed[i] for i in ids),Vector())/len(ids) for n,ids in rigdata['joints'].items()}
 for n,b in rigdata['bones'].items():
  bone=arm.edit_bones.new(n);bone.head=conv(joints[b['head']]);bone.tail=conv(joints[b['tail']]);
  if (bone.tail-bone.head).length<.0001:bone.tail.z+=.001
 for n,b in rigdata['bones'].items():
  if b.get('parent'):arm.edit_bones[n].parent=arm.edit_bones[b['parent']]
 bpy.ops.object.mode_set(mode='OBJECT');rig.location=offset;rig.select_set(False);allrigs.append(rig);return rig

def mesh(name,verts,uvs,fs,mat,rig,weights_for_vertex):
 # Reindex to omit body helper vertices from exports.
 used=sorted({i for _,f in fs for i,j in f});lookup={a:i for i,a in enumerate(used)}
 geo=bpy.data.meshes.new(name);geo.from_pydata([conv(verts[i]) for i in used],[],[[lookup[i] for i,j in f] for _,f in fs]);geo.update();ob=bpy.data.objects.new(name,geo);bpy.context.collection.objects.link(ob);ob.data.materials.append(mat);ob.parent=rig
 layer=geo.uv_layers.new(name='UVMap')
 for poly,(_,f) in zip(geo.polygons,fs):
  poly.use_smooth=True
  for loop,(_,j) in zip(poly.loop_indices,f):layer.data[loop].uv=uvs[j]
 for original in used:
  d=weights_for_vertex[original] if isinstance(weights_for_vertex,list) else weights_for_vertex.get(original,{})
  if not d:d={'head':1} if verts[original].y>6 else {'spine03':1}
  for n,w in d.items():
   if n not in rig.data.bones:continue
   vg=ob.vertex_groups.get(n) or ob.vertex_groups.new(name=n);vg.add([lookup[original]],w,'REPLACE')
 mod=ob.modifiers.new('Performance rig','ARMATURE');mod.object=rig
 return ob

def garment(folder,name,rig,mat):
 v,u,f,g=objdata(folder/(name+'.obj'));fitted,w,deleted=proxy(folder/(name+'.mhclo'));assert len(fitted)==len(v),(name,len(fitted),len(v));ob=mesh(name,fitted,u,f,mat,rig,w);style_garment(role,ob);return deleted

exec((ROOT/'scripts/band-details.py').read_text(),globals())
exec((ROOT/'scripts/band-heads.py').read_text(),globals())

FRAMES=133
bpy.context.scene.render.fps=30
for role,position in [('Bassist',(-2.8,6.6,.42)),('Guitarist',(2.4,6.1,.42)),('Drummer',(0,8.1,-.3))]:
 morphed=member_anatomy(role);S=MEMBERS[role][2]/(top-foot)
 rig=rig_for(role,position);rig['member']=MEMBERS[role][0];rig['reference']='I Miss You official video, 2003 appearance'
 outfit='male_casualsuit04' if role=='Drummer' else 'male_elegantsuit01'
 outfitmat=material(outfit,None if role=='Drummer' else SYSTEM/'clothes'/outfit/(outfit+'_diffuse.png'),color=(.06,.065,.06,1),rough=.95)
 deleted=garment(SYSTEM/'clothes'/outfit,outfit,rig,outfitmat)
 deleted.update(garment(SYSTEM/'clothes/shoes01','shoes01',rig,shoe))
 body=mesh(MEMBERS[role][0]+' skin',morphed,uv,[(g,f) for g,f in faces if g=='body' and not any(i in deleted for i,j in f)],skin,rig,vw)
 skin_for_member(role,body,rig);hair_cards(role,rig,body)
 if role=='Drummer':suspenders(rig,next(o for o in rig.children if o.name.startswith('male_casualsuit04')))
 v,u,f,g=objdata(SRC/'eyes.obj');fit,w,d=proxy(SRC/'eyes.mhclo');eyes_ob=mesh(role+' eyes',fit,u,f,eye,rig,w);layered_eyes(role,rig,eyes_ob);eyelashes(role,rig)
 # Anatomical two-segment arm solve; twist bones follow their limb rigidly.
 def aim_bone(name,head,direction):
  pb=rig.pose.bones[name];rest=pb.bone
  rot=(rest.tail_local-rest.head_local).rotation_difference(direction)
  pb.rotation_mode='QUATERNION'
  pb.matrix=Matrix.Translation(head) @ rot.to_matrix().to_4x4() @ rest.matrix_local.to_3x3().to_4x4()
  bpy.context.view_layer.update()
  pb.keyframe_insert('rotation_quaternion',frame=frame)
  pb.keyframe_insert('location',frame=frame)
 for frame in range(1,FRAMES+1):
  bpy.context.scene.frame_set(frame)
  for side,sgn in [('L',1),('R',-1)]:
   beat=(frame-1)/(FRAMES-1)*8;t=beat*math.tau;up=math.sin(t+(0 if side=='L' else math.pi))
   if role=='Bassist':target=Vector((.64 if side=='L' else .62,-.62,3.10+.09*math.sin(t/4) if side=='L' else 1.93+.06*up))
   elif role=='Guitarist':target=Vector((1.14+.045*math.sin(t/4) if side=='L' else .15+.055*up,-.65,2.31 if side=='L' else 1.97+.16*up))
   else:target=Vector((1.02 if side=='L' else -.78,-.83 if side=='L' else -1.16,(3.02 if side=='L' else 2.72)+.22*(.5+.5*up)))
   names=[p+side for p in ['upperarm01.','upperarm02.','lowerarm01.','lowerarm02.']]
   bones=[rig.data.bones[n] for n in names];lengths=[b.length for b in bones]
   shoulder=bones[0].head_local.copy();u=(target-shoulder).normalized()
   l1=sum(lengths[:2]);l2=sum(lengths[2:]);d=min((target-shoulder).length,l1+l2-.005)
   target=shoulder+u*d
   pole=Vector((sgn*1.5,-.1,2.4))-shoulder;v=(pole-u*pole.dot(u)).normalized()
   a=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(.0001,l1*l1-a*a));elbow=shoulder+u*a+v*h
   upper=(elbow-shoulder).normalized();lower=(target-elbow).normalized()
   heads=[shoulder,shoulder+upper*lengths[0],elbow,elbow+lower*lengths[2]]
   for n,head,dr in zip(names,heads,[upper,upper,lower,lower]):aim_bone(n,head,dr)
   if role=='Drummer':handdir=Vector((sgn*.1,-.65,-.38))
   elif role=='Guitarist':handdir=Vector((-.08 if side=='L' else .1,-.15,-.24))
   else:handdir=Vector((.04 if side=='L' else -.03,-.18,-.24 if side=='L' else -.10))
   aim_bone('wrist.'+side,target,handdir)
 if role=='Drummer':
  for side,sgn in [('L',1),('R',-1)]:
   for n in ['upperleg02.','lowerleg02.']:
    p=rig.pose.bones[n+side];p.lock_ik_x=p.lock_ik_y=p.lock_ik_z=True
   pb=rig.pose.bones['lowerleg02.'+side];ik=pb.constraints.new('IK');ik.chain_count=4
   target=bpy.data.objects.new('Drummer foot '+side,None);bpy.context.collection.objects.link(target);target.location=Vector(position)+Vector((sgn*.35,-.85,.65));ik.target=target
   pole=bpy.data.objects.new('Drummer knee '+side,None);bpy.context.collection.objects.link(pole);pole.location=Vector(position)+Vector((sgn*.5,-2,1.7));ik.pole_target=pole
 for pbone in rig.pose.bones:
  if pbone.name.startswith('finger'):
   # Curl around the palm-facing anatomical axis, independent of bone roll.
   direction=pbone.bone.tail_local-pbone.bone.head_local
   axis=direction.cross(Vector((0,-1,0))).normalized()
   local_axis=pbone.bone.matrix_local.to_3x3().inverted()@axis
   from mathutils import Quaternion
   pbone.rotation_mode='QUATERNION';pbone.rotation_quaternion=Quaternion(local_axis,.85 if role=='Guitarist' else .65);pbone.keyframe_insert('rotation_quaternion',frame=1)
 for frame in range(1,FRAMES+1):
  # A small independent finger stroke, while the fretting hand holds its grip.
  t=(frame-1)/(FRAMES-1)*math.tau
  if role=='Bassist':
   for name in ['finger2-1.R','finger2-2.R']:
    finger=rig.pose.bones.get(name)
    if finger:
     d=finger.bone.tail_local-finger.bone.head_local;axis=finger.bone.matrix_local.to_3x3().inverted()@d.cross(Vector((0,-1,0))).normalized();finger.rotation_quaternion=Quaternion(axis,.6+.16*math.sin(t*8));finger.keyframe_insert('rotation_quaternion',frame=frame)
  spine=rig.pose.bones['spine03'];spine.rotation_mode='XYZ';spine.rotation_euler[2]=math.sin(t)*(.012 if role=='Drummer' else .009);spine.keyframe_insert('rotation_euler',frame=frame)
  t=(frame-1)/(FRAMES-1)*math.tau;pb=rig.pose.bones['head'];pb.rotation_mode='XYZ';pb.rotation_euler[0]=(.19 if role=='Drummer' else -.03)+math.sin(t*4)*(.06 if role=='Drummer' else .025);pb.rotation_euler[2]=math.sin(t)*(.055 if role=='Bassist' else .075);pb.keyframe_insert('rotation_euler',frame=frame)
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='POSE');bpy.ops.pose.select_all(action='SELECT');bpy.ops.nla.bake(frame_start=1,frame_end=FRAMES,only_selected=False,visual_keying=True,clear_constraints=True,use_current_action=True,bake_types={'POSE'});bpy.ops.object.mode_set(mode='OBJECT');rig.animation_data.action.name=MEMBERS[role][0]+' performance';rig.select_set(False)
 if role=='Drummer':
  bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
  stickmat=material('Maple drumsticks',color=(.46,.29,.12,1),rough=.72)
  for side,sgn in [('L',1),('R',-1)]:
   wrist=rig.pose.bones['wrist.'+side];direction=Vector((sgn*.45,-.65,-.4)).normalized()
   grip=rig.matrix_world@wrist.tail
   bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=.013,radius2=.007,depth=.75,location=grip+direction*.2)
   stick=bpy.context.object;stick.name='Drumstick '+side;stick.rotation_euler=direction.to_track_quat('Z','Y').to_euler();stick.data.materials.append(stickmat)
   bpy.context.view_layer.update();world=stick.matrix_world.copy();stick.parent=rig;stick.parent_type='BONE';stick.parent_bone='wrist.'+side;stick.matrix_world=world

# Inspectable source and an efficient GLB with real anatomical geometry/skin.
for ob in list(bpy.data.objects):
 if ob.type=='EMPTY':bpy.data.objects.remove(ob,do_unlink=True)
bpy.context.scene.frame_set(1);bpy.context.scene.render.fps=30
bpy.context.scene.render.filepath='//'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets-src/musicians.blend'))
# Keep the editable scene portable: project-relative image paths, packed pixels.
bpy.ops.file.make_paths_relative();bpy.ops.file.pack_all()
for im in bpy.data.images:
 for pf in im.packed_files:pf.filepath=im.filepath # packing records absolute source paths
bpy.ops.wm.save_mainfile()
bpy.ops.export_scene.gltf(filepath=str(ROOT/'dist/models/musicians-v6.glb'),export_format='GLB',export_animations=True,export_force_sampling=True,export_nla_strips=False,export_image_format='AUTO',export_yup=True)
print('MUSICIANS_READY',S,top-foot)
