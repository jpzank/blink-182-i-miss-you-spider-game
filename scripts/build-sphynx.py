"""Original Sphynx reconstruction inspired by reference frames 42/45s.
Run: blender -b --python scripts/build-sphynx.py
All geometry/materials procedural. No downloaded third-party model.
"""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'assets-src/sphynx';OUT.mkdir(exist_ok=True)
random.seed(19)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene; scene.render.engine='CYCLES';scene.cycles.samples=8
parts=[]
def mesh(name,vs,fs):
 m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.update();o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o)
 for p in m.polygons:p.use_smooth=True
 return o
def sphere(name,p,s):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=p);o=bpy.context.object;o.name=name;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);parts.append(o);return o
def muscle(name,a,b,r1,r2=None):
 a,b=Vector(a),Vector(b);o=sphere(name,(a+b)/2,(r1,r2 or r1,(a-b).length*.62));o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
# Underlying anatomy: shoulders, thorax, tucked pelvis and long tapering limbs.
sphere('Thorax',(0,.07,.75),(.197,.25,.32));sphere('Rib cage',(0,.30,.73),(.242,.46,.385));sphere('Pelvis',(0,.77,.42),(.285,.38,.36));sphere('Lumbar curve',(0,.55,.73),(.25,.35,.36))
for sign in [-1,1]:
 sphere('Shoulder blade',(sign*.17,-.06,.99),(.075,.19,.21));sphere('Thigh',(sign*.24,.58,.37),(.137,.30,.28))
 muscle('Hind hock',(sign*.30,.42,.29),(sign*.30,.16,.13),.075,.08)
 sphere('Hind foot',(sign*.30,.07,.083),(.095,.20,.079))
 for i in range(4):sphere('Hind toe',(sign*.30+(i-1.5)*.043,-.071-(.016 if i in [1,2] else 0),.065),(.031,.065,.047))
muscle('Grounded upper foreleg',(.185,-.12,.99),(.20,-.18,.59),.058,.065)
muscle('Grounded radius',(.20,-.18,.60),(.21,-.51,.15),.047,.055)
sphere('Grounded wrist',(.21,-.50,.15),(.055,.072,.086));sphere('Grounded paw',(.21,-.63,.073),(.083,.13,.071))
for i in range(4):sphere('Front toes',(.21+(i-1.5)*.037,-.715-(.014 if i in [1,2] else 0),.058),(.026,.052,.044))
muscle('Raised upper foreleg',(-.18,-.10,.99),(-.235,-.25,.57),.057,.066)
muscle('Raised radius',(-.235,-.25,.57),(-.16,-.69,.89),.044,.055)
sphere('Raised wrist',(-.16,-.69,.89),(.05,.068,.066));sphere('Raised paw',(-.13,-.775,.945),(.081,.095,.057))
for i in range(4):sphere('Raised toes',(-.13+(i-1.5)*.035,-.843,.951),(.026,.048,.039))
muscle('Neck',(0,-.13,1.04),(0,-.34,1.27),.16,.17)
# Unequal elliptic rings produce a broad-cheeked wedge, tapering to muzzle.
rings=[(-.20,1.28,.13,.17),(-.29,1.30,.185,.205),(-.41,1.30,.222,.214),(-.51,1.28,.212,.184),(-.58,1.245,.166,.132),(-.635,1.19,.104,.082),(-.69,1.17,.060,.052)]
vs=[];fs=[];N=48
for y,z,rx,rz in rings:
 for j in range(N):
  a=j*2*math.pi/N; vs.append((rx*math.cos(a),y,z+rz*math.sin(a)))
for k in range(len(rings)-1):
 for j in range(N):fs.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
fs.append(tuple(reversed(range(N))));fs.append(tuple((len(rings)-1)*N+j for j in range(N)));parts.append(mesh('Wedge skull',vs,fs))
# Distinct cheekbones and compact feline whisker pads, rather than round head/muzzle spheres.
for s in [-1,1]:
 sphere('Cheekbone',(s*.157,-.52,1.247),(.069,.061,.094));sphere('Muzzle pad',(s*.043,-.670,1.150),(.048,.039,.027))
