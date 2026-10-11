"""Dedicated head surfaces for the band: high-resolution face textures,
procedural skin relief, strand-card hair, layered eyes and eyelashes.

Executed in the build-musicians.py context after band-details.py. The
MakeHuman body UV gives the whole head about 150 px of the shared skin
texture, so each head gets its own UV set and baked maps instead:

* Face island: face and temples wrapped cylindrically around the skull axis,
  so the facial atlas keeps more than its source resolution without overlaps.
* Rest of the head (crown, nape, ears, hidden folds): Smart UV Project islands.
* Albedo (2048 px JPEG), roughness (512 px) and tangent normal (1024 px)
  are baked from Blender shader trees; all relief is procedural.
"""
import bmesh
from mathutils.bvhtree import BVHTree

HEAD_SIZE=1536
HAIR_COLORS={'Bassist':(.030,.022,.018,1),'Guitarist':(.034,.025,.020,1),'Drummer':(.016,.013,.012,1)}
IRIS={'Bassist':((.30,.33,.28),(.36,.44,.45)),'Guitarist':((.32,.25,.13),(.36,.36,.25)),'Drummer':((.22,.14,.07),(.30,.21,.11))}

def head_frame(ob,rig):
 """Facial landmarks in the rig's rest space, in units of eye-to-mouth height."""
 el=rig.data.bones['eye.L'].head_local;er=rig.data.bones['eye.R'].head_local
 eye=(el+er)/2;mouth=conv(morphed[493]);du=eye.z-mouth.z
 return {'eye':eye,'mouth':mouth,'du':du,'eyehalf':abs(el.x-er.x)/2}

def head_coords(co,F):
 """Return face-relative X (side), Z (mouth=0, eyes=1) and D (depth, forward positive)."""
 return co.x/F['du'],(co.z-F['mouth'].z)/F['du'],(F['eye'].y-co.y)/F['du']

def is_head_poly(c,F):
 X,Z,D=head_coords(c,F);return Z>-2.05 and abs(X)<1.45

def head_axis(F):return F['eye'].y+.9*F['du']

def azimuth(co,F):
 """Angle around the skull's vertical axis; 0 faces forward (-Y)."""
 return math.atan2(co.x,-(co.y-head_axis(F)))

def face_island_poly(c,n,F):
 X,Z,D=head_coords(c,F)
 ear=abs(X)>.9 and .2<Z<1.55 and D<-.3
 radial=Vector((c.x,c.y-head_axis(F),0)).normalized()
 return -1.25<Z<2.35 and abs(azimuth(c,F))<1.75 and not ear and n.dot(radial)>.15

