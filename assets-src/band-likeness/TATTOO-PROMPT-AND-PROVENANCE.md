# Tattoo albedo — original period-style approximation

- Saved asset: `tattoo-albedo-v1.png`, 1024 × 1024 px.
- Tool: built-in `image_gen`, single generation, no retries and no CLI/API fallback.
- Created: 2026-10-10.
- The generated master was resized to 1024 × 1024 for the game; the distributed texture is included alongside this document.
- Reference 1: `analysis/frames/0136.jpg`, visually inspected from the user-supplied video https://www.youtube.com/watch?v=s1tAYmMjLdY. Used for general muted/dense ink style only.
- Reference 2: `facial-atlas-v1.png`, rightmost panel used only for skin color.
- Nature: original invented motifs. This is a visual approximation of early-2000s tattoo style, **not a reproduction or inventory of Travis Barker's actual tattoos**.
- Inspection: square flat texture, black-and-grey ornamental linework, roses and muted skull motifs, occasional desaturated red, skin visible between motifs. No text, logos, borders, portraits or body anatomy. Not guaranteed mathematically seamless; wrapping/masking is handled by the game mesh pipeline.
- No game code or model script changed by this asset task.

## Exact generation prompt

```text
Use case: photorealistic-natural.
Asset type: ONE square 1024×1024 original tattoo diffuse/albedo texture sheet for mapping onto the arms and neck of a 3D musician character.
Primary request: create an original dense early-2000s black-and-grey tattoo ink pattern on flat light human skin color. This is a seamless-looking flat technical texture, NOT a picture of a body or a tattooed person.
References: image 1 is the 2003/2004 I Miss You video frame and is ONLY a reference for the general dense tattoo style and muted ink treatment visible on Travis Barker's arms. Do not claim or attempt exact tattoo replication. Image 2 is a facial texture atlas; use ONLY the light warm skin color of the RIGHTMOST Travis panel as the background color reference, not its head or facial features.
Composition: fill the whole square edge to edge with moderately dense interlocking illustrative tattoo motifs of varied small sizes: small roses, dark ornamental outlines, muted skull silhouettes, winding shaded scrolls, leaf shapes and fine-line flourishes, with skin-colored breathing room between designs. A few tiny rose petals can have very desaturated muted red; nearly all ink is black and faded charcoal-grey. Several organically interlocking motifs, not one giant central picture and not a contact sheet with panels. Motifs should extend naturally through the edges for wrapping onto cylindrical arms.
Materials: fine realistic ink lines and soft healed tattoo shading embedded in skin, subtle pores, slightly faded mature black/grey ink, warm light skin background matching the rightmost panel of the atlas. Enough contrast to read on an animated low-light game character; avoid large black solid blocks.
Lighting: perfectly flat unlit diffuse color, no cast shadows, no highlights, no directional illumination, no shadows from anatomy.
Constraints: original invented motifs conveying a similar period style, not an exact reproduction of anyone's existing body art. No text, no lettering, no numbers, no names, no logos, no band symbols, no border, no watermark, no photographic body parts, no faces or portraits, no actual arm/hand/neck anatomy, no clothing, no hair. Whole output is one flat square albedo material texture.
```
