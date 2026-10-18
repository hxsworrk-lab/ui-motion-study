"""Self-initiated edit study, not gameplay or a client commission. No network.
Run with bundled Python; needs installed Pillow and the existing ffmpeg executable.
"""
from pathlib import Path
import hashlib, json, math, subprocess, wave, shutil
from array import array
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FFMPEG = Path(shutil.which('ffmpeg') or 'ffmpeg')
W, H, FPS, SR = 540, 960, 24, 44100
FONT = r'C:\Windows\Fonts\segoeuib.ttf'
REGULAR = r'C:\Windows\Fonts\segoeui.ttf'
SPRITE_DIR = HERE / 'character-frames'
sprites = []
for path in sorted(SPRITE_DIR.glob('walk-*.png')):
    im = Image.open(path).convert('RGBA')
    # A common crop for all phases prevents frame-to-frame scale pumping.
    sprites.append(im)
box = (min(im.getbbox()[0] for im in sprites), min(im.getbbox()[1] for im in sprites),
       max(im.getbbox()[2] for im in sprites), max(im.getbbox()[3] for im in sprites))
sprites = [im.crop(box).resize((95, 180), Image.Resampling.LANCZOS) for im in sprites]

def text(draw, xy, value, size, color, anchor='mm', bold=True):
    draw.text(xy, value, font=ImageFont.truetype(FONT if bold else REGULAR, size),
              fill=color, anchor=anchor)

def scene(t):
    im = Image.new('RGB', (W, H), '#e7eddf')
    d = ImageDraw.Draw(im)
    d.rectangle((0, 255, W, 690), fill='#203e40')
    for y in range(300, 690, 70):
        d.line((0, y, W, y), fill='#315456', width=2)
    for x in range(-200, 750, 90):
        d.line((270, 240, x, 690), fill='#315456', width=2)
    d.rounded_rectangle((36, 300, 166, 353), 12, fill='#426765')
    # No text in the scene crop: punch-ins must not expose clipped lettering.
    d.line((62, 326, 139, 326), fill='#a1d2a7', width=4)
    # Source event: approach, door shuts, impact, parcel rebounds, awkward pause.
    x = 48 + min(t / 4.0, 1) * 300
    if t >= 4.3:
        x = 348 - min((t - 4.3) / .45, 1) * 53
    phase = int(t * 12) % 12 if t < 4.3 else 2
    door_closed = t >= 3.7
    d.rounded_rectangle((415, 330, 495, 625), 10, fill='#101e27')
    if door_closed:
        d.rectangle((422, 337, 488, 619), fill='#db754a')
        for yy in range(350, 615, 28):
            d.line((422, yy, 488, yy), fill='#9e4a35', width=3)
    else:
        d.rectangle((422, 337, 488, 619), fill='#9fc5af')
    d.ellipse((435, 293, 454, 312), fill='#efb565' if door_closed else '#a1d2a7')
    d.ellipse((x - 2, 583, x + 110, 607), fill='#153133')
    character = sprites[phase]
    if 4.3 <= t < 4.55:
        character = character.rotate(13, resample=Image.Resampling.BICUBIC, expand=True)
    im.paste(character, (round(x), 418), character)
    d = ImageDraw.Draw(im)
    parcel_x = x + 65
    parcel_y = 490
    if t >= 4.3:
        q = min((t - 4.3) / .8, 1)
        parcel_x = 415 - 150 * q
        parcel_y = 490 - 90 * math.sin(math.pi * q) + 82 * q
    d.rounded_rectangle((parcel_x, parcel_y, parcel_x + 28, parcel_y + 28), 5, fill='#e6bd6a')
    d.line((parcel_x + 14, parcel_y, parcel_x + 14, parcel_y + 28), fill='#795d39', width=3)
    if 4.3 <= t < 4.7:
        for angle in range(0, 360, 45):
            a = math.radians(angle)
            d.line((413 + math.cos(a)*27, 485 + math.sin(a)*27,
                    413 + math.cos(a)*42, 485 + math.sin(a)*42), fill='#f4c86d', width=4)
    text(d, (270, 755), 'FICTIONAL SCENE · CODE AUTHORED', 17, '#466259')
    text(d, (270, 787), 'Self-initiated study / Hx Works', 17, '#466259', bold=False)
    return im

