"""Two clothed adult women reclining, interpreted from the I Miss You video.
Standalone MakeHuman CC0 conversion, dress tailoring and repose. Blender 4+.
"""
import bpy, json, math, random
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'assets-src/makehuman'; OUT=ROOT/'assets-src/reclining-women'; SRC=OUT/'source'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def objdata(path):
 vs=[];uv=[];faces=[];groups={};group=''
 for ln in Path(path).read_text().splitlines():
  t=ln.split()
  if not t:continue
  if t[0]=='v':vs.append(Vector(map(float,t[1:4])))
  elif t[0]=='vt':uv.append(tuple(map(float,t[1:3])))
  elif t[0]=='g':group=t[1]
  elif t[0]=='f':
   f=[(int(p.split('/')[0])-1,int(p.split('/')[1])-1 if '/' in p and p.split('/')[1] else 0) for p in t[1:]];faces.append((group,f));groups.setdefault(group,set()).update(i for i,j in f)
 return vs,uv,faces,groups
base,uv,faces,groups=objdata(BASE/'base.obj');morphed=[v.copy() for v in base]
for name in ['universal-female-young-averagemuscle-averageweight.target','caucasian-female-young.target']:
 for ln in (SRC/name).read_text().splitlines():
  t=ln.split()
  if len(t)==4 and t[0].isdigit():morphed[int(t[0])]+=Vector(map(float,t[1:]))
foot=min(morphed[i].y for i in groups['body']);top=max(morphed[i].y for i in groups['body']);S=3.48/(top-foot);anatomy=[v.copy() for v in morphed]
def conv(v):return Vector((v.x*S,-v.z*S,(v.y-foot)*S))
rigdata=json.load(open(BASE/'default.mhskel'));weights=json.load(open(BASE/'default_weights.mhw'))['weights'];vw={}
for name,pairs in weights.items():
 for i,w in pairs:vw.setdefault(i,{})[name]=w
materials={}
def material(name,texture=None,color=(.2,.2,.2,1),rough=.8,alpha=False):
 if name in materials:return materials[name]
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=color;p.inputs['Roughness'].default_value=rough
 if texture:
  tex=n.new('ShaderNodeTexImage');im=bpy.data.images.load(str(texture),check_existing=True)
  if im.size[0]>1536:im.scale(1536,1536)
  tex.image=im;m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
  if alpha:m.node_tree.links.new(tex.outputs['Alpha'],p.inputs['Alpha']);m.surface_render_method='DITHERED'
 if 'skin' in name:p.inputs['Subsurface Weight'].default_value=.08
 materials[name]=m;return m
skin=material('Adult skin',SRC/'skins/young_caucasian_female/young_lightskinned_female_diffuse.png',rough=.65)
eye=material('Brown eyes',BASE/'brown_eye.png',rough=.27)
ivory=material('Ivory silk crepe',color=(.68,.61,.44,1),rough=.83);ivory.node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value=.25
pearl=material('Pale champagne beading',color=(.78,.67,.46,1),rough=.4);dark=material('Midnight black hair',color=(.008,.005,.005,1),rough=.42)
red=material('Deep garnet choker',color=(.14,.006,.009,1),rough=.35)
# Compact original linen weave maps for close-range textile response.
rng=random.Random(21);size=256;pixels=[];normals=[]
for y in range(size):
 for x in range(size):
  line=.012*math.sin(x*math.pi/2)+.008*math.sin(y*math.pi/2);noise=rng.uniform(-.008,.008);f=1+line+noise
  pixels.extend((.77*f,.71*f,.59*f,1));normals.extend((.5+.11*math.cos(x*math.pi/2),.5+.07*math.cos(y*math.pi/2),.985,1))
