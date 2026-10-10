# Band facial atlas — generated texture reference

The separate tattoo texture and exact generation prompt are documented in [TATTOO-PROMPT-AND-PROVENANCE.md](TATTOO-PROMPT-AND-PROVENANCE.md).

- Saved asset: `facial-atlas-v1.png` (2172 × 724 px, RGB, three 724 px columns).
- Column order: Mark Hoppus, Tom DeLonge, Travis Barker.
- Tool: built-in `image_gen`, no CLI/API fallback.
- Created: 2026-10-10.
- Purpose: project-specific frontal diffuse color reference for 3D facial projection; period hairstyle is separate geometry.
- Nature: AI-generated likeness approximation, not a photogrammetric scan or an authentic photograph of the band. Facial proportions remain approximate, especially Mark and Tom. Exact identity is not guaranteed by the texture alone; geometry, hairstyle, costume and movement are needed together.
- Reference source supplied by user: https://www.youtube.com/watch?v=s1tAYmMjLdY
- Local reference frames: `analysis/frames/0032.jpg`, `0057.jpg` (Mark); `0168.jpg` (Tom); `0054.jpg`, `0136.jpg` (Travis). All were visually inspected before generation.
- The initial generation used all five reference frames. The selected refinement used the initial atlas followed by frames 0032, 0057, 0168 and 0054, in that order. A rejected invocation with six inputs did not generate an image; the tool supports at most five reference paths.
- No game or build code was edited for this asset task.

## Projection notes

See `landmarks.json` for approximate global pixel coordinates (top-left origin). The scalp top has only 3–8 px margin, less than requested; all heads are intact. Skin extends to the bottom as upper neck. The atlas includes close shaved scalp texture. Hide it beneath period hair geometry. There is mild baked shading under the jaw and nose; use a low-contrast blend into the original skin texture to avoid double lighting. Facial heads were generated with closed mouths, open eyes and neutral expression. Hair, costumes, body tattoos and animations are deliberately out of scope of this atlas.

## Initial exact prompt

```text
Use case: photorealistic-natural.
Asset type: ONE frontal facial diffuse texture atlas for projection onto three separate 3D game character heads.
Primary request: recreate the recognisable youthful 2003/2004 facial appearances of blink-182 members in the supplied I Miss You music-video reference frames. This is a technical texture sheet, not a poster or scene.
Input images are reference only, not edit targets. References 1 and 2: Mark Hoppus; reference 3: Tom DeLonge; references 4 and 5: Travis Barker. Preserve each named person's distinctive facial anatomy and youthful music-video era appearance; no present-day aging.
Composition: exact 3:1 wide landscape atlas, ideally 3072 by 1024. Three equal-width columns without visible borders. LEFT column Mark Hoppus, CENTER column Tom DeLonge, RIGHT column Travis Barker. Each is one fully frontal orthographic head and upper neck, eyes forward, head upright, relaxed neutral expression, lips CLOSED. Head completely visible including both ears; top of head about 8% from top, chin about 82% from top, neck extends to bottom. Consistent eye level around 40% from top, nose around 58%, mouth around 70%, consistent scale. Head fills almost the full width of its own column, leaving a small clean margin. Faces should be distinct, not three versions of a generic actor.
Identity specifics: Mark has a relatively full rounded-square face, wide jaw and chin, straight nose and fuller lips; match his eyes and eyebrows from references 1 and 2. Tom has an elongated face, broad cheekbones, prominent nose and wider mouth; match reference 3. Travis has a narrow angular face, prominent nose, thinner jaw and cheeks and the subtle small lower-lip facial hair visible in his era reference. Do not invent facial tattoos.
Technical constraint: ALL THREE must have absent head hair or extremely close barely visible shaved hair, only because exact period hairstyles will be added as separate 3D geometry. Keep natural eyebrows, eyelashes and Travis's subtle lower-lip facial hair. No scalp tattoos, no modern tattoos. Both ears unobstructed. Bare upper neck, no clothes visible, no shoulders occupying the bottom. No hair cast shadows.
Style and materials: photographic human skin diffuse color, pores and subtle age-appropriate features, not painted, not stylized, not waxy, no beauty retouch.
Lighting and backdrop: uniform neutral light skin-tone background filling the whole atlas. Soft perfectly even neutral illumination for an albedo texture. Avoid directional lighting, highlights, strong shadows, dark eye sockets, dramatic video color grading, vignettes and rim lights. The light is only for seeing surface color clearly.
No text, no names, no frames, no borders, no watermarks, no objects, no instruments. Do not merge or overlap heads across columns.
```

## Selected refinement exact prompt

```text
Edit target: the first image, a 3-column facial albedo atlas. Supporting identity references: images 2 and 3 show MARK HOPPUS in I Miss You (2003/2004); image 4 shows TOM DELONGE; image 5 shows TRAVIS BARKER. Correct the FACIAL LIKENESS in the atlas, especially the first two men. The first draft made Mark and Tom into generic lookalikes. Make them recognisably their actual youthful public-figure identities, with reference-faithful eyes, brows, nose, lips, jaw and cheek proportions rather than standard handsome faces. Mark on LEFT needs Mark Hoppus's characteristic fuller square face and chin, distinctive fuller mouth and light blue-green eyes with dark broad brows as seen in the supplied close-up. Tom in CENTER needs Tom DeLonge's long facial proportions, nose shape, mouth width, narrower eyes and his distinctive upper lip and jaw; do not repeat Mark's face. Travis on RIGHT should retain the long narrow angular face, brown eyes, prominent slender nose and tiny patch below the lower lip. Keep the same neutral CLOSED-mouth expression, fully frontal orthographic views, equal column widths, natural photographic skin, ears visible, unobstructed neck, no clothes, even neutral albedo lighting and plain skin-tone background. Keep shaved hair only as a 3D texture-production requirement; geometry will supply period hairstyles later. No tattoos invented, no modern aging, no stylisation. Preserve 3:1 atlas composition and order, no text or borders. Each full head must have a visible margin above the scalp, not crop. Only improve each actual person's facial identity and exact proportions, not scenery or composition.
```
