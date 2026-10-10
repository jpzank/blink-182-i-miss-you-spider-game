# Deployment on Vercel

Production: **https://blink-182-i-miss-you-spider-game.vercel.app/**

The Vercel project uses this GitHub repository and publishes the `main` branch. The game is static: no server functions, environment variables, credentials or database are required for players.

## Build settings

- Framework preset: Other (`framework: null`).
- Root directory: repository root.
- Install command: empty, because runtime dependencies are already vendored.
- Build command: `npm run check && npm test`.
- Output directory: `dist`.

These settings are stored in `vercel.json`. Keep Blender files and art sources in GitHub for contributors; only `dist/` is served on the public game site.

## Access and releases

Production is public over HTTPS and does not require a Vercel account. Preview deployments retain Vercel authentication protection. Pull requests from forks require the project owner to authorize a preview deployment.

Review contributions and the validation results before merging into `main`: Vercel publishes that branch. Check the Vercel deployment state and the actual production URL after a release. A passing GitHub workflow alone does not confirm publication.

For another community deployment, fork or import the repository into your own Vercel account using the same settings. The in-game share button uses the current site origin. Update the fixed social-preview URLs in `dist/index.html` to your own production address.