sphere('Chin',(0,-.64,1.111),(.068,.061,.025))
# Join/remesh provides uninterrupted skin over torso, limbs and head.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();body=bpy.context.object;body.name='Sphynx continuous skin';bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
rem=body.modifiers.new('Continuous anatomical surface','REMESH');rem.mode='VOXEL';rem.voxel_size=.009;rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name)
sm=body.modifiers.new('Soft tissue','SMOOTH');sm.factor=.72;sm.iterations=8;bpy.ops.object.modifier_apply(modifier=sm.name)
# Fine folds from real skin contraction: forehead, neck, upper chest and shoulders.
for v in body.data.vertices:
 x,y,z=v.co;n=v.normal
 forehead=math.exp(-((x/.23)**6+((z-1.405)/.075)**4+((y+.43)/.23)**4))
 neck=math.exp(-((x/.19)**4+((z-1.05)/.16)**4+((y+.28)/.17)**4))
 shoulder=math.exp(-(((abs(x)-.18)/.13)**4+((z-.96)/.16)**4+((y+.03)/.19)**4))
 amp=.0021*forehead*math.sin((z+abs(x)*.17+.01*math.sin(x*43))*175)+.0028*neck*math.sin((z+x*x*.5+.008*math.sin(x*31))*130)+.0017*shoulder*math.sin((z+y*.4+.012*math.sin(y*39))*145)
 v.co+=n*amp
for p in body.data.polygons:p.use_smooth=True
dec=body.modifiers.new('Web detail budget','DECIMATE');dec.ratio=.38;bpy.ops.object.modifier_apply(modifier=dec.name)
# Material helpers.
def simple(name,col,rough=.58,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
skin=bpy.data.materials.new('Ivory rose Sphynx skin');skin.use_nodes=True;nodes=skin.node_tree.nodes;links=skin.node_tree.links;pr=nodes.get('Principled BSDF');pr.inputs['Roughness'].default_value=.61;pr.inputs['Subsurface Weight'].default_value=.075
tex=nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=6;tex.inputs['Detail'].default_value=3.5;tex.inputs['Roughness'].default_value=.78
ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.16;ramp.color_ramp.elements[0].color=(.29,.205,.175,1);ramp.color_ramp.elements[1].position=.84;ramp.color_ramp.elements[1].color=(.57,.445,.34,1);links.new(tex.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs['Color'],pr.inputs['Base Color'])
pores=nodes.new('ShaderNodeTexNoise');pores.inputs['Scale'].default_value=160;pores.inputs['Detail'].default_value=2
bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.009;links.new(pores.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],pr.inputs['Normal']);body.data.materials.append(skin)
pink=simple('Inner ear muted rose',(.34,.19,.155),.67);rimskin=simple('Fine fold ivory',(.45,.335,.263),.66);nosemat=simple('Soft charcoal rose nose',(.09,.047,.04),.54);eyedge=simple('Thin natural eyelid',(.115,.095,.064),.65);iris=simple('Golden green irises',(.265,.29,.088),.23);pupilmat=simple('Vertical black pupil',(.004,.006,.004),.12);corneamat=simple('Small corneal reflection',(.54,.52,.39),.12);padmat=simple('Paw pads',(.235,.138,.13),.75)
# Compact original iris texture: radial pigment fibers and a narrow vertical pupil.
eyeimage=bpy.data.images.new('Sphynx iris fibers and slit',width=256,height=256);pix=[]
for iy in range(256):
 for ix in range(256):
  xx=(ix-127.5)/127.5;zz=(iy-127.5)/127.5;r=math.sqrt(xx*xx+zz*zz);a=math.atan2(zz,xx);grain=(math.sin(a*91+r*20)+.5*math.sin(a*153-r*35))*.035;edge=max(.38,1-max(0,r-.65)*1.5)
  col=[(.24+grain)*edge,(.275+grain)*edge,(.092+grain*.5)*edge]
  if abs(zz)<.9 and abs(xx)<.105*math.sqrt(max(0,1-(zz/.9)**2)):col=[.005,.007,.004]
  pix.extend([*col,1])
