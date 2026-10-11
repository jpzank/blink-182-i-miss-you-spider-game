"""Period-specific anatomy, face projection and costume for the band.

Executed in the build-musicians.py context. Generated facial albedo is baked
into the body's native UVs and, via band-heads.py, into a dedicated head UV;
nothing is projected at runtime.
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
 heads,frame=head_uv(role,ob,rig)
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
 tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=native_tint(role);links.new(base.outputs['Color'],tint.inputs[1])
 face=n.new('ShaderNodeTexImage');face.image=bpy.data.images.load(str(LIK/'facial-atlas-v1.png'),check_existing=True);face.extension='EXTEND'
 uvface=n.new('ShaderNodeUVMap');uvface.uv_map='FaceProjection';links.new(uvface.outputs[0],face.inputs['Vector'])
 attribute=n.new('ShaderNodeVertexColor');attribute.layer_name='FaceMask';mix=n.new('ShaderNodeMixRGB');links.new(attribute.outputs['Color'],mix.inputs[0]);links.new(tint.outputs[0],mix.inputs[1]);links.new(face.outputs['Color'],mix.inputs[2])
 color=mix.outputs[0]
 tattoo=LIK/'tattoo-albedo-v1.png'
 if role=='Drummer' and tattoo.exists():
  tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(tattoo),check_existing=True);uvink=n.new('ShaderNodeUVMap');uvink.uv_map='InkProjection';links.new(uvink.outputs[0],tex.inputs['Vector'])
  masknode=n.new('ShaderNodeVertexColor');masknode.layer_name='InkMask';mixink=n.new('ShaderNodeMixRGB');links.new(masknode.outputs['Color'],mixink.inputs[0]);links.new(color,mixink.inputs[1]);links.new(tex.outputs['Color'],mixink.inputs[2]);color=mixink.outputs[0]
 links.new(color,em.inputs['Color']);ob.data.materials.clear();ob.data.materials.append(m)
 baked=bpy.data.images.new(member+' albedo',width=1024,height=1024,alpha=False);target=n.new('ShaderNodeTexImage');target.image=baked;n.active=target
 ob.data.uv_layers.active=ob.data.uv_layers['UVMap'];ob.data.uv_layers['UVMap'].active_render=True
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=1;bpy.context.scene.render.bake.margin=12
 bpy.ops.object.bake(type='EMIT')
 path=LIK/'baked'/f'{role.lower()}-albedo.jpg';baked=save_jpeg(baked,path,90)
 albedo,rough,normal=bake_head(role,ob,rig,m,color,frame)
 final=material(member+' skin',path,rough=.7);ob.data.materials.clear();ob.data.materials.append(final);ob.data.materials.append(face_material(member,albedo,rough,normal))
 for poly in ob.data.polygons:poly.material_index=1 if poly.index in heads else 0
 ob.data.uv_layers.remove(ob.data.uv_layers['FaceProjection']);ob.data.uv_layers.remove(ob.data.uv_layers['InkProjection']);ob.data.color_attributes.remove(ob.data.color_attributes['FaceMask']);ob.data.color_attributes.remove(ob.data.color_attributes['InkMask'])
 ob.data.uv_layers.active=ob.data.uv_layers['UVMap']
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
  path=LIK/'baked'/f'{role.lower()}-costume.jpg';baked=save_jpeg(baked,path,90)
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
