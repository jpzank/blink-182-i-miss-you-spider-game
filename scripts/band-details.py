"""Period-specific anatomy, face projection, hair and costume for the band.

Executed in the build-musicians.py context. Generated facial albedo is baked
into the body's native UVs; nothing is projected at runtime.
"""
LIK=ROOT/'assets-src/band-likeness'
LANDMARKS=json.load(open(LIK/'landmarks.json'))
MEMBERS={'Bassist':('Mark Hoppus',0,3.9),'Guitarist':('Tom DeLonge',1,4.06),'Drummer':('Travis Barker',2,3.74)}
def clamp(x):return min(1,max(0,x))
def smooth(a,b,x):
 t=clamp((x-a)/(b-a));return t*t*(3-2*t)

def member_anatomy(role):
 out=[v.copy() for v in anatomy]
 for p in out:
  x,y,z=p;face=smooth(6.8,7.25,y)
  if role=='Bassist':
   jaw=math.exp(-((y-7.4)/.45)**2);p.x*=1+face*(.065+.065*jaw);p.y=8.15+(y-8.15)*(1-.035*face)
   p.z+=.07*face*math.exp(-((y-7.15)/.25)**2)
  elif role=='Guitarist':
   p.y=8.15+(y-8.15)*(1+.065*face);p.x*=1+.035*face
   p.z+=.085*face*math.exp(-((y-7.85)/.26)**2)*math.exp(-(x/.22)**2)
  else:
   p.x*=1-.12*face;p.z-=.07*face*math.exp(-((abs(x)-.45)/.2)**2)*math.exp(-((y-7.75)/.45)**2)
   p.z+=.08*face*math.exp(-((y-7.83)/.23)**2)*math.exp(-(x/.2)**2)
   if y<6.6:p.x*=.94
 return out

def skin_for_member(role,ob,rig):
 idx=MEMBERS[role][1];member=MEMBERS[role][0];lm=LANDMARKS['columns'][idx]
 eyes=lm['eyes'];eye_px=sum(p[0] for p in eyes)/2;eye_py=sum(p[1] for p in eyes)/2
 e=rig.data.bones['eye.L'].tail_local;eyex=abs(e.x/S);eyey=e.z/S+foot;mouth=morphed[493].y
 sx=(eyes[1][0]-eyes[0][0])/(2*eyex);sy=(lm['mouthCenter'][1]-eye_py)/(eyey-mouth)
 faceuv=ob.data.uv_layers.new(name='FaceProjection');inkuv=ob.data.uv_layers.new(name='InkProjection')
 mask=ob.data.color_attributes.new(name='FaceMask',type='FLOAT_COLOR',domain='CORNER')
 ink=ob.data.color_attributes.new(name='InkMask',type='FLOAT_COLOR',domain='CORNER')
 for poly in ob.data.polygons:
  for li in poly.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;x,y,z=v.x/S,v.z/S+foot,-v.y/S
   py=eye_py+(eyey-y)*sy
   if role=='Drummer':py=max(90,py) # Extend shaved scalp; never sample the atlas background above the head.
   faceuv.data[li].uv=((eye_px+x*sx)/LANDMARKS['width'],1-py/LANDMARKS['height'])
   weight=smooth(.65,1.2,z)*smooth(6.9,7.25,y)*(1-smooth(.8,1.13,abs(x)))
   if role=='Drummer':weight=max(weight,smooth(8.15,8.6,y)*(1-smooth(.72,1.05,abs(x))))
   mask.data[li].color=(weight,weight,weight,1)
   arm=smooth(1.8,2.45,abs(x))*(1-smooth(5.0,5.35,abs(x)))*smooth(1.8,2.4,y)
   neck=smooth(6.1,6.4,y)*(1-smooth(6.8,7.1,y))*(1-smooth(.45,.7,abs(x)))
   imask=max(arm,neck*.75) if role=='Drummer' else 0
   ink.data[li].color=(imask,imask,imask,1)
   inkuv.data[li].uv=(abs(x)*.42+z*.2,y*.31)
 m=bpy.data.materials.new(member+' skin bake');m.use_nodes=True;n=m.node_tree.nodes;n.clear();links=m.node_tree.links
 out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');links.new(em.outputs[0],out.inputs['Surface'])
 base=n.new('ShaderNodeTexImage');base.image=bpy.data.images.load(str(SYSTEM/'skins/young_caucasian_male/young_lightskinned_male_diffuse.png'),check_existing=True)
 native=n.new('ShaderNodeUVMap');native.uv_map='UVMap';links.new(native.outputs[0],base.inputs['Vector'])
 face=n.new('ShaderNodeTexImage');face.image=bpy.data.images.load(str(LIK/'facial-atlas-v1.png'),check_existing=True);face.extension='EXTEND'
 uvface=n.new('ShaderNodeUVMap');uvface.uv_map='FaceProjection';links.new(uvface.outputs[0],face.inputs['Vector'])
 attribute=n.new('ShaderNodeVertexColor');attribute.layer_name='FaceMask';mix=n.new('ShaderNodeMixRGB');links.new(attribute.outputs['Color'],mix.inputs[0]);links.new(base.outputs['Color'],mix.inputs[1]);links.new(face.outputs['Color'],mix.inputs[2])
 color=mix.outputs[0]
 tattoo=LIK/'tattoo-albedo-v1.png'
 if role=='Drummer' and tattoo.exists():
  tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(tattoo),check_existing=True);uvink=n.new('ShaderNodeUVMap');uvink.uv_map='InkProjection';links.new(uvink.outputs[0],tex.inputs['Vector'])
  masknode=n.new('ShaderNodeVertexColor');masknode.layer_name='InkMask';mixink=n.new('ShaderNodeMixRGB');links.new(masknode.outputs['Color'],mixink.inputs[0]);links.new(color,mixink.inputs[1]);links.new(tex.outputs['Color'],mixink.inputs[2]);color=mixink.outputs[0]
 links.new(color,em.inputs['Color']);ob.data.materials.clear();ob.data.materials.append(m)
 baked=bpy.data.images.new(member+' albedo',width=1536,height=1536,alpha=False);target=n.new('ShaderNodeTexImage');target.image=baked;n.active=target
 ob.data.uv_layers.active=ob.data.uv_layers['UVMap'];ob.data.uv_layers['UVMap'].active_render=True
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=1;bpy.context.scene.render.bake.margin=12
 bpy.ops.object.bake(type='EMIT')
 path=LIK/'baked'/f'{role.lower()}-albedo.png';baked.filepath_raw=str(path);baked.file_format='PNG';baked.save()
 final=material(member+' skin',path,rough=.7);ob.data.materials.clear();ob.data.materials.append(final)
 ob.data.uv_layers.remove(faceuv);ob.data.uv_layers.remove(inkuv);ob.data.color_attributes.remove(mask);ob.data.color_attributes.remove(ink)
 ob.select_set(False)

