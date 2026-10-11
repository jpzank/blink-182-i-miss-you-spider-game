# Working on graphics and animation

## Editable sources

| Asset | Blender source | Builder | Runtime export |
| --- | --- | --- | --- |
| Band | `assets-src/musicians.blend` | `scripts/build-musicians.py` plus `scripts/band-details.py` and `scripts/band-heads.py` | `dist/models/musicians-v6.glb` |
| Reclining figures | `assets-src/reclining-women/reclining-women.blend` | `scripts/build-reclining-women.py` | `dist/models/reclining-women-v6.glb` |
| Sphynx | `assets-src/sphynx/sphynx.blend` | `scripts/build-sphynx.py` | `dist/models/sphynx-v7.glb` |

The Blender scenes embed their image data and keep both image paths and packed-resource source paths relative to the project tree. Keep those fields, render output paths, and any File Browser workspace paths free of workstation-specific directories before saving a source file. Source maps are also included for painting and rebuilding. The builders were tested with Blender 5.1.2; the band and Sphynx builders were last run with Blender 5.2.2 LTS (also usable as the `bpy==5.2.2` Python module with its bundled numpy). Use `blender -b --python <script>` from the project root. The band and Sphynx builders start from an empty factory scene and re-pack images with project-relative source paths before saving. They regenerate meshes and exports, so manual Blender edits should be preserved on a branch before rerunning a builder.

The spider, bed and much of the environment are procedural JavaScript geometry, so edit their runtime modules directly. Furniture comes from the credited Poly Haven models.

## Heads, hair and skin shading

`scripts/band-heads.py` gives each musician's head its own UV set (`HeadUV`): the face and temples are wrapped cylindrically around the skull, and the crown, nape, ears and hidden folds are packed above. It bakes per-member face albedo (1536 px), roughness and tangent normal maps from the facial atlas plus procedural relief (pores, expression creases), builds a strand-textured hair volume grown from the scalp with strand cards on top, replaces the proxy eyes with smooth eyeballs, a raised cornea and procedural irises, and adds eyelash strips on MakeHuman's eyelash helpers. Hair textures share one neutral strand map; `dist/musicians.js` applies each member's hair colour.

`dist/skin.js` patches the physical lighting of skin materials at runtime: a red-shifted wrapped diffuse approximates subsurface scattering, and an optional per-vertex `thin` mask (exported as the Sphynx's `Thin` colour attribute) lets backlit ears glow. Eyes become clear-coated physical materials.

## Coordinates and animation

Blender uses Z-up; GLB export converts to the game's Y-up coordinates. The reclining figures lie along local X, heads toward +X; the Sphynx faces local +Z in glTF, with feet near Y=0. Inspect the loading groups in `dist/alcove.js` for placement. The band loader and its named animation conventions are in `dist/musicians.js`.

Use self-contained GLBs with embedded textures. Preserve working skins, node names, clips and loop durations unless you update the corresponding loader/tests. Bake procedural Blender materials into textures for the browser. Include a normal map when it helps; avoid adding geometry that does not contribute at the actual game camera scale.

## Verify a replacement

1. Run `npm test` and `npm run check`.
2. Inspect the asset in the running game, with its actual lighting and animation.
3. Check close-up contact, silhouettes, alpha edges, skinning, loops and shadows.
4. Test associated collisions, climbing and checkpoint behavior.
5. Record any change in model size, triangle count and frame rate; identify the test device.
6. Include the editable source and attribution with the exported file.

The current characters are approximations. The band faces come from an AI-generated likeness atlas projected onto CC0 MakeHuman heads; the Sphynx is an original procedural sculpture. Do not label improvements as exact scans or motion capture unless that is actually how they were produced and the source can be redistributed.