for name,px,isnormal in [('ivory-weave',pixels,False),('ivory-weave-normal',normals,True)]:
 im=bpy.data.images.new(name,width=size,height=size,alpha=False);im.pixels[:]=px;im.filepath_raw=str(OUT/(name+'.png'));im.file_format='PNG';im.save();node=ivory.node_tree.nodes.new('ShaderNodeTexImage');node.image=im
 uvnode=ivory.node_tree.nodes.new('ShaderNodeTexCoord');mapping=ivory.node_tree.nodes.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs['Scale'].default_value=8;ivory.node_tree.links.new(uvnode.outputs['UV'],mapping.inputs[0]);ivory.node_tree.links.new(mapping.outputs[0],node.inputs['Vector'])
 if isnormal:
  im.colorspace_settings.name='Non-Color';normal=ivory.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.2;ivory.node_tree.links.new(node.outputs['Color'],normal.inputs['Color']);ivory.node_tree.links.new(normal.outputs['Normal'],ivory.node_tree.nodes.get('Principled BSDF').inputs['Normal'])
 else:ivory.node_tree.links.new(node.outputs['Color'],ivory.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])

allrigs=[]
def rig_for(name):
 arm=bpy.data.armatures.new(name+' skeleton');rig=bpy.data.objects.new(name,arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 joints={n:sum((morphed[i] for i in ids),Vector())/len(ids) for n,ids in rigdata['joints'].items()}
 for n,b in rigdata['bones'].items():
  bone=arm.edit_bones.new(n);bone.head=conv(joints[b['head']]);bone.tail=conv(joints[b['tail']]);
  if (bone.tail-bone.head).length<.0001:bone.tail.z+=.001
 for n,b in rigdata['bones'].items():
  if b.get('parent'):arm.edit_bones[n].parent=arm.edit_bones[b['parent']]
 bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False);allrigs.append(rig);return rig

def mesh(name,verts,uvs,fs,mat,rig,weightset,convert=True):
 used=sorted({i for _,f in fs for i,j in f});lookup={i:j for j,i in enumerate(used)};geo=bpy.data.meshes.new(name);geo.from_pydata([conv(verts[i]) if convert else verts[i] for i in used],[],[[lookup[i] for i,j in f] for _,f in fs]);geo.update();ob=bpy.data.objects.new(name,geo);bpy.context.collection.objects.link(ob);ob.data.materials.append(mat);ob.parent=rig
 layer=geo.uv_layers.new(name='UVMap')
 for p,(_,f) in zip(geo.polygons,fs):
  p.use_smooth=True
  for loop,(_,j) in zip(p.loop_indices,f):layer.data[loop].uv=uvs[j] if uvs else (0,0)
 for original in used:
  d=weightset[original] if isinstance(weightset,list) else weightset.get(original,{})
  for n,w in d.items():
   if n in rig.data.bones:
    vg=ob.vertex_groups.get(n) or ob.vertex_groups.new(name=n);vg.add([lookup[original]],w,'REPLACE')
 mod=ob.modifiers.new('Repose','ARMATURE');mod.object=rig;return ob

def proxy(path):
 mapping=[];scales=[1,1,1];mode=''
 for ln in Path(path).read_text().splitlines():
  t=ln.split()
  if not t or t[0].startswith('#'):continue
  if t[0] in ['x_scale','y_scale','z_scale']:
   ax={'x_scale':0,'y_scale':1,'z_scale':2}[t[0]];a,b=int(t[1]),int(t[2]);scales[ax]=abs(morphed[a][ax]-morphed[b][ax])/float(t[3]);continue
  if t[0]=='verts':mode='verts';continue
  if t[0]=='delete_verts':mode='delete';continue
  if not (t[0][0].isdigit() or t[0][0]=='-'):continue
  if mode=='verts':
   if len(t)==1:mapping.append(([int(t[0])],[1.],Vector((0,0,0))))
   elif len(t)==9:mapping.append((list(map(int,t[:3])),list(map(float,t[3:6])),Vector(map(float,t[6:9]))))
 out=[];ow=[]
 for inds,ws,offset in mapping:
  p=sum((morphed[i]*w for i,w in zip(inds,ws)),Vector())+Vector(tuple(offset[i]*scales[i] for i in range(3)));out.append(p);d={}
  for i,ww in zip(inds,ws):
   for n,w in vw.get(i,{}).items():d[n]=d.get(n,0)+w*ww
  ow.append({n:w for n,w in d.items() if w>.005})
 return out,ow

