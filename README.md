# Hx Works — selected technical and visual studies

Inspect the output, the source and the checks behind it. These are self-initiated studies, with fictional or synthetic inputs. They are capability examples; none is presented as paid client work.

[View the project studies in a browser](https://hxsworrk-lab.github.io/ui-motion-study/studies.html) — previews, editable files and evidence limits in one page.

[Misfiled Archive Box — stylized 3D prop study](archive-box-study/) · actual model render, GLB, source and bounded native import checks; self-initiated, not Unity-production validated.

## Technical evidence and editable files

| Study | What you can inspect | Scope of the evidence |
| --- | --- | --- |
| [WordPress REST validation](wordpress-rest-study/) | PHP handler, synthetic fixture and unchanged recorded JSON. | Seven in-process authorization, validation and sanitized-save checks; HTTP/session authentication, process-exit persistence and production integrations remain untested. |
| [Browser cleanup comparison](https://hxsworrk-lab.github.io/browser-cleanup-check/) · [source](https://github.com/hxsworrk-lab/browser-cleanup-check) | A runnable Svelte 5.23.2 comparison, ordered events and a JSON report. | Component mount/unmount and mock cleanup calls in a controlled setup. Real HTTP/SSE traffic, memory retention and production acceptance remain untested. |
| [Creative format lab](creative-format-lab/) | Dependency-free JavaScript source, three advertising sizes, English/Chinese copy and a local preview dialog. | Six layout combinations, three measured overflow rejections and native keyboard interaction checked. Reduced-motion runtime, animation smoothness and ad-network certification remain untested. |
| [Native n8n HTTP workflow checks](n8n-http-validation/) | Workflow generator, synthetic HTTP fixtures and recorded execution checks. | Seven controlled scenarios cover transient failures, retry bounds, batch validation and within-batch deduplication. Real Google Sheets, OAuth and production reliability remain untested. |
| [Editable supplier decision deck](supplier-decision/) | Three slides, editable text and a native PowerPoint table, plus rendered previews. | The fictional cost comparison and decision threshold were checked. Desktop PowerPoint opened the original file and exported all three slides for visual checks. On a copy, one text shape and one table cell retained edits after save, close and reopen. Animations and other Office software remain untested. |
| [Architectural openings](architectural-openings/) | Named Blender geometry, a GLB export, dimensions and fresh-import checks. | Fourteen checks examine the actual opening geometry. This is a conceptual layout; it carries no building-code, structural or construction approval. |
| [Contour-constrained curved relief](curved-relief-study/) | A synthetic STL, Blender source and fresh-import checks. | Contour-aligned analytic geometry and basic topology only; arbitrary STL editing, slicers, physical printing and can fit are untested. |

## Motion examples

| Study | Output and source |
| --- | --- |
| [Isometric workflow](isometric-workflow/) | A silent six-second data-flow loop: request, validate, record, confirm. MP4, an editable SVG still and Python animation source. It has no AE/C4D project file. |
| [Minimal typography loops](minimal-loops-20261017/) | Two six-second vertical motion studies with source and export notes. |
| [Quote comparison](#quote-comparison--motion-study) | The twelve-second fictional supplier comparison below, including its renderer and offline player. |

## Discuss a specific task

Send the expected result, input format and required output format to **hxsgmail@gmail.com**. A public or redacted example is enough for an initial discussion. Keep confidential files back until the permitted tools and material rights are agreed.

Scope, acceptance checks, revisions, timing, price and payment are agreed before work starts. Relevant tool workflows are described in each study; a sample does not establish suitability for every production system or source format.

---

## Quote comparison — motion study

**Hx Works · Self-initiated concept · Fictional data**

A silent, 12-second UI animation exploring the trade-offs between unit price, minimum order quantity and lead time. Three fictional supplier cards enter in sequence, a single MOQ filter narrows the comparison, and the final state holds for reading.

[Watch or download the full MP4](hx-works-quote-comparison-motion-study.mp4) · [Offline player source — download before use](index.html)

![Animated preview of the fictional quote-comparison interface](quote-comparison-motion.webp)

The MP4 is 1080 × 1350 at 30 fps. This inline preview is 540 × 675 at 15 fps and loops. All names and figures are fictional. This is a code-authored concept, not a client campaign or a claim of sales, CTR or other campaign results.

### Source and rebuild

The included `render_ui_motion_study_20261016.py` is the unchanged source used to render the full MP4. With an existing Python 3.11+ installation, Pillow, ffmpeg with the `libx264` encoder, and Windows Segoe UI fonts, run from this folder:

```powershell
python render_ui_motion_study_20261016.py --output-dir .
```

The explicit output folder makes the copied source portable. The renderer emits the MP4, preview frames and local checks; it does not download dependencies or contact a service. It overwrites its named outputs when deliberately rerun. Exact pixels and encoding depend on the installed font and tool versions.

`poster.png` is an actual frame extracted at 11.2 seconds. The animated WebP was derived from the full MP4. No fonts, ffmpeg executable, customer assets or third-party brand materials are included. Fonts are rendered into pixels only. This package does not add a new licence grant.
