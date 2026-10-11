# Model sources

## Musicians
Anatomy, skin, garment, hair and eye sources: MakeHuman Community, CC0. The three individual visual reconstructions are based on Mark Hoppus, Tom DeLonge and Travis Barker in the user-referenced I Miss You video. Facial likeness, hairstyle, costume and performance are approximations, not scans or motion capture.
https://static.makehumancommunity.org/about/license.html
https://github.com/makehumancommunity/makehuman
https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html

Individual facial albedos and an original illustrative tattoo albedo were generated with built-in Image Gen using selected video frames as visual reference. Tattoos are not exact copies of Travis Barker's tattoos. Sources and exact prompts are in assets-src/band-likeness/PROMPTS-AND-PROVENANCE.md and TATTOO-PROMPT-AND-PROVENANCE.md. The hair is project-made: a volume grown from each scalp with a procedural strand texture, plus strand cards.

Performance poses, inverse kinematics, head UVs and face/roughness/normal bakes, hair volumes and strand cards, eyes and eyelashes, suspenders, costume materials, animation baking and GLB assembly: scripts/build-musicians.py, scripts/band-details.py and scripts/band-heads.py. All relief, hair, lash and iris textures are procedural (no photographs). Editable source: assets-src/musicians.blend.

## Furniture
Poly Haven, CC0:
- Sofa 03 by Fran Calvente: https://polyhaven.com/a/sofa_03
- Gothic Coffee Table by Ulan Cabanilla: https://polyhaven.com/a/gothic_coffee_table
https://polyhaven.com/license

## Spider
Original procedural geometry, textures, articulations and fur in dist/spider.js.

## Reclining women and alcove
Two fully clothed adult interpretations of the reclining scene around 00:44 in the supplied video. MakeHuman CC0 anatomy, female targets, skin and bob hair; original clothing, makeup adaptation, finger waves, choker and six-second breathing cycles. Procedural bed and textiles in dist/alcove.js. Editable scene and full provenance: assets-src/reclining-women/. No video pixels are embedded in this model.

## Sphynx
Original procedural sculpture (signed-distance anatomy, dense wrinkle detail baked to a normal map), procedural skin, iris and roughness maps, a 17-bone rig and an eight-second grooming loop, inspired by the hairless cat around 00:42 and 00:45. Editable scene and provenance: assets-src/sphynx/. Builder: scripts/build-sphynx.py. No third-party mesh, photographs or video pixels.