def poly_mesh(name,verts,fs,mat,rig,weights):
 ob=mesh(name,[Vector(v) for v in verts],[],[('',[(i,0) for i in f]) for f in fs],mat,rig,weights,False)
 for loop in ob.data.loops:
  p=ob.data.vertices[loop.vertex_index].co;ob.data.uv_layers.active.data[loop.index].uv=((math.atan2(p.y,p.x)/math.tau+1)%1,p.z*.4)
 return ob
def tube(name,points,radius,mat,rig,bone='spine03',sides=6):
 vs=[];fs=[]
 for j,p in enumerate(points):
  p=Vector(p);t=(Vector(points[min(j+1,len(points)-1)])-Vector(points[max(0,j-1)])).normalized();a=t.cross(Vector((0,1,0))).normalized()
  if a.length<.1:a=t.cross(Vector((1,0,0))).normalized()
  b=t.cross(a).normalized()
  for k in range(sides):vs.append(p+radius*(a*math.cos(k*math.tau/sides)+b*math.sin(k*math.tau/sides)))
 for j in range(len(points)-1):
  for k in range(sides):fs.append((j*sides+k,j*sides+(k+1)%sides,(j+1)*sides+(k+1)%sides,(j+1)*sides+k))
 return poly_mesh(name,vs,fs,mat,rig,[{bone:1} for _ in vs])

def makeup(ob,rig,index):
 # Paint period eye shadow and muted lipstick through object-space masks,
 # then bake into the original CC0 facial UVs for a plain portable albedo.
 m=bpy.data.materials.new('Period makeup bake');m.use_nodes=True;n=m.node_tree.nodes;n.clear();links=m.node_tree.links
 out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');links.new(em.outputs[0],out.inputs['Surface']);tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(SRC/'skins/young_caucasian_female/young_lightskinned_female_diffuse.png'),check_existing=True)
 attr=ob.data.color_attributes.new(name='PeriodMakeup',type='FLOAT_COLOR',domain='CORNER');mask=ob.data.color_attributes.new(name='MakeupMask',type='FLOAT_COLOR',domain='CORNER')
 ex=rig.data.bones['eye.L'].head_local.x;ez=rig.data.bones['eye.L'].head_local.z
 mouth=conv(morphed[493]).z
 for loop in ob.data.loops:
  p=ob.data.vertices[loop.vertex_index].co;eyeval=math.exp(-((abs(p.x)-ex)/.06)**2-((p.z-ez-.02)/.040)**2)*(.7 if p.z>ez else .28)
  lipval=math.exp(-(p.x/.055)**4-((p.z-mouth)/.018)**4)*.78
  front=max(0,min(1,(-p.y-.18)/.08));value=max(eyeval,lipval)*front
  col=(.045,.032,.038,1) if eyeval>lipval else (.22,.025,.035,1)
  attr.data[loop.index].color=col;mask.data[loop.index].color=(value,value,value,1)
 a=n.new('ShaderNodeVertexColor');a.layer_name='PeriodMakeup';b=n.new('ShaderNodeVertexColor');b.layer_name='MakeupMask';mix=n.new('ShaderNodeMixRGB');mix.blend_type='MIX';links.new(b.outputs['Color'],mix.inputs[0]);links.new(tex.outputs['Color'],mix.inputs[1]);links.new(a.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],em.inputs['Color']);ob.data.materials.clear();ob.data.materials.append(m)
 baked=bpy.data.images.new('Period face '+str(index),width=1536,height=1536,alpha=False);target=n.new('ShaderNodeTexImage');target.image=baked;n.active=target
 bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=1;bpy.context.scene.render.bake.margin=12;bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.bake(type='EMIT')
 path=OUT/('period-face-'+str(index)+'.png');baked.filepath_raw=str(path);baked.file_format='PNG';baked.save();ob.data.materials.clear();ob.data.materials.append(material('Period skin '+str(index),path,rough=.66));ob.select_set(False)
 for a in list(ob.data.color_attributes):ob.data.color_attributes.remove(a)