def head_uv(role,ob,rig):
 """Create HeadUV: face and temples wrapped cylindrically across the lower
 half, the crown, nape, ears and hidden folds packed above."""
 F=head_frame(ob,rig);me=ob.data
 heads=set(p.index for p in me.polygons if is_head_poly(p.center,F))
 face=set(i for i in heads if face_island_poly(me.polygons[i].center,me.polygons[i].normal,F))
 # The wrap must not overlap: drop faces occluded along the radial direction
 # (mouth cavity, nostrils, lid folds); they go to the packed remainder.
 bvh=BVHTree.FromPolygons([v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
 hidden=set()
 for i in face:
  c=me.polygons[i].center;r=Vector((c.x,c.y-head_axis(F),0)).normalized()
  hit=bvh.ray_cast(c+r*2,-r)
  if hit[2] is not None and hit[2]!=i and hit[3]<2-1e-4:hidden.add(i)
 face-=hidden
 uvl=me.uv_layers.new(name='HeadUV')
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 me.uv_layers.active=uvl
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='DESELECT')
 bm=bmesh.from_edit_mesh(me);bm.faces.ensure_lookup_table()
 rest=heads-face
 for f in bm.faces:f.select=f.index in rest
 for e in bm.edges:
  idx=[f.index for f in e.link_faces]
  inr=[i in rest for i in idx]
  e.seam=any(inr) and not all(inr)
  if all(inr) and all(abs(v.co.x)<2e-3 and v.co.y>F['eye'].y+.12 for v in e.verts):e.seam=True
 bm.select_flush_mode();bmesh.update_edit_mesh(me)
 bpy.ops.uv.smart_project(angle_limit=math.radians(60),island_margin=.02,area_weight=0)
 bpy.ops.object.mode_set(mode='OBJECT')
 uvl=me.uv_layers['HeadUV']
 # Smart UV Project packs the remainder's islands into the unit square without
 # overlaps; place that square beside the face island.
 for i in rest:
  for l in me.polygons[i].loop_indices:
   p=uvl.data[l].uv;uvl.data[l].uv=(.005+p.x*.44,.555+p.y*.44)
 # Cylindrical wrap for the face island: arc length across, height up.
 R=sum(Vector((me.vertices[v].co.x,me.vertices[v].co.y-head_axis(F),0)).length for i in face for v in me.polygons[i].vertices)/max(1,sum(len(me.polygons[i].vertices) for i in face))
 def wrap(co):return Vector((azimuth(co,F)*R,co.z))
 cs=[wrap(me.vertices[v].co) for i in face for v in me.polygons[i].vertices]
 x0=min(c.x for c in cs);x1=max(c.x for c in cs);z0=min(c.y for c in cs);z1=max(c.y for c in cs)
 s=min(.99/(x1-x0),.54/(z1-z0))
 for i in face:
  for l in me.polygons[i].loop_indices:
   c=wrap(me.vertices[me.loops[l].vertex_index].co);uvl.data[l].uv=(.005+(c.x-x0)*s,.005+(c.y-z0)*s)
 for p in me.polygons:
  if p.index not in heads:
   for l in p.loop_indices:uvl.data[l].uv=(-4,-4)
 return heads,F

def bump(x,c,w):return math.exp(-((x-c)/w)**2)

def hairline(role,X,Z,D):
 """1 on the scalp above each member's hairline, 0 on face, ears and neck.
 The hairline height follows the azimuth around the skull: forehead, temple
 recession, over the ear, then down behind the ear to the nape."""
 a=math.atan2(abs(X),D+.9)
 front={'Bassist':2.02,'Guitarist':1.96,'Drummer':1.84}[role]
 keys=[(0,front),(.45,front+.06),(.72,front),(.92,1.30),(1.10,.90),(1.28,1.22),(1.62,1.22),(1.95,.85),(2.35,.15),(math.pi,.05)]
 for (a0,z0),(a1,z1) in zip(keys,keys[1:]):
  if a<=a1:t=(a-a0)/(a1-a0);line=z0+(z1-z0)*t*t*(3-2*t);break
 return smooth(-.04,.12,Z-line)

def head_masks(role,ob,F):
 """Per-corner masks used by the bakes: HeadPaintA (scalp, beard, flush, lips) and HeadPaintB (relief)."""
 me=ob.data
 a=me.color_attributes.new(name='HeadPaintA',type='FLOAT_COLOR',domain='CORNER')
 b=me.color_attributes.new(name='HeadPaintB',type='FLOAT_COLOR',domain='CORNER')
 c=me.color_attributes.new(name='HeadPaintC',type='FLOAT_COLOR',domain='CORNER')
 for poly in me.polygons:
  for li in poly.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co;X,Z,D=head_coords(co,F);ax=abs(X)
   front=smooth(-.9,-.2,D)
   scalp=hairline(role,X,Z,D)
   beard=smooth(.42,.18,Z)*smooth(-1.25,-.75,Z)*(1-smooth(.95,1.3,ax))*(1-bump(ax,0,.42)*bump(Z,0,.17))
   beard=max(beard,smooth(.55,.25,Z)*smooth(.8,1.15,ax)*(1-smooth(1.25,1.4,ax))*smooth(-1.0,-.4,Z)*front)
   if role=='Drummer':beard*=.4
   flush=max(bump(ax,.68,.24)*bump(Z,.55,.3)*front,bump(ax,0,.18)*bump(Z,.62,.2)*front,smooth(1.05,1.35,ax)*smooth(-.5,-1.2,D)*bump(Z,1.0,.55))
   lips=bump(ax,0,.36)*bump(Z,0,.13)*front
   a.data[li].color=(scalp,beard,flush,lips)
   forehead=smooth(1.45,1.75,Z)*smooth(2.25,2.05,Z)*(1-smooth(.85,1.15,ax))*front
   crow=bump(ax,1.0,.12)*bump(Z,1.0,.22)
   undereye=bump(ax,.52,.25)*bump(Z,.78,.08)*front
   naso=0
   for t in [i/8 for i in range(9)]:
    px=.30+.20*t;pz=.48-.52*t;naso=max(naso,bump(ax,px,.06)*bump(Z,pz,.08))
   naso*=front
   b.data[li].color=(forehead,crow,undereye,naso)
   brow=bump(ax,.52,.32)*bump(Z,1.33,.12)*front
   tzone=max(bump(ax,0,.28)*smooth(.3,.6,Z)*smooth(2.3,1.9,Z),forehead*.6)*front
   nose=bump(ax,0,.22)*bump(Z,.55,.32)*front
   cavity=bump(ax,0,.55)*bump(Z,0,.22)*smooth(.36,.16,D)
   c.data[li].color=(brow,tzone,nose,cavity)

def _attr(nt,name):
 n=nt.nodes.new('ShaderNodeVertexColor');n.layer_name=name;s=nt.nodes.new('ShaderNodeSeparateColor');nt.links.new(n.outputs['Color'],s.inputs['Color'])
 a=nt.nodes.new('ShaderNodeMath');a.operation='MULTIPLY';a.inputs[1].default_value=1;nt.links.new(n.outputs['Alpha'],a.inputs[0])
 return [s.outputs['Red'],s.outputs['Green'],s.outputs['Blue'],a.outputs[0]]

def _math(nt,op,a,b=None,clamp_=False):
 n=nt.nodes.new('ShaderNodeMath');n.operation=op;n.use_clamp=clamp_
 for i,v in enumerate([a,b]):
  if v is None:continue
  if isinstance(v,(int,float)):n.inputs[i].default_value=v
  else:nt.links.new(v,n.inputs[i])
 return n.outputs[0]

def _mix(nt,fac,a,b,blend='MIX'):
 n=nt.nodes.new('ShaderNodeMixRGB');n.blend_type=blend
 for i,v in enumerate([fac,a,b]):
  if isinstance(v,(int,float)):n.inputs[i].default_value=v
  elif isinstance(v,tuple):n.inputs[i].default_value=v
  else:nt.links.new(v,n.inputs[i])
 return n.outputs[0]

def _noise(nt,scale,detail=4,rough=.55,coord='Object'):
 tc=nt.nodes.new('ShaderNodeTexCoord');n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;n.inputs['Detail'].default_value=detail;n.inputs['Roughness'].default_value=rough
 nt.links.new(tc.outputs[coord],n.inputs['Vector']);return n.outputs['Fac']

def _voronoi(nt,scale,feature='F1',jitter=1.0):
 tc=nt.nodes.new('ShaderNodeTexCoord');n=nt.nodes.new('ShaderNodeTexVoronoi');n.feature=feature;n.inputs['Scale'].default_value=scale;n.inputs['Randomness'].default_value=jitter
 nt.links.new(tc.outputs['Object'],n.inputs['Vector']);return n.outputs['Distance']

def bake_image(name,size,path=None):
 return bpy.data.images.new(name,width=size,height=size,alpha=False)

def run_bake(ob,img,kind,margin=6):
 nt=ob.active_material.node_tree;t=nt.nodes.new('ShaderNodeTexImage');t.image=img;nt.nodes.active=t
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=1;sc.render.bake.margin=margin
 if kind=='NORMAL':sc.render.bake.normal_space='TANGENT'
 bpy.ops.object.bake(type=kind)
 nt.nodes.remove(t)

def save_jpeg(img,path,quality=90):
 img.filepath_raw=str(path);img.file_format='JPEG';img.save(quality=quality);return img

def bake_head(role,ob,rig,m,color,F):
 """Bake face albedo, roughness and normal into HeadUV. m is the emission bake material."""
 member=MEMBERS[role][0];nt=m.node_tree;links=nt.links
 head_masks(role,ob,F)
 A=_attr(nt,'HeadPaintA');B=_attr(nt,'HeadPaintB');C=_attr(nt,'HeadPaintC')
 scalp,beard,flush,lips=A
 brow,tzone,nose,cavity=C
 # Subtle photographic variation: mottling, a few small moles, vascular flush.
 mott=_noise(nt,180,6,.62)
 mott=_mix(nt,.07,(1,1,1,1),_mix(nt,mott,(.86,.80,.78,1),(1.08,1.04,1.0,1)),'MULTIPLY')
 col=_mix(nt,1,color,mott,'MULTIPLY')
 col=_mix(nt,_math(nt,'MULTIPLY',flush,.32),col,_mix(nt,1,col,(1.0,.72,.68,1),'MULTIPLY'))
 col=_mix(nt,_math(nt,'MULTIPLY',lips,.22),col,_mix(nt,1,col,(.95,.70,.70,1),'MULTIPLY'))
 # Beard shadow: dense short dark follicles under the skin, stronger for Mark and Tom.
 fol=_voronoi(nt,2600,'F1',1)
 follicle=_math(nt,'LESS_THAN',fol,.32)
 stub=_math(nt,'MULTIPLY',beard,_math(nt,'ADD',.22,_math(nt,'MULTIPLY',follicle,.55)),True)
 col=_mix(nt,_math(nt,'MULTIPLY',stub,.62),col,(.20,.17,.16,1),'MULTIPLY')
 # Scalp: buzzed hair for Travis's shaved sides, dense dark hair base under the other hairstyles.
 hc=HAIR_COLORS[role]
 hairdots=_math(nt,'LESS_THAN',_voronoi(nt,1700,'F1',1),.5)
 if role=='Drummer':
  skin=_mix(nt,_noise(nt,90,5,.6),(.40,.31,.27,1),(.48,.37,.32,1))
  buzz=_mix(nt,_math(nt,'ADD',.42,_math(nt,'MULTIPLY',hairdots,.5)),skin,(hc[0]*1.3,hc[1]*1.3,hc[2]*1.4,1))
  col=_mix(nt,scalp,col,buzz)
 else:
  base=_mix(nt,_math(nt,'MULTIPLY',hairdots,.5),(hc[0]*1.6,hc[1]*1.6,hc[2]*1.6,1),(hc[0]*.8,hc[1]*.8,hc[2]*.8,1))
  col=_mix(nt,scalp,col,base)
 col=_mix(nt,cavity,col,(.16,.075,.065,1))
 em=next(n for n in nt.nodes if n.type=='EMISSION');links.new(col,em.inputs['Color'])
 me=ob.data;me.uv_layers.active=me.uv_layers['HeadUV']
 img=bake_image(member+' face albedo',HEAD_SIZE,None);run_bake(ob,img,'EMIT',8)
 albedo=save_jpeg(img,LIK/'baked'/f'{role.lower()}-face-albedo.jpg',90)
 # Roughness: oilier T-zone and lips, matte scalp/hair base and neck.
 r=_math(nt,'ADD',.60,_math(nt,'MULTIPLY',tzone,-.16))
 r=_math(nt,'ADD',r,_math(nt,'MULTIPLY',nose,-.08))
 r=_math(nt,'ADD',r,_math(nt,'MULTIPLY',lips,-.20))
 r=_math(nt,'ADD',r,_math(nt,'MULTIPLY',scalp,.18))
 r=_math(nt,'ADD',r,_math(nt,'MULTIPLY',_math(nt,'SUBTRACT',_noise(nt,240,3,.5),.5),.10),True)
 links.new(r,em.inputs['Color'])
 img=bake_image(member+' face roughness',512,None);img.colorspace_settings.name='Non-Color';run_bake(ob,img,'EMIT',8)
 rough=save_jpeg(img,LIK/'baked'/f'{role.lower()}-face-roughness.jpg',92);rough.colorspace_settings.name='Non-Color'
 # Relief: pores, fine crosshatched skin lines and expression creases as a bump field.
 forehead,crow,undereye,naso=B
 tc=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');links.new(tc.outputs['Object'],sep.inputs[0])
 du=F['du']
 lines=_math(nt,'SINE',_math(nt,'MULTIPLY',_math(nt,'ADD',sep.outputs['Z'],_math(nt,'MULTIPLY',_noise(nt,40,2,.5),.006)),2*math.pi/(du*.075)))
 h=_math(nt,'MULTIPLY',_math(nt,'MULTIPLY',lines,forehead),.05)
 crowl=_math(nt,'SINE',_math(nt,'MULTIPLY',_math(nt,'ADD',sep.outputs['Z'],_math(nt,'MULTIPLY',sep.outputs['Y'],.8)),2*math.pi/(du*.05)))
 h=_math(nt,'ADD',h,_math(nt,'MULTIPLY',_math(nt,'MULTIPLY',crowl,crow),.22))
 h=_math(nt,'ADD',h,_math(nt,'MULTIPLY',undereye,-.45))
 h=_math(nt,'ADD',h,_math(nt,'MULTIPLY',naso,-.65))
 liplines=_math(nt,'SINE',_math(nt,'MULTIPLY',sep.outputs['X'],2*math.pi/(du*.03)))
 h=_math(nt,'ADD',h,_math(nt,'MULTIPLY',_math(nt,'MULTIPLY',liplines,lips),.12))
 pores=_math(nt,'SUBTRACT',1,_math(nt,'LESS_THAN',_voronoi(nt,800,'F1',1),.24))
 porew=_math(nt,'ADD',.55,_math(nt,'MULTIPLY',_math(nt,'ADD',nose,_math(nt,'MULTIPLY',tzone,.5)),.6))
 h=_math(nt,'ADD',h,_math(nt,'MULTIPLY',_math(nt,'MULTIPLY',pores,porew),.22))
 cross1=_noise(nt,700,2,.4)
 h=_math(nt,'ADD',h,_math(nt,'MULTIPLY',cross1,.10))
 h=_math(nt,'MULTIPLY',h,_math(nt,'SUBTRACT',1,_math(nt,'MULTIPLY',scalp,.6)))
 bsdf=nt.nodes.new('ShaderNodeBsdfPrincipled');bumpn=nt.nodes.new('ShaderNodeBump');bumpn.inputs['Strength'].default_value=1;bumpn.inputs['Distance'].default_value=du*.010
 links.new(h,bumpn.inputs['Height']);links.new(bumpn.outputs['Normal'],bsdf.inputs['Normal'])
 out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');links.new(bsdf.outputs[0],out.inputs['Surface'])
 img=bake_image(member+' face normal',1024,None);img.colorspace_settings.name='Non-Color'
 bpy.context.scene.cycles.samples=1;run_bake(ob,img,'NORMAL',8)
 normal=save_jpeg(img,LIK/'baked'/f'{role.lower()}-face-normal.jpg',93);normal.colorspace_settings.name='Non-Color'
 for name in ['HeadPaintA','HeadPaintB','HeadPaintC']:me.color_attributes.remove(me.color_attributes[name])
 return albedo,rough,normal

def face_material(member,albedo,rough,normal):
 m=bpy.data.materials.new(member+' face');m.use_nodes=True;nt=m.node_tree;p=nt.nodes.get('Principled BSDF')
 uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='HeadUV'
 def tex(img,noncolor=False):
  t=nt.nodes.new('ShaderNodeTexImage');t.image=img;nt.links.new(uv.outputs[0],t.inputs['Vector'])
  if noncolor:img.colorspace_settings.name='Non-Color'
  return t
 nt.links.new(tex(albedo).outputs['Color'],p.inputs['Base Color'])
 nt.links.new(tex(rough,True).outputs['Color'],p.inputs['Roughness'])
 nm=nt.nodes.new('ShaderNodeNormalMap');nm.uv_map='HeadUV';nm.inputs['Strength'].default_value=1
 nt.links.new(tex(normal,True).outputs['Color'],nm.inputs['Color']);nt.links.new(nm.outputs['Normal'],p.inputs['Normal'])
 p.inputs['Subsurface Weight'].default_value=.12
 return m

def native_tint(role):
 """Linear RGB factor matching the CC0 body skin to this member's facial atlas cheek colour."""
 lm=LANDMARKS['columns'][MEMBERS[role][1]];atlas=bpy.data.images.load(str(LIK/'facial-atlas-v1.png'),check_existing=True)
 body=bpy.data.images.load(str(SYSTEM/'skins/young_caucasian_male/young_lightskinned_male_diffuse.png'),check_existing=True)
 def mean(img,box=None):
  w,h=img.size;a=np.empty(w*h*4,np.float32);img.pixels.foreach_get(a);a=a.reshape(h,w,4)[::-1,:,:3]**2.2
  if box:x0,y0,x1,y1=box;a=a[y0:y1,x0:x1]
  a=a.reshape(-1,3);return a[a.mean(1)>.05].mean(0)
 ex,ey=lm['eyes'][0];nx,ny=lm['noseTip']
 cheek=mean(atlas,(int(ex-30),int(ny-20),int(ex+30),int(ny+30)));skin=mean(body)
 return tuple(float(min(1.3,max(.6,c/s))) for c,s in zip(cheek,skin))+(1,)

# ---------------------------------------------------------------- textures
import numpy as np

def _save_rgba(name,arr,path):
 """arr: H×W×4 float, row 0 at the top. Saved as PNG and returned as a Blender image."""
 h,w=arr.shape[:2];img=bpy.data.images.new(name,width=w,height=h,alpha=True)
 img.pixels.foreach_set(np.ascontiguousarray(arr[::-1]).astype(np.float32).ravel())
 img.filepath_raw=str(path);img.file_format='PNG';img.save();return img

def _strokes(h,w,rng,count,thick,length,clump=.28,sway=.012,color=(.43,.33,.26),light=(.62,.50,.40)):
 """Antialiased strands for one card column, roots at the bottom (row h-1)."""
 out=np.zeros((h,w,4),np.float32);rows=np.arange(h,dtype=np.float32)
 for k in range(count):
  L=rng.uniform(*length)*h;x0=w*(.5+rng.normal(0,clump));x0=min(w*.96,max(w*.04,x0))
  xt=w*.5+(x0-w*.5)*rng.uniform(.25,.75);ph=rng.uniform(0,6.3);fr=rng.uniform(1.5,4.5);t=rng.uniform(*thick)
  shade=rng.uniform(0,1)**1.6;c=np.array(color)*(1-shade)+np.array(light)*shade
  y=rows[rows>=h-L];v=(h-1-y)/L # 0 root .. 1 tip
  x=x0+(xt-x0)*v**1.4+w*sway*np.sin(v*fr*math.pi+ph)
  width=t*(1-.75*v**2);alpha=np.clip((1-v)/.18,0,1)*rng.uniform(.75,1)
  for dx in range(-3,4):
   px=np.floor(x).astype(int)+dx;cov=np.clip(width/2+.5-np.abs(px+.5-x),0,1)*alpha
   ok=(px>=0)&(px<w);yy=y[ok].astype(int);xx=px[ok];a=cov[ok][:,None]
   # Root shading darkens the strand where it leaves the scalp.
   col=c*(.55+.45*np.clip(v[ok]*4,0,1))[:,None]
   out[yy,xx,:3]=col*a+out[yy,xx,:3]*(1-a);out[yy,xx,3]=a[:,0]+out[yy,xx,3]*(1-a[:,0])
 return out

def hair_texture():
 """Four strand-card variants side by side; neutral brown, tinted per member at runtime."""
 path=LIK/'hair-strands.png'
 if 'Band hair strands' in bpy.data.images:return bpy.data.images['Band hair strands']
 rng=np.random.default_rng(182);H,W=1024,256;cols=[]
 for count,thick,length,clump in [(150,(2.4,3.8),(.75,1.0),.20),(190,(2.0,3.2),(.6,1.0),.26),(120,(2.8,4.4),(.85,1.0),.16),(230,(1.8,2.8),(.45,.95),.30)]:
  cols.append(_strokes(H,W,rng,count,thick,length,clump))
 img=_save_rgba('Band hair strands',np.concatenate(cols,axis=1),path);return img

def lash_texture():
 path=LIK/'lashes.png'
 if 'Band eyelashes' in bpy.data.images:return bpy.data.images['Band eyelashes']
 rng=np.random.default_rng(7);H,W=128,512;out=np.zeros((H,W,4),np.float32);rows=np.arange(H,dtype=np.float32)
 for k in range(150):
  x0=rng.uniform(4,W-4);L=rng.uniform(.55,1)*H;curl=rng.uniform(6,16)*(1 if x0>W/2 else -1)*.4;t=rng.uniform(1.6,2.6)
  y=rows[rows>=H-L];v=(H-1-y)/L;x=x0+curl*v**2+rng.uniform(-4,4)*v;width=t*(1-.8*v)
  for dx in range(-2,3):
   px=np.floor(x).astype(int)+dx;cov=np.clip(width/2+.5-np.abs(px+.5-x),0,1)*np.clip((1-v)/.25,0,1)
   ok=(px>=0)&(px<W);yy=y[ok].astype(int);xx=px[ok];a=cov[ok]
   out[yy,xx,:3]=.012*a[:,None]+out[yy,xx,:3]*(1-a[:,None]);out[yy,xx,3]=a+out[yy,xx,3]*(1-a)
 return _save_rgba('Band eyelashes',out,path)

def iris_texture(role):
 """Procedural eye: sclera with faint vessels, fibrous iris, collarette, limbal ring, pupil."""
 path=LIK/'baked'/f'{role.lower()}-iris.jpg';n=512;rng=np.random.default_rng({'Bassist':1,'Guitarist':2,'Drummer':3}[role])
 y,x=np.mgrid[0:n,0:n].astype(np.float32);u=(x+.5)/n-.5;v=.5-(y+.5)/n;r=np.hypot(u,v);a=np.arctan2(v,u)
 inner,outer=[np.array(c) for c in IRIS[role]]
 R=.215;P=.075
 # Radial fibres from summed angular harmonics.
 fib=np.zeros_like(r)
 for k in range(26):
  f=rng.integers(20,140);fib+=np.sin(a*f+rng.uniform(0,6.3)+r*rng.uniform(-30,30))*rng.uniform(.3,1)
 fib=(fib-fib.min())/(fib.max()-fib.min())
 t=np.clip((r-P)/(R-P),0,1)
 iris=inner[None,None,:]*(1-t[...,None])+outer[None,None,:]*t[...,None]
 iris*=(.62+.62*fib[...,None]**1.3)
 collar=np.exp(-((t-.33)/.07)**2);iris=iris*(1-.35*collar[...,None])+np.array([.62,.48,.28])*.35*collar[...,None]*(inner.mean()/.3)
 crypt=np.clip(np.sin(a*9+t*7)*np.sin(t*18),0,1)**4*(t>.35);iris*=(1-.35*crypt[...,None])
 limbal=np.exp(-((r-R)/.016)**2);iris*=(1-.75*np.clip((r-(R-.035))/.035,0,1)[...,None])
 sclera=np.array([.72,.68,.64])*(1-.20*np.clip((r-.30)/.2,0,1))[...,None]*np.ones_like(iris)
 ves=np.zeros_like(r)
 for k in range(14):
  ang=rng.uniform(0,6.3);ves+=np.exp(-(((a-ang+np.pi)%(2*np.pi)-np.pi)*r/.004+np.sin(r*90+k)*1.5)**2)*np.clip((r-.30)/.15,0,1)
 sclera=sclera*(1-.25*np.clip(ves,0,1)[...,None])+np.array([.55,.12,.10])*.25*np.clip(ves,0,1)[...,None]
 m=np.clip((r-R)/.01,0,1)[...,None];col=iris*(1-m)+sclera*m
 col=col*(1-limbal[...,None]*.55)
 col[r<P]=.012;edge=np.exp(-((r-P)/.008)**2);col*=(1-.4*edge[...,None])
 img=bpy.data.images.new(MEMBERS[role][0]+' iris',width=n,height=n,alpha=False)
 rgba=np.concatenate([np.clip(col,0,1),np.ones((n,n,1),np.float32)],axis=2)
 img.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).astype(np.float32).ravel())
 return save_jpeg(img,path,92)

