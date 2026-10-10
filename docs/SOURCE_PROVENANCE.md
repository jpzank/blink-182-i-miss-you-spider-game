# Public baseline

This repository starts with a public snapshot of the playable game, revision 7, exported on 2026-10-10 from source commit `27cc87ada241ebed030332e25e3797888c8bd461`.

The initial public snapshot preserves the baseline's gameplay code and decoded image content. Asset metadata was sanitized during the 2026-10-10 history cleanup. The public package adds English community documentation, a project license, contribution/issue templates and validation CI. Package metadata uses the public repository name.

Editable Blender sources were repacked to contain their image resources and use relative paths. Their ready-to-use GLB exports were not changed. Local deployment configuration, workspace-only notes, older QA screenshots, backups and workstation-specific generated-image paths were excluded. The managed hosting repository retains its original history separately; this public repository starts with one reviewable baseline commit.

No production credentials are required. Serving `dist/` is sufficient to play. Vercel now hosts the game and deploys `main`. GitHub CI validates code; Vercel handles deployment.

On 2026-10-10, the game moved to Vercel. Sharing metadata and links now use the Vercel address, and the in-game X share button uses the current origin so forks can share their own deployment. The game assets and mechanics remain those of revision 7.
