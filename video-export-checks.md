# Checking a code-authored MP4: export, decode and playback

**Hx Works · Self-initiated creative-software study**

Recorded example: 16 October 2026. Documentation checked: 21 October 2026.

For a short video handover, I separate three questions: did the export match its intended settings, could the resulting file be decoded, and did the intended player actually finish it? Each check supplies different evidence. A successful encoding process answers only part of the handover question.

This example uses an existing, silent [12-second quote-comparison animation](hx-works-quote-comparison-motion-study.mp4). Three fictional supplier cards enter, a minimum-order filter narrows the choice, and the result holds for reading. The images were drawn with Python/Pillow and encoded with FFmpeg. This is a self-initiated study, with AI-assisted code production and writing.

## Start with the intended export

The [published renderer](render_ui_motion_study_20261016.py) declares 1080 × 1350 pixels, 30 frames per second and 12 seconds. Its encoding command supplies raw RGB frames, selects `libx264` and `yuv420p`, and disables audio with `-an`.

Those are production settings, rather than independent measurements of the finished stream. In particular, the recorded `fps` field comes from the renderer's constant. It is not an independently probed average frame rate. Keeping that distinction visible prevents a configuration value from being presented as an observed result.

Option placement also matters. FFmpeg's [video-options documentation](https://ffmpeg.org/ffmpeg.html#Video-Options) distinguishes input and output frame-rate options; output encoding with `-r` can duplicate or drop frames. The existing renderer instead declares its raw input rate with `-framerate`. Copying a frame-rate flag into a different position can change what a command does.

## Decode the finished file

The original check decoded the first video stream into FFmpeg's per-packet testing format:

```text
ffmpeg -nostdin -hide_banner -loglevel error -i hx-works-quote-comparison-motion-study.mp4 -map 0:v:0 -f framemd5 pipe:1
```

FFmpeg documents [`framemd5`](https://ffmpeg.org/ffmpeg-formats.html#framemd5) as a hash-based testing format. Here, counting its non-comment output records produced 360 decoded video frames. At the intended constant rate of 30 fps, 360 frames correspond to 12 seconds. A separate `ffmpeg -i` text inspection reported `00:00:12.00`, dimensions of 1080 × 1350, and no audio stream.

That agreement is useful evidence for this particular export. It does not measure browser frame delivery, visual pacing or whether a platform's later transcode will preserve the result. The stream hashes are test output; they are not a substitute for watching the file.

## Observe a real playback

The recorded local browser check started with a 12-second duration, the expected video dimensions, `readyState` 4 and no media error. After one normal click on “Play from start,” the player advanced and eventually reported time 12, `ended: true`, `paused: true` and no error.

That establishes completed playback in that browser session. It does not establish a zero dropped-frame count: the playback-quality counters were unavailable. Nor does it establish mobile compatibility, cross-browser coverage or successful playback after social-platform compression.

MDN's [`ended` event reference](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/ended_event) describes the end-of-media signal and notes that it does not fire during normal forward looping. A deliberately looping preview therefore needs different observations from a one-pass completion check.

## Keep previews separate from the deliverable

The repository's animated WebP is 540 × 675 at 15 fps and loops. It is a reduced preview, not the 1080 × 1350, 30 fps MP4. The poster is a still extracted at 11.2 seconds. Inspecting either asset cannot establish the MP4's full playback behaviour.

The final scene was designed to hold from 9.2 to 12 seconds. That gives it about 2.8 seconds on the production timeline; no reader study was conducted to establish that every viewer can finish reading it.

### Can I call the file “tested”?

Name the checks and environment: decoded-frame count, reported dimensions and duration, plus completed local browser playback. Keep unmeasured performance and device coverage explicit.

### Does this prove advertising performance?

No. The suppliers and figures are fictional, and there are no client acceptance, click-through or sales results.

### What should accompany a handover?

Identify the exact file, its editable source where applicable, the intended playback environment and the checks actually performed. Agree any additional device, audio or platform requirements before treating the handover as complete.