eyeimage.pixels=pix;eyeimage.filepath_raw=str(OUT/'iris.png');eyeimage.file_format='PNG';eyeimage.save();it=iris.node_tree.nodes.new('ShaderNodeTexImage');it.image=eyeimage;iris.node_tree.links.new(it.outputs['Color'],iris.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
headparts=[];pawparts=[];tailparts=[]
def curve(name,points,radius,mat,group=None):
 cv=bpy.data.curves.new(name,'CURVE');cv.dimensions='3D';cv.resolution_u=4;cv.bevel_depth=radius;cv.bevel_resolution=2;s=cv.splines.new('POLY');s.points.add(len(points)-1)
 for p,co in zip(s.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,cv);bpy.context.collection.objects.link(o);o.data.materials.append(mat)
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.select_set(False)
 if group is not None:group.append(o)
 return o
# Large thin, concave triangular ears. Deep interior cup and softly rolled outer rim.
for sign in [-1,1]:
 # Front facing camera (-Y); tip is slightly splayed out, not vertical bunny ears.
 a=Vector((sign*.095,-.305,1.397));b=Vector((sign*.372,-.24,1.412));c=Vector((sign*.325,-.165,1.79));vv=[];ff=[];n=22;indices={}
 for i in range(n+1):
  for j in range(n+1-i):
   u=i/n;v=j/n;w=1-u-v;p=a*w+b*u+c*v
   # Cavity bows backwards; narrow forward rim gives thickness and readable structure.
   p.y+=.09*27*u*v*w;p.x+=sign*.046*math.sin(math.pi*v)*(u-w);p.z+=.018*math.sin(math.pi*u)*(1-v);indices[(i,j)]=len(vv);vv.append(tuple(p))
 for i in range(n):
  for j in range(n-i):
   ff.append((indices[i,j],indices[i+1,j],indices[i,j+1]))
   if j<n-i-1:ff.append((indices[i+1,j],indices[i+1,j+1],indices[i,j+1]))
 ear=mesh(('Left' if sign<0 else 'Right')+' cupped ear',vv,ff);ear.data.materials.append(pink);solid=ear.modifiers.new('Ear cartilage thickness','SOLIDIFY');solid.thickness=.012;solid.offset=1
 sub=ear.modifiers.new('Soft ear cartilage','SUBSURF');sub.levels=1;bpy.context.view_layer.objects.active=ear;ear.select_set(True)
 for mod in list(ear.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 ear.select_set(False);headparts.append(ear)
 pts=[]
 for va,vb in [(a,b),(b,c),(c,a)]:
  for k in range(16):
   p=va.lerp(vb,k/16);v=max(0,(p.z-1.40)/.39);u=max(0,(abs(p.x)-.095-.23*v)/.277);w=1-u-v;p.x+=sign*.046*math.sin(math.pi*v)*(u-w);p.z+=.018*math.sin(math.pi*u)*(1-v);p.y-=.003;pts.append(tuple(p))
 pts.append(pts[0]);curve('Rolled ear cartilage',pts,.009,rimskin,headparts)
 # A short inner tragus folds into each opening.
 curve('Ear tragus',[(sign*.134,-.32,1.41),(sign*.173,-.295,1.45),(sign*.214,-.275,1.475),(sign*.248,-.255,1.46)],.014,rimskin,headparts)
# Eyes are seated on the true skull surface so pupils and lids never clip into skin.
bvh=BVHTree.FromPolygons([v.co for v in body.data.vertices],[list(p.vertices) for p in body.data.polygons])
def front_skin(x,z):
 hit=bvh.ray_cast(Vector((x,-2,z)),Vector((0,1,0)))[0]
 return hit.y if hit is not None else -.63
# Almond eye surfaces follow the sloping skull, with slight corneal bulge.
for sign in [-1,1]:
 center=Vector((sign*.124,front_skin(sign*.124,1.284)-.01,1.284));width=.065;height=.026;vs=[tuple(center+Vector((0,-.012,0)))];fs=[];N=48
 def edge(t):
  xx=math.cos(t)*width;zz=math.sin(t)*height*(.85+.15*abs(math.sin(t)))+sign*xx*.17;x=center.x+xx;z=center.z+zz;return Vector((x,front_skin(x,z)-.006,z))
 for i in range(N):vs.append(tuple(edge(i*2*math.pi/N)))
 for j in range(N):fs.append((0,j+1,(j+1)%N+1))
 eye=mesh('Narrow almond eye',vs,fs);eye.data.materials.append(iris);headparts.append(eye)
 uv=eye.data.uv_layers.new(name='Iris UV')
 for poly in eye.data.polygons:
  for li in poly.loop_indices:
   vi=eye.data.loops[li].vertex_index;angle=(vi-1)*2*math.pi/N;uv.data[li].uv=(.5,.5) if vi==0 else (.5+.5*math.cos(angle),.5+.5*math.sin(angle))
 curve('Upper lower eyelid margin',[tuple(edge(i*2*math.pi/N)) for i in range(N+1)],.006,eyedge,headparts)
# Broad feline nose and small mouth seams.
nose=mesh('Sphynx triangular nose',[(-.038,-.710,1.193),(.038,-.710,1.193),(0,-.720,1.165),(-.03,-.697,1.20),(.03,-.697,1.20)],[(0,1,2),(0,3,4,1),(0,2,3),(1,4,2),(2,4,3)]);nose.data.materials.append(nosemat);bev=nose.modifiers.new('Soft nose','BEVEL');bev.width=.009;bev.segments=3;bpy.context.view_layer.objects.active=nose;bpy.ops.object.modifier_apply(modifier=bev.name);headparts.append(nose)
curve('Mouth philtrum',[(0,-.714,1.165),(0,-.712,1.149)],.003,nosemat,headparts)
for sign in [-1,1]:
 curve('Soft mouth corner',[(0,-.712,1.149),(sign*.024,-.710,1.14),(sign*.052,-.695,1.142)],.0025,nosemat,headparts)
 # Sphynx has tiny sparse whisker stubble; avoid long cartoon wires.
 for i in range(3):curve('Whisker follicle',[(sign*(.056+i*.01),-.709+i*.009,1.163-i*.005),(sign*(.066+i*.011),-.713+i*.009,1.164-i*.005)],.0008,rimskin,headparts)
# Paw pads glimpsed while grooming.
for i in range(3):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=(-.13+(i-1)*.041,-.82,1.002));o=bpy.context.object;o.name='Raised paw toe pad';o.scale=(.02,.024,.006);o.data.materials.append(padmat);pawparts.append(o)
# Long tapering tail follows a natural S, root joins pelvis.
pts=[Vector(p) for p in [(0,.98,.49),(-.14,1.18,.43),(-.39,1.36,.26),(-.68,1.43,.17),(-.97,1.40,.20),(-1.19,1.25,.34),(-1.29,1.02,.45),(-1.26,.85,.47)]]
def catmull(p0,p1,p2,p3,t):return .5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
path=[];ext=[pts[0]]+pts+[pts[-1]]
for k in range(len(pts)-1):
 for j in range(12):path.append(catmull(ext[k],ext[k+1],ext[k+2],ext[k+3],j/12))
path.append(pts[-1]);vs=[];fs=[];R=12
for i,p in enumerate(path):
 tangent=(path[min(i+1,len(path)-1)]-path[max(i-1,0)]).normalized();basis=tangent.cross(Vector((0,0,1))).normalized();up=tangent.cross(basis).normalized();radius=.057*(1-i/(len(path)-1))**.65+.006
 for j in range(R):vs.append(tuple(p+radius*(math.cos(j*2*math.pi/R)*basis+math.sin(j*2*math.pi/R)*up)))
for i in range(len(path)-1):
 for j in range(R):fs.append((i*R+j,i*R+(j+1)%R,(i+1)*R+(j+1)%R,(i+1)*R+j))
fs.append(tuple(reversed(range(R))));fs.append(tuple((len(path)-1)*R+j for j in range(R)));tail=mesh('Long slender curved tail',vs,fs);tail.data.materials.append(skin);tailparts.append(tail)
# Bake skin color and micro-normal to self-contained texture maps.
def bake_skin(objects):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name='Sphynx continuous skin and tail';bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.1519,island_margin=.012);bpy.ops.object.mode_set(mode='OBJECT')
 # Merged objects share same skin material.
 image=bpy.data.images.new('Sphynx mottled ivory skin',width=1024,height=1024);node=nodes.new('ShaderNodeTexImage');node.image=image;nodes.active=node
 scene.cycles.samples=2;scene.render.bake.use_pass_direct=False;scene.render.bake.use_pass_indirect=False;scene.render.bake.use_pass_color=True;scene.render.bake.margin=12;bpy.ops.object.bake(type='DIFFUSE');image.filepath_raw=str(OUT/'skin-albedo.png');image.file_format='PNG';image.save()
 normal=bpy.data.images.new('Sphynx pores normal',width=1024,height=1024);normal.colorspace_settings.name='Non-Color';node.image=normal;bpy.ops.object.bake(type='NORMAL');normal.filepath_raw=str(OUT/'skin-normal.png');normal.file_format='PNG';normal.save()
 nodes.clear();out=nodes.new('ShaderNodeOutputMaterial');p=nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Roughness'].default_value=.61;p.inputs['Subsurface Weight'].default_value=.06;t=nodes.new('ShaderNodeTexImage');t.image=image;nt=nodes.new('ShaderNodeTexImage');nt.image=normal;nm=nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.7;links.new(t.outputs['Color'],p.inputs['Base Color']);links.new(nt.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],p.inputs['Normal']);links.new(p.outputs[0],out.inputs[0]);return o
