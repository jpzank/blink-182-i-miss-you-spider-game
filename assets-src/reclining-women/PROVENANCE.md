# Reclining women — source and implementation

Two original, fully clothed adult character interpretations for Entre os Fios, created 2026-10-10. They are not scans or exact likenesses of the actresses.

Visual reference: the official Blink-182 **I Miss You** video supplied by the user, https://www.youtube.com/watch?v=s1tAYmMjLdY . Locally inspected reference frames at 26 s, 44 s and 89 s show a black bob, short dark finger waves, ivory period dresses, dark eye makeup and a garnet choker. Reference video frames are not included in the published asset.

## CC0 anatomy and source textures

MakeHuman community assets, licensed **CC0 1.0 Universal**:

- Existing project `assets-src/makehuman/base.obj`, `default.mhskel`, `default_weights.mhw`, `eyes.obj`, `eyes.mhclo`, `brown_eye.png`; license in `assets-src/makehuman/LICENSE.md`.
- Female adult macro targets from the official repository: https://github.com/makehumancommunity/makehuman/tree/master/makehuman/data/targets/macrodetails : `universal-female-young-averagemuscle-averageweight.target` and `caucasian-female-young.target`.
- Official CC0 system pack: https://files.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip . Uses `skins/young_caucasian_female` and `hair/bob01`.

Only the needed files were extracted. The original sources are preserved under `source/`. No external model marketplace material was used.

## Original work

`scripts/build-reclining-women.py` is a standalone conversion/build script; it does not invoke or alter the band builder. It constructs loose, opaque ivory dresses with fabric weave, folds, bead trim and fringe, subtle makeup baked into skin UVs, short finger-wave details and a red choker. Pose bones give relaxed asymmetrical torso/head turns and bent arms. A six-second loop adds restrained breathing. A shaped skirt suggests bent knees, with extra waist overlap to keep the torso/skirt join closed when the torso turns.

The faces and hands use human anatomical geometry. The hair is a lightweight real-time card/mesh model, so it remains a game interpretation at extreme close-up. No Image Gen was used for this asset. Texture modifications, clothing and jewelry are reproducible in the script.

## Deliverables

- `dist/models/reclining-women-v6.glb`: embedded images, two independently skinned adult characters and two breathing clips.
- `assets-src/reclining-women/reclining-women.blend`: editable scene without bed, lights or camera.
- `inspection.png`: full-figure render, inspecting clothing coverage, silhouette and pose.
- `face-inspection.png`: closer face/hand inspection render.
- `bounds.json`: evaluated bounds in Blender coordinates at the first frame.

Model axes: +X points toward heads. Blender +Z is height, mapped to Three.js +Y; Blender +Y maps to Three.js -Z. The support plane is around local height zero. Heads should be supported by separate pillows; no bed/pillow meshes are exported.

Build:

```sh
/opt/homebrew/bin/blender -b --python scripts/build-reclining-women.py
```
