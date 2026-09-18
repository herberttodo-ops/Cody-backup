#!/usr/bin/env python3
"""
Multi-track crossfaded music bed builder for long-form narration video.

Solves: a 26-minute video backed by 2 short tracks audibly loops, and tracks
sourced from different places arrive at different loudness so the bed jumps in
volume at every seam.

Behaviour:
  - Auto-discovers every audio file in MUSIC_DIR. Drop files in, no config.
  - Loudness-normalizes each track to a common LUFS target FIRST (cached), so a
    bed built from mixed-source tracks has no level jumps.
  - Crossfades (acrossfade) between segments instead of hard cuts.
  - Never places the same track back-to-back when 2+ tracks are available.
  - Deterministic: same seed -> same running order, so rebuilds are identical.
  - Refuses to run on an empty music dir rather than generating synthetic noise.

Validated 2026-09-17:
  - 23.5-min bed from 2 tracks: -19.8 LUFS integrated, 0 dropouts,
    per-minute RMS within +/-1.5 dB.
  - 10-min bed from 5 tracks whose inputs spanned -15.2 to -50.5 dB:
    -20.0 LUFS integrated, spread collapsed to +/-2.7 dB, no adjacent repeats.

Adapt MUSIC_DIR / TARGET_LUFS for the project.

CLI:
    python3 music_bed_builder.py <duration_sec> <out_path> [seed] [--xfade N]

Import:
    from music_bed_builder import build_bed
    build_bed(duration, out_path, seed="story_name")
"""
import random
import subprocess
import sys
from pathlib import Path

MUSIC_DIR = Path.home() / "music"          # <-- point at the project's music dir
CACHE_DIR = MUSIC_DIR / ".normalized"
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac", ".opus"}

TARGET_LUFS = -20.0   # bed level BEFORE ducking; narration sits on top
XFADE_SEC = 6.0
HEAD_FADE = 3.0
TAIL_FADE = 6.0
SR = 48000


class MusicError(RuntimeError):
    pass


def _run(cmd, what):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise MusicError(f"{what} failed:\n{r.stderr[-1200:]}")
    return r


def _duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True)
    try:
        return float(r.stdout.strip().split("\n")[0])
    except (ValueError, IndexError):
        raise MusicError(f"cannot probe duration: {path}")


def discover_tracks():
    """Every audio file directly in MUSIC_DIR. Cache/subdirs ignored."""
    if not MUSIC_DIR.exists():
        raise MusicError(f"music dir missing: {MUSIC_DIR}")
    tracks = sorted(p for p in MUSIC_DIR.iterdir()
                    if p.is_file() and p.suffix.lower() in AUDIO_EXT)
    if not tracks:
        raise MusicError(
            f"no music tracks in {MUSIC_DIR}. Refusing to substitute generated noise.")
    return tracks


