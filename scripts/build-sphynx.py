"""Sphynx cat for the window alcove: anatomical signed-distance sculpture,
baked photographic-style skin maps, layered eyes and an organic grooming loop.

Run: blender -b --python scripts/build-sphynx.py   (Blender 5.x, bundled numpy)

Everything is procedural and original: no third-party mesh, scan, photograph
or video pixels. The body is modelled as a smooth union of anatomical
primitives (skull wedge, cheekbones, whisker pads, scapulae, sagging belly,
folded hind legs, toes, cupped ears, wrapped tail), with skin folds displaced
into the distance field. A dense surface is extracted (naive surface nets),
decimated for the browser, and the dense detail is baked into a normal map.
"""
import bpy, bmesh, math, json, random
import numpy as np
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets-src/sphynx';OUT.mkdir(exist_ok=True)
GLB=ROOT/'dist/models/sphynx-v7.glb'
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU'
rng=np.random.default_rng(42)

# ------------------------------------------------------------------ anatomy
# Blender coordinates: Z up, the cat faces -Y, paws rest on z=0. Seated
# grooming pose: the right forepaw (-X) is raised to the mouth.
P=[]
def V(*a):return np.array(a,np.float32)
def ell(bone,c,r,sub=False):P.append(('ell',bone,V(*c),V(*r),sub))
def cone(bone,a,b,r1,r2):P.append(('cone',bone,V(*a),V(*b),r1,r2))
def ear(bone,side):P.append(('ear',bone,side))
# The head is sculpted around the skull pivot, then seated low on a short,
# thick neck (a seated cat's head sits almost on its shoulders).
PIV=np.array([0,-.16,1.16],np.float32);HS=1.12;HOFF=np.array([0,.03,-.07],np.float32)
def hp(c):return tuple(PIV+(np.array(c,np.float32)-PIV)*HS+HOFF)

# Hindquarters folded under the body, feet pointing forward.
ell('body',(0,.36,.30),(.215,.235,.25))
for s,b in [(1,'body'),(-1,'body')]:
 ell(b,(s*.165,.27,.25),(.13,.24,.20))
 cone(b,(s*.19,.37,.085),(s*.18,.12,.048),.052,.054)
 cone(b,(s*.18,.12,.045),(s*.175,-.10,.036),.055,.046)
 for k,(dx,dy) in enumerate([(-.042,0),(-.015,-.016),(.015,-.016),(.042,0)]):ell(b,(s*.175+dx,-.12+dy,.03),(.022,.03,.026))
ell('body',(0,.12,.34),(.20,.23,.23))          # loose belly skin
cone('spine',(0,.30,.42),(0,.02,.80),.215,.185)
ell('spine',(0,-.06,.66),(.17,.18,.22))           # deep narrow chest
for s in [1,-1]:ell('spine',(s*.115,.03,.90),(.072,.11,.10)) # scapulae
cone('neck',(0,-.02,.90),(0,-.13,1.06),.128,.112)
# Supporting foreleg (+X).
cone('arm.L',(.11,-.06,.86),(.125,-.10,.56),.062,.05)
cone('forearm.L',(.125,-.10,.56),(.115,-.17,.12),.05,.038)
cone('hand.L',(.115,-.17,.12),(.115,-.24,.04),.036,.04)
ell('hand.L',(.115,-.25,.034),(.05,.066,.03))
for dx,dy in [(-.036,0),(-.012,-.016),(.012,-.016),(.036,0)]:ell('hand.L',(.115+dx,-.305+dy,.026),(.02,.026,.024))
# Raised, groomed forepaw (-X), pads turned toward the mouth.
cone('arm.R',(-.11,-.06,.86),(-.15,-.19,.62),.062,.05)
cone('forearm.R',(-.15,-.19,.62),(-.12,-.33,.88),.046,.036)
cone('paw',(-.12,-.33,.88),(-.10,-.385,.975),.036,.04)
ell('paw',(-.10,-.39,.985),(.046,.036,.056))
for dx,dz in [(-.03,-.006),(-.01,.012),(.012,.012),(.032,-.006)]:ell('paw',(-.10+dx,-.395,1.04+dz),(.018,.021,.019))
# Wedge head: cranium, high cheekbones, short muzzle, whisker pads, strong chin.
ell('head',hp((0,-.22,1.23)),tuple(np.array((.13,.13,.112))*HS))
ell('head',hp((0,-.15,1.21)),tuple(np.array((.105,.10,.10))*HS))
for s in [1,-1]:
 ell('head',hp((s*.093,-.285,1.175)),tuple(np.array((.064,.075,.058))*HS))
 ell('head',hp((s*.058,-.322,1.12)),tuple(np.array((.058,.058,.048))*HS))
 ell('head',hp((s*.03,-.388,1.122)),tuple(np.array((.034,.03,.027))*HS))
 ell('head',hp((s*.058,-.322,1.252)),tuple(np.array((.05,.03,.022))*HS))
 ell('head',hp((s*.062,-.338,1.214)),tuple(np.array((.038,.03,.022))*HS),True)  # eye socket
 ear('ear.'+('L' if s>0 else 'R'),s)
