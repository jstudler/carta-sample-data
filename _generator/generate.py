"""Generate royalty-free abstract media files for sample-data.

All media is procedurally generated — no external assets — so it is
original work and safe for open-source use.
"""

import math
import os
import struct
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent.parent  # sample-data/

RNG = np.random.default_rng(42)

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def save_picture(img: Image.Image, stem: str) -> None:
    """Save a PIL image as .jpg."""
    rgb = img.convert("RGB")
    rgb.save(OUT / f"{stem}.jpg", quality=85)


def write_wav(path: str, samples: np.ndarray, sr: int = 44100) -> None:
    """Write mono float32 numpy array to 16-bit WAV."""
    pcm = np.clip(samples, -1, 1)
    pcm = (pcm * 32767).astype(np.int16)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


def convert_audio(wav_path: str, stem: str) -> None:
    """Convert WAV to .mp3."""
    subprocess.run(
        ["ffmpeg", "-y", "-i", wav_path,
         "-b:a", "128k", str(OUT / f"{stem}.mp3")],
        check=True, capture_output=True,
    )


def make_video(frames_dir: str, audio_wav: str, stem: str,
               fps: int = 24) -> None:
    """Combine image sequence + audio into .mp4."""
    subprocess.run(
        ["ffmpeg", "-y",
         "-framerate", str(fps),
         "-i", f"{frames_dir}/frame_%04d.png",
         "-i", audio_wav,
         "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "128k",
         "-shortest",
         str(OUT / f"{stem}.mp4")],
        check=True, capture_output=True,
    )


# ---------------------------------------------------------------------------
# image generators — each produces a distinct abstract style
# ---------------------------------------------------------------------------

def gen_gradient_circles(w: int = 1200, h: int = 900, seed: int = 0) -> Image.Image:
    """Overlapping translucent gradient circles."""
    rng = np.random.default_rng(seed)
    img = Image.new("RGBA", (w, h), (20, 18, 30, 255))
    draw = ImageDraw.Draw(img)
    palettes = [
        [(80, 140, 220), (200, 60, 100), (60, 200, 160)],
        [(220, 180, 60), (60, 80, 180), (180, 60, 180)],
    ]
    colors = palettes[seed % len(palettes)]
    for _ in range(15):
        cx, cy = rng.integers(0, w), rng.integers(0, h)
        r = rng.integers(80, 300)
        color = colors[rng.integers(0, len(colors))]
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([cx - r, cy - r, cx + r, cy + r],
                   fill=(*color, 60))
        img = Image.alpha_composite(img, overlay)
    return img.filter(ImageFilter.GaussianBlur(12))


def gen_noise_field(w: int = 1200, h: int = 900, seed: int = 0) -> Image.Image:
    """Colored noise field with smooth gradients."""
    rng = np.random.default_rng(seed)
    # generate low-res noise and upscale for smooth look
    sw, sh = w // 8, h // 8
    r = rng.integers(0, 255, (sh, sw), dtype=np.uint8)
    g = rng.integers(0, 255, (sh, sw), dtype=np.uint8)
    b = rng.integers(0, 255, (sh, sw), dtype=np.uint8)
    ri = Image.fromarray(r, "L").resize((w, h), Image.BICUBIC)
    gi = Image.fromarray(g, "L").resize((w, h), Image.BICUBIC)
    bi = Image.fromarray(b, "L").resize((w, h), Image.BICUBIC)
    return Image.merge("RGB", (ri, gi, bi)).filter(ImageFilter.GaussianBlur(6))


def gen_concentric_rings(w: int = 1200, h: int = 900, seed: int = 0) -> Image.Image:
    """Concentric rings with color shifts — evokes sensor data."""
    rng = np.random.default_rng(seed)
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    cx, cy = w // 2 + rng.integers(-100, 100), h // 2 + rng.integers(-100, 100)
    yy, xx = np.mgrid[:h, :w]
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    hue_shift = rng.uniform(0, 2 * math.pi)
    for c in range(3):
        freq = 0.015 + c * 0.005
        phase = hue_shift + c * 2.094  # 120° apart
        arr[:, :, c] = np.clip(
            128 + 100 * np.sin(dist * freq + phase), 0, 255
        ).astype(np.uint8)
    img = Image.fromarray(arr)
    return img.filter(ImageFilter.GaussianBlur(2))