# ---------------------------------------------------------------- hair
def shell_textures():
 """Tileable strand colour and normal maps for the hair volume (512 px, wraps in u and v)."""
 if 'Band hair volume' in bpy.data.images:return bpy.data.images['Band hair volume'],bpy.data.images['Band hair volume normal']
 n=512;rng=np.random.default_rng(1820);col=np.zeros((n,n,3));col[:]=(.028,.022,.018);h=np.zeros((n,n))
 for k in range(1700):
  x0=rng.uniform(0,n);y0=rng.uniform(0,n);m=int(rng.uniform(.3,.85)*n);t=rng.uniform(1.0,2.0);ph=rng.uniform(0,6.3);sw=rng.uniform(1,5);drift=rng.uniform(-8,8)
  shade=rng.uniform(0,1)**1.5;c=np.array([.34,.26,.21])*(.35+1.1*shade)
  vv=np.arange(m)/m;yy=((y0+np.arange(m))%n).astype(int);x=x0+sw*np.sin(vv*3+ph)+drift*vv;fade=np.sin(vv*np.pi)**.6
  for dx in range(-2,3):
   px=np.floor(x)+dx;cov=np.clip(t/2+.5-np.abs(px+.5-x),0,1)*fade;xi=(px%n).astype(int)
   col[yy,xi]=c*cov[:,None]+col[yy,xi]*(1-cov[:,None]);h[yy,xi]=np.maximum(h[yy,xi],cov*(.55+.45*shade))
 dx=(np.roll(h,-1,1)-np.roll(h,1,1))/2;dy=(np.roll(h,1,0)-np.roll(h,-1,0))/2 # +v points up the image
 nrm=np.stack([-dx*2.2,-dy*2.2,np.ones_like(h)],2);nrm/=np.linalg.norm(nrm,axis=2,keepdims=True)
 out=[]
 for name,arr,path in [('Band hair volume',col,LIK/'hair-volume.jpg'),('Band hair volume normal',nrm*.5+.5,LIK/'hair-volume-normal.jpg')]:
  img=bpy.data.images.new(name,width=n,height=n,alpha=False)
  rgba=np.concatenate([np.clip(arr,0,1),np.ones((n,n,1))],2)
  img.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).astype(np.float32).ravel());out.append(save_jpeg(img,path,92))
 out[1].colorspace_settings.name='Non-Color'
 return out

