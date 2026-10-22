import {PLAYER_COLORS} from './player-colors.js';
export const visuals=new URL('../visuals/',import.meta.url);
export const DISPLAY_COLORS=['#6599D1','#D99B63','#79AE84','#A18BC5','#CD87AA','#C5B56C','#70B8BF','#C6C8CE'];
export const ANIMALS=['lion','bat','turtle','fox','owl','whale','rabbit','deer'];
// Retain the server's stable color-slot identity, including rooms created before the redesign.
export function playerVisual(p,index=0){let slot=DISPLAY_COLORS.indexOf(p.color);if(slot<0)slot=PLAYER_COLORS.indexOf(p.color);if(slot<0)slot=Math.max(0,index)%8;return {slot,color:DISPLAY_COLORS[slot],animal:ANIMALS[slot]};}
export function animalBadge(p,index=0){return new URL('avatars/'+playerVisual(p,index).animal+'-badge.svg',visuals).href;}
export function modeArt(mode){const name=mode==='duel'?'turf':mode;return `<img class="mode-art" src="${new URL('modes/'+name+'.svg',visuals).href}" alt="" aria-hidden="true">`;}