ell('head',hp((0,-.352,1.135)),tuple(np.array((.068,.058,.05))*HS))
cone('head',hp((0,-.30,1.27)),hp((0,-.392,1.172)),.034*HS,.026*HS)
ell('head',hp((0,-.405,1.158)),tuple(np.array((.021,.012,.016))*HS))     # nose leather
ell('head',hp((0,-.36,1.077)),tuple(np.array((.034,.034,.024))*HS))       # chin
# Long tail wrapped forward around the right side.
TAIL=[(0,.55,.12),(.12,.63,.06),(.30,.56,.045),(.39,.36,.04),(.37,.13,.036),(.28,-.05,.034)]
TR=[.05,.042,.035,.029,.022,.014]
for k in range(len(TAIL)-1):cone('tail' if k==0 else f'tail.{k:03d}',TAIL[k],TAIL[k+1],TR[k],TR[k+1])
BONES_TAIL=['tail']+[f'tail.{k:03d}' for k in range(1,len(TAIL)-1)]

def ear_frame(side):
 base=np.array(hp((side*.093,-.19,1.322)),np.float32);f=V(side*.42,-1,.18);f/=np.linalg.norm(f);u=V(side*.5,.08,1);u-=f*np.dot(u,f);u/=np.linalg.norm(u);r=np.cross(u,f)
 return base,r,u,f

def sdf_prim(p,pr):
 kind=pr[0]
 if kind=='ell':
  _,_,c,r,sub=pr;q=(p-c)/r;k0=np.linalg.norm(q,axis=-1);k1=np.linalg.norm(q/r,axis=-1)
  return k0*(k0-1)/np.maximum(k1,1e-6)
 if kind=='cone':
  _,_,a,b,r1,r2=pr;ba=b-a;t=np.clip(((p-a)@ba)/np.dot(ba,ba),0,1);d=np.linalg.norm(p-(a+t[...,None]*ba),axis=-1)
  return d-(r1+(r2-r1)*t)
 _,_,side=pr;base,r,u,f=ear_frame(side);q=p-base;a=q@r;b=q@u;c=q@f
 # Cupped shell: mid-surface bows forward at the edges, thinner toward the tip.
 hgt=.245*HS;mid=-.012+2.3*a*a-.02*b/hgt;t=np.clip(.024-.012*b/hgt,.011,.024)
 shell=np.abs(c-mid)-t/2
 w=.092*(1-np.clip(b/hgt,0,1))**.9+.004
 tri=np.maximum(np.abs(a+side*.012*b/hgt)-w,-b-.03)
 tri=np.maximum(tri,b-hgt)
 return smax(shell,tri,.012)

def smin(a,b,k):h=np.clip(.5+.5*(b-a)/k,0,1);return b*(1-h)+a*h-k*h*(1-h)
def smax(a,b,k):return -smin(-a,-b,k)

def wrinkles(p):
 x,y,z=p[...,0],p[...,1],p[...,2]
 def m(c,r):return np.exp(-(((x-c[0])/r[0])**2+((y-c[1])/r[1])**2+((z-c[2])/r[2])**2))
 n=np.sin(x*37+z*21)*np.sin(y*29-z*13)
 fh=hp((0,-.27,1.30));d=.0055*m(fh,(.09,.07,.055))*np.sin(x*190+np.sin(z*70)*.8+n)          # forehead furrows
 d+=.0025*m(fh,(.09,.07,.05))*np.sin(z*260+n)
 d+=.0065*m((0,-.12,.98),(.13,.12,.10))*np.sin((z+.22*y)*150+n*1.5)                   # throat folds
 d+=.0025*m((0,-.2,.80),(.10,.07,.10))*np.sin(z*125+x*14+n)                              # chest
 for s in [1,-1]:
  d+=.0045*m((s*.13,-.08,.74),(.07,.09,.12))*np.sin((z-y*.5)*155+n)                     # behind the elbows
  d+=.0040*m((s*.12,.0,.95),(.08,.10,.07))*np.sin((z+abs(x)*.6)*170+n)                  # over the shoulders
 d+=.0045*m((0,.02,.27),(.17,.14,.09))*np.sin(z*115+np.sin(x*25)*.6)                    # belly sag
 return d