for index,name in enumerate(['Woman with black bob','Woman with finger waves']):
 morphed=[v.copy() for v in anatomy]
 if index:
  for v in morphed:
   if v.y>6.8:v.x*=.965;v.y=7+(v.y-7)*1.025
 rig=rig_for(name);rig['adult']=True;rig['source']='Original clothed figure inspired by I Miss You video; CC0 MakeHuman anatomy'
 # Keep the clavicle and upper chest behind the continuous opaque neckline.
 bodyfaces=[];bodicefaces=[]
 for g,f in faces:
  if g!='body':continue
  cs=[conv(morphed[i]) for i,j in f];c=sum(cs,Vector())/len(cs)
  torso=abs(c.x)<.65 and 1.61<c.z<2.76
  armweight=max(sum(w for n,w in vw.get(i,{}).items() if 'arm' in n or 'wrist' in n or 'finger' in n or 'metacarpal' in n) for i,j in f)
  if torso and armweight<.35:
   bodicefaces.append((g,f))
   if c.z>2.66:bodyfaces.append((g,f))
  elif c.z>2.55 or armweight>.3:bodyfaces.append((g,f))
 body=mesh(name+' face and arms',morphed,uv,bodyfaces,skin,rig,vw);makeup(body,rig,index)
 # Opaque tailored slip with a smooth continuous neckline and fabric volume.
 vs=[];fs=[];ws=[];N=72;R=30
 def dress_width(z):
  if z<2.18:return .35-.06*(z-1.78)/.40
  if z<2.55:return .29+.095*(z-2.18)/.37
  return .385-.045*(z-2.55)/.23
 def dress_point(z,a):
  rx=dress_width(z);front=.34+.060*math.sin(max(0,min(1,(z-2.1)/.65))*math.pi);dep=front if math.sin(a)<0 else .15
  return ((rx+.005*math.sin(a*17+z*4))*math.cos(a),dep*math.sin(a)-.025,z)
 for j in range(R):
  z=1.78+j/(R-1)*1.0
  for k in range(N):
   a=k/N*math.tau;p=Vector(dress_point(z,a));p.z-=.035*max(0,-math.sin(a))*(j/(R-1))**5;vs.append(p);ws.append({'spine03':1})
 for j in range(R-1):
  for k in range(N):fs.append((j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k))
 bodice=poly_mesh(name+' tailored slip',vs,fs,ivory,rig,ws)
 for z in [2.78,2.12]:
  pts=[dress_point(z,k/72*math.tau) for k in range(73)];tube(name+' beaded trim',pts,.007,pearl,rig,'spine03',6)
 # Full-length loose skirt: irregular small folds and softly gathered hem.
 vs=[];fs=[];ws=[];N=72;R=42
 for j in range(R):
  z=.09+j/(R-1)*1.87;h=z/1.96;rx=.38-.03*h;ry=.265-.01*h
  for k in range(N):
   a=k/N*math.tau;fold=(.009+.01*(1-h))*math.sin(a*13+j*.20)+.005*math.sin(a*27-j*.12);x=(rx+fold)*math.cos(a);y=(ry+fold*.8)*math.sin(a)-.025-.09*math.exp(-((z-1.05)/.32)**2)
   zz=z+.016*math.sin(a*7)*(1-h);vs.append((x,y,zz));blend=max(0,min(1,(z-1.62)/.22));ws.append({'spine03':blend,'root':1-blend})
 for j in range(R-1):
  for k in range(N):fs.append((j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k))
 skirt=poly_mesh(name+' long folded skirt',vs,fs,ivory,rig,ws)
 # Satin straps and layered beaded fringes sit on the fully opaque bodice.
 for sign in [-1,1]:
  tube(name+' shoulder strap',[(sign*.33,-.24,2.70),(sign*.36,-.20,2.88),(sign*.37,-.09,3.01),(sign*.36,.07,2.94),(sign*.32,.16,2.72)],.022,pearl,rig,'spine03',8)
 for row in range(3):
  z=1.9+row*.15
  for k in range(48):
   a=k/48*math.tau;pts=[]
   for dz in [0,-.055,-.11]:
    p=Vector(dress_point(z+dz,a));p.x*=1.015;p.y*=1.025;pts.append(p)
   tube(name+' silk fringe',pts,.0025,pearl,rig,'spine03',5)
 # Fitted CC0 black bob, shortened and waved for second figure.
 hairname='bob01';folder=SRC/'hair'/hairname;v,u,f,g=objdata(folder/(hairname+'.obj'));fit,w=proxy(folder/(hairname+'.mhclo'))
 for v in fit:
  p=conv(v)
  if p.z<3.37 and p.y<-.21 and abs(p.x)<.12:v.y+=(3.37-p.z)*.80/S
  if index:
   v.x*=1.025;v.x+=.045*math.sin(v.y*12+v.z*3);v.z+=.03*math.sin(v.y*10)
 hair=mesh(name+' black coiffure',fit,u,f,material('Black bob strands',folder/(hairname+'_diffuse.png'),rough=.67,alpha=True),rig,w)
 # Bake dark hair to avoid exporter losing a multiply node.
 hairmat=hair.data.materials[0];tex=next(n for n in hairmat.node_tree.nodes if n.type=='TEX_IMAGE');im=tex.image
 if index==0:
  pix=list(im.pixels)
  for j in range(0,len(pix),4):pix[j]*=.16;pix[j+1]*=.14;pix[j+2]*=.16
  im.pixels[:]=pix;im.filepath_raw=str(OUT/'black-bob.png');im.file_format='PNG';im.save()
 # Eyes, original dark iris texture.
 v,u,f,g=objdata(BASE/'eyes.obj');fit,w=proxy(BASE/'eyes.mhclo');mesh(name+' eyes',fit,u,f,eye,rig,w)
 # Visible sculpted finger waves and a garnet necklace distinguish the second.
 if index:
  for sign in [-1,1]:
   for curl in range(2):
    pts=[]
    for j in range(25):
     a=j/24*math.tau*1.55;rad=.029*(1-j/30);pts.append((sign*(.135+curl*.018)+rad*math.cos(a),-.265+.015*curl,3.32-curl*.075+rad*math.sin(a)))
    tube('Dark finger curl',pts,.005,dark,rig,'head',6)
  pts=[(.135*math.cos(k/40*math.tau),-.03+.12*math.sin(k/40*math.tau),2.965) for k in range(41)];tube('Garnet ribbon choker',pts,.025,red,rig,'neck01',8)
  for k in range(14):
   a=k/14*math.tau;bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=6,radius=.025,location=(.15*math.cos(a),-.035+.135*math.sin(a),2.92));ob=bpy.context.object;ob.name='Garnet necklace bead';ob.data.materials.append(red);bpy.ops.object.transform_apply(location=True,rotation=False,scale=False);ob.parent=rig;vg=ob.vertex_groups.new(name='neck01');vg.add(list(range(len(ob.data.vertices))),1,'REPLACE');mo=ob.modifiers.new('Repose','ARMATURE');mo.object=rig
 # Anatomical two-segment arm solve, hands relaxed on dress / pillow.
 def aim(n,head,dr):
  p=rig.pose.bones[n];rest=p.bone;rot=(rest.tail_local-rest.head_local).rotation_difference(dr);p.rotation_mode='QUATERNION';p.matrix=Matrix.Translation(head)@rot.to_matrix().to_4x4()@rest.matrix_local.to_3x3().to_4x4();bpy.context.view_layer.update()
 for side,sign in [('L',1),('R',-1)]:
  if index and side=='L':target=Vector((.43,-.03,3.18));pole=Vector((1.03,.15,2.69))
  elif not index and side=='R':target=Vector((-.58,.035,2.03));pole=Vector((-.82,.08,2.43))
  else:target=Vector((sign*(.35 if side=='L' else .43),-.27,1.68 if side=='L' else 2.03));pole=Vector((sign*.86,-.08,2.3))
  names=[p+side for p in ['upperarm01.','upperarm02.','lowerarm01.','lowerarm02.']];bones=[rig.data.bones[n] for n in names];lengths=[b.length for b in bones];shoulder=bones[0].head_local.copy();u=(target-shoulder).normalized();l1=sum(lengths[:2]);l2=sum(lengths[2:]);d=min((target-shoulder).length,l1+l2-.002);target=shoulder+u*d;pole-=shoulder;v=(pole-u*pole.dot(u)).normalized();a=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(.0001,l1*l1-a*a));elbow=shoulder+u*a+v*h;upper=(elbow-shoulder).normalized();lower=(target-elbow).normalized();heads=[shoulder,shoulder+upper*lengths[0],elbow,elbow+lower*lengths[2]]
  for n,head,dr in zip(names,heads,[upper,upper,lower,lower]):aim(n,head,dr)
  aim('wrist.'+side,target,Vector((-.1*sign,-.01,-.24)) if not(index and side=='L') else Vector((-.25,-.04,.08)))
 for p in rig.pose.bones:
  if p.name.startswith('finger'):
   d=p.bone.tail_local-p.bone.head_local;axis=p.bone.matrix_local.to_3x3().inverted()@d.cross(Vector((0,-1,0))).normalized();p.rotation_mode='QUATERNION';p.rotation_quaternion=Quaternion(axis,.15 if '-1.' in p.name else .24)
 # Lay body axis along +X, faces toward +Z and slightly toward -Y.
 rot=Matrix(((0,0,1),(-1,0,0),(0,-1,0)));rig.rotation_euler=(Matrix.Rotation(-.10 if index==0 else .06,3,'X')@rot).to_euler();rig.location=(-1.72,-.72 if index==0 else .72,.265)
 for frame in range(1,182,5):
  t=(frame-1)/180*math.tau;bpy.context.scene.frame_set(frame)
  for p in rig.pose.bones:
   if p.name in ['spine03','spine02','head']:
    p.rotation_mode='XYZ'
    if p.name=='spine03':p.rotation_euler=(.10+(.10 if index else 0)+.006*math.sin(t),.09 if index else -.08,0)
    elif p.name=='spine02':p.rotation_euler=(.045 if index else .015,0,-.015 if index else .015)
    else:p.rotation_euler=(.12 if index else .05,.30 if index else -.35,-.02 if index else .08)
    p.keyframe_insert('rotation_euler',frame=frame)
   else:p.keyframe_insert('rotation_quaternion' if p.rotation_mode=='QUATERNION' else 'rotation_euler',frame=frame);p.keyframe_insert('location',frame=frame)
 rig.animation_data.action.name=name+' subtle breathing'

