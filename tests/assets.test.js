import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {dirname,resolve} from 'node:path';
test('three musicians have skinned geometry and playable animation in their packaged GLB',()=>{
 const b=readFileSync(new URL('../dist/models/musicians-v6.glb',import.meta.url));assert.equal(b.readUInt32LE(0),0x46546c67);assert.equal(b.readUInt32LE(8),b.length);
 const model=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)).toString());assert.equal(model.skins.length,3);assert.equal(model.animations.length,3);assert.ok(model.animations.every(a=>a.channels.length>0));assert.ok(model.images.every(i=>Number.isInteger(i.bufferView)));
 for(const name of ['Mark Hoppus','Tom DeLonge','Travis Barker']){
  assert.ok(model.animations.some(a=>a.name===name+' performance'),name+' animation');assert.ok(model.materials.some(m=>m.name===name+' skin'),name+' albedo');
  // Each head has its own high-resolution face material with colour, roughness and normal maps.
  const face=model.materials.find(m=>m.name===name+' face');assert.ok(face,name+' face');
  assert.ok(face.pbrMetallicRoughness.baseColorTexture&&face.pbrMetallicRoughness.metallicRoughnessTexture&&face.normalTexture,name+' face maps');
  for(const part of ['hairstyle','hair volume','eyelashes'])assert.ok(model.nodes.some(n=>n.name===name+' '+part),name+' '+part);
 }
 assert.ok(model.nodes.some(n=>n.name==='Travis black suspenders'));
});
test('furniture models include every referenced texture and geometry buffer',()=>{
 for(const name of ['sofa_03','gothic_coffee_table']){const file=resolve(`dist/models/${name}/${name}.gltf`),model=JSON.parse(readFileSync(file));for(const item of [...model.buffers,...model.images])if(item.uri)assert.ok(existsSync(resolve(dirname(file),item.uri)),item.uri);}
});
test('alcove characters ship self-contained geometry, textures and finite animation loops',()=>{
 for(const name of ['reclining-women-v6','sphynx-v7']){
  const b=readFileSync(new URL(`../dist/models/${name}.glb`,import.meta.url));
  assert.equal(b.readUInt32LE(0),0x46546c67);assert.equal(b.readUInt32LE(8),b.length);
  const model=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)).toString());
  assert.ok(model.meshes.length>0);assert.ok(model.skins.length>0);
  assert.ok(model.buffers.every(v=>!v.uri));assert.ok(model.images.every(v=>Number.isInteger(v.bufferView)));
  assert.ok(model.animations.length>0);
  for(const animation of model.animations){
   assert.ok(animation.channels.length>0);
   let duration=0,moving=false;
   for(const sampler of animation.samplers){
    const time=model.accessors[sampler.input];assert.ok(time.count>=1);
    assert.ok(time.min.every(Number.isFinite)&&time.max.every(Number.isFinite));
    duration=Math.max(duration,time.max[0]-time.min[0]);moving ||= time.count>2;
   }
   assert.ok(duration>=4&&moving,'animation loop must have a usable duration and sampled movement');
  }
 }
});