ORDER=['ell','cone','ear']
def field(p,with_detail=True):
 d=None;neg=[]
 for pr in P:
  if pr[0]=='ell' and pr[4]:neg.append(pr);continue
  di=sdf_prim(p,pr);k=.012 if pr[0]=='ear' else .028
  if pr[1].startswith('hand') or pr[1]=='paw' or pr[0]=='ear':k=.016
  d=di if d is None else smin(d,di,k)
 for pr in neg:d=smax(d,-sdf_prim(p,pr),.012)
 if with_detail:d=d-wrinkles(p)
 return d

# ------------------------------------------------------------------ surface
def surface_nets(lo,hi,step):
 nx,ny,nz=[int(math.ceil((hi[i]-lo[i])/step))+1 for i in range(3)]
 xs=lo[0]+np.arange(nx)*step;ys=lo[1]+np.arange(ny)*step;zs=lo[2]+np.arange(nz)*step
 F=np.empty((nx,ny,nz),np.float32)
 for k in range(nz):
  g=np.stack(np.meshgrid(xs,ys,[zs[k]],indexing='ij'),-1)[:,:,0].astype(np.float32);F[:,:,k]=field(g)
 F[0,:,:]=F[-1,:,:]=F[:,0,:]=F[:,-1,:]=F[:,:,0]=F[:,:,-1]=1  # closed surface
 s=F<0
 cs=np.zeros((nx-1,ny-1,nz-1),np.uint8);
 for dx in (0,1):
  for dy in (0,1):
   for dz in (0,1):cs+=s[dx:nx-1+dx,dy:ny-1+dy,dz:nz-1+dz]
 active=(cs>0)&(cs<8);idx=-np.ones(active.shape,np.int64);ai=np.argwhere(active);idx[active]=np.arange(len(ai))
 acc=np.zeros((len(ai),3));cnt=np.zeros(len(ai))
 corners=[(dx,dy,dz) for dx in (0,1) for dy in (0,1) for dz in (0,1)]
 edges=[(a,b) for a in range(8) for b in range(a+1,8) if sum(abs(corners[a][i]-corners[b][i]) for i in range(3))==1]
 i,j,k=ai[:,0],ai[:,1],ai[:,2]
 for a,b in edges:
  ca,cb=corners[a],corners[b];fa=F[i+ca[0],j+ca[1],k+ca[2]];fb=F[i+cb[0],j+cb[1],k+cb[2]]
  cross=(fa<0)!=(fb<0);t=np.where(cross,fa/np.where(fa-fb==0,1,fa-fb),0)
  pa=np.stack([i+ca[0],j+ca[1],k+ca[2]],1);pb=np.stack([i+cb[0],j+cb[1],k+cb[2]],1)
  acc+=np.where(cross[:,None],pa+(pb-pa)*t[:,None],0);cnt+=cross
 verts=lo+acc/cnt[:,None]*step
 quads=[]
 for axis in range(3):
  sh=[nx,ny,nz];o1,o2=[a for a in range(3) if a!=axis]
  sl=[slice(0,sh[a]-1) if a==axis else slice(1,sh[a]-1) for a in range(3)]
  sl2=[slice(1,sh[a]) if a==axis else slice(1,sh[a]-1) for a in range(3)]
  e=s[tuple(sl)]!=s[tuple(sl2)];inside=s[tuple(sl)][e];pos=np.argwhere(e)
  for a in range(3):
   if a!=axis:pos[:,a]+=1
  def cell(d1,d2):
   q=pos.copy();q[:,o1]-=d1;q[:,o2]-=d2;return idx[q[:,0],q[:,1],q[:,2]]
  c00,c10,c11,c01=cell(1,1),cell(0,1),cell(0,0),cell(1,0)
  quad=np.stack([c00,c10,c11,c01],1)
  flip=inside if axis!=1 else ~inside
  quad[flip]=quad[flip][:,::-1]
  quads.append(quad)
 return verts,np.concatenate(quads)

lo=np.array([-.36,-.56,-.01]);hi=np.array([.48,.74,1.62])
verts,quads=surface_nets(lo,hi,.0045)
def build(name,verts,faces):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in verts],[],[tuple(int(i) for i in f) for f in faces]);me.validate();me.update()
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
 for p in me.polygons:p.use_smooth=True
 return o