def hair_volume_material(role):
 name=MEMBERS[role][0]+' hair volume';col,nrm=shell_textures()
 m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;p=nt.nodes.get('Principled BSDF')
 t=nt.nodes.new('ShaderNodeTexImage');t.image=col;nt.links.new(t.outputs['Color'],p.inputs['Base Color'])
 tn=nt.nodes.new('ShaderNodeTexImage');tn.image=nrm;nm=nt.nodes.new('ShaderNodeNormalMap');nt.links.new(tn.outputs['Color'],nm.inputs['Color']);nt.links.new(nm.outputs['Normal'],p.inputs['Normal'])
 p.inputs['Roughness'].default_value=.55;return m

def hair_card_material(role):
 name=MEMBERS[role][0]+' hair'
 if name in bpy.data.materials:bpy.data.materials.remove(bpy.data.materials[name])
 m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;p=nt.nodes.get('Principled BSDF')
 t=nt.nodes.new('ShaderNodeTexImage');t.image=hair_texture()
 nt.links.new(t.outputs['Color'],p.inputs['Base Color']);clip=nt.nodes.new('ShaderNodeMath');clip.operation='GREATER_THAN';clip.inputs[1].default_value=.4
 nt.links.new(t.outputs['Alpha'],clip.inputs[0]);nt.links.new(clip.outputs[0],p.inputs['Alpha']);p.inputs['Roughness'].default_value=.5
 m.surface_render_method='DITHERED';return m