# Explicit edit decision lists: output start/end, source start, playback speed.
EDLS = {
    'source': [(0, 8, 0, 1)],
    'chronological': [(0, 2.5, 0, 1.45), (2.5, 3.5, 3.625, .675),
                      (3.5, 4.5, 4.3, 0), (4.5, 7, 4.3, 1)],
    'cold-open': [(0, .75, 4.3, .4), (.75, 1.5, 4.3, 0),
                  (1.5, 3.5, 0, 1.85), (3.5, 4.5, 3.7, .6), (4.5, 7, 4.3, 1)]
}
DURATIONS = {'source': 8, 'chronological': 7, 'cold-open': 7}
CAPTIONS = {
    'chronological': [(0, 2.5, 'QUICK DELIVERY.'), (2.5, 3.5, 'DOOR: NOT TODAY.'),
                      (3.5, 4.5, 'PERFECT TIMING.'), (4.5, 7, 'DELIVERY: ATTEMPTED.')],
    'cold-open': [(0, 1.5, 'ONE JOB.'), (1.5, 3.5, '3 SECONDS EARLIER...'),
                  (3.5, 4.5, 'ALMOST THERE.'), (4.5, 7, 'THE PARCEL DISAGREED.')]
}
EVENTS = {'source': [(3.7, 300), (4.3, 120)],
          'chronological': [(2.61, 300), (3.5, 120), (4.5, 170)],
          'cold-open': [(0, 120), (1.5, 650), (3.5, 300), (4.5, 120)]}

def source_time(mode, t):
    for start, end, src, speed in EDLS[mode]:
        if start <= t < end:
            return src + (t - start) * speed
    return 7.99

def frame(mode, t):
    im = scene(source_time(mode, t))
    if mode != 'source':
        if (mode == 'chronological' and 3.5 <= t < 4.5) or (mode == 'cold-open' and t < 1.5):
            # Punch-in on the same source scene, no invented client footage.
            im.paste(im.crop((140, 320, 500, 650)).resize((W, 495), Image.Resampling.LANCZOS), (0, 220))
        d = ImageDraw.Draw(im)
        text(d, (48, 65), 'HX WORKS', 19, '#254d43', anchor='lm')
        text(d, (492, 65), 'EDIT STUDY / 01', 15, '#466259', anchor='rm')
        for start, end, caption in CAPTIONS[mode]:
            if start <= t < end:
                text(d, (270, 161), caption, 27, '#203e40')
        text(d, (270, 857), 'Same scene. Different pacing.', 20, '#254d43')
        text(d, (270, 889), 'Not actual gameplay or client work', 16, '#466259', bold=False)
    return im

def audio(mode, path):
    samples = array('h')
    for i in range(round(DURATIONS[mode] * SR)):
        t = i / SR
        value = 0
        for event, freq in EVENTS[mode]:
            dt = t - event
            if 0 <= dt < .16:
                value += .24 * math.exp(-dt * 24) * math.sin(2 * math.pi * (freq * dt + 160 * dt * dt))
        samples.append(round(max(-.9, min(.9, value)) * 32767))
    with wave.open(str(path), 'wb') as w:
        w.setparams((1, 2, SR, 0, 'NONE', 'not compressed'))
        w.writeframes(samples.tobytes())

def main():
    result = {'width': W, 'height': H, 'fps': FPS, 'source': 'character-frames (owned code-authored courier study)',
              'disclosure': 'One self-initiated fictional coded-scene study, two edits; not gameplay, client work or a full application.',
              'edl': EDLS, 'captions': CAPTIONS, 'audio_events_seconds': EVENTS, 'outputs': {}}
    contact = Image.new('RGB', (W * 3, H * 2), 'white')
    for row, mode in enumerate(['chronological', 'cold-open']):
        for col, t in enumerate([.5, 3.75, 5.5]):
            contact.paste(frame(mode, t), (col * W, row * H))
    contact.resize((810, 960)).save(HERE / 'contact-sheet.jpg', quality=90)
    for mode in EDLS:
        wav = HERE / f'{mode}.wav'
        audio(mode, wav)
        output = HERE / f'hx-fictional-scene-{mode}.mp4'
        args = [str(FFMPEG), '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                '-s', f'{W}x{H}', '-r', str(FPS), '-i', 'pipe:0', '-i', str(wav),
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '21', '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', '-shortest', str(output)]
        proc = subprocess.Popen(args, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        for i in range(DURATIONS[mode] * FPS):
            proc.stdin.write(frame(mode, i / FPS).tobytes())
        proc.stdin.close()
        error = proc.stderr.read().decode(errors='replace')
        if proc.wait() != 0:
            raise RuntimeError(error)
        wav.unlink()  # Task-created intermediate only; reproducible from retained synthesis.
        result['outputs'][mode] = {'file': output.name, 'bytes': output.stat().st_size,
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'duration': DURATIONS[mode],
            'frames': DURATIONS[mode] * FPS}
        print(mode, result['outputs'][mode], flush=True)
    (HERE / 'render-result.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')

if __name__ == '__main__':
    main()
