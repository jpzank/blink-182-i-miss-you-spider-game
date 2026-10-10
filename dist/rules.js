export const CYCLE_SECONDS=229;
export const NODES=[
 {id:'gallery',name:'The gallery',pos:[-9,6.25,-7],land:[-9,6,-5.8],title:'Find the gallery thread.',hint:'A trail climbs the wall on your left.',area:'01 / THE HALL',range:11},
 {id:'garden',name:'The garden',pos:[6,.65,-21],land:[6,0,-19.5],title:'There is a thread in the garden.',hint:'Blue light shines through the far doorway.',area:'02 / THE GALLERY',range:14},
 {id:'window',name:'The window',pos:[10,4.6,5.5],land:[9.2,4,5.5],title:'The last thread is at the window.',hint:'Return to the hall. The curtain hides a passage.',area:'03 / THE GARDEN',range:14}
];
export const HOME=[10,4.4,7];
export function createState(){return {phase:'intro',elapsed:0,collected:[],rescues:0};}
export function connect(state,id){const next=NODES[state.collected.length];if(state.phase!=='playing'||!next||next.id!==id)return false;state.collected.push(id);return true;}
export function cycleAt(elapsed){return ((elapsed%CYCLE_SECONDS)+CYCLE_SECONDS)%CYCLE_SECONDS;}
export function birdBlocking(elapsed){const t=cycleAt(elapsed);return t>=203&&t<211;}
export function canFinish(state,distance){return state.phase==='playing'&&state.collected.length===3&&distance<2.3;}
export function formatTime(seconds){const s=Math.max(0,Math.floor(seconds));return `${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}`;}
export function moveClamped(x,z,dx,dz){return {x:Math.max(-11.5,Math.min(11.5,x+dx)),z:Math.max(-27,Math.min(11.5,z+dz))};}