def hair_shell(role,rig,body,F):
 """Hair mass grown from the scalp itself, so skin never shows between locks.
 Mark's gelled clumps and Travis's crest are sculpted into the mass; strand
 cards on top only break up the silhouette."""
 me=body.data;du=F['du'];vmask={}
 for v in me.vertices:
  X,Z,D=head_coords(v.co,F)
  if abs(X)>1.6 or Z<-2:continue
  hm=hairline(role,X,Z,D)
  if role=='Drummer':hm*=1-smooth(.22,.30,abs(X))
  vmask[v.index]=hm
 polys=[p for p in me.polygons if all(vmask.get(i,0)>=.3 for i in p.vertices) and is_head_poly(p.center,F)]
 bm=bmesh.new();vmap={}
 for p in polys:
  for i in p.vertices:
   if i not in vmap:
    nv=bm.verts.new(me.vertices[i].co);nv.normal=me.vertices[i].normal;vmap[i]=nv
  bm.faces.new([vmap[i] for i in p.vertices])
 bm.normal_update()
 bmesh.ops.subdivide_edges(bm,edges=bm.edges[:],cuts=1,use_grid_fill=True,smooth=1.0)
 bm.normal_update()
 rng=random.Random({'Bassist':4,'Guitarist':5,'Drummer':6}[role])
 # Clump centres for Mark's spikes, scattered over the top of the head.
 tops=[v.co.copy() for v in bm.verts if head_coords(v.co,F)[1]>1.75 and abs(head_coords(v.co,F)[0])<.85]
 clumps=[(rng.choice(tops),rng.uniform(.55,1.0),rng.uniform(.10,.16)*du) for _ in range(70 if role=='Bassist' else 0)]
 fwd=Vector((0,-1,0));up=Vector((0,0,1))
 for v in bm.verts:
  X,Z,D=head_coords(v.co,F);hm=hairline(role,X,Z,D)
  if role=='Drummer':hm*=1-smooth(.22,.30,abs(X))
  edge=smooth(.3,.8,hm);n=v.normal.copy();top=1-smooth(.5,.95,abs(X))
  if role=='Bassist':
   t=.05+.07*top*smooth(1.5,2.1,Z);spike=0
   for c,amp,rad in clumps:
    d=(v.co-c).length
    if d<rad*2.2:spike=max(spike,amp*max(0,1-d/(rad*2.2))**1.6)
   disp=n*du*t+(n*.75+up*.45+fwd*.35*smooth(-.8,.1,D)).normalized()*du*.42*spike
   disp+=n*du*.018*math.sin(math.atan2(X,D+.9)*31+Z*5)
  elif role=='Guitarist':
   t=.07+.16*top*smooth(1.3,2.3,Z)+.05*smooth(-.3,-1.2,D)
   disp=n*du*t+fwd*du*.05*smooth(1.8,2.3,Z)*top
   az=math.atan2(X,D+.9);disp+=n*du*.035*math.sin(az*23+Z*3.1+math.sin(az*7)*2)*smooth(1.0,1.8,Z)
  else:
   ridge=max(0,1-abs(X)/.26)**1.3
   disp=n*du*(.04+.30*ridge*smooth(1.7,2.1,Z)*(.75+.25*math.sin(Z*19+X*9)))
  v.co=v.co+disp*edge
 # Strands radiate from the crown whorl: polar angle -> v, azimuth -> u.
 centre=Vector((0,F['eye'].y+.9*du,F['eye'].z+.4*du));crown=Vector((0,.45,1)).normalized()
 e1=Vector((1,0,0));e2=crown.cross(e1).normalized();R=1.7*du
 uvl=bm.loops.layers.uv.new('UVMap')
 for f in bm.faces:
  uv=[]
  for l in f.loops:
   d=(l.vert.co-centre).normalized();th=math.acos(max(-1,min(1,d.dot(crown))));ph=math.atan2(d.dot(e2),d.dot(e1))
   uv.append(Vector((ph/math.tau*7,th*R/(.55*du))))
  mx=max(u.x for u in uv)
  for l,u in zip(f.loops,uv):l[uvl].uv=(u.x+7 if mx-u.x>3.5 else u.x,u.y)
  f.smooth=True
 geo=bpy.data.meshes.new(MEMBERS[role][0]+' hair volume');bm.to_mesh(geo);bm.free()
 o=bpy.data.objects.new(MEMBERS[role][0]+' hair volume',geo);bpy.context.collection.objects.link(o);o.parent=rig;o.data.materials.append(hair_volume_material(role))
 vg=o.vertex_groups.new(name='head');vg.add(list(range(len(geo.vertices))),1,'REPLACE');mod=o.modifiers.new('Follow performer','ARMATURE');mod.object=rig
 return o