high=build('Sphynx sculpt (bake source)',verts,quads)
bpy.context.view_layer.objects.active=high;high.select_set(True)
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
sm=high.modifiers.new('Relax voxel steps','SMOOTH');sm.factor=.5;sm.iterations=2;bpy.ops.object.modifier_apply(modifier=sm.name)
# Browser mesh: same volume without wrinkles, decimated to a phone budget.
_field=field
def field(p,with_detail=False):return _field(p,False)
lverts,lquads=surface_nets(lo,hi,.0075)
field=_field
low=build('Sphynx skin',lverts,lquads)
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=low;low.select_set(True)
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
sm=low.modifiers.new('Relax voxel steps','SMOOTH');sm.factor=.6;sm.iterations=3;bpy.ops.object.modifier_apply(modifier=sm.name)
dec=low.modifiers.new('Browser budget','DECIMATE');dec.ratio=min(1,26000/max(1,len(low.data.polygons)*2));bpy.ops.object.modifier_apply(modifier=dec.name)
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.quads_convert_to_tris();bpy.ops.uv.smart_project(angle_limit=math.radians(58),island_margin=.004);bpy.ops.uv.pack_islands(rotate=True,margin=.003);bpy.ops.object.mode_set(mode='OBJECT')

# ------------------------------------------------------------------ eyes
def iris_image():
 n=512;y,x=np.mgrid[0:n,0:n].astype(np.float32);u=(x+.5)/n-.5;v=.5-(y+.5)/n;r=np.hypot(u,v);a=np.arctan2(v,u)
 R=.44
 t=np.clip(r/R,0,1)
 inner=np.array([.62,.48,.16]);outer=np.array([.30,.42,.20]) # amber centre, green rim
 col=inner*(1-t[...,None]**1.6)+outer*t[...,None]**1.6
 fib=np.zeros_like(r)
 for k in range(30):f=rng.integers(30,160);fib+=np.sin(a*f+rng.uniform(0,6.3)+r*rng.uniform(-40,40))*rng.uniform(.3,1)
 fib=(fib-fib.min())/(fib.max()-fib.min());col*=(.7+.55*fib[...,None]**1.4)
 col*=(1-.6*np.clip((r-(R-.05))/.05,0,1))[...,None]
 # Vertical slit pupil, moderately open for the dim mansion.
 pupil=(np.abs(u)/(.075*np.sqrt(np.clip(1-(v/.36)**2,0,1))+1e-4))<1
 edge=np.clip(1-np.abs(np.abs(u)-.075*np.sqrt(np.clip(1-(v/.36)**2,0,1)))/.01,0,1)*(np.abs(v)<.36)
 col=col*(1-.5*edge[...,None]);col[pupil&(np.abs(v)<.36)]=.008
 sclera=np.array([.55,.47,.40]);col=np.where((r>R)[...,None],sclera*(1-.4*np.clip((r-R)/.06,0,1))[...,None],col)
 img=bpy.data.images.new('Sphynx iris',n,n);img.pixels.foreach_set(np.concatenate([np.clip(col,0,1),np.ones((n,n,1))],2)[::-1].astype(np.float32).ravel())
 img.filepath_raw=str(OUT/'iris.jpg');img.file_format='JPEG';img.save(quality=92);return img
iris=iris_image()
eyemat=bpy.data.materials.new('Sphynx eyes');eyemat.use_nodes=True;pe=eyemat.node_tree.nodes['Principled BSDF']
te=eyemat.node_tree.nodes.new('ShaderNodeTexImage');te.image=iris;eyemat.node_tree.links.new(te.outputs['Color'],pe.inputs['Base Color']);pe.inputs['Roughness'].default_value=.05;pe.inputs['Coat Weight'].default_value=1
eyes=[]
for s in [1,-1]:
 c=Vector(hp((s*.062,-.316,1.214)));fwd=Vector((s*.30,-1,.04)).normalized();r=.032
 bm=bmesh.new();bmesh.ops.create_uvsphere(bm,u_segments=28,v_segments=18,radius=r)
 q=Vector((0,0,1)).rotation_difference(fwd)
 uvl=bm.loops.layers.uv.new('UVMap')
 for vtx in bm.verts:
  d=vtx.co.normalized();ang=math.acos(max(-1,min(1,d.z)));bulge=r*.16*max(0,math.cos(min(math.pi/2,ang/.9*math.pi/2)))**1.4 if ang<.9 else 0
  vtx.co=c+q@(d*(r+bulge))
 for f in bm.faces:
  for l in f.loops:
   d=q.inverted()@(l.vert.co-c);l[uvl].uv=(.5+d.x/(2*r)*.96,.5+d.y/(2*r)*.96)
  f.smooth=True
 me=bpy.data.meshes.new('Sphynx eye');bm.to_mesh(me);bm.free();o=bpy.data.objects.new('Sphynx eye '+('L' if s>0 else 'R'),me);bpy.context.collection.objects.link(o);o.data.materials.append(eyemat);eyes.append(o)