def normalize(track):
    """Two-pass loudnorm to TARGET_LUFS. Cached by name+mtime+size."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    st = track.stat()
    out = CACHE_DIR / f"{track.stem}_{int(st.st_mtime)}_{st.st_size}.wav"
    if out.exists():
        return out

    # pass 1: measure
    r = subprocess.run(
        ["ffmpeg", "-i", str(track), "-af",
         f"loudnorm=I={TARGET_LUFS}:TP=-2.0:LRA=11:print_format=json",
         "-f", "null", "-"],
        capture_output=True, text=True)
    measured = {}
    for key in ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset"):
        for line in r.stderr.splitlines():
            if f'"{key}"' in line:
                try:
                    measured[key] = float(line.split(":")[1].strip().strip(',"'))
                except ValueError:
                    pass
                break

    af = f"loudnorm=I={TARGET_LUFS}:TP=-2.0:LRA=11"
    if len(measured) == 5:
        af += (f":measured_I={measured['input_i']}"
               f":measured_TP={measured['input_tp']}"
               f":measured_LRA={measured['input_lra']}"
               f":measured_thresh={measured['input_thresh']}"
               f":offset={measured['target_offset']}:linear=true")

    _run(["ffmpeg", "-y", "-i", str(track), "-af", af,
          "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(out)],
         f"normalize {track.name}")
    return out


def plan_sequence(tracks, duration, seed, xfade):
    """Running order covering `duration`. No adjacent repeats when 2+ tracks."""
    rng = random.Random(seed)
    durs = {t: _duration(t) for t in tracks}
    order, total, last = [], 0.0, None
    while total < duration + xfade:
        pool = [t for t in tracks if t != last] or list(tracks)
        pick = rng.choice(pool)
        order.append(pick)
        # each added segment contributes its length minus one crossfade overlap
        total += durs[pick] - (xfade if len(order) > 1 else 0)
        last = pick
        if len(order) > 400:
            raise MusicError("sequence planner runaway; tracks too short")
    return order


def build_bed(duration, out_path, seed="bed", xfade=XFADE_SEC, verbose=True):
    tracks = discover_tracks()
    if verbose:
        print(f"  music: {len(tracks)} track(s): {', '.join(t.stem for t in tracks)}")

    norm = {t: normalize(t) for t in tracks}
    if verbose:
        print(f"  music: normalized to {TARGET_LUFS} LUFS (cached)")

    # crossfade needs each segment longer than twice the fade
    usable = [t for t in tracks if _duration(norm[t]) > xfade * 2]
    if not usable:
        xfade = max(1.0, min(_duration(norm[t]) for t in tracks) / 3)
        usable = tracks
        if verbose:
            print(f"  music: tracks short, reducing crossfade to {xfade:.1f}s")

    order = plan_sequence(usable, duration, seed, xfade)
    if verbose:
        print(f"  music: {len(order)} segment(s), {xfade:.0f}s crossfades")

    if len(order) == 1:
        src = norm[order[0]]
        _run(["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(src),
              "-t", f"{duration:.3f}",
              "-af", f"afade=t=in:st=0:d={HEAD_FADE},"
                     f"afade=t=out:st={max(0, duration-TAIL_FADE):.3f}:d={TAIL_FADE}",
              "-ar", str(SR), "-ac", "2", "-c:a", "aac", "-b:a", "192k",
              str(out_path)], "single-track bed")
    else:
        inputs, filt, label = [], [], None
        for t in order:
            inputs += ["-i", str(norm[t])]
        for i in range(len(order) - 1):
            a = label or f"[{i}:a]"
            out_lbl = f"[x{i}]"
            filt.append(f"{a}[{i+1}:a]acrossfade=d={xfade:.3f}:c1=tri:c2=tri{out_lbl}")
            label = out_lbl
        chain = ";".join(filt)
        chain += (f";{label}atrim=0:{duration:.3f},"
                  f"afade=t=in:st=0:d={HEAD_FADE},"
                  f"afade=t=out:st={max(0, duration-TAIL_FADE):.3f}:d={TAIL_FADE}[bed]")
        _run(["ffmpeg", "-y", *inputs, "-filter_complex", chain,
              "-map", "[bed]", "-ar", str(SR), "-ac", "2",
              "-c:a", "aac", "-b:a", "192k", str(out_path)], "crossfade bed")

    got = _duration(out_path)
    if got < duration - 1.5:
        raise MusicError(f"bed {got:.1f}s short of required {duration:.1f}s")
    if verbose:
        print(f"  music: bed {got:.1f}s OK")
    return got


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    duration, out = float(sys.argv[1]), sys.argv[2]
    seed = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else "bed"
    xfade = XFADE_SEC
    if "--xfade" in sys.argv:
        xfade = float(sys.argv[sys.argv.index("--xfade") + 1])
    build_bed(duration, out, seed=seed, xfade=xfade)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except MusicError as e:
        print(f"MUSIC ERROR: {e}")
        sys.exit(1)