def _scalp_surface(body,F,role):
 me=body.data;verts=[v.co.copy() for v in me.vertices]
 polys=[p for p in me.polygons if is_head_poly(p.center,F)]
 bvh=BVHTree.FromPolygons(verts,[tuple(p.vertices) for p in polys])
 samples=[]
 for p in polys:
  X,Z,D=head_coords(p.center,F)
  if hairline(role,X,Z,D)>.6:samples.append((p.center.copy(),p.normal.copy(),p.area,X,Z,D))
 return bvh,samples

def _ribbon(verts,faces,uvs,points,side,width,u0,u1,taper=.55):
 n=len(points);start=len(verts)
 for i,p in enumerate(points):
  t=i/(n-1);w=width*(1-taper*t);s=side[i] if isinstance(side,list) else side
  verts+=[p-s*w/2,p+s*w/2];uvs+=[(u0,t*.98+.01),(u1,t*.98+.01)]
 for i in range(n-1):a=start+2*i;faces.append((a,a+1,a+3,a+2))

def hair_cards(role,rig,body):
 """Hair volume plus narrow strand cards that break up the silhouette."""
 F=head_frame(body,rig);hair_shell(role,rig,body,F);bvh,samples=_scalp_surface(body,F,role)
 rng=random.Random({'Bassist':72,'Guitarist':31,'Drummer':18}[role]);du=F['du'];eye=F['eye']
 verts=[];faces=[];uvs=[];weights=[s[2] for s in samples];up=Vector((0,0,1));fwd=Vector((0,-1,0))
 def variant():k=rng.randrange(4);return (k*.25+.01,k*.25+.24)
 def spikes(count,length,width,aim,filt):
  pool=[s for s in samples if filt(s[3],s[4],s[5])];pw=[s[2] for s in pool]
  for _ in range(count):
   c,n,a,X,Z,D=rng.choices(pool,pw)[0]
   L=length(X,Z,D)*rng.uniform(.7,1.25);d=(aim(c,n,X,Z,D)+Vector((rng.uniform(-.3,.3),rng.uniform(-.3,.3),rng.uniform(-.1,.2)))).normalized()
   bend=Vector((rng.uniform(-.25,.25),rng.uniform(-.25,.25),-.15))
   root=c-n*du*.02;pts=[root+d*L*t+bend*L*.3*t*t for t in [0,.25,.5,.75,1]]
   s1=d.cross(n if abs(d.dot(n))<.95 else e1x).normalized();s2=d.cross(s1).normalized()
   w=width*rng.uniform(.75,1.3);u0,u1=variant()
   _ribbon(verts,faces,uvs,pts,s1,w,u0,u1,.7);_ribbon(verts,faces,uvs,pts,s2,w,u0,u1,.7)
 e1x=Vector((1,0,0))
 if role=='Bassist':
  # Textured top pushed up and forward into irregular, clumped spikes.
  spikes(340,lambda X,Z,D:du*(.22+.22*smooth(1.7,2.3,Z)*(1-smooth(.5,.9,abs(X)))),du*.09,
         lambda c,n,X,Z,D:(n+up*.6+fwd*.45*smooth(-.8,.1,D)).normalized(),lambda X,Z,D:abs(X)<.95 and Z>1.5)
  spikes(260,lambda X,Z,D:du*.13,du*.08,lambda c,n,X,Z,D:(n*.6+Vector((0,.5,-.6))).normalized(),lambda X,Z,D:abs(X)>.7)
 elif role=='Guitarist':
  # Side-swept fringe falling across the forehead toward the viewer's left.
  front=[s for s in samples if abs(s[3])<.8 and s[4]>1.85 and s[5]>-.5]
  for k in range(170):
   c,n,a,X,Z,D=rng.choice(front);L=du*rng.uniform(.8,1.25);pts=[];p=c+n*du*.10;d=(fwd*.7+Vector((-.55,0,-.45))).normalized()
   for i in range(6):
    t=i/5;loc,nor,_,_=bvh.find_nearest(p);pts.append(loc+nor*du*(.10+.05*math.sin(t*math.pi)+.03*t))
    d=(d+Vector((-.12,0,-.22))).normalized();d=(d-nor*d.dot(nor)).normalized();p=loc+d*L/5
   sides=[]
   for i in range(6):
    tan=(pts[min(i+1,5)]-pts[max(i-1,0)]).normalized();_,nor,_,_=bvh.find_nearest(pts[i]);sides.append(tan.cross(nor).normalized())
   u0,u1=variant();_ribbon(verts,faces,uvs,pts,sides,du*rng.uniform(.16,.26),u0,u1,.6)
  spikes(420,lambda X,Z,D:du*.42,du*.12,lambda c,n,X,Z,D:(n*.55+fwd*.6+Vector((-.4,0,0))).normalized(),lambda X,Z,D:abs(X)<.7 and Z>1.8)
 else:
  # Short spiked mohawk strip from the hairline over the crown.
  spikes(240,lambda X,Z,D:du*(.36+.14*smooth(1.9,2.3,Z)),du*.08,lambda c,n,X,Z,D:(n+up*.2-fwd*.2).normalized(),lambda X,Z,D:abs(X)<.12)
 o=rigid_mesh(MEMBERS[role][0]+' hairstyle',verts,faces,hair_card_material(role),rig)
 layer=o.data.uv_layers.new(name='UVMap')
 for poly in o.data.polygons:
  for li,vi in zip(poly.loop_indices,poly.vertices):layer.data[li].uv=uvs[vi]
 return o