# ------------------------------------------------------------------ skin bake
def masks(co):
 """Per-vertex anatomical masks: thin tissue (ears), nose leather, pads, pink zones."""
 x,y,z=co
 thin=0.0;nose=0.0;pad=0.0;pink=0.0
 for s in [1,-1]:
  base,r,u,f=ear_frame(s);q=np.array(co)-base;b=float(q@u);a=float(q@r)
  if b>-.01:thin=max(thin,min(1,(b+.01)/.06))
 nc=hp((0,-.405,1.158));nose=math.exp(-(((x)/.024)**2+((y-nc[1])/.018)**2+((z-nc[2])/.019)**2))
 for c in [(.115,-.30,.02),(-.10,-.395,1.04)]:pad=max(pad,math.exp(-(((x-c[0])/.05)**2+((y-c[1])/.03)**2+((z-c[2])/.04)**2)))
 mc=hp((0,-.36,1.12));pink=max(thin*.8,math.exp(-(((y-mc[1])/.05)**2+((z-mc[2])/.05)**2+(x/.07)**2)),math.exp(-((z-.25)/.12)**2-((y-.05)/.15)**2)*.6)
 return thin,nose,pad,pink

me=low.data;thinattr=me.color_attributes.new('Thin','FLOAT_COLOR','POINT');paint=me.color_attributes.new('Paint','FLOAT_COLOR','POINT')
for v in me.vertices:
 thin,nose,pad,pink=masks(tuple(v.co));thinattr.data[v.index].color=(thin,thin,thin,1);paint.data[v.index].color=(nose,pad,pink,1)
mat=bpy.data.materials.new('Sphynx skin');mat.use_nodes=True;nt=mat.node_tree;nodes=nt.nodes;links=nt.links;nodes.clear()
out=nodes.new('ShaderNodeOutputMaterial');em=nodes.new('ShaderNodeEmission');links.new(em.outputs[0],out.inputs[0])
def node(kind,**kw):
 n=nodes.new(kind)
 for k,v in kw.items():
  if k in('operation','blend_type','feature','layer_name','attribute_name'):setattr(n,k,v)
  else:n.inputs[k].default_value=v
 return n
def mathn(op,a,b=None,clamp=False):
 n=nodes.new('ShaderNodeMath');n.operation=op;n.use_clamp=clamp
 for i,v in enumerate([a,b]):
  if v is None:continue
  if isinstance(v,(int,float)):n.inputs[i].default_value=v
  else:links.new(v,n.inputs[i])
 return n.outputs[0]
def mix(f,a,b,blend='MIX'):
 n=nodes.new('ShaderNodeMixRGB');n.blend_type=blend
 for i,v in enumerate([f,a,b]):
  if isinstance(v,(int,float)):n.inputs[i].default_value=v
  elif isinstance(v,tuple):n.inputs[i].default_value=v
  else:links.new(v,n.inputs[i])
 return n.outputs[0]
tc=nodes.new('ShaderNodeTexCoord')
def noise(scale,detail=4,rough=.6):
 n=node('ShaderNodeTexNoise',Scale=scale,Detail=detail,Roughness=rough);links.new(tc.outputs['Object'],n.inputs['Vector']);return n.outputs['Fac']
def vor(scale,feature='F1'):
 n=node('ShaderNodeTexVoronoi',feature=feature,Scale=scale);links.new(tc.outputs['Object'],n.inputs['Vector']);return n.outputs['Distance']
attr=node('ShaderNodeAttribute',attribute_name='Paint');sep=nodes.new('ShaderNodeSeparateColor');links.new(attr.outputs['Color'],sep.inputs[0])
nose,pad,pink=sep.outputs['Red'],sep.outputs['Green'],sep.outputs['Blue']
tattr=node('ShaderNodeAttribute',attribute_name='Thin');thin=tattr.outputs['Fac']
# Ivory-rose base, warmer peach variation, faint grey-brown pigment mottling.
base=mix(noise(5,4,.6),(.64,.46,.39,1),(.72,.53,.44,1))
mott=mathn('MULTIPLY',mathn('SUBTRACT',noise(3.2,5,.65),.5,True),2.2,True)
base=mix(mathn('MULTIPLY',mott,.55),base,(.42,.34,.34,1))
warm=mathn('MULTIPLY',mathn('SUBTRACT',noise(1.6,3,.5),.45,True),1.8,True)
base=mix(mathn('MULTIPLY',warm,.35),base,(.80,.52,.42,1))
base=mix(mathn('MULTIPLY',pink,.55),base,(.78,.45,.42,1))
# Capillaries on the thin ear cartilage.
cap=mathn('LESS_THAN',vor(38,'DISTANCE_TO_EDGE'),.03)
base=mix(mathn('MULTIPLY',mathn('MULTIPLY',thin,cap),.35),base,(.62,.25,.25,1))
# Fine fuzz follicles and pores.
fol=mathn('LESS_THAN',vor(240),.2)
base=mix(mathn('MULTIPLY',fol,.07),base,(.30,.20,.18,1))
base=mix(nose,base,(.36,.24,.24,1))
base=mix(pad,base,(.50,.30,.30,1))
ao=nodes.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=.05;ao.samples=16
base=mix(mathn('MULTIPLY',mathn('SUBTRACT',1,ao.outputs['AO']),.55),base,(.20,.11,.10,1))
links.new(base,em.inputs['Color']);low.data.materials.append(mat)
sc=scene;sc.cycles.samples=16;sc.render.bake.margin=8
def bake(img,kind,**kw):
 t=nodes.new('ShaderNodeTexImage');t.image=img;nodes.active=t
 bpy.ops.object.select_all(action='DESELECT');low.select_set(True);bpy.context.view_layer.objects.active=low
 bpy.ops.object.bake(type=kind,**kw);nodes.remove(t)
