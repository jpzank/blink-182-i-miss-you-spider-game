import * as T from './vendor/three.module.js';
import {GLTFLoader} from './vendor/addons/loaders/GLTFLoader.js';
import {skin,eye,hairCards} from './skin.js?v=8';
// Strand cards share one neutral texture; each musician's hair colour is applied here.
const HAIR={'Mark Hoppus hair':'#3a3330','Tom DeLonge hair':'#3d3330','Travis Barker hair':'#262322'};
// Eight-beat performance loops share the video clock. Each singer has an
// independent, restrained jaw/neck gesture in his sections of the clip.
export function loadMusicians(scene){
 let mixer;const singers=[];
 const ready=new GLTFLoader().loadAsync('./models/musicians-v6.glb').then(gltf=>{
  const root=gltf.scene;root.name='Mark, Tom e Travis';
  root.traverse(o=>{if(!o.isMesh)return;o.castShadow=true;o.receiveShadow=true;o.frustumCulled=false;
   const mats=Array.isArray(o.material)?o.material:[o.material];
   mats.forEach((mat,i)=>{mat.roughness=Math.max(.48,mat.roughness);if(mat.map)mat.map.anisotropy=4;
    if(mat.name.endsWith(' skin')){mat.color.set('#e6dbd0');mat.roughness=.74;skin(mat);}
    if(mat.name.endsWith(' face')){mat.color.set('#ddd1c6');mat.roughness=1;skin(mat);if(mat.normalMap)mat.normalScale.set(.9,.9);}
    if(mat.name.endsWith(' eyes')){const m=eye(mat);if(Array.isArray(o.material))o.material[i]=m;else o.material=m;}
    if(mat.name.endsWith(' hair'))hairCards(mat,HAIR[mat.name]||'#2a211c');
    if(mat.name.endsWith(' hair volume')){mat.color.set(HAIR[mat.name.replace(' volume','')]||'#2a211c').multiplyScalar(2.6);mat.roughness=.66;if(mat.normalMap)mat.normalScale.set(1.4,1.4);}
    if(mat.name==='Band eyelashes'){mat.alphaTest=.35;mat.transparent=false;mat.side=T.DoubleSide;o.castShadow=false;}
    if(mat.name.includes('shoes'))mat.color.set('#24231f');
   });
  });
  for(const [role,start,end] of [['Bassist',28,79],['Guitarist',80,219]]){
   const rig=root.getObjectByName(role);let jaw,neck;
   rig?.traverse(o=>{if(o.isBone&&o.name.startsWith('jaw'))jaw=o;if(o.isBone&&o.name.startsWith('neck01'))neck=o;});
   if(jaw)singers.push({jaw,neck,start,end});
  }
  scene.add(root);mixer=new T.AnimationMixer(root);gltf.animations.forEach(c=>mixer.clipAction(c).play());return root;
 });
 return {ready,update(t){if(!mixer)return;mixer.setTime(t*1.0083333);const cycle=((t%229)+229)%229;
  for(const {jaw,neck,start,end} of singers){const active=cycle>start&&cycle<end;
   if(active){const syllable=Math.max(0,Math.sin(t*8.1)+.35*Math.sin(t*13.7));jaw.rotateX(.10*syllable);if(neck)neck.rotateX(-.022*syllable);}
  }
 }};
}

export function loadFurniture(scene){const loader=new GLTFLoader();function add(asset,x,y,z,scale,rotation){return loader.loadAsync(`./models/${asset}/${asset}.gltf`).then(({scene:root})=>{root.scale.setScalar(scale);root.rotation.y=rotation;root.position.set(x,y,z);root.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;if(o.material.map)o.material.map.anisotropy=4;}});scene.add(root);return root;});}return Promise.all([add('sofa_03',9.1,0,4.1,2.2,-Math.PI/2),add('gothic_coffee_table',7,0,.1,2.8,0)]);}
