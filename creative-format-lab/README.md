# Creative format lab — self-initiated study

A small, dependency-free JavaScript prototype for adapting a fictional notebook creative. It is not client work, an ad-network-certified deliverable, a checkout, or evidence of campaign performance.

## Problem and implementation

Changing output size and language can silently clip advertising copy. One copy model drives 300×250, 728×90 and 320×50 layouts in English and Chinese. The native DOM renderer checks headline/action bounds; oversized copy is rejected with a visible message instead of exported or silently truncated. The decorative notebook is original inline SVG. No external assets, libraries, remote fonts, analytics or data endpoints are used.

Open `index.html` in a browser. Choose a format, language and copy condition. The preview button opens a local fictional-detail dialog; it does not navigate to a merchant or collect information.

## Actual validation — 19 October 2026

- Six normal size/language combinations rendered at their declared dimensions. An independent DOM bounds read found the visible headline, supporting text where present, and action inside the creative.
- The intentionally long headline was rejected in all three sizes. Rejection depends on measured bounds, not a test-case flag.
- A real browser click opened the dialog. Native Escape closed it and returned focus to the action; native Enter opened it again.
- Native screenshots inspected for rectangle, leaderboard and mobile layouts.

The first label-based test locator failed; explicit element IDs succeeded. A text-presence check against an accessibility *diff* did not establish visibility for the unchanged first case; independent DOM bounds and rendered inspection supplied the evidence instead.

## Limits and learning

This is a bounded capability example supporting a creative-automation workflow, not a completed campaign or an accepted brief. Automated checks catch geometric overflow, not the best visual hierarchy or language for every market. New sizes and real client copy still require review.

CSS and the replay action consult `prefers-reduced-motion`, but only the normal-motion environment was observed. The tool could not inspect animation objects, so animation timing, reduced-motion runtime behaviour and smooth playback are not claimed as tested. There is no ad-network click-tag, package validator, asset export pipeline, browser/device compatibility certification, conversion result, Adobe source file or client material in this study.

Hx Works · Original synthetic copy/artwork · AI-assisted code production.
