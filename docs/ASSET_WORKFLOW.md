# Working on graphics and animation

## Editable sources

| Asset | Blender source | Builder | Runtime export |
| --- | --- | --- | --- |
| Band | `assets-src/musicians.blend` | `scripts/build-musicians.py` plus `scripts/band-details.py` | `dist/models/musicians-v5.glb` |
| Reclining figures | `assets-src/reclining-women/reclining-women.blend` | `scripts/build-reclining-women.py` | `dist/models/reclining-women-v6.glb` |
| Sphynx | `assets-src/sphynx/sphynx.blend` | `scripts/build-sphynx.py` | `dist/models/sphynx-v6.glb` |

The public Blender scenes have packed image resources and relative paths. Source maps are also included for painting and rebuilding. The builders were tested with Blender 5.1.2; use `blender -b --python <script>` from the project root. They regenerate meshes and exports, so manual Blender edits should be preserved on a branch before rerunning a builder.

The spider, bed and much of the environment are procedural JavaScript geometry, so edit their runtime modules directly. Furniture comes from the credited Poly Haven models.

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

The current characters are approximations. Do not label improvements as exact scans or motion capture unless that is actually how they were produced and the source can be redistributed.