def style_garment(role,ob):
 if ob.name.startswith('male_elegantsuit'):
  # Keep the source UV's collar, seams and buttons; recolor the woven cloth
  # with a baked material instead of assigning whole faces across UV islands.
  m=bpy.data.materials.new(MEMBERS[role][0]+' costume bake');m.use_nodes=True;n=m.node_tree.nodes;n.clear();links=m.node_tree.links
  out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');links.new(em.outputs[0],out.inputs['Surface'])
  tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(SYSTEM/'clothes/male_elegantsuit01/male_elegantsuit01_diffuse.png'),check_existing=True)
  hsv=n.new('ShaderNodeHueSaturation');links.new(tex.outputs['Color'],hsv.inputs['Color'])
  if role=='Bassist':
   hsv.inputs['Saturation'].default_value=0
   gamma=n.new('ShaderNodeGamma');gamma.inputs[1].default_value=.65;links.new(hsv.outputs[0],gamma.inputs[0]);color=gamma.outputs[0]
   sep=n.new('ShaderNodeSeparateColor');links.new(tex.outputs['Color'],sep.inputs['Color'])
   diff=n.new('ShaderNodeMath');diff.operation='SUBTRACT';links.new(sep.outputs['Blue'],diff.inputs[0]);links.new(sep.outputs['Red'],diff.inputs[1])
   threshold=n.new('ShaderNodeMath');threshold.operation='GREATER_THAN';links.new(diff.outputs[0],threshold.inputs[0]);threshold.inputs[1].default_value=.005
   tie=n.new('ShaderNodeMixRGB');links.new(threshold.outputs[0],tie.inputs[0]);links.new(color,tie.inputs[1]);tie.inputs[2].default_value=(.009,.012,.011,1);color=tie.outputs[0]
   uvnode=n.new('ShaderNodeTexCoord');uvsep=n.new('ShaderNodeSeparateXYZ');links.new(uvnode.outputs['UV'],uvsep.inputs[0])
   def mathnode(op,a,b):
    node=n.new('ShaderNodeMath');node.operation=op
    for i,value in enumerate([a,b]):
     if isinstance(value,(float,int)):node.inputs[i].default_value=value
     else:links.new(value,node.inputs[i])
    return node.outputs[0]
   diagonal=mathnode('MULTIPLY',mathnode('SUBTRACT',uvsep.outputs['Y'],.818),.26)
   low=mathnode('GREATER_THAN',uvsep.outputs['X'],mathnode('ADD',diagonal,.359));high=mathnode('LESS_THAN',uvsep.outputs['X'],mathnode('ADD',diagonal,.389))
   lowy=mathnode('GREATER_THAN',uvsep.outputs['Y'],.818);highy=mathnode('LESS_THAN',uvsep.outputs['Y'],.929)
   inside=mathnode('MULTIPLY',mathnode('MULTIPLY',low,high),mathnode('MULTIPLY',lowy,highy))
   dark=n.new('ShaderNodeMixRGB');links.new(inside,dark.inputs[0]);links.new(color,dark.inputs[1]);dark.inputs[2].default_value=(.009,.012,.011,1);color=dark.outputs[0]
  else:
   hsv.inputs['Hue'].default_value=.84;hsv.inputs['Saturation'].default_value=1.15;color=hsv.outputs[0]
  links.new(color,em.inputs['Color']);ob.data.materials.clear();ob.data.materials.append(m)
  baked=bpy.data.images.new(MEMBERS[role][0]+' costume',width=1536,height=1536,alpha=False);target=n.new('ShaderNodeTexImage');target.image=baked;n.active=target
  bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
  bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=1;bpy.context.scene.render.bake.margin=12;bpy.ops.object.bake(type='EMIT')
  path=LIK/'baked'/f'{role.lower()}-costume.png';baked.filepath_raw=str(path);baked.file_format='PNG';baked.save()
  ob.data.materials.clear();ob.data.materials.append(material(MEMBERS[role][0]+' suit',path,rough=.91));ob.select_set(False)
 elif ob.name.startswith('male_casualsuit'):
  tee=material('Travis white T-shirt',color=(.82,.80,.74,1),rough=.96);pants=material('Travis black trousers',color=(.018,.023,.022,1),rough=.93)
  ob.data.materials.clear();ob.data.materials.append(tee);ob.data.materials.append(pants)
  for p in ob.data.polygons:p.material_index=0 if p.center.z>1.8 else 1