high.hide_render=True # occlusion must only see the browser surface itself
albedo=bpy.data.images.new('Sphynx skin albedo',1536,1536);bake(albedo,'EMIT')
albedo.filepath_raw=str(OUT/'skin-albedo.jpg');albedo.file_format='JPEG';albedo.save(quality=90)
# Roughness: moist nose, waxier folds, matte velvet elsewhere.
r=mathn('ADD',.62,mathn('MULTIPLY',nose,-.32));r=mathn('ADD',r,mathn('MULTIPLY',pad,-.08));r=mathn('ADD',r,mathn('MULTIPLY',mathn('SUBTRACT',noise(60,3,.5),.5),.12),True)
links.new(r,em.inputs['Color'])
rough=bpy.data.images.new('Sphynx skin roughness',512,512);rough.colorspace_settings.name='Non-Color';sc.cycles.samples=1;bake(rough,'EMIT')
rough.filepath_raw=str(OUT/'skin-roughness.jpg');rough.file_format='JPEG';rough.save(quality=92)
# Normal: the dense sculpted folds plus micro pores, baked onto the browser mesh.
links.new(nodes.new('ShaderNodeBsdfPrincipled').outputs[0],out.inputs[0])
# Micro relief lives on the sculpture's shading: pores and a fine crepe texture.
hm=bpy.data.materials.new('Sphynx sculpt relief');hm.use_nodes=True;hn=hm.node_tree.nodes;hl=hm.node_tree.links
htc=hn.new('ShaderNodeTexCoord');hv=hn.new('ShaderNodeTexVoronoi');hv.inputs['Scale'].default_value=240;hl.new(htc.outputs['Object'],hv.inputs['Vector'])
hz=hn.new('ShaderNodeTexNoise');hz.inputs['Scale'].default_value=95;hz.inputs['Detail'].default_value=6;hl.new(htc.outputs['Object'],hz.inputs['Vector'])
hmix=hn.new('ShaderNodeMath');hmix.operation='MULTIPLY_ADD';hl.new(hv.outputs['Distance'],hmix.inputs[0]);hmix.inputs[1].default_value=.6;hl.new(hz.outputs['Fac'],hmix.inputs[2])
hb=hn.new('ShaderNodeBump');hb.inputs['Distance'].default_value=.0015;hb.inputs['Strength'].default_value=.5;hl.new(hmix.outputs[0],hb.inputs['Height']);hl.new(hb.outputs['Normal'],hn['Principled BSDF'].inputs['Normal'])
high.data.materials.append(hm)
normal=bpy.data.images.new('Sphynx skin normal',1536,1536);normal.colorspace_settings.name='Non-Color'
high.hide_render=False;high.select_set(True);sc.render.bake.use_selected_to_active=True;sc.render.bake.cage_extrusion=.012;sc.render.bake.max_ray_distance=.03;sc.render.bake.normal_space='TANGENT'
t=nodes.new('ShaderNodeTexImage');t.image=normal;nodes.active=t
bpy.ops.object.select_all(action='DESELECT');high.select_set(True);low.select_set(True);bpy.context.view_layer.objects.active=low
bpy.ops.object.bake(type='NORMAL');nodes.remove(t);sc.render.bake.use_selected_to_active=False
normal.filepath_raw=str(OUT/'skin-normal.jpg');normal.file_format='JPEG';normal.save(quality=92)
# Crease occlusion from the sculpted folds, multiplied into the albedo so the
# wrinkles read as soft darker valleys rather than only as shading.
crease=bpy.data.images.new('Sphynx crease occlusion',768,768);crease.colorspace_settings.name='Non-Color'
sc.render.bake.use_selected_to_active=True;sc.cycles.samples=24;bpy.context.scene.world=bpy.data.worlds.new('Bake sky') if not bpy.context.scene.world else bpy.context.scene.world
t=nodes.new('ShaderNodeTexImage');t.image=crease;nodes.active=t;bpy.ops.object.bake(type='AO');nodes.remove(t);sc.render.bake.use_selected_to_active=False
A=np.empty(1536*1536*4,np.float32);albedo.pixels.foreach_get(A);A=A.reshape(1536,1536,4)
C=np.empty(768*768*4,np.float32);crease.pixels.foreach_get(C);C=np.repeat(np.repeat(C.reshape(768,768,4)[...,0],2,0),2,1)
occ=np.clip((1-C)*1.6,0,1)[...,None];A[...,:3]=A[...,:3]*(1-occ*.45)+np.array([.32,.17,.15])*A[...,:3]*occ*.45
albedo.pixels.foreach_set(A.ravel());albedo.save(quality=90)
# Final browser material.
nodes.clear();out=nodes.new('ShaderNodeOutputMaterial');p=nodes.new('ShaderNodeBsdfPrincipled');links.new(p.outputs[0],out.inputs[0])
ta=nodes.new('ShaderNodeTexImage');ta.image=bpy.data.images.load(str(OUT/'skin-albedo.jpg'));links.new(ta.outputs['Color'],p.inputs['Base Color'])
tr=nodes.new('ShaderNodeTexImage');tr.image=bpy.data.images.load(str(OUT/'skin-roughness.jpg'));tr.image.colorspace_settings.name='Non-Color';links.new(tr.outputs['Color'],p.inputs['Roughness'])
tn=nodes.new('ShaderNodeTexImage');tn.image=bpy.data.images.load(str(OUT/'skin-normal.jpg'));tn.image.colorspace_settings.name='Non-Color';nm=nodes.new('ShaderNodeNormalMap');links.new(tn.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],p.inputs['Normal'])
p.inputs['Subsurface Weight'].default_value=.15;p.inputs['Sheen Weight'].default_value=.25
me.color_attributes.remove(me.color_attributes['Paint']);me.color_attributes.active_color=me.color_attributes['Thin'];me.color_attributes.render_color_index=me.color_attributes.active_color_index
bpy.data.objects.remove(high,do_unlink=True)