body=bake_skin([body,tail]);tailparts=[]
# Minimal skeleton gives an actual grooming loop, without moving the cat through the room.
bpy.ops.object.select_all(action='DESELECT');bpy.ops.object.armature_add();rig=bpy.context.object;rig.name='Sphynx';rig.data.name='Sphynx grooming skeleton';bpy.ops.object.mode_set(mode='EDIT');b=rig.data.edit_bones[0];b.name='body';b.head=(0,.3,.2);b.tail=(0,.3,.7)
for name,head,tail in [('head',(0,-.29,1.21),(0,-.66,1.21)),('paw',(-.23,-.25,.57),(-.15,-.70,.90)),('tail',(-.13,1.17,.41),(-.69,1.42,.19))]:
 b=rig.data.edit_bones.new(name);b.head=head;b.tail=tail;b.parent=rig.data.edit_bones['body']
bpy.ops.object.mode_set(mode='OBJECT')
def bind(o,weights):
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.select_set(False)
 for name in ['body','head','paw','tail']:o.vertex_groups.new(name=name)
 for v in o.data.vertices:
  ws=weights(v.co)
  for n,w in ws.items():
   if w>.0001:o.vertex_groups[n].add([v.index],w,'REPLACE')
 m=o.modifiers.new('Sphynx anatomy animation','ARMATURE');m.object=rig;o.parent=rig

