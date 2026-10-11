import * as T from './vendor/three.module.js';
// Real-time skin for the band and the Sphynx. Light wraps a little further
// around the terminator in red than in blue (a cheap approximation of
// subsurface scattering), and thin tissue marked by a vertex attribute glows
// when lit from behind. One extra dot product per light keeps it phone-friendly.
const DIFFUSE='reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseContribution ) * ( 1.0 - F );';
export function skin(material,{wrap=[.42,.2,.14],thin=null,glow='#ff6f5a',strength=.55}={}){
 material.onBeforeCompile=shader=>{
  shader.uniforms.skinWrap={value:new T.Vector3(...wrap)};shader.uniforms.skinGlow={value:new T.Color(glow).multiplyScalar(strength)};
  const thinVarying=!!thin;
  if(thinVarying){
   shader.vertexShader=shader.vertexShader.replace('#include <common>',`#include <common>\nattribute vec4 ${thin};\nvarying float vSkinThin;`).replace('#include <begin_vertex>',`#include <begin_vertex>\nvSkinThin=${thin}.r;`);
  }
  shader.fragmentShader=shader.fragmentShader
   .replace('#include <common>',`#include <common>\nuniform vec3 skinWrap;uniform vec3 skinGlow;${thinVarying?'varying float vSkinThin;':'const float vSkinThin=0.0;'}`)
   .replace('#include <lights_physical_pars_fragment>',T.ShaderChunk.lights_physical_pars_fragment.replace(DIFFUSE,`{
	vec3 wrapped = saturate( ( vec3( dot( geometryNormal, directLight.direction ) ) + skinWrap ) / ( 1.0 + skinWrap ) );
	reflectedLight.directDiffuse += wrapped * wrapped * directLight.color * BRDF_Lambert( material.diffuseContribution ) * ( 1.0 - F );
	float back = pow( saturate( dot( geometryViewDir, - normalize( directLight.direction + geometryNormal * .4 ) ) ), 3.0 );
	reflectedLight.directDiffuse += back * vSkinThin * skinGlow * directLight.color * material.diffuseContribution;
}`));
  if(!shader.fragmentShader.includes('skinWrap ) / ( 1.0 + skinWrap )'))console.warn('skin shader patch not applied');
 };
 material.customProgramCacheKey=()=>'skin'+(thin||'')+wrap.join();
 material.needsUpdate=true;return material;
}

// Wet eye: a clear coat over the iris catches the room's lights and environment.
export function eye(material){
 const m=new T.MeshPhysicalMaterial({map:material.map,roughness:.32,clearcoat:1,clearcoatRoughness:.035,envMapIntensity:2.2,name:material.name});
 material.dispose();return m;
}

// Alpha-clipped strand cards, double sided so a lock reads from every angle.
export function hairCards(material,color){
 material.color.set(color);material.alphaTest=.42;material.transparent=false;material.depthWrite=true;material.side=T.DoubleSide;material.roughness=.52;material.metalness=0;
 return material;
}
