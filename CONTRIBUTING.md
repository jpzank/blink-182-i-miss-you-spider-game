# Contributing

Help make the game more immersive and more fun to explore. Contributions to art, animation, gameplay, accessibility, performance and documentation are welcome.

## Start a change

1. Check existing issues and pull requests for related work.
2. Fork this repository, clone your fork and create a branch for one focused change.
3. Run the game locally as described in the README.
4. Make the change and run `npm test` and `npm run check`.
5. Open a pull request with the problem, what changed, and how you checked it.

For a larger gameplay change or replacement of a major character, open a proposal issue first. Screenshots or a short capture of the actual game are useful for visual changes. Include the editable source as well as the exported asset when possible.

## Graphics and animation

- Read [the asset workflow](docs/ASSET_WORKFLOW.md) before replacing a GLB.
- Preserve the runtime naming and coordinate conventions, or update their consumers in the same change.
- Include source, author and license for new assets. Use original work or material you are allowed to redistribute and modify; keep upstream notices.
- Document AI-generated textures and their source prompts. Do not describe generated approximations as photographs or scans.
- Report the effect on file size, triangle count and measured frame rate when relevant. Name the hardware/browser used.
- Inspect the result in the game's lighting and from the spider's camera, including contact with floors, clothing and furniture.

## Gameplay and interface

- Keep the interface in English.
- Check keyboard and touch controls, pause/resume, and camera comfort.
- If progression or collision changes, complete all three threads and the ending. Check the cat checkpoint and bed traversal when those areas are affected.
- Add focused tests for new behavior. UI copy or cosmetic changes do not need tests that merely repeat the implementation.
- Keep the game usable if YouTube cannot load. Do not commit audio/video copies of the music video.

## Validation and review

GitHub CI runs the existing Node tests and JavaScript syntax checks with read-only permissions. Vercel deploys `main` to production and can create PR previews; fork previews require owner authorization. Clearly distinguish checks that passed from checks you could not run. A viewport resized on a desktop is not physical-device testing.

Do not commit `.env` files, credentials, local deployment settings, caches or Blender backup files. Avoid unrelated dependency changes. Check peer dependencies and runtime requirements before a major upgrade, and update the lockfile together with the dependency declaration.

Your original contributions are submitted under this repository's MIT license unless a clearly identified third-party component has its own compatible terms. Please keep discussion constructive and credit other contributors' work.
