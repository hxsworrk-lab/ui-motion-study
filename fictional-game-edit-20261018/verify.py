"""Independently decode the final MP4s; no browser or auditory acceptance implied."""
from pathlib import Path
import hashlib, json, math, subprocess
from array import array
from PIL import Image
from build import HERE, FFMPEG, W, H, FPS, EVENTS

result = {'scope': 'Final encoded video/audio decoding, sampled visual frames, frame count and synthesized event timing. No subjective auditory or buyer-style acceptance.', 'outputs': {}}
sheet = Image.new('RGB', (810, 960), 'white')
for mode in ['source', 'chronological', 'cold-open']:
    path = HERE / f'hx-fictional-scene-{mode}.mp4'
    proc = subprocess.Popen([str(FFMPEG), '-v', 'error', '-i', str(path), '-an',
        '-f', 'rawvideo', '-pix_fmt', 'rgb24', 'pipe:1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    count, wanted = 0, [12, 90, 132]
    hashes = []
    while True:
        raw = proc.stdout.read(W * H * 3)
        if not raw:
            break
        if len(raw) != W * H * 3:
            raise RuntimeError('Partial decoded video frame')
        if count in wanted:
            hashes.append(hashlib.sha256(raw).hexdigest())
            if mode != 'source':
                row = 0 if mode == 'chronological' else 1
                sheet.paste(Image.frombytes('RGB', (W,H),raw).resize((270,480)), (wanted.index(count)*270,row*480))
        count += 1
    error = proc.stderr.read().decode(errors='replace')
    if proc.wait() != 0 or error:
        raise RuntimeError(error)
    pcm = subprocess.run([str(FFMPEG), '-v', 'error', '-i', str(path), '-vn',
        '-f', 's16le', '-ac', '1', '-ar', '44100', 'pipe:1'], capture_output=True, check=True)
    samples = array('h', pcm.stdout)
    peak = max(abs(x) for x in samples) / 32768
    bins = []
    for start in range(0, len(samples), 441):
        block = samples[start:start+441]
        rms = math.sqrt(sum(x*x for x in block) / len(block)) / 32768
        if rms > .01:
            bins.append(round(start/44100, 2))
    windows = {str(t): any(abs(x-t) <= .04 for x in bins) for t, freq in EVENTS[mode]}
    expected = (8 if mode == 'source' else 7) * FPS
    if count != expected or len(set(hashes)) < 2 or not all(windows.values()) or peak >= .99:
        raise RuntimeError(f'Encoding check failed: {mode}')
    result['outputs'][mode] = {'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'decoded_frames': count, 'video_seconds_at_24fps': count/FPS,
        'sampled_decoded_frame_sha256': hashes, 'audio_decoded_seconds': len(samples)/44100,
        'audio_absolute_peak': peak, 'event_energy_within_40ms': windows,
        'decode_exit': 0}
sheet.save(HERE / 'contact-sheet.jpg', quality=90)
result['visual_sheet'] = 'contact-sheet.jpg (sampled from final encoded MP4s, not source drawings)'
(HERE / 'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
