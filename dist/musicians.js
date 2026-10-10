import * as T from './vendor/three.module.js';
import {GLTFLoader} from './vendor/addons/loaders/GLTFLoader.js';
// Eight-beat performance loops share the video clock. Each singer has an
// independent, restrained jaw/neck gesture in his sections of the clip.
export function loadMusicians(scene){
 let mixer;const singers=[];
 const ready=new GLTFLoader().loadAsync('./models/musicians-v5.glb').then(gltf=>{
  const root=gltf.scene;root.name='Mark, Tom e Travis';
  root.traverse(o=>{if(!o.isMesh)return;o.castShadow=true;o.receiveShadow=true;o.frustumCulled=false;
   const mats=Array.isArray(o.material)?o.material:[o.material];
   for(const mat of mats){mat.roughness=Math.max(.48,mat.roughness);if(mat.map)mat.map.anisotropy=4;
    if(mat.name.endsWith(' skin')){mat.color.set('#dfd3c8');mat.roughness=.78;}
    if(mat.name.includes('shoes'))mat.color.set('#24231f');
    if(mat.name==='Tom dark fringe'){mat.color.set('#3e302a');mat.alphaTest=.38;mat.transparent=false;mat.side=T.DoubleSide;}
   }
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
