"""Offline, code-authored fictional quote-comparison motion study.

Writes only the explicitly selected output directory; no network or shell execution.
Segoe UI is used for local raster rendering only, never copied or embedded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

from PIL import Image, ImageDraw, ImageFont, ImageFilter, __version__ as PILLOW_VERSION

WIDTH, HEIGHT, FPS, SECONDS = 1080, 1350, 30, 12
BG = "#111C29"
CREAM = "#F4F0E6"
MUTED = "#A5B4C5"
LIME = "#D6F36B"
INK = "#172331"
DATA = [
    {"supplier": "North", "unit_price_usd": "0.82", "moq": 1000, "lead_days": 28},
    {"supplier": "Vale", "unit_price_usd": "1.06", "moq": 500, "lead_days": 18},
    {"supplier": "Ridge", "unit_price_usd": "1.24", "moq": 250, "lead_days": 12},
]
FONT_DIR = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
FONTS: dict[tuple[int, bool], ImageFont.FreeTypeFont] = {}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    key = (size, bold)
    if key not in FONTS:
        path = FONT_DIR / ("seguisb.ttf" if bold else "segoeui.ttf")
        if not path.is_file():
            raise RuntimeError("Required local Segoe UI font is unavailable; no substitute installed.")
        FONTS[key] = ImageFont.truetype(str(path), size)
    return FONTS[key]


def text(draw: ImageDraw.ImageDraw, xy: tuple[float, float], value: str,
         size: int, color: str = CREAM, bold: bool = False) -> None:
    draw.text((round(xy[0]), round(xy[1])), value, font=font(size, bold), fill=color)


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def ease(value: float) -> float:
    value = clamp(value)
    return 1 - (1 - value) ** 3


def composite(base: Image.Image, layer: Image.Image, x: float, y: float,
              opacity: float = 1.0) -> None:
    if opacity <= 0:
        return
    if opacity < 0.999:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(lambda a: round(a * opacity)))
    base.alpha_composite(layer, (round(x), round(y)))


def card(row: dict) -> Image.Image:
    layer = Image.new("RGBA", (968, 194), (0, 0, 0, 0))
    shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((18, 22, 950, 177), radius=20,
                                            fill=(0, 0, 0, 75))
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(9)))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((10, 10, 958, 164), radius=20, fill=CREAM)
    text(d, (36, 31), "SAMPLE SUPPLIER", 18, "#65727D")
    text(d, (36, 69), row["supplier"], 42, INK, True)
    text(d, (373, 63), "$" + row["unit_price_usd"], 47, INK, True)
    text(d, (608, 73), f'{row["moq"]:,}', 34, INK, True)
    text(d, (779, 73), f'{row["lead_days"]} days', 32, INK, True)
    return layer


CARDS: list[Image.Image] = []


def frame(t: float) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), BG)
    d = ImageDraw.Draw(image)
    # Persistent attribution is present from the first frame to the last.
    text(d, (72, 52), "Hx Works", 30, CREAM, True)
    text(d, (814, 58), "STUDY 01", 22, MUTED)
    d.line((72, 108, 1008, 108), fill="#354353", width=1)
    intro = ease(t / 1.1)
    headline = Image.new("RGBA", (970, 242), (0, 0, 0, 0))
    hd = ImageDraw.Draw(headline)
    text(hd, (0, 0), "Compare quotes.", 70, CREAM, True)
    text(hd, (0, 82), "See the trade-offs.", 70, CREAM, True)
    text(hd, (2, 184), "Cost, quantity and timing — in one view.", 28, MUTED)
    composite(image, headline, 72, 149 + 22 * (1 - intro), 0.25 + 0.75 * intro)
    d = ImageDraw.Draw(image)

    active = ease((t - 4.3) / 0.8)
    d.rounded_rectangle((72, 415, 600, 487), radius=36, fill="#233246")
    if active > 0:
        active_pill = Image.new("RGBA", (528, 72), (0, 0, 0, 0))
        ImageDraw.Draw(active_pill).rounded_rectangle((0, 0, 527, 71), radius=36, fill=LIME)
        composite(image, active_pill, 72, 415, active)
    d = ImageDraw.Draw(image)
    if active < 0.5:
        text(d, (104, 432), "MOQ: any quantity", 28, CREAM, True)
    else:
        text(d, (104, 432), "MOQ: at most 500", 28, INK, True)
    d.ellipse((536, 438, 562, 464), outline=INK if active >= 0.5 else MUTED, width=2)
    if active >= 0.5:
        d.line((542, 450, 547, 456, 557, 445), fill=INK, width=3)
    counter = "2 quotes match" if active >= 0.5 else "3 sample quotes"
    text(d, (772, 436), counter, 25, LIME if active >= 0.5 else MUTED)

    for x, label in ((104, "SUPPLIER"), (441, "USD / UNIT"),
                     (676, "MOQ"), (847, "LEAD TIME")):
        text(d, (x, 531), label, 18, MUTED, True)
    for i, layer in enumerate(CARDS):
        arrival = ease((t - (1.05 + i * 0.55)) / 0.85)
        if arrival <= 0:
            continue
        opacity = arrival * (1 - 0.70 * active if i == 0 else 1)
        focus = ease((t - 6.1) / 0.8) if i == 1 else 0
        x, y = 62 + 62 * (1 - arrival), 568 + i * 177 - 3 * focus
        composite(image, layer, x, y, opacity)
        if i == 1 and focus > 0:
            border = Image.new("RGBA", image.size, (0, 0, 0, 0))
            bd = ImageDraw.Draw(border)
            bd.rounded_rectangle((72, round(y + 10), 1020, round(y + 164)),
                                 radius=20, outline=LIME, width=4)
            composite(image, border, 0, 0, focus)
    summary = ease((t - 8.3) / 0.9)
    ending = Image.new("RGBA", (950, 110), (0, 0, 0, 0))
    ed = ImageDraw.Draw(ending)
    text(ed, (0, 0), "Price is one part of the decision.", 34, CREAM, True)
    text(ed, (0, 54), "Compare quantity and lead time alongside it.", 26, MUTED)
    composite(image, ending, 72, 1139 + 12 * (1 - summary), summary)
    d = ImageDraw.Draw(image)
    d.line((72, 1254, 1008, 1254), fill="#354353", width=1)
    text(d, (72, 1280), "Self-initiated concept · Fictional data", 25, CREAM)
    return image.convert("RGB")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, shell=False, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).resolve().parents[1] /
                        "preparation/assets/ui-motion-study-20261016")
    parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg"))
    args = parser.parse_args()
    if not args.ffmpeg or not Path(args.ffmpeg).is_file():
        raise RuntimeError("Existing ffmpeg executable required; nothing is downloaded.")
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    video = out / "hx-works-quote-comparison-motion-study.mp4"
    CARDS.extend(card(row) for row in DATA)
    started = time.monotonic()
    command = [args.ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
               "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size", f"{WIDTH}x{HEIGHT}",
               "-framerate", str(FPS), "-i", "pipe:0", "-an", "-c:v", "libx264",
               "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
               "-metadata", "title=Hx Works - Quote comparison motion study",
               "-metadata", "comment=Self-initiated concept; fictional data; silent; code-authored",
               str(video)]
    process = subprocess.Popen(command, shell=False, stdin=subprocess.PIPE,
                               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        assert process.stdin is not None
        for n in range(FPS * SECONDS):
            process.stdin.write(frame(n / FPS).tobytes())
        process.stdin.close()
        assert process.stderr is not None
        error = process.stderr.read().decode("utf-8", errors="replace")
        result = process.wait(timeout=90)
        if result:
            raise RuntimeError("FFmpeg encoding failed: " + error[-600:])
    except BaseException:
        if process.poll() is None:
            process.kill()
            process.wait()
        raise
    stills = []
    for at in (0.8, 3.4, 7.4, 11.2):
        path = out / ("frame-" + str(at).replace(".", "p") + "s.png")
        run([args.ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
             "-ss", str(at), "-i", str(video), "-frames:v", "1", str(path)])
        stills.append({"requested_seconds": at, "file": path.name,
                       "sha256": sha(path), "bytes": path.stat().st_size})
    sheet = Image.new("RGB", (936, 1244), BG)
    sd = ImageDraw.Draw(sheet)
    for index, still in enumerate(stills):
        x, y = 24 + (index % 2) * 456, 24 + (index // 2) * 610
        text(sd, (x, y), f'{still["requested_seconds"]:.1f} seconds', 24, CREAM, True)
        with Image.open(out / still["file"]) as source:
            thumb = source.convert("RGB").resize((432, 540), Image.Resampling.LANCZOS)
            sheet.paste(thumb, (x, y + 42))
    sheet_path = out / "contact-sheet.jpg"
    sheet.save(sheet_path, quality=94, subsampling=0)
    decoded = run([args.ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error",
                   "-i", str(video), "-map", "0:v:0", "-f", "framemd5", "pipe:1"])
    md5_lines = decoded.stdout.decode("ascii").splitlines()
    frame_count = sum(1 for line in md5_lines if line and not line.startswith("#"))
    version = run([args.ffmpeg, "-nostdin", "-version"]).stdout.decode("utf-8", errors="replace")
    video_info = subprocess.run([args.ffmpeg, "-nostdin", "-hide_banner", "-i", str(video)],
                                shell=False, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE).stderr.decode("utf-8", errors="replace")
    duration_match = re.search(r"Duration: (\d+:\d+:\d+\.\d+)", video_info)
    dimensions_match = re.search(r"Video:.*?\b(\d{3,5})x(\d{3,5})\b", video_info)
    receipt = {
        "authorship": "Code-authored self-initiated UI motion concept; no customer assets or real supplier data.",
        "source_file": Path(__file__).name, "source_sha256": sha(Path(__file__)),
        "python": sys.version.split()[0], "pillow": PILLOW_VERSION,
        "ffmpeg_version": version.splitlines()[0],
        "ffmpeg_configuration": next((line for line in version.splitlines() if line.startswith("configuration:")), ""),
        "font_rendering_only": ["Segoe UI", "Segoe UI Semibold"], "font_files_distributed": False,
        "video": {"file": video.name, "sha256": sha(video), "bytes": video.stat().st_size,
                  "decoded_frame_count": frame_count, "fps": FPS,
                  "observed_duration": duration_match.group(1) if duration_match else None,
                  "observed_dimensions": dimensions_match.groups() if dimensions_match else None,
                  "audio_stream_present": "Audio:" in video_info},
        "stills": stills, "contact_sheet": {"file": sheet_path.name, "sha256": sha(sheet_path)},
        "timeline_seconds": {"headline": [0, 1.1], "three_cards": [1.05, 3.0],
                             "moq_filter": [4.3, 5.1], "vale_focus": [6.1, 6.9],
                             "summary": [8.3, 9.2], "static_end_hold": [9.2, 12]},
        "fictional_quotes": DATA, "elapsed_render_and_validation_seconds": round(time.monotonic() - started, 2),
        "boundaries": ["Not Jitter, After Effects or Figma motion experience.",
                       "Not a client project, paid case or buyer-approved visual style.",
                       "No CTR, sales, time-saving or commercial-outcome claim.",
                       "No binary or font distribution. Resource monetary costs unquantified.",
                       "Extracted frames and decode checks do not replace full playback or buyer acceptance."],
    }
    (out / "render-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if frame_count != FPS * SECONDS or receipt["video"]["audio_stream_present"]:
        raise RuntimeError("Decoded frame count or silent-stream check failed; see receipt.")
    print(json.dumps({"file": video.name, "sha256": sha(video), "frames": frame_count,
                      "duration": receipt["video"]["observed_duration"],
                      "dimensions": receipt["video"]["observed_dimensions"],
                      "elapsed_seconds": receipt["elapsed_render_and_validation_seconds"]}))


if __name__ == "__main__":
    main()