def rigid_mesh(name,verts,faces,mat,rig,bone='head'):
 geo=bpy.data.meshes.new(name);geo.from_pydata(verts,[],faces);geo.update();o=bpy.data.objects.new(name,geo);bpy.context.collection.objects.link(o);o.parent=rig;o.data.materials.append(mat)
 vg=o.vertex_groups.new(name=bone);vg.add(list(range(len(verts))),1,'REPLACE');mod=o.modifiers.new('Follow performer','ARMATURE');mod.object=rig
 for p in geo.polygons:p.use_smooth=True
 return o

def member_hair(role,rig):
 hair=material(MEMBERS[role][0]+' hair',color=(.018,.014,.012,1),rough=.86)
 if role=='Guitarist':
  path=SYSTEM/'hair/short03';h=material('Tom dark fringe',path/'short03_diffuse.png',rough=.86,alpha=True)
  # Darken the source hair through the texture shader before it is exported.
  bs=h.node_tree.nodes.get('Principled BSDF');tex=next(n for n in h.node_tree.nodes if n.type=='TEX_IMAGE');mult=h.node_tree.nodes.new('ShaderNodeMixRGB');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1;mult.inputs[2].default_value=(.12,.09,.075,1);h.node_tree.links.new(tex.outputs['Color'],mult.inputs[1]);h.node_tree.links.new(mult.outputs[0],bs.inputs['Base Color'])
  garment(path,'short03',rig,h)
  return
 # Anatomical scalp shell with a raised, irregular silhouette.
 rawfaces=[]
 for g,f in faces:
  if g!='body':continue
  c=sum((morphed[i] for i,j in f),Vector())/len(f)
  keep=(c.y>8.55 or c.y>8.2 and c.z<.5) if role=='Bassist' else abs(c.x)<.20 and (c.y>8.6 or c.y>7.85 and c.z<.05)
  if keep:rawfaces.append((g,f))
 cap=[v.copy() for v in morphed]
 for p in cap:
  if p.y>7.7:p.x*=1.015;p.z=.45+(p.z-.45)*1.015;p.y+=.035
 weights_hair={i:{'head':1} for i in range(len(cap))};mesh(MEMBERS[role][0]+' hair cap',cap,uv,rawfaces,hair,rig,weights_hair)
 rng=random.Random(72 if role=='Bassist' else 18);vertices=[];polys=[]
 count=680 if role=='Bassist' else 170
 # Anchor every tuft to the fitted scalp, including its actual front/back depth.
 candidates=[]
 for _,f in rawfaces:
  pts=[conv(morphed[i]) for i,j in f];c=sum(pts,Vector())/len(pts)
  normal=(pts[1]-pts[0]).cross(pts[2]-pts[0]).normalized()
  if normal.z>.15 or role=='Drummer':candidates.append((c,normal))
 for k in range(count):
  c,normal=rng.choice(candidates);root=c+normal*.008
  if role=='Bassist':
   root+=Vector((rng.uniform(-.009,.009),rng.uniform(-.009,.009),0));height=rng.uniform(.023,.063);tip=root+Vector((normal.x*.03,-.02,height));radius=rng.uniform(.003,.007)
  else:
   root.x*=.7;tip=root+normal*.045+Vector((0,-.006,.043+rng.uniform(0,.022)));radius=.006
  axis=(tip-root).normalized();a=axis.cross(Vector((0,1,0))).normalized();b=axis.cross(a);start=len(vertices)
  for ring,factor in [(0,1),(.42,.62),(1,.018)]:
   p=root.lerp(tip,ring)
   for j in range(5):vertices.append(p+radius*factor*(math.cos(j*math.tau/5)*a+math.sin(j*math.tau/5)*b))
  for ring in range(2):
   for j in range(5):polys.append((start+ring*5+j,start+ring*5+(j+1)%5,start+(ring+1)*5+(j+1)%5,start+(ring+1)*5+j))
 rigid_mesh(MEMBERS[role][0]+' hairstyle',vertices,polys,hair,rig)

