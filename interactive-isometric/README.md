# From request to record — interactive 3D study

Self-initiated Hx Works capability study, not a client commission or a client website. It is an illustrative route, not an implemented financial system. Original artwork/code with automated assistance; no private or client material.

## Scope

- Native Three.js WebGL meshes: four platforms, document/shield/record/check symbols and a travelling sphere. Not a video or Canvas 2D substitute.
- Mouse picking and native step buttons; keyboard selection with Tab/Enter, arrows and scene-focused number keys 1–4.
- A pausable six-second packet loop and bounded, native-scroll camera adjustment (about 12 degrees total).
- `prefers-reduced-motion` disables automatic packet and scroll motion, with on-demand static 3D rendering. If WebGL/module initialization fails, the original vector still and text controls remain available.
- Actual navigation-to-render-call timing and rolling requestAnimationFrame intervals are exposed in the page and the read-only `window.studyDiagnostics()` hook. These do not establish GPU timing, paint time, 60fps or subsecond loading across devices.

## Provenance

The geometry, palette and Request / Validate / Record / Confirm labels derive from the existing own-source study at `../ui-motion-deck-publish-20261019/isometric-workflow/render.py` (source SHA-256 `9422077e858e4e89811d8c28b03bf33c5b34d65eccd87b60b13a7cf1fa3112f4`). Its original vector poster is copied unchanged to `assets/original-poster.svg` as the static fallback (SHA-256 `0b6afd69e2165c03af5861c81f2c992461a084952573a2ed7229f33d4e182c26`). This version translates the flat isometric construction into simple actual 3D primitives; it does not claim pixel-identical reproduction.

Three.js **0.180.0**, MIT, is vendored from the official npm registry. `vendor/source-receipt.json` records exact URLs, npm integrity verification, byte counts and local SHA-256 hashes. `acquire_vendor.py` fetches only this pinned package and extracts the two runtime modules, original package metadata and LICENSE. No npm install, global package change or package lifecycle script. The compressed archive is retained under `vendor/cache/` as source evidence; deployment needs only the two JS modules and license, not the cache or Python utilities.

## Run

Serve this folder through a normal static HTTP server. `python serve.py` binds only `127.0.0.1` on an OS-assigned port and prints the actual URL. Stop with Ctrl+C. No build process, account, API key, remote font, tracker or external runtime service is required.

The portable runtime files are `index.html`, `styles.css`, `app.mjs`, `assets/original-poster.svg`, and `vendor/{three.module.min.js,three.core.min.js,LICENSE-three.txt}`. Keep this README with shared source for scope/attribution. No publication is performed by these scripts.

## Validation boundary

CLI syntax, dependency integrity, referenced-file and loopback HTTP checks passed. Root then observed the local page in the in-app browser: actual WebGL2 rendering with 27 geometries and 27 draw calls; all four nodes visible in the desktop English layout; step buttons, ArrowRight, scene-focused key 3, and a raycast click selecting Request from Record worked. Pausing changed the control to Play packet and stopped continuous sampling. Native scroll changed the displayed progress from 0% to 30%, 66% and 74%, with changed projected positions. Reduced-motion mode kept the scene static while selection remained usable. Browser console warning/error arrays were empty.

At a 390 CSS-pixel viewport, root observed document client/scroll widths of 390/390 with no horizontal DOM overflow; a scrollbar variant reported 374 CSS pixels. The mobile screenshot used a CDP capture scale of 1.5 to account for OS scaling. This is browser viewport evidence, not a physical mobile-device test.

The first render-call return was observed at 248.1 ms on the first local load and 119.8 ms on reload. Two observed requestAnimationFrame samples reported median intervals of 6.2 and 6.3 ms, with p95 6.4 ms. These are local, device-specific observations: render-call return is not paint, GPU or network timing, and rAF intervals are not a 60fps guarantee. No general subsecond-loading claim follows.

Local evidence is recorded in `browser-qa-receipt.json`, `desktop-live-webgl.png` and `mobile-reduced-motion.png`; those QA files are not required for deployment. Cross-browser, physical-device and production performance remain unverified. This study does not establish Spline expertise, commercial Three.js experience, a full sprint estimate or client acceptance. Root retains the publication/application decision.