def clamp(v):return min(1,max(0,v))
def weights(v):
 x,y,z=v;head=clamp((z-.96)/.22)*clamp((-y-.15)/.20);paw=clamp((-x-.075)/.07)*clamp((-y-.35)/.22)*clamp((1.10-z)/.14)*clamp((z-.52)/.09);tail=clamp((y-1.02)/.23) if x<.04 else 0
 if (y<-.48 and z>1.045) or (y<-.14 and z>1.215):head=1
 if x<-.045 and y<-.63 and .85<z<1.025:paw=1;head=0
 total=head+paw+tail
 if total>1:head/=total;paw/=total;tail/=total
 return {'head':head,'paw':paw,'tail':tail,'body':max(0,1-head-paw-tail)}
bind(body,weights)
for o in headparts:bind(o,lambda v:{'head':1})
for o in pawparts:bind(o,lambda v:{'paw':1})
# A grooming cat folds forward from its shoulder girdle. Lowering the head and
# extended paw in the bind pose avoids a humanlike upright seated silhouette.
head_delta=Vector((0,-.14,-.27));paw_delta=Vector((0,-.025,-.27))
for ob in rig.children:
 if ob.type!='MESH':continue
 for vert in ob.data.vertices:
  weights_by_name={ob.vertex_groups[g.group].name:g.weight for g in vert.groups};hw=weights_by_name.get('head',0);pw=weights_by_name.get('paw',0);x,y,z=vert.co
  shoulder=math.exp(-((y+.02)/.30)**4)*clamp((z-.69)/.39)*(1-hw)*(1-pw)
  vert.co+=head_delta*hw+paw_delta*pw+Vector((0,-.085,-.095))*shoulder
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
rig.data.edit_bones['head'].head+=head_delta;rig.data.edit_bones['head'].tail+=head_delta
rig.data.edit_bones['paw'].tail+=paw_delta
bpy.ops.object.mode_set(mode='OBJECT')
rig['species']='Sphynx cat';rig['reference']='blink-182 I Miss You (2003), grooming cat around 00:42–00:46';rig['orientation']='Blender front -Y, glTF front +Z';rig['source']='Original procedural reconstruction; no source video pixels or third-party mesh embedded.'
scene.render.fps=30;scene.frame_start=1;scene.frame_end=241
for frame in range(1,242,4):
 t=(frame-1)/240*2*math.pi;pb=rig.pose.bones['head'];pb.rotation_mode='XYZ';pb.rotation_euler=(0,0,0)
 # bone local X points across the face, slow nod and short paired grooming strokes.
 pb.rotation_euler.x=-.57+.075*math.sin(4*t)+.024*math.sin(8*t);pb.rotation_euler.y=.045*math.sin(t);pb.rotation_euler.z=-.055+.026*math.sin(2*t);pb.keyframe_insert('rotation_euler',frame=frame)
 pa=rig.pose.bones['paw'];pa.rotation_mode='XYZ';pa.rotation_euler=(.025*math.sin(4*t),.012*math.sin(t),.018*math.sin(4*t));pa.keyframe_insert('rotation_euler',frame=frame)
 ta=rig.pose.bones['tail'];ta.rotation_mode='XYZ';ta.rotation_euler=(.014*math.sin(t),.035*math.sin(t),.045*math.sin(t));ta.keyframe_insert('rotation_euler',frame=frame)