# ------------------------------------------------------------------ rig
BONES={'body':((0,.40,.20),(0,.20,.44),None),'spine':((0,.20,.44),(0,-.02,.80),'body'),'neck':((0,-.02,.90),(0,-.13,1.06),'spine'),
 'head':(hp((0,-.16,1.16)),hp((0,-.40,1.16)),'neck'),'ear.L':(hp((.093,-.19,1.32)),hp((.17,-.17,1.54)),'head'),'ear.R':(hp((-.093,-.19,1.32)),hp((-.17,-.17,1.54)),'head'),
 'arm.L':((.11,-.06,.86),(.125,-.10,.56),'spine'),'forearm.L':((.125,-.10,.56),(.115,-.17,.12),'arm.L'),'hand.L':((.115,-.17,.12),(.115,-.30,.03),'forearm.L'),
 'arm.R':((-.11,-.06,.86),(-.15,-.19,.62),'spine'),'forearm.R':((-.15,-.19,.62),(-.12,-.33,.88),'arm.R'),'paw':((-.12,-.33,.88),(-.095,-.40,1.05),'forearm.R')}
for k,b in enumerate(BONES_TAIL):BONES[b]=(TAIL[k],TAIL[k+1],'body' if k==0 else BONES_TAIL[k-1])
arm=bpy.data.armatures.new('Sphynx grooming skeleton');rig=bpy.data.objects.new('Sphynx',arm);bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
for name,(h,t,par) in BONES.items():
 eb=arm.edit_bones.new(name);eb.head=h;eb.tail=t
for name,(h,t,par) in BONES.items():
 if par:arm.edit_bones[name].parent=arm.edit_bones[par]
bpy.ops.object.mode_set(mode='OBJECT')
# Skin weights from the sculpture itself: each vertex follows the anatomical
# parts that form it, softly blended where the smooth union blends them.
def bind(o,fixed=None):
 o.parent=rig;mod=o.modifiers.new('Sphynx anatomy','ARMATURE');mod.object=rig
 for name in BONES:o.vertex_groups.new(name=name)
 co=np.array([v.co[:] for v in o.data.vertices],np.float32)
 if fixed:
  o.vertex_groups[fixed].add(list(range(len(co))),1,'REPLACE');return
 ds=np.stack([sdf_prim(co,pr) if not(pr[0]=='ell' and pr[4]) else np.full(len(co),9,np.float32) for pr in P],1)
 names=[pr[1] for pr in P];w={n:np.zeros(len(co)) for n in BONES}
 dmin=ds.min(1,keepdims=True);soft=np.exp(-(ds-dmin)/.018)
 for i,n in enumerate(names):w[n]+=soft[:,i]
 # Tail cones also lean on the next bone so the tail bends smoothly.
 W=np.stack([w[n] for n in BONES],1);W/=W.sum(1,keepdims=True)
 top=np.argsort(-W,1)[:,:4]
 for vi in range(len(co)):
  ws=W[vi,top[vi]];ws=ws/ws.sum()
  for bi,ww in zip(top[vi],ws):
   if ww>.01:o.vertex_groups[list(BONES)[bi]].add([vi],float(ww),'REPLACE')
