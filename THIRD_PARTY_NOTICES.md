# Component licenses and asset provenance

The root MIT license applies to original project code and original project-authored materials to the extent the project author controls those rights. It does not replace third-party licenses or grant rights in third-party music, recordings, trademarks or likenesses.

| Component | Location | License / source |
| --- | --- | --- |
| Three.js 0.186.1 and vendored addons | `dist/vendor/` | MIT; [included notice](dist/vendor/THREE-LICENSE.txt), [upstream](https://github.com/mrdoob/three.js) |
| MakeHuman core meshes, rigs, clothing, eyes, hair and skin | `assets-src/makehuman/`, `assets-src/reclining-women/source/`; adapted into character models | CC0; [included license explanation](assets-src/makehuman/LICENSE.md), [official asset license](https://static.makehumancommunity.org/about/license.html) |
| Poly Haven Sofa 03 and Gothic Coffee Table | `dist/models/sofa_03/`, `dist/models/gothic_coffee_table/` | CC0; [model sources](dist/models/SOURCES.md), [official license](https://polyhaven.com/license) |
| Poly Haven photographic PBR textures | `dist/textures/` | CC0; [texture source list](dist/textures/SOURCES.md) |
| Generated wall, rug, facial atlas and illustrative tattoo textures | `assets-src/`, `dist/textures/`; baked into band model | Project-authored generated material; [wall/rug prompts](assets-src/PROMPTS.md), [facial atlas provenance](assets-src/band-likeness/PROMPTS-AND-PROVENANCE.md), [tattoo provenance](assets-src/band-likeness/TATTOO-PROMPT-AND-PROVENANCE.md) |
| Spider, bed, Sphynx, character adaptation, procedural hair/eye/skin-relief textures, skin shading, costumes and animation | `dist/spider.js`, `dist/alcove.js`, `dist/skin.js`, `scripts/`, `assets-src/` | Original project work, with the CC0 character bases noted above; [women provenance](assets-src/reclining-women/PROVENANCE.md), [Sphynx provenance](assets-src/sphynx/PROVENANCE.md) |

MakeHuman's application source has a separate copyleft license; this repository includes its CC0 asset data, not the MakeHuman application. The custom Blender builders are project code. Blender itself is not distributed here.

The official [blink-182 — I Miss You video](https://www.youtube.com/watch?v=s1tAYmMjLdY) is an external reference and embedded player. No recording, extracted soundtrack, lyrics or reference video frames are distributed in this repository. The band likenesses are artistic approximations; illustrative tattoos are not a faithful inventory of anyone's tattoos. This independent fan project is not endorsed by the band or the recording's rights holders.
