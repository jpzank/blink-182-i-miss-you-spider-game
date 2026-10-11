# Public baseline

This repository starts with a public snapshot of the playable game, revision 7, exported on 2026-10-10 from source commit `27cc87ada241ebed030332e25e3797888c8bd461`.

The initial public snapshot preserves the baseline's gameplay code and decoded image content. Asset metadata was sanitized during the 2026-10-10 history cleanup. The public package adds English community documentation, a project license, contribution/issue templates and validation CI. Package metadata uses the public repository name.

In this revision, the editable Blender sources retain their packed image resources and use project-relative image and packed-source paths. Preview PNGs retain their pixel and color data with EXIF and text metadata removed; distributed texture JPEGs retain the same decoded pixels with EXIF and Photoshop metadata removed. The ready-to-use GLB exports were not changed. The 2026-10-10 history cleanup replaces the affected assets in every commit on the public main branch. Existing clones must be recreated or rebased onto the cleaned history. Old commit URLs or independent copies may remain outside the branch history; the rewrite cannot remove those copies.

No production credentials are required. Serving `dist/` is sufficient to play. Vercel now hosts the game and deploys `main`. GitHub CI validates code; Vercel handles deployment.

On 2026-10-10, the game moved to Vercel. Sharing metadata and links now use the Vercel address, and the in-game X share button uses the current origin so forks can share their own deployment. The game assets and mechanics remain those of revision 7.