def gen_light_streaks(w: int = 1200, h: int = 900, seed: int = 0) -> Image.Image:
    """Diagonal light streaks — evokes projection mapping."""
    rng = np.random.default_rng(seed)
    img = Image.new("RGB", (w, h), (10, 10, 15))
    draw = ImageDraw.Draw(img)
    for _ in range(30):
        x0 = rng.integers(-200, w)
        thickness = rng.integers(2, 40)
        brightness = rng.integers(40, 200)
        color_choice = rng.integers(0, 3)
        if color_choice == 0:
            color = (brightness, brightness // 2, brightness // 4)
        elif color_choice == 1:
            color = (brightness // 4, brightness // 2, brightness)
        else:
            color = (brightness, brightness, brightness)
        draw.line([(x0, 0), (x0 + h // 2, h)], fill=color, width=thickness)
    return img.filter(ImageFilter.GaussianBlur(8))


def gen_dot_grid(w: int = 1200, h: int = 900, seed: int = 0) -> Image.Image:
    """Grid of dots with varying sizes — evokes LED array."""
    rng = np.random.default_rng(seed)
    img = Image.new("RGB", (w, h), (15, 12, 20))
    draw = ImageDraw.Draw(img)
    spacing = 40
    for y in range(spacing // 2, h, spacing):
        for x in range(spacing // 2, w, spacing):
            r = rng.integers(2, 14)
            bright = rng.integers(80, 255)
            hue = rng.uniform(0, 1)
            cr = int(bright * (0.5 + 0.5 * math.sin(hue * 6.28)))
            cg = int(bright * (0.5 + 0.5 * math.sin(hue * 6.28 + 2.09)))
            cb = int(bright * (0.5 + 0.5 * math.sin(hue * 6.28 + 4.19)))
            draw.ellipse([x - r, y - r, x + r, y + r], fill=(cr, cg, cb))
    return img.filter(ImageFilter.GaussianBlur(3))


# ---------------------------------------------------------------------------
# audio generators
# ---------------------------------------------------------------------------

def gen_ambient_drone(duration: float = 8.0, seed: int = 0) -> np.ndarray:
    """Layered sine waves with slow modulation — ambient gallery tone."""
    rng = np.random.default_rng(seed)
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    signal = np.zeros_like(t)
    freqs = [110, 165, 220, 330, 440]
    for f in freqs:
        amp = rng.uniform(0.05, 0.2)
        mod = 0.5 + 0.5 * np.sin(2 * math.pi * rng.uniform(0.05, 0.3) * t)
        signal += amp * mod * np.sin(2 * math.pi * f * t)
    # fade in/out
    fade = int(sr * 0.5)
    signal[:fade] *= np.linspace(0, 1, fade)
    signal[-fade:] *= np.linspace(1, 0, fade)
    signal /= np.max(np.abs(signal)) + 1e-6
    return signal * 0.7


def gen_pulse_sequence(duration: float = 6.0, seed: int = 0) -> np.ndarray:
    """Rhythmic pulses with reverb-like decay — evokes sensor calibration."""
    rng = np.random.default_rng(seed)
    sr = 44100
    n = int(sr * duration)
    signal = np.zeros(n)
    pulse_interval = sr  # one pulse per second
    freq = 440 + rng.integers(-100, 100)
    for start in range(0, n, pulse_interval):
        decay_len = min(int(sr * 0.4), n - start)
        t = np.arange(decay_len) / sr
        pulse = np.sin(2 * math.pi * freq * t) * np.exp(-t * 8)
        signal[start:start + decay_len] += pulse
        freq *= rng.uniform(0.95, 1.05)
    # fade in/out
    fade = int(sr * 0.3)
    signal[:fade] *= np.linspace(0, 1, fade)
    signal[-fade:] *= np.linspace(1, 0, fade)
    signal /= np.max(np.abs(signal)) + 1e-6
    return signal * 0.7


# ---------------------------------------------------------------------------
# video frame generators
# ---------------------------------------------------------------------------

def gen_video_frames_glow(tmpdir: str, n_frames: int = 288,
                          w: int = 640, h: int = 480) -> None:
    """12-second animation of a pulsing glow — evokes breathing sculpture."""
    for i in range(n_frames):
        t_norm = i / n_frames
        # slow breathing cycle (~3 breaths over 12 seconds)
        phase = 2 * math.pi * 3 * t_norm
        brightness = int(60 + 140 * (0.5 + 0.5 * math.sin(phase)))
        # glow center drifts slowly
        cx = w // 2 + int(60 * math.sin(2 * math.pi * t_norm * 0.7))
        cy = h // 2 + int(40 * math.cos(2 * math.pi * t_norm * 0.5))
        arr = np.zeros((h, w, 3), dtype=np.uint8)
        yy, xx = np.mgrid[:h, :w]
        dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        max_dist = math.sqrt((w // 2) ** 2 + (h // 2) ** 2)
        glow = np.clip(brightness * (1 - dist / max_dist), 0, 255).astype(np.uint8)
        # tint: warm amber pulsing to cool blue, with slow hue rotation
        r_mult = 0.5 + 0.5 * math.sin(phase)
        b_mult = 0.5 + 0.5 * math.sin(phase + math.pi)
        g_mod = 0.3 + 0.15 * math.sin(2 * math.pi * t_norm * 1.3)
        arr[:, :, 0] = np.clip(glow * (0.3 + 0.7 * r_mult), 0, 255).astype(np.uint8)
        arr[:, :, 1] = np.clip(glow * g_mod, 0, 255).astype(np.uint8)
        arr[:, :, 2] = np.clip(glow * (0.3 + 0.7 * b_mult), 0, 255).astype(np.uint8)
        Image.fromarray(arr).save(f"{tmpdir}/frame_{i:04d}.png")


def gen_video_frames_sweep(tmpdir: str, n_frames: int = 288,
                           w: int = 640, h: int = 480) -> None:
    """12-second animation of light sweeping back and forth across a surface."""
    xx = np.arange(w, dtype=np.float64)
    yy = np.arange(h, dtype=np.float64)
    for i in range(n_frames):
        t_norm = i / n_frames
        arr = np.zeros((h, w, 3), dtype=np.uint8)
        # beam sweeps back and forth (2 full sweeps in 12 seconds)
        sweep = math.sin(2 * math.pi * 2 * t_norm)
        beam_x = w // 2 + int(sweep * w * 0.4)
        beam_width = 50 + 30 * math.sin(2 * math.pi * t_norm * 3)
        intensity = np.exp(-0.5 * ((xx - beam_x) / beam_width) ** 2)
        # color shifts as beam moves
        r_weight = 0.5 + 0.5 * math.sin(2 * math.pi * t_norm * 1.5)
        b_weight = 0.5 + 0.5 * math.cos(2 * math.pi * t_norm * 1.5)
        for y_idx in range(h):
            y_var = 0.6 + 0.4 * math.sin(2 * math.pi * (yy[y_idx] / h + t_norm * 0.5))
            row = (intensity * 220 * y_var).astype(np.uint8)
            arr[y_idx, :, 0] = np.clip(row * (0.4 + 0.6 * r_weight), 0, 255).astype(np.uint8)
            arr[y_idx, :, 1] = np.clip(row * 0.5, 0, 255).astype(np.uint8)
            arr[y_idx, :, 2] = np.clip(row * (0.4 + 0.6 * b_weight), 0, 255).astype(np.uint8)
        Image.fromarray(arr).save(f"{tmpdir}/frame_{i:04d}.png")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Generating 10 pictures...")

    # -- Pictures --
    # sensor-integration cards
    img = gen_concentric_rings(seed=1)
    save_picture(img, "sensor-integration/sensor-integration_2025-04-15--140000")
    print("  1/10 sensor board abstract")

    img = gen_noise_field(seed=2)
    save_picture(img, "sensor-integration/sensor-integration_2025-05-20--110000")
    print("  2/10 signal processing abstract")

    img = gen_dot_grid(seed=3)
    save_picture(img, "sensor-integration/sensor-integration_2025-06-12--150000")
    print("  3/10 calibration grid")

    # projection-mapping cards
    img = gen_gradient_circles(seed=4)
    save_picture(img, "projection-mapping/projection-mapping_2025-05-10--160000")
    print("  4/10 resin glow")

    img = gen_dot_grid(seed=5)
    save_picture(img, "projection-mapping/projection-mapping_2025-05-10--160500")
    print("  5/10 LED array detail")

    img = gen_light_streaks(seed=6)
    save_picture(img, "projection-mapping/projection-mapping_2025-06-22--140000")
    print("  6/10 projection streaks")

    img = gen_gradient_circles(seed=7)
    save_picture(img, "projection-mapping/projection-mapping_2025-08-20--190000")
    print("  7/10 exhibition view")

    # audience-interaction cards
    img = gen_light_streaks(seed=8)
    save_picture(img, "audience-interaction/audience-interaction_2025-07-20--150000")
    print("  8/10 alcove installation")

    img = gen_concentric_rings(seed=9)
    save_picture(img, "audience-interaction/audience-interaction_2025-07-20--150500")
    print("  9/10 interaction rings")

    img = gen_noise_field(seed=10)
    save_picture(img, "audience-interaction/audience-interaction_2025-08-10--140000")
    print("  10/10 ambient field")

    # -- Audio --
    print("Generating 2 audio files...")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav1 = f.name
    samples = gen_ambient_drone(duration=8.0, seed=1)
    write_wav(wav1, samples)
    convert_audio(wav1, "sensor-integration/sensor-integration_2025-06-12--calibration-tone")
    os.unlink(wav1)
    print("  1/2 calibration tone")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav2 = f.name
    samples = gen_pulse_sequence(duration=6.0, seed=2)
    write_wav(wav2, samples)
    convert_audio(wav2, "audience-interaction/audience-interaction_2025-08-10--gallery-ambient")
    os.unlink(wav2)
    print("  2/2 gallery ambient")

    # -- Videos --
    print("Generating 2 videos (this takes a moment)...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Video 1: pulsing glow (12 seconds)
        gen_video_frames_glow(tmpdir, n_frames=288)
        wav_path = os.path.join(tmpdir, "audio.wav")
        samples = gen_ambient_drone(duration=12.0, seed=10)
        write_wav(wav_path, samples)
        make_video(tmpdir, wav_path, "projection-mapping/projection-mapping_2025-06-22--141500", fps=24)
        print("  1/2 glow pulse video")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Video 2: light sweep (12 seconds)
        gen_video_frames_sweep(tmpdir, n_frames=288)
        wav_path = os.path.join(tmpdir, "audio.wav")
        samples = gen_pulse_sequence(duration=12.0, seed=11)
        write_wav(wav_path, samples)
        make_video(tmpdir, wav_path, "audience-interaction/audience-interaction_2025-07-20--160000", fps=24)
        print("  2/2 light sweep video")

    print("Done! All media files written to", OUT)


if __name__ == "__main__":
    main()