def eyelashes(role,rig):
 """Lash strips on MakeHuman's eyelash helper geometry (follows the fitted lids)."""
 mat=bpy.data.materials.get('Band eyelashes')
 if not mat:
  mat=bpy.data.materials.new('Band eyelashes');mat.use_nodes=True;nt=mat.node_tree;p=nt.nodes.get('Principled BSDF')
  t=nt.nodes.new('ShaderNodeTexImage');t.image=lash_texture();nt.links.new(t.outputs['Color'],p.inputs['Base Color'])
  clip=nt.nodes.new('ShaderNodeMath');clip.operation='GREATER_THAN';clip.inputs[1].default_value=.35;nt.links.new(t.outputs['Alpha'],clip.inputs[0]);nt.links.new(clip.outputs[0],p.inputs['Alpha'])
  mat.surface_render_method='DITHERED'
 sel=[(g,f) for g,f in faces if 'eyelashes' in g]
 ids=sorted({i for _,f in sel for i,j in f});lookup={a:k for k,a in enumerate(ids)}
 geo=bpy.data.meshes.new(MEMBERS[role][0]+' eyelashes');geo.from_pydata([conv(morphed[i]) for i in ids],[],[[lookup[i] for i,j in f] for _,f in sel]);geo.update()
 ob=bpy.data.objects.new(MEMBERS[role][0]+' eyelashes',geo);bpy.context.collection.objects.link(ob);ob.parent=rig;ob.data.materials.append(mat)
 # UV: u runs along the lid (angle around the eye centre), v from the lid root outwards.
 layer=geo.uv_layers.new(name='UVMap')
 groups={}
 for g,f in sel:groups.setdefault(g,[]).extend(lookup[i] for i,j in f)
 vu={}
 for g,vs in groups.items():
  vs=set(vs);c=sum((geo.vertices[i].co for i in vs),Vector())/len(vs)
  side=1 if c.x>0 else -1;eyec=rig.data.bones['eye.'+('L' if side>0 else 'R')].head_local
  ang={i:math.atan2(geo.vertices[i].co.z-eyec.z,(geo.vertices[i].co.x-eyec.x)*side) for i in vs}
  rad={i:(geo.vertices[i].co-eyec).length for i in vs}
  a0,a1=min(ang.values()),max(ang.values());r0,r1=min(rad.values()),max(rad.values())
  for i in vs:vu[i]=((ang[i]-a0)/max(1e-6,a1-a0),(rad[i]-r0)/max(1e-6,r1-r0))
 for poly in geo.polygons:
  poly.use_smooth=True
  for li,vi in zip(poly.loop_indices,poly.vertices):layer.data[li].uv=vu[vi]
 vg=ob.vertex_groups.new(name='head');vg.add(list(range(len(geo.vertices))),1,'REPLACE')
 mod=ob.modifiers.new('Follow performer','ARMATURE');mod.object=rig
 return ob

