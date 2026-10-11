import * as T from './vendor/three.module.js';
import {createSpider,createViewLegs} from './spider.js?v=6';
import {loadMusicians,loadFurniture} from './musicians.js?v=8';
import {createAlcove} from './alcove.js?v=8';
import {mergeGeometries} from './vendor/BufferGeometryUtils.js';
import {NODES,cycleAt,birdBlocking} from './rules.js';
const V=(x,y,z)=>new T.Vector3(x,y,z);
function texture(kind){const c=document.createElement('canvas');c.width=c.height=512;const a=c.getContext('2d');let seed=39;const random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296};
 if(kind==='wood'){a.fillStyle='#45382a';a.fillRect(0,0,512,512);for(let j=0;j<8;j++){a.fillStyle=j%2?'#4b3c2d':'#3f3429';a.fillRect(j*64,0,63,512);for(let i=0;i<150;i++){a.strokeStyle=`rgba(16,12,8,${random()*.15})`;a.beginPath();const x=j*64+random()*62;a.moveTo(x,0);a.bezierCurveTo(x+random()*12,160,x-8,350,x,512);a.stroke()}a.fillStyle='#211b16';a.fillRect(j*64,0,2,512);a.fillRect(j*64,(j%3)*150+20,64,2)}}
 if(kind==='wall'){a.fillStyle='#36413b';a.fillRect(0,0,512,512);for(let y=0;y<512;y+=64)for(let x=0;x<512;x+=64){a.strokeStyle='#495147';a.lineWidth=2;a.beginPath();a.ellipse(x+32,y+32,15,25,0,0,Math.PI*2);a.stroke();a.beginPath();a.moveTo(x+32,y+8);a.bezierCurveTo(x+58,y+35,x+5,y+40,x+32,y+55);a.stroke()}}
 if(kind==='rug'){a.fillStyle='#432d29';a.fillRect(0,0,512,512);for(let i=0;i<7;i++){a.strokeStyle=['#927a53','#594c37','#273933'][i%3];a.lineWidth=6;a.strokeRect(10+i*10,10+i*10,492-i*20,492-i*20)}for(let y=96;y<440;y+=60)for(let x=95;x<440;x+=65){a.strokeStyle='#887955';a.lineWidth=2;a.beginPath();a.moveTo(x,y-22);a.lineTo(x+17,y);a.lineTo(x,y+22);a.lineTo(x-17,y);a.closePath();a.stroke();a.fillStyle='#69705a';a.fillRect(x-3,y-3,6,6)}}
 if(kind==='stone'){a.fillStyle='#40504b';a.fillRect(0,0,512,512);for(let i=0;i<9000;i++){a.fillStyle=`rgba(${random()>.5?'160,172,142':'10,20,20'},${random()*.13})`;a.fillRect(random()*512,random()*512,random()*12+2,random()*5+1)}}
 const t=new T.CanvasTexture(c);t.wrapS=t.wrapT=T.RepeatWrapping;t.colorSpace=T.SRGBColorSpace;return t;}
