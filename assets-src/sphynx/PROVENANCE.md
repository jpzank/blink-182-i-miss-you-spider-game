# Sphynx: Between the Threads

Original asset, generated procedurally by `scripts/build-sphynx.py` (Blender 5.2, bundled numpy). It uses no third-party mesh, scan, photograph, image generation or video pixels.

Visual reference: the hairless cat grooming itself in the user-supplied official video blink-182, I Miss You (2003), around 00:42 and 00:45. This version aims at the breed's anatomy: wedge-shaped skull, high cheekbones, short muzzle with prominent whisker pads, large thin open ears, lemon-shaped eyes, visible scapulae, loose belly skin, forehead/throat/shoulder folds and a long whip tail. It is an artistic reconstruction, not a scan of the cat in the video.

## How it is built

1. Anatomy is a smooth union of signed-distance primitives in a seated grooming pose, with the right forepaw raised to the mouth. Skin folds are displaced into the distance field.
2. A dense surface (about 0.0045 units/voxel) is extracted with naive surface nets. A smoother low surface is decimated to about 28k triangles for the browser.
3. The dense folds and procedural pores are baked into a tangent normal map. Albedo combines ivory-rose skin, faint grey pigment mottling, warmer and pinker thin-skin zones, ear capillaries, fine follicles and the occlusion of the sculpted creases. Roughness is wetter on the nose leather.
4. Eyes are separate eyeballs with a raised cornea and a procedural iris with a vertical slit pupil.
5. Seventeen bones (body, spine, neck, head, both ears, both forelegs, five tail segments). Skin weights come from the anatomical primitive that forms each vertex.
6. The 8-second loop has licks at three per second, head and paw following each lick, a pause to look into the room, an ear twitch, breathing and a travelling tail-tip wave.

```sh
blender -b --python scripts/build-sphynx.py
```

- Root `Sphynx`, clip `Sphynx grooming • 8s`
- Blender front -Y, glTF front +Z; paws on z=0 (Blender) / y=0 (glTF)
- `Thin` colour attribute (exported as COLOR_0) marks ear tissue; `dist/alcove.js` renames it to `thin` for the translucency shader and draws the cat at 1.18× scale.
- Maps: `skin-albedo.jpg`, `skin-normal.jpg` (1536 px), `skin-roughness.jpg`, `iris.jpg`; statistics in `stats.json`.
- `preview.jpg` is a capture of the running game (SwiftShader software rendering), not an offline render.

Limits: no simulated muscles, tongue or blinking; the mouth stays closed while grooming; skin weights are automatic, so extreme poses would need cleanup.