def layered_eyes(role,rig,proxy):
 """Replace the 43-face proxy eyes with smooth eyeballs, a raised cornea and a procedural iris."""
 member=MEMBERS[role][0];co=[v.co for v in proxy.data.vertices]
 geo=bpy.data.meshes.new(role+' eyes');bm=bmesh.new();uvl=bm.loops.layers.uv.new('UVMap')
 for side,bone in [(1,'eye.L'),(-1,'eye.R')]:
  pts=[c for c in co if c.x*side>0];lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)));hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
  r=(hi.z-lo.z)/2*.95;centre=Vector(((lo.x+hi.x)/2,lo.y+r*.96,(lo.z+hi.z)/2))
  tmp=bmesh.new();bmesh.ops.create_uvsphere(tmp,u_segments=28,v_segments=18,radius=r)
  for v in tmp.verts:
   d=Vector((v.co.x,-v.co.z,v.co.y)).normalized() # pole along -Y (forward)
   ang=math.acos(max(-1,min(1,-d.y)));bulge=r*.085*max(0,math.cos(min(math.pi/2,ang/0.62*math.pi/2)))**1.5 if ang<.62 else 0
   v.co=centre+d*(r+bulge)
  vmap={}
  for v in tmp.verts:vmap[v]=bm.verts.new(v.co)
  for f in tmp.faces:
   nf=bm.faces.new([vmap[v] for v in f.verts]);nf.smooth=True
  tmp.free()
 # UVs: frontal planar projection per eye.
 centres={}
 for side in [1,-1]:
  pts=[v.co for v in bm.verts if v.co.x*side>0];lo=min(p.x for p in pts);hi=max(p.x for p in pts);zl=min(p.z for p in pts);zh=max(p.z for p in pts)
  centres[side]=(Vector(((lo+hi)/2,0,(zl+zh)/2)),(hi-lo)/2)
 for f in bm.faces:
  for l in f.loops:
   side=1 if l.vert.co.x>0 else -1;c,r=centres[side];p=l.vert.co
   l[uvl].uv=(.5+(p.x-c.x)/(2*r)*.98,.5+(p.z-c.z)/(2*r)*.98)
 bm.to_mesh(geo);bm.free()
 ob=bpy.data.objects.new(role+' eyes',geo);bpy.context.collection.objects.link(ob);ob.parent=rig
 img=iris_texture(role)
 m=bpy.data.materials.new(member+' eyes');m.use_nodes=True;nt=m.node_tree;p=nt.nodes.get('Principled BSDF')
 t=nt.nodes.new('ShaderNodeTexImage');t.image=img;nt.links.new(t.outputs['Color'],p.inputs['Base Color']);p.inputs['Roughness'].default_value=.08
 p.inputs['Coat Weight'].default_value=1;p.inputs['Coat Roughness'].default_value=.03
 ob.data.materials.append(m)
 for side,bone in [(1,'eye.L'),(-1,'eye.R')]:
  vg=ob.vertex_groups.new(name=bone);vg.add([v.index for v in geo.vertices if v.co.x*side>0],1,'REPLACE')
 mod=ob.modifiers.new('Performance rig','ARMATURE');mod.object=rig
 bpy.data.objects.remove(proxy,do_unlink=True);ob.name=role+' eyes'
 return ob