def suspenders(rig,body):
 blackstrap=material('Travis suspenders',color=(.012,.015,.015,1),rough=.86)
 # Follow the tee's actual front surface, with separate upper/lower spine weights.
 verts=[];polys=[];weights_out=[]
 for sign in [-1,1]:
  start=len(verts)
  topstrap=max(v.co.z for v in body.data.vertices if abs(v.co.x-sign*.34)<.1)-.028
  for j in range(17):
   z=1.82+j/16*(topstrap-1.82);x=sign*(.34+.035*math.sin(j/16*math.pi));target=Vector((x,0,z))
   nearby=[v.co for v in body.data.vertices if abs(v.co.x-x)<.10 and abs(v.co.z-z)<.11]
   y=min((v.y for v in nearby),default=-.30)-.025
   for s in [-1,1]:verts.append(Vector((x+s*.028,y,z)));weights_out.append('spine01' if z>2.55 else 'spine02')
   if j:polys.append((start+(j-1)*2,start+(j-1)*2+1,start+j*2+1,start+j*2))
 o=rigid_mesh('Travis black suspenders',verts,polys,blackstrap,rig,'spine01');o.vertex_groups.clear()
 for i,n in enumerate(weights_out):
  vg=o.vertex_groups.get(n) or o.vertex_groups.new(name=n);vg.add([i],1,'REPLACE')

def member_eyes(role,ob):
 # The CC0 base iris is strongly orange. Retain its iris fibres and sclera,
 # with a cool light iris for Mark and subdued brown for Tom and Travis.
 m=bpy.data.materials.new(MEMBERS[role][0]+' iris bake');m.use_nodes=True;n=m.node_tree.nodes;n.clear();links=m.node_tree.links
 out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');links.new(em.outputs[0],out.inputs['Surface'])
 tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(SRC/'brown_eye.png'),check_existing=True)
 hsv=n.new('ShaderNodeHueSaturation');hsv.inputs['Hue'].default_value=.02 if role=='Bassist' else .5;hsv.inputs['Saturation'].default_value=.38;hsv.inputs['Value'].default_value=.8;links.new(tex.outputs['Color'],hsv.inputs['Color']);links.new(hsv.outputs[0],em.inputs['Color'])
 ob.data.materials.clear();ob.data.materials.append(m);baked=bpy.data.images.new(MEMBERS[role][0]+' eyes',width=512,height=512,alpha=False);target=n.new('ShaderNodeTexImage');target.image=baked;n.active=target
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.bake(type='EMIT')
 path=LIK/'baked'/f'{role.lower()}-eyes.png';baked.filepath_raw=str(path);baked.file_format='PNG';baked.save();ob.data.materials.clear();ob.data.materials.append(material(MEMBERS[role][0]+' eyes',path,rough=.3));ob.select_set(False)