# Consolidate the beading and fitted clothing by material: low runtime draw calls.
for rig in allrigs:
 mats={}
 for ob in list(rig.children):
  if ob.type=='MESH' and ob.data.materials:mats.setdefault(ob.data.materials[0].name,[]).append(ob)
 for mat,objects in mats.items():
  if len(objects)<2:continue
  bpy.ops.object.select_all(action='DESELECT')
  for ob in objects:ob.select_set(True)
  bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();objects[0].name=rig.name+' '+mat
bpy.context.scene.frame_set(1);bpy.context.scene.render.fps=30
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'reclining-women.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'dist/models/reclining-women-v6.glb'),export_format='GLB',export_animations=True,export_force_sampling=True,export_nla_strips=False,export_yup=True)
# Inspection render: broad frontal soft light, geometric bed plane only for contact.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.025));plane=bpy.context.object;plane.data.materials.append(material('Render backdrop',color=(.025,.031,.028,1)))
bpy.ops.object.camera_add(location=(5,-5.5,5.2));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.32))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=5.2;bpy.context.scene.camera=cam
for loc,power,size in [((0,-2,5),600,5),((1,3,4),420,4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);ob=bpy.context.object;ob.data.energy=power;ob.data.shape='DISK';ob.data.size=size;ob.rotation_euler=(Vector((0,0,0))-ob.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'inspection.png');scene.world.color=(.12,.12,.12);bpy.ops.render.render(write_still=True)
print('RECLINING_WOMEN_READY',S)
