import * as T from './vendor/three.module.js';
import {GLTFLoader} from './vendor/addons/loaders/GLTFLoader.js';
import {RoundedBoxGeometry} from './vendor/addons/geometries/RoundedBoxGeometry.js';
import {skin,eye} from './skin.js?v=8';

// The reclining scene lives beside the salon window, within the existing map.
// Its cover trails onto the floor so a spider can climb up to the mattress.
export function createAlcove(scene,materials,walkables,flame){
 const {wood,red,gold,cream}=materials,root=new T.Group();root.name='Alcova da janela';scene.add(root);
 const V=(x,y,z)=>new T.Vector3(x,y,z);
 const walnut=wood.clone();walnut.color.set('#4c3525');walnut.roughness=.72;
 const brocade=red.clone();brocade.color.set('#725b3c');brocade.roughness=.96;
 const linen=cream.clone();linen.color.set('#c2b495');linen.roughness=.98;
 const velvet=red.clone();velvet.color.set('#4c2428');velvet.roughness=1;
 const brass=gold.clone();brass.color.set('#7f6940');brass.roughness=.61;
 function mesh(geo,mat,x,y,z,parent=root){const o=new T.Mesh(geo,mat);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o;}
 function rounded(x,y,z,w,h,d,r,mat){return mesh(new RoundedBoxGeometry(w,h,d,3,r),mat,x,y,z);}
 function tube(points,r,mat,parent=root){return mesh(new T.TubeGeometry(new T.CatmullRomCurve3(points),Math.max(16,points.length*8),r,6,false),mat,0,0,0,parent);}
 function turn(x,z,height){
  const profile=[[0,.11],[.08,.16],[.18,.13],[.27,.09],[.45,.10],[.58,.16],[.65,.17],[.74,.09],[.89,.09],[1,.035]].map(([y,r])=>new T.Vector2(r,y*height));
  mesh(new T.LatheGeometry(profile,24),walnut,x,0,z);
 }
 for(const x of [6.05,11.08])for(const z of [6.35,10.45])turn(x,z,x>10?3.6:1.35);
 rounded(8.55,.72,8.4,5.25,.36,4.22,.1,walnut);
 for(const z of [6.27,10.53])rounded(8.55,.81,z,5.1,.13,.1,.025,brass);
 rounded(8.55,1.0,8.4,5.02,.42,4.08,.17,linen);
 // Piped seam follows the rounded mattress perimeter.
 const seam=[];for(let i=0;i<=80;i++){const a=i/80*Math.PI*2;seam.push(V(8.55+2.43*Math.sign(Math.cos(a))*Math.pow(Math.abs(Math.cos(a)),.27),1.07,8.4+1.97*Math.sign(Math.sin(a))*Math.pow(Math.abs(Math.sin(a)),.27)));}tube(seam,.012,brocade);
 const back=new T.Group();back.position.set(11.05,0,8.4);back.rotation.y=-Math.PI/2;back.scale.y=.92;root.add(back);
 const shape=new T.Shape();shape.moveTo(-2.1,.65);shape.lineTo(-2.1,2.6);shape.bezierCurveTo(-2.12,3.26,-1.48,3.04,-1.12,3.3);shape.bezierCurveTo(-.64,3.95,.64,3.95,1.12,3.3);shape.bezierCurveTo(1.48,3.04,2.12,3.26,2.1,2.6);shape.lineTo(2.1,.65);shape.closePath();
 mesh(new T.ExtrudeGeometry(shape,{depth:.16,bevelEnabled:true,bevelSize:.045,bevelThickness:.04,bevelSegments:3,curveSegments:28}),walnut,0,0,0,back);
 tube(shape.getPoints(90).map(p=>V(p.x,p.y,.19)),.025,brass,back);
 const inset=mesh(new RoundedBoxGeometry(3.65,1.48,.12,3,.15),velvet,0,2.22,.18,back);
 // Upholstery buttons and small carved scrolls, rather than a flat headboard.
 for(let row=0;row<3;row++)for(let col=0;col<7;col++)mesh(new T.SphereGeometry(.025,8,6),brass,-1.48+col*.49+(row%2)*.08,1.82+row*.4,.26,back);
 for(const side of [-1,1])for(let k=0;k<3;k++){
  const points=[];for(let j=0;j<40;j++){const a=j/39*Math.PI*3.5,r=.22*(1-j/45);points.push(V(side*(.36+k*.46+Math.cos(a)*r),3.14+Math.sin(a)*r-.07*k,.23));}tube(points,.027,walnut,back);
 }
 for(const z of [7.57,9.2]){
  const p=rounded(10.08,z<8?1.63:1.48,z,1.23,.3,1.48,.14,brocade);p.rotation.z=.11;const vp=p.geometry.attributes.position;for(let i=0;i<vp.count;i++){const x=vp.getX(i),y=vp.getY(i),zz=vp.getZ(i);vp.setY(i,y+.012*Math.sin(x*29+zz*2)*Math.sin(zz*23)*(1-Math.abs(y)/.3));}p.geometry.computeVertexNormals();
  if(z<8){const support=rounded(9.37,1.38,z,1.12,.29,1.35,.14,brocade);support.rotation.z=.18;}
  const bolster=mesh(new T.CylinderGeometry(.20,.20,1.28,28),velvet,10.60,1.44,z);bolster.rotation.x=Math.PI/2;
  for(const side of [-1,1])mesh(new T.SphereGeometry(.085,12,8),brass,10.60,1.44,z+side*.65);
 }
 const clothMat=brocade.clone();clothMat.side=T.DoubleSide;
 const sheet=new T.PlaneGeometry(3.0,4.75,58,74),a=sheet.attributes.position;
 for(let i=0;i<a.count;i++){
  const x=6.78+a.getX(i),z=8.4+a.getY(i),dx=Math.max(0,6.0-x),dz=Math.max(0,Math.abs(z-8.4)-2.06);
  const folds=.045*Math.sin(z*13+x*2)+.025*Math.sin(x*21-z*4);
  const legs=.11*Math.exp(-(((z-7.65)/.42)**2))+.11*Math.exp(-(((z-9.17)/.42)**2));
  a.setXYZ(i,x,Math.max(.12,1.36-dx*1.5-dz*3.6)+folds+legs,z);
 }
 sheet.computeVertexNormals();walkables.push(mesh(sheet,clothMat,0,0,0));
 // Dropped runner makes the foot of the bed actually traversable.
 const ramp=new T.BufferGeometry();ramp.setAttribute('position',new T.Float32BufferAttribute([4.85,.035,7.4,6.22,1.245,7.4,6.22,1.245,9.4,4.85,.035,9.4],3));ramp.setAttribute('uv',new T.Float32BufferAttribute([0,0,0,1,1,1,1,0],2));ramp.setIndex([0,2,1,0,3,2]);ramp.computeVertexNormals();const runner=mesh(ramp,clothMat,0,0,0);walkables.push(runner);
 const top=mesh(new T.PlaneGeometry(4.95,4.05),linen,8.55,1.22,8.4);top.rotation.x=-Math.PI/2;walkables.push(top);
 // Alcove light remains soft enough to keep skin and fabric detail readable.
 const lamp=new T.PointLight('#efc994',22,9,1.8);lamp.position.set(8.0,3.45,10.7);scene.add(lamp);
 for(const z of [6.4,10.4]){const base=mesh(new T.CylinderGeometry(.21,.3,.32,20),brass,10.8,1.3,z);mesh(new T.CylinderGeometry(.06,.075,.57,18),linen,10.8,1.72,z);flame(10.8,2.045,z,.32);}

 const loader=new GLTFLoader(),mixers=[];
 function finish(model){model.traverse(o=>{if(!o.isMesh)return;o.castShadow=true;o.receiveShadow=true;o.frustumCulled=false;for(const m of Array.isArray(o.material)?o.material:[o.material]){if(m.map)m.map.anisotropy=4;m.roughness=Math.max(.4,m.roughness);if(m.transparent||m.alphaMap){m.alphaTest=.35;m.transparent=false;m.depthWrite=true;m.side=T.DoubleSide;}}});}
 // Sphynx: velvet sheen of the fine down, red-shifted light bleed and ears
 // that glow when the lamp is behind them (the exported 'Thin' mask).
 function sphynx(model){model.traverse(o=>{if(!o.isMesh)return;
  if(o.material.name==='Sphynx skin'){const old=o.material;const m=new T.MeshPhysicalMaterial({name:old.name,map:old.map,normalMap:old.normalMap,roughnessMap:old.roughnessMap,roughness:1,sheen:.35,sheenRoughness:.75,sheenColor:new T.Color('#f3c9b6'),envMapIntensity:.8});
   const g=o.geometry;if(g.getAttribute('color')){g.setAttribute('thin',g.getAttribute('color'));g.deleteAttribute('color');}
   skin(m,{thin:'thin',wrap:[.5,.24,.18],glow:'#f07a66',strength:.4});old.dispose();o.material=m;}
  if(o.material.name==='Sphynx eyes'){o.material=eye(o.material);o.material.roughness=.35;o.castShadow=false;}
 });}
 const women=new T.Group();women.name='Duas mulheres reclinadas';women.position.set(8.5,1.25,8.4);scene.add(women);
 const cat=new T.Group();cat.name='Gato sem pelos';cat.position.set(4.15,.04,4.9);cat.rotation.y=-.85;scene.add(cat);
 const ready=Promise.all([
  loader.loadAsync('./models/reclining-women-v6.glb').then(gltf=>{finish(gltf.scene);women.add(gltf.scene);gltf.scene.traverse(o=>{if(o.isMesh)walkables.push(o);});const mixer=new T.AnimationMixer(gltf.scene);gltf.animations.forEach(a=>mixer.clipAction(a).play());mixers.push(mixer);}),
  loader.loadAsync('./models/sphynx-v7.glb').then(gltf=>{finish(gltf.scene);sphynx(gltf.scene);gltf.scene.scale.setScalar(1.18);cat.add(gltf.scene);const mixer=new T.AnimationMixer(gltf.scene);gltf.animations.forEach(a=>mixer.clipAction(a).play());mixers.push(mixer);})
 ]);
 return {ready,cat,women,update(t){for(const mixer of mixers)mixer.setTime(t);}};
}