if rig.animation_data:rig.animation_data.action.name='Sphynx grooming • 8s'
scene.frame_set(1)
# Studio preview is only in .blend; export selects the model only.
world=bpy.data.worlds.new('Preview charcoal');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.06,.063,.07,1);world.node_tree.nodes['Background'].inputs[1].default_value=.45;scene.world=world
bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;floor.name='PREVIEW ground';floor.data.materials.append(simple('Preview floor',(.10,.105,.11),.8))
for p,power,size in [((-3,-4,6),650,4),((3,1,4),800,3),((1,-4,2),70,2)]:
 bpy.ops.object.light_add(type='AREA',location=p);o=bpy.context.object;o.name='PREVIEW softbox';o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.8))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(3.3,-4.7,2.45));cam=bpy.context.object;cam.name='PREVIEW camera';cam.rotation_euler=(Vector((-.1,.30,.77))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=59;scene.camera=cam
scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.cycles.samples=16;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'sphynx.blend'))
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
for o in list(rig.children):o.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(ROOT/'dist/models/sphynx-v6.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIONS',export_frame_range=True,export_force_sampling=True,export_skins=True,export_yup=True,export_apply=False)
meshes=[o.data for o in rig.children if o.type=='MESH']
for m in meshes:m.calc_loop_triangles()
triangles=sum(len(m.loop_triangles) for m in meshes);(OUT/'stats.json').write_text(json.dumps({'triangles':triangles,'vertices':sum(len(o.data.vertices) for o in rig.children if o.type=='MESH'),'height':1.52,'bodyLengthWithoutTail':1.94,'totalBoundsApprox':{'x':[-1.32,.42],'y':[-.93,1.52],'z':[0,1.52]},'clip':'Sphynx grooming • 8s','root':'Sphynx','bones':['body','head','paw','tail']},indent=2))
bpy.ops.render.render(write_still=True)
