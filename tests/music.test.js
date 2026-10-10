import test from 'node:test';
import assert from 'node:assert/strict';
import {ClipMusic} from '../dist/music.js';
test('official player starts, follows media time, pauses with game and resumes',()=>{
 const els=new Map();globalThis.document={querySelector:s=>{if(!els.has(s))els.set(s,{textContent:'',hidden:true,attributes:{},setAttribute(name,value){this.attributes[name]=value},focus(){this.focused=true},querySelector(){return {textContent:''}}});return els.get(s)},createElement:()=>({}),head:{append(){}}};globalThis.window={};globalThis.location={origin:'https://example.test'};
 let opts,plays=0,pauses=0,seeks=[];globalThis.YT={Player:class{constructor(id,o){opts=o;}playVideo(){plays++;}pauseVideo(){pauses++;}seekTo(t){seeks.push(t);}unMute(){}setVolume(){}getCurrentTime(){return 64.25;}}};
 const music=new ClipMusic();window.onYouTubeIframeAPIReady();assert.equal(opts.videoId,'s1tAYmMjLdY');assert.equal(opts.playerVars.hl,'en');opts.events.onReady();music.setPhase('playing');music.start();assert.equal(plays,1);assert.deepEqual(seeks,[0]);opts.events.onStateChange({data:1});assert.equal(music.clock(100),64.25);
 els.get('#video-close').onclick();assert.equal(els.get('#music-panel').hidden,true);assert.equal(els.get('#video-toggle').attributes['aria-expanded'],'false');assert.equal(els.get('#video-toggle').focused,true);assert.equal(plays,1);assert.equal(pauses,0);assert.deepEqual(seeks,[0]);assert.equal(music.running,true);assert.equal(music.clock(100),64.25);
 music.setPhase('paused');assert.equal(pauses,1);opts.events.onStateChange({data:2});assert.equal(music.clock(110),64.25);music.setPhase('playing');assert.equal(plays,2);assert.equal(els.get('#music-panel').hidden,true);els.get('#video-toggle').onclick();assert.equal(els.get('#music-panel').hidden,false);assert.equal(els.get('#video-toggle').attributes['aria-label'],'Hide video');assert.equal(plays,2);assert.deepEqual(seeks,[0]);music.setPhase('won');assert.equal(pauses,2);
 opts.events.onError({data:101});assert.equal(music.clock(110),110);assert.equal(els.get('#music-link').hidden,false);
 for(const k of ['document','window','location','YT'])delete globalThis[k];
});