bind(low)
for e in eyes:bind(e,'head')
low.name='Sphynx skin'

# ------------------------------------------------------------------ grooming loop
FPS=30;LEN=8.0;scene.render.fps=FPS;scene.frame_start=1;scene.frame_end=int(LEN*FPS)+1
rig.animation_data_create();act=bpy.data.actions.new('Sphynx grooming • 8s');rig.animation_data.action=act
def win(t,a,b,ramp=.45):
 return min(1,max(0,(t-a)/ramp))*min(1,max(0,(b-t)/ramp))
def sm(x):return x*x*(3-2*x)
def rot(pb,*pairs):
 q=Quaternion()
 m=pb.bone.matrix_local.to_3x3().inverted()
 for axis,ang in pairs:q=q@Quaternion(m@Vector(axis),ang)
 pb.rotation_mode='QUATERNION';pb.rotation_quaternion=q
X,Y,Z=(1,0,0),(0,1,0),(0,0,1)
for frame in range(1,int(LEN*FPS)+2):
 t=(frame-1)/FPS;w=2*math.pi/LEN
 look=sm(win(t,3.3,5.7,.5))          # lifts the head and looks into the room
 lick=1-look
 stroke=max(0,math.sin(t*w*24))**1.5  # three licks per second
 breathe=math.sin(t*w*4)
 pb=rig.pose.bones
 rot(pb['body'],(X,.004*breathe))
 rot(pb['spine'],(X,.012*breathe-.02*look))
 rot(pb['neck'],(X,.10*lick-.05*look),(Z,-.10*lick+.12*look*math.sin(t*w*2)))
 rot(pb['head'],(X,(.22+.09*stroke)*lick-.12*look),(Z,-.16*lick+.30*look),(Y,.08*lick*math.sin(t*w*8)-.10*look))
 rot(pb['paw'],(X,(.06+.07*stroke)*lick-.25*look),(Z,.04*math.sin(t*w*8)))
 rot(pb['forearm.R'],(X,.05*stroke*lick+.32*look))
 rot(pb['arm.R'],(X,.10*look))
 twitch=math.exp(-((t-6.4)/.08)**2)+.6*math.exp(-((t-6.62)/.07)**2)
 rot(pb['ear.L'],(Y,.30*twitch),(Z,-.10*look))
 rot(pb['ear.R'],(Y,-.08*look),(Z,.10*look))
 for k,b in enumerate(BONES_TAIL):
  rot(pb[b],(Z,(.06+.05*k)*math.sin(t*w*2-k*.7)),(X,(.03*k)*max(0,math.sin(t*w*1-k*.5))))
 for b in pb:
  b.keyframe_insert('rotation_quaternion',frame=frame)
scene.frame_set(1)

# ------------------------------------------------------------------ save/export
rig['species']='Sphynx cat';rig['reference']='blink-182 I Miss You (2003), grooming hairless cat around 00:42-00:46'
rig['orientation']='Blender front -Y, glTF front +Z';rig['source']='Original procedural sculpture; no third-party mesh, photographs or video pixels.'
scene.render.filepath='//'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'sphynx.blend'))
bpy.ops.file.make_paths_relative();bpy.ops.file.pack_all()
for im in bpy.data.images:
 for pf in im.packed_files:pf.filepath=im.filepath # packing records absolute source paths
bpy.ops.wm.save_mainfile()
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
for o in rig.children:o.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(GLB),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_skins=True,export_yup=True,export_apply=False,export_vertex_color='NAME',export_vertex_color_name='Thin',export_all_vertex_colors=False,export_image_format='AUTO')
tris=sum(len(o.data.polygons) if o.name=='Sphynx skin' else sum(len(p.vertices)-2 for p in o.data.polygons) for o in rig.children)
(OUT/'stats.json').write_text(json.dumps({'triangles':tris,'vertices':sum(len(o.data.vertices) for o in rig.children),'glbBytes':GLB.stat().st_size,'clip':'Sphynx grooming • 8s','root':'Sphynx','bones':list(BONES),'animationDuration':LEN},indent=2))
print('SPHYNX_READY',tris)