function glowTexture(){const c=document.createElement('canvas');c.width=c.height=64;const a=c.getContext('2d'),g=a.createRadialGradient(32,32,0,32,32,32);g.addColorStop(0,'rgba(255,243,199,1)');g.addColorStop(.14,'rgba(255,210,131,.8)');g.addColorStop(.45,'rgba(234,158,83,.14)');g.addColorStop(1,'rgba(220,150,90,0)');a.fillStyle=g;a.fillRect(0,0,64,64);return new T.CanvasTexture(c)}
export function makeWorld(scene){
 const band=loadMusicians(scene),furniture=loadFurniture(scene);const architecture=new T.Group();scene.add(architecture);const walkables=[],solids=[],flames=[],actors=[];
 const mat=(color,roughness=.85,metalness=0)=>new T.MeshStandardMaterial({color,roughness,metalness});
 const wood=mat('#5a4130'),dark=mat('#182321'),gold=mat('#8e784f',.43,.7),stone=mat('#6c7265'),cream=mat('#c0bca2'),black=mat('#171e1f'),red=mat('#5b252b'),leaf=mat('#314b3e');
 wood.map=texture('wood');
 const floorMat=mat('#a99e80');floorMat.map=texture('wood');floorMat.map.repeat.set(6,6);
 const wallMat=mat('#8b9989');wallMat.map=texture('wall');wallMat.map.repeat.set(5,2);
 const rugMat=mat('#bfb396');rugMat.map=texture('rug');const stoneMat=mat('#778d80');stoneMat.map=texture('stone');stoneMat.map.repeat.set(5,5);
 const loader=new T.TextureLoader();
 function pbr(material,name,repeat=[1,1],strength=.7){for(const [channel,slot] of [['Diffuse','map'],['nor_gl','normalMap'],['rough','roughnessMap']]){const tex=loader.load(`./textures/${name}_${channel}.jpg`);tex.wrapS=tex.wrapT=T.RepeatWrapping;tex.repeat.set(...repeat);tex.anisotropy=4;if(channel==='Diffuse')tex.colorSpace=T.SRGBColorSpace;material[slot]=tex;}material.normalScale=new T.Vector2(strength,strength);material.needsUpdate=true;}
 pbr(floorMat,'wood_floor_worn',[5,5],.85);floorMat.color.set('#a59881');floorMat.roughness=.92;
 pbr(wood,'wood_floor_worn',[1,2],.35);wood.color.set('#6b4b32');
 pbr(wallMat,'worn_plaster_wall',[3,2],.65);wallMat.color.set('#7c7762');
 pbr(stoneMat,'forest_floor',[5,5],.85);stoneMat.color.set('#8d9785');
 pbr(red,'quatrefoil_jacquard_fabric',[2,2],.4);red.color.set('#663635');
 pbr(cream,'quatrefoil_jacquard_fabric',[3,3],.25);cream.color.set('#c3bba7');cream.map=null;
 const panelling=loader.load('./textures/manor-panelling-v4.jpg');panelling.colorSpace=T.SRGBColorSpace;panelling.wrapS=T.RepeatWrapping;panelling.repeat.set(2,1);panelling.anisotropy=8;wallMat.map=panelling;wallMat.normalMap=null;wallMat.roughnessMap=null;wallMat.color.set('#b9b7a6');wallMat.bumpMap=panelling;wallMat.bumpScale=.025;
 const carpet=loader.load('./textures/persian-rug-v4.jpg');carpet.colorSpace=T.SRGBColorSpace;carpet.anisotropy=8;rugMat.map=carpet;rugMat.color.set('#cdc5b8');
 rugMat.normalMap=red.normalMap;rugMat.normalScale=new T.Vector2(.3,.3);rugMat.roughness=1;
 const silkMat=new T.MeshBasicMaterial({color:'#d4d0bc',transparent:true,opacity:.46,depthWrite:false});
 const mesh=(geo,m,x,y,z,parent=architecture)=>{const o=new T.Mesh(geo,m);o.position.set(x,y,z);parent.add(o);return o};
 const box=(x,y,z,w,h,d,m,parent)=>mesh(new T.BoxGeometry(w,h,d),m,x,y,z,parent);
 const ball=(x,y,z,r,m,parent,s=[1,1,1])=>{const o=mesh(new T.SphereGeometry(r,24,16),m,x,y,z,parent);o.scale.set(...s);return o};
 const cyl=(x,y,z,rt,rb,h,m,parent)=>mesh(new T.CylinderGeometry(rt,rb,h,20),m,x,y,z,parent);
 const link=(a,b,r,m,parent=architecture)=>{const dir=b.clone().sub(a),o=cyl(0,0,0,r,r,dir.length(),m,parent);o.position.copy(a).add(b).multiplyScalar(.5);o.quaternion.setFromUnitVectors(V(0,1,0),dir.normalize());return o};
 const torus=(x,y,z,r,t,m,parent=architecture)=>mesh(new T.TorusGeometry(r,t,6,32),m,x,y,z,parent);
 function floor(x,y,z,w,d,m){const o=mesh(new T.PlaneGeometry(w,d),m,x,y,z);o.rotation.x=-Math.PI/2;walkables.push(o);return o}
 floor(0,0,0,24,24,floorMat);floor(0,-.02,-20,24,16,stoneMat);
 box(-12,5,0,.35,10,24,wallMat);box(12,5,0,.35,10,24,wallMat);box(0,5,12,24,10,.35,wallMat);
 box(-5.5,5,-12,13,10,.4,wallMat);box(9.5,5,-12,5,10,.4,wallMat);box(4,8.9,-12,6,2.2,.4,wallMat);
 box(0,10,0,24,.35,24,wood);
 // Dark timber ceiling, moulded coffers and the curved gallery lintel from the salon.
 for(let z=-10;z<=10;z+=2.5){box(0,9.7,z,24,.5,.22,wood);box(0,9.4,z,23,.08,.34,dark);}
 for(let x=-10;x<=10;x+=4)box(x,9.7,0,.32,.5,24,wood);
 const arch=new T.EllipseCurve(0,0,5.8,2.2,0,Math.PI,false,0);
 const archPts=arch.getPoints(40).map(p=>V(p.x,7.4+p.y,-8.6));
 mesh(new T.TubeGeometry(new T.CatmullRomCurve3(archPts),48,.16,8,false),wood,0,0,0);
 for(let side of [-1,1]){box(side*5.85,7.5,-8.6,.35,3,.5,wood);for(let k=0;k<3;k++)box(side*5.85,6.35+k*.14,-8.6,.6-k*.1,.1,.65,wood);}

 // Panelling, pilasters and cornices make the room readable at spider scale.
 for(let side of [-1,1]){for(let z=-10;z<=10;z+=4){box(side*11.6,4.7,z,.38,9.4,.4,wood);box(side*11.4,8.8,z,.7,.28,.8,gold)}for(let y of [.15,1.65,8.6,9.6])box(side*11.7,y,0,.24,.12,24,gold)}
 for(let y of [.15,1.65,8.6,9.6])box(0,y,11.75,24,.12,.24,gold);
 for(let x=-10;x<=10;x+=4){box(x,4.7,11.6,.4,9.4,.4,wood)}
 floor(0,.025,-1,12,14,rugMat);box(0,.2,-7,12,.4,4,wood);floor(0,.415,-7,12,4,wood);
 for(let x of [-5.8,5.8]){box(x,4.5,-9,.35,8.2,.4,gold);for(let i=0;i<9;i++){const o=cyl(x+(i-4)*.32,4.45,-9.5,.25,.25,8.3,red);o.scale.z=.65}}
 // Gallery and an accessible ramp, disguised as a folded runner beside the stairs.
 floor(-9,6,-7,5.5,3.5,wood);box(-9,5.83,-7,5.5,.34,3.5,wood);floor(2.75,6,-10.2,17.5,2.8,wood);box(2.75,5.83,-10.2,17.5,.34,2.8,wood);
 for(let x=-10.8;x<=10.8;x+=.75){if(x< -7.5)continue;cyl(x,6.75,-8.8,.045,.045,1.5,gold)}link(V(-7.5,7.5,-8.8),V(11.3,7.5,-8.8),.065,wood);
 for(let x of [-8,8]){box(x,3,-10.3,.25,6,.25,wood);box(x,5.2,-10.3,.55,.3,.5,wood)}
 const ramp=floor(-9,3,1.1,3.2,Math.sqrt(13.8**2+6**2),rugMat);ramp.rotation.x=-Math.PI/2+Math.atan2(6,13.8);
 for(let i=0;i<20;i++){const y=(i+.5)*.3,z=8-i*.69;box(-10.9,y/2,z,1.2,y,.72,wood);cyl(-11.3,y+1,z,.04,.04,1.5,gold)}link(V(-11.3,1.2,8),V(-11.3,7.2,-5.8),.065,wood);
 // Carved wall panels and iron scrollwork, with depth at floor level.
 for(let side of [-1,1])for(let z=-9;z<11;z+=2){for(let yy of [.25,1.4])box(side*11.55,yy,z,.12,.07,1.65,wood);for(let zz of [-.8,.8])box(side*11.55,.83,z+zz,.12,1.15,.06,wood);}
 for(let x=-7;x<11;x+=.75){for(let sign of [-1,1]){const scroll=torus(x+sign*.11,6.8,-8.8,.18,.017,black);scroll.scale.y=1.7;}ball(x,7.45,-8.8,.085,gold);}
 // Window balcony.
 floor(9.5,4,5.5,4,5,wood);box(9.5,3.85,5.5,4,.3,5,wood);box(11.68,6,5.5,.1,5.5,4.8,gold);
 const glass=new T.MeshBasicMaterial({color:'#a6c2ba',transparent:true,opacity:.32});box(11.5,6,5.5,.08,5,4.4,glass);
 for(let z of [3.3,5.5,7.7])box(11.35,6,z,.15,5,.09,wood);box(11.35,6,5.5,.15,.09,4.5,wood);
 function curtain(x,y,z,width,height,rotation=0,material=cream){const geo=new T.PlaneGeometry(width,height,36,28),p=geo.attributes.position;for(let i=0;i<p.count;i++){const xx=p.getX(i),yy=p.getY(i),f=(yy+height/2)/height;p.setZ(i,Math.sin(xx/width*Math.PI*14)*(.08+.15*(1-f))+Math.sin(f*4+xx)*.08);p.setY(i,yy+Math.cos(xx*4)*.05*(1-f));}geo.computeVertexNormals();const m=material.clone();m.side=T.DoubleSide;const c=mesh(geo,m,x,y,z);c.rotation.y=rotation;return c;}
 curtain(10.94,6,3.2,1.25,5.6,Math.PI/2);curtain(10.94,6,7.8,1.25,5.6,Math.PI/2);
 curtain(-5.3,4.9,-9.3,1.4,8.1,0,red);curtain(5.3,4.9,-9.3,1.4,8.1,0,red);
 const moon=mesh(new T.SphereGeometry(1.2,24,16),new T.MeshBasicMaterial({color:'#d2e5d5'}),9,12,-30);
 // Fireplace and armchairs.
 box(11.2,1.6,-.6,1.4,3.2,4.8,stone);box(10.42,1.35,-.6,.08,2.3,3.2,black);box(10.8,3.2,-.6,2,.35,5.3,wood);box(11.6,5.5,-.6,.5,4.3,3.4,stoneMat);
 for(let i=0;i<6;i++)link(V(10.1,.4,-1.4+i*.3),V(10.7,.4,-.8+i*.3),.12,wood);
 const glow=glowTexture();const flameMaterial=new T.SpriteMaterial({map:glow,color:'#ffc77e',transparent:true,depthWrite:false,blending:T.AdditiveBlending});
 function flame(x,y,z,size=.45){const o=new T.Sprite(flameMaterial);o.position.set(x,y,z);o.scale.set(size,size*1.7,1);scene.add(o);flames.push({o,size,phase:x*3+z});return o}
 function candle(x,y,z,height=.55){cyl(x,y+height/2,z,.075,.085,height,cream);cyl(x,y-.06,z,.18,.22,.12,gold);flame(x,y+height+.08,z,.38)}
 for(let i=0;i<5;i++)flame(10.15,.65+i%2*.18,-1.6+i*.5,.9);
 candle(7,1.59,.1);solids.push({x:7,z:.1,r:1.4},{x:9,z:3,r:1.1},{x:9,z:5,r:1.1});
 // Suspended chandelier with long strands and crystal drops.
 const ring=torus(0,7.8,0,2.2,.08,gold);ring.rotation.x=Math.PI/2;const small=torus(0,8.8,0,1,.06,gold);small.rotation.x=Math.PI/2;link(V(0,8,0),V(0,10,0),.055,gold);
 for(let i=0;i<12;i++){const a=i*Math.PI/6,x=Math.cos(a)*2.2,z=Math.sin(a)*2.2;link(V(x,7.8,z),V(Math.cos(a),8.8,Math.sin(a)),.025,gold);candle(x,7.8,z,.35);link(V(x,7.7,z),V(x,7.15,z),.015,gold);mesh(new T.OctahedronGeometry(.15),cream,x,7.1,z)}
 // Cascading crystal chains catch candlelight as the spider moves below.
 const crystal=new T.MeshPhysicalMaterial({color:'#dedbc9',metalness:0,roughness:.12,clearcoat:1,transmission:.7,thickness:.08,ior:1.46});
 for(let tier=0;tier<3;tier++){const radius=2.2-tier*.62,yy=7.7+tier*.45;
  for(let i=0;i<24;i++){const a=i*Math.PI/12,b=(i+1)*Math.PI/12;for(let j=0;j<7;j++){const u=j/6,ang=a+(b-a)*u,cy=yy-Math.sin(u*Math.PI)*.45;ball(Math.cos(ang)*radius,cy,Math.sin(ang)*radius,.047,crystal);}
   const len=.3+.25*(i%3);link(V(Math.cos(a)*radius,yy,Math.sin(a)*radius),V(Math.cos(a)*radius,yy-len,Math.sin(a)*radius),.007,gold);const drop=mesh(new T.OctahedronGeometry(.09),crystal,Math.cos(a)*radius,yy-len,Math.sin(a)*radius);drop.scale.y=2.2;
  }
 }
 for(let z of [-8,2,9])for(let x of [-10.8,10.8]){box(x,2.9,z,.3,.2,.5,gold);candle(x,3,z,.6)}
 // Moonlit garden, stones, wrought iron gate and vegetation.
 for(let side of [-1,1]){box(side*11.7,1.2,-20,.5,2.4,16,stoneMat);for(let z=-27;z<-12;z+=2.2){cyl(side*11.7,3,z,.055,.055,4,gold);ball(side*11.7,5.1,z,.11,gold)}}
 box(0,1.2,-27.5,24,2.4,.4,stoneMat);for(let x=-11;x<=11;x+=.7){cyl(x,3,-27.5,.045,.045,4,gold);const ar=torus(x,4,-27.5,.3,.025,gold);ar.scale.y=2}
 const waterMaterial=new T.MeshStandardMaterial({color:'#183d3b',metalness:.55,roughness:.2,transparent:true,opacity:.85});const water=mesh(new T.CircleGeometry(3.7,48),waterMaterial,-2,.06,-21);water.rotation.x=-Math.PI/2;
 for(let i=0;i<32;i++){const a=i*Math.PI/16;const rock=ball(-2+Math.cos(a)*4,.1,-21+Math.sin(a)*4,.5,stoneMat);rock.scale.set(1,.5,.8)}
 const ripples=[];for(let i=0;i<5;i++){const r=torus(-2,.08+i*.004,-21,.8+i*.55,.012,new T.MeshBasicMaterial({color:'#7faaa0',transparent:true,opacity:.15}),scene);r.rotation.x=-Math.PI/2;ripples.push(r)}
 let seed=42;const rand=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296};
 function fern(x,z,s=1){const y=.1;for(let i=0;i<7;i++){const ang=i*Math.PI*2/7;const end=V(x+Math.cos(ang)*s,y+.8*s,z+Math.sin(ang)*s);link(V(x,y,z),end,.022,leaf);for(let j=1;j<6;j++){const f=j/6,p=V(x,y,z).lerp(end,f);for(let side of [-1,1]){const o=ball(p.x+Math.sin(ang)*side*.2*s*(1-f),p.y,p.z-Math.cos(ang)*side*.2*s*(1-f),.15,leaf);o.scale.set(.4,.22,1.6);o.rotation.y=ang+side*.5}}}}
 for(let i=0;i<24;i++){const side=i%2?-1:1;fern(side*(8.8+rand()*2),-13-rand()*13,.6+rand()*.8)}
 // Branching silhouettes and curved leaves replace the sphere trees.
 const leafMats=['#263d30','#3c5140','#526347'].map(c=>{const m=mat(c);m.side=T.DoubleSide;return m;});
 function foliage(x,y,z,scale,angle){const geo=new T.PlaneGeometry(.32*scale,1.25*scale,4,8),p=geo.attributes.position;for(let k=0;k<p.count;k++){const f=(p.getY(k)/scale+ .625)/1.25;p.setX(k,p.getX(k)*Math.sin(f*Math.PI));p.setZ(k,Math.sin(f*Math.PI)*scale*.2+Math.abs(p.getX(k))*.5);}geo.computeVertexNormals();const o=mesh(geo,leafMats[Math.floor(rand()*3)],x,y,z);o.rotation.set(.45+rand(),angle,rand()*.4);}
 for(let i=0;i<18;i++){const x=i<10?-10+rand()*20:(i%2?-10.5:10.5),z=i<10?-26-rand()*2:-14-rand()*10,h=4+rand()*3;
  link(V(x,0,z),V(x+.25,h,z),.12,wood);
  for(let b=0;b<7;b++){const a=b*2.4+i,by=1+b*.65,end=V(x+Math.cos(a)*1.7,Math.min(h,by+1.2),z+Math.sin(a)*1.7);link(V(x,by,z),end,.035,wood);for(let k=0;k<9;k++){const f=k/9,pt=V(x,by,z).lerp(end,f);foliage(pt.x,pt.y,pt.z,.7+rand()*.6,a+k*.4);}}
 }
 for(let i=0;i<80;i++){const a=rand()*Math.PI*2,r=4.1+rand()*.65;foliage(-2+Math.cos(a)*r,.4,-21+Math.sin(a)*r,.5+rand()*.5,a);}

 for(let i=0;i<12;i++){const x=7+rand()*2,z=-21+rand()*3;link(V(x,0,z),V(x,1+rand(),z),.025,leaf);ball(x,1.2,z,.18,red)}
 for(let x of [-7,8]){cyl(x,.55,-25,.6,.8,1.1,stone);cyl(x,1.6,-25,.27,.45,1.2,stone);ball(x,2.6,-25,.37,stone);link(V(x,2.1,-25),V(x+.6,1.7,-25),.12,stone)}
 // Portraits and a tall, imperfect mirror.
 for(let z of [-5,5]){box(-11.5,4.5,z,.25,3.2,2.3,gold);box(-11.3,4.5,z,.1,2.9,2,black);ball(-11.18,4.8,z,.44,stone,architecture,[.18,1,.75]);box(-11.16,3.95,z,.12,.8,1,wood)}
 const mirror=new T.MeshStandardMaterial({color:'#849287',metalness:.9,roughness:.22});box(-11.4,7.2,-7,.12,2,1.8,gold);box(-11.28,7.2,-7,.04,1.8,1.6,mirror);
 // Small domestic detail: books, glass and floor fibres.
 for(let i=0;i<8;i++){const o=box(5.4+i*.12,.12,5,.09,.24,.4,i%2?red:wood);o.rotation.z=.15*i}
 for(let i=0;i<90;i++){const x=(rand()-.5)*10,z=rand()*9+1;link(V(x,.03,z),V(x+.03,.035+rand()*.025,z+.05),.002,i%2?wood:gold)}
 function instruments(x,z,role){const varnish=new T.MeshPhysicalMaterial({color:'#552912',map:wood.map,roughness:.64,clearcoat:.18,clearcoatRoughness:.5});const chrome=new T.MeshStandardMaterial({color:'#9b9d91',metalness:.85,roughness:.3});const drumSkin=new T.MeshStandardMaterial({color:'#b6ad95',roughness:.96});const g=new T.Group();scene.add(g);g.position.set(x,.42,z);
 function instrument(cx,cy,cz,scale){const outline=new T.Shape();outline.moveTo(0,1.1);outline.bezierCurveTo(-.6,1.15,-.67,.65,-.34,.36);outline.bezierCurveTo(-.25,.2,-.5,.05,-.61,-.2);outline.bezierCurveTo(-1,-1.1,1,-1.1,.61,-.2);outline.bezierCurveTo(.5,.05,.25,.2,.34,.36);outline.bezierCurveTo(.67,.65,.6,1.15,0,1.1);const geo=new T.ExtrudeGeometry(outline,{depth:.2,bevelEnabled:true,bevelSize:.055,bevelThickness:.04,bevelSegments:3,steps:1,curveSegments:20});const inst=mesh(geo,varnish,cx,cy,cz,g);inst.scale.setScalar(scale);return inst;}
 if(role==='guitar'){
 const guitar=new T.Group();g.add(guitar);guitar.position.set(0,1.9,.4);guitar.rotation.z=-1.27;
 const lacquer=new T.MeshPhysicalMaterial({color:'#151914',roughness:.42,clearcoat:.3,clearcoatRoughness:.42});
 const outline=new T.Shape();outline.moveTo(0,.52);
 outline.bezierCurveTo(-.14,.43,-.2,.91,-.37,.64);outline.bezierCurveTo(-.60,.43,-.25,.12,-.34,-.06);
 outline.bezierCurveTo(-.82,-.75,.82,-.75,.34,-.06);outline.bezierCurveTo(.25,.12,.60,.43,.37,.64);outline.bezierCurveTo(.2,.91,.14,.43,0,.52);
 mesh(new T.ExtrudeGeometry(outline,{depth:.16,bevelEnabled:true,bevelSize:.022,bevelThickness:.02,bevelSegments:3,curveSegments:24}),lacquer,0,0,0,guitar);
 const binding=new T.CatmullRomCurve3(outline.getPoints(70).map(p=>V(p.x,p.y,.181)),true);mesh(new T.TubeGeometry(binding,160,.008,5,true),cream,0,0,0,guitar);
 box(0,1.18,.17,.115,1.5,.08,wood,guitar);box(0,1.16,.219,.105,1.48,.022,black,guitar);box(0,1.99,.17,.18,.3,.065,lacquer,guitar);
 box(0,-.25,.207,.3,.045,.035,chrome,guitar);box(0,-.36,.207,.25,.035,.035,chrome,guitar);
 for(const y of [.1,.36]){box(0,y,.201,.29,.083,.035,cream,guitar);box(0,y,.224,.25,.058,.021,chrome,guitar);for(let j=0;j<6;j++)ball((j-2.5)*.039,y,.238,.008,black,guitar,[1,1,.3]);}
 for(const side of [-1,1]){const c=new T.CatmullRomCurve3([V(side*.28,.26,.185),V(side*.24,.15,.185),V(side*.33,.03,.185),V(side*.3,-.10,.185)]);mesh(new T.TubeGeometry(c,18,.012,6,false),black,0,0,0,guitar);}
 for(let i=0;i<4;i++){const knob=cyl(.25+(i%2)*.12,-.26-Math.floor(i/2)*.13,.205,.022,.026,.025,cream,guitar);knob.rotation.x=Math.PI/2;}
 for(let j=0;j<15;j++){const yy=.46+j*.087;link(V(-.052,yy,.239),V(.052,yy,.239),.004,chrome,guitar);}
 for(let j=0;j<6;j++){const xx=(j-2.5)*.012;link(V(xx,-.27,.244),V(xx,2.11,.244),.0018,chrome,guitar);const side=j%2?-1:1,yy=1.89+Math.floor(j/2)*.09;link(V(side*.07,yy,.17),V(side*.135,yy,.17),.013,chrome,guitar);ball(side*.14,yy,.17,.025,cream,guitar,[1,1,.65]);}
 }
 if(role==='bass'){box(.65,1.12,.75,.18,.65,.06,black,g);box(.65,1.62,.76,.34,.06,.05,cream,g);for(let j=0;j<4;j++){link(V(.65,4.03+j*.09,.55),V(.85,4.03+j*.09,.55),.014,chrome,g);ball(.86,4.03+j*.09,.55,.04,black,g,[1,.6,1]);}instrument(.65,1.6,.4,1);link(V(.65,.05,.55),V(.65,4.3,.55),.045,gold,g);box(.65,3.3,.65,.12,2.1,.08,black,g);for(let k=0;k<4;k++)link(V(.605+k*.03,.6,.71),V(.605+k*.03,4.25,.71),.003,gold,g);for(let side of [-1,1]){const a=.65+side*.3,curve=new T.CatmullRomCurve3([V(a+side*.045,1.94,.705),V(a-side*.04,1.78,.705),V(a+side*.04,1.56,.705),V(a-side*.04,1.41,.705)]);mesh(new T.TubeGeometry(curve,18,.019,6,false),black,0,0,0,g);ball(a+side*.045,1.94,.706,.035,black,g,[1,1,.1]);ball(a-side*.04,1.41,.706,.034,black,g,[1,1,.1]);}}
 if(role==='drummer'){const drum=cyl(0,.75,1,.8,.8,.7,wood,g);drum.rotation.x=Math.PI/2;const skin=cyl(0,.75,1.37,.76,.76,.035,drumSkin,g);skin.rotation.x=Math.PI/2;for(let s of [-1,1]){cyl(s*1.05,1.7,.7,.45,.45,.45,wood,g);cyl(s*1.05,1.94,.7,.44,.44,.025,drumSkin,g);cyl(s*1.4,1.3,.8,.025,.025,2.6,gold,g);const profile=[new T.Vector2(0,.07),new T.Vector2(.12,.07),new T.Vector2(.2,.01),new T.Vector2(.62,-.03),new T.Vector2(.65,-.035)];mesh(new T.LatheGeometry(profile,40),gold,s*1.4,2.6,.8,g);for(let a=0;a<3;a++){const k=a*Math.PI*2/3;link(V(s*1.4,.15,.8),V(s*1.4+Math.cos(k)*.45,.025,.8+Math.sin(k)*.45),.02,chrome,g);}if(s===1){cyl(0,.7,0,.035,.035,1.4,chrome,g);cyl(0,1.4,0,.4,.4,.16,black,g)}}}
 else{cyl(.2,1.5,1.15,.025,.025,3,gold,g);const mic=ball(.2,3.32,1.15,.115,chrome,g,[.72,1.65,1]);for(let i=0;i<7;i++){const ring=torus(.2,3.19+i*.04,1.15,.091,.009,black,g);ring.rotation.x=Math.PI/2;}for(let a=0;a<3;a++){const k=a*Math.PI*2/3;link(V(.2,.18,1.15),V(.2+Math.cos(k)*.4,.015,1.15+Math.sin(k)*.4),.02,chrome,g);}}return g}
 for(let i=0;i<10;i++){const a=i*Math.PI/5;link(V(Math.cos(a)*.77,1.17+Math.sin(a)*.77,-7.55),V(Math.cos(a)*.77,1.17+Math.sin(a)*.77,-6.75),.016,gold);};
 instruments(-2.8,-6.6,'bass');instruments(2.4,-6.1,'guitar');instruments(0,-8.1,'drummer');
 const dancer=new T.Group();scene.add(dancer);dancer.position.set(-3,.1,-21);const dress=new T.CylinderGeometry(.28,.85,2.5,40,20),dp=dress.attributes.position;for(let i=0;i<dp.count;i++){const a=Math.atan2(dp.getZ(i),dp.getX(i)),f=(1.25-dp.getY(i))/2.5,fold=1+Math.sin(a*12)*.075*f;dp.setX(i,dp.getX(i)*fold);dp.setZ(i,dp.getZ(i)*fold);}dress.computeVertexNormals();mesh(dress,cream,0,1.25,0,dancer);ball(0,2.85,0,.3,stone,dancer);for(let s of [-1,1])link(V(0,2.3,0),V(s*.85,2,0),.08,cream,dancer);
 const alcove=createAlcove(scene,{wood,red,gold,cream},walkables,flame),cat=alcove.cat;
 const bird=new T.Group();scene.add(bird);bird.position.set(10.3,4.8,6);ball(0,0,0,.42,black,bird,[.7,1,1.25]);ball(0,.55,.25,.25,black,bird);const beak=mesh(new T.ConeGeometry(.13,.42,5),black,0,.54,.6,bird);beak.rotation.x=Math.PI/2;for(let s of [-1,1]){const wing=ball(s*.25,.03,-.1,.4,black,bird,[.25,1,1.6]);wing.rotation.z=s*.2;link(V(s*.15,-.25,0),V(s*.15,-.65,.1),.025,black,bird)}
 function spider(x,y,z,size=.2){const g=createSpider(size/.2);g.position.set(x,y,z);scene.add(g);return g;}
 const companion=spider(10,4.02,7,.18);companion.visible=false;
 function thread(points,parent=architecture,material=silkMat){const curve=new T.CatmullRomCurve3(points);return mesh(new T.TubeGeometry(curve,30,.0015,4,false),material,0,0,0,parent)}
 for(let i=0;i<12;i++){const a=i*Math.PI/6;thread([V(10,4.3,7),V(10+Math.cos(a)*.65,4.3+Math.sin(a)*.65-.06,7.1),V(10+Math.cos(a)*1.2,4.3+Math.sin(a)*1.2,7.4)]);}
 for(let ring=1;ring<=7;ring++){const points=[];for(let i=0;i<=48;i++){const a=i*Math.PI/24,r=ring*.145;points.push(V(10+Math.cos(a)*r,4.3+Math.sin(a)*r-.035*Math.sin(a*6)**2,7+.32*r*r));}thread(points);}
 const nodes=NODES.map((n,i)=>{const g=new T.Group();scene.add(g);g.position.set(...n.pos);const m=new T.MeshStandardMaterial({color:'#e1cf9d',emissive:'#bba36a',emissiveIntensity:.65,metalness:.3,roughness:.4});const core=mesh(new T.OctahedronGeometry(.16),m,0,0,0,g);const halo=torus(0,0,0,.35,.008,m,g);for(let j=0;j<7;j++){const a=j*Math.PI*2/7;link(V(0,0,0),V(Math.cos(a)*.55,Math.sin(a)*.55,0),.004,silkMat,g)}const light=new T.Sprite(new T.SpriteMaterial({map:glow,color:'#e4d5a4',transparent:true,depthWrite:false,blending:T.AdditiveBlending}));light.scale.set(1.8,1.8,1);g.add(light);return {g,core,halo,m,light};});
 // Broken route, visible against the dark wall.
 thread([V(-8,.15,8),V(-9,2,5),V(-9,4.8,-2),V(-9,6.25,-7)]);
 // Dust motes in warm light and a low moonlit haze outside.
 const dustGeo=new T.BufferGeometry(),dustPos=[];for(let i=0;i<230;i++)dustPos.push((rand()-.5)*22,rand()*9,(rand()-.5)*24);dustGeo.setAttribute('position',new T.Float32BufferAttribute(dustPos,3));const dust=new T.Points(dustGeo,new T.PointsMaterial({color:'#cbb789',size:.025,transparent:true,opacity:.43,depthWrite:false}));scene.add(dust);
 // Merge static architecture by material to keep mobile draw calls down.
 architecture.updateMatrixWorld(true);const batches=new Map();architecture.traverse(o=>{if(!o.isMesh||walkables.includes(o))return;const geo=(o.geometry.index?o.geometry.toNonIndexed():o.geometry.clone()).applyMatrix4(o.matrixWorld);if(!batches.has(o.material))batches.set(o.material,[]);batches.get(o.material).push(geo)});
 const keep=new Set(walkables);const remove=[];architecture.traverse(o=>{if(o.isMesh&&!keep.has(o))remove.push(o)});remove.forEach(o=>o.removeFromParent());for(const [material,geos] of batches){const merged=mergeGeometries(geos,false);if(merged)scene.add(new T.Mesh(merged,material));geos.forEach(g=>g.dispose())}
 scene.updateMatrixWorld(true);
 return {ready:Promise.all([band.ready,furniture,alcove.ready]),walkables,solids,nodes,companion,cat,bird,thread,spider,update(t,collected){const cycle=cycleAt(t);band.update(t);alcove.update(t);companion.userData.animate(t);dancer.rotation.z=Math.sin(t*.7)*.07;dancer.rotation.y=t*.15;dancer.position.y=cycle>58&&cycle<76?-.7+.2*Math.sin(t):.1;dancer.position.x=-3+Math.sin(t*.14)*.8;bird.visible=cycle>195&&cycle<219;bird.rotation.y=Math.sin(t)*.2;if(!birdBlocking(t))bird.position.y=4.8+Math.max(0,cycle-211)*.65;else bird.position.y=4.8;flames.forEach(({o,size,phase})=>{const s=size*(.93+.08*Math.sin(t*6+phase));o.scale.set(s,s*1.7,1)});nodes.forEach((n,i)=>{n.core.rotation.y=t*.6;n.halo.rotation.z=-t*.15;n.g.visible=i>=collected;n.light.material.opacity=i===collected?.55+.25*Math.sin(t*2):.15;});ripples.forEach((r,i)=>{r.scale.setScalar(1+Math.sin(t*.7+i)*.05)});dust.rotation.y=t*.004;},makeLegs:createViewLegs};
}
