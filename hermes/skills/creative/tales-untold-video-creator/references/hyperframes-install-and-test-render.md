## HyperFrames (HeyGen) — Install, Build, First Render

"Write HTML. Render video. Built for agents."
Repo: https://github.com/heygen-com/hyperframes (50.3k stars)

### Prerequisites
- Node.js (for Bun install compatibility)
- Linux/macOS with Chrome/Chromium available

### Install Steps

```bash
# 1. Install Bun (required package manager)
curl -fsSL https://bun.sh/install | bash
export PATH="$HOME/.bun/bin:$PATH"

# 2. Clone and build
bun install                # 773 packages
bun run build              # Compiles all packages (~2 min)

# 3. Link CLI for global use
bun link                   # Register monorepo
bun link @hyperframes/cli  # Link CLI package

# Verify
npx hyperframes --version   # Should show 0.8.40+
```

### First Render Test

Create `composition.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=1080, height=1920">
  <title>Test</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { width: 1080px; height: 1920px; background: #000; overflow: hidden; }
    .scene { position: absolute; inset: 0; opacity: 0; }
    .scene img { position: absolute; min-width: 120%; min-height: 120%; object-fit: cover; }
  </style>
</head>
<body>
  <div class="scene" id="s1"><img src="./scene1.png" alt="s1"></div>
  <script>
    const tl = gsap.timeline({ paused: true });
    window.__timelines = [tl];
    tl.to('#s1', { opacity: 1, duration: 0.5 }, 0);
    tl.fromTo('#s1 img', { scale: 1.08 }, { scale: 1.22, duration: 8, ease: 'none' }, 0);
  </script>
</body>
</html>
```

**CRITICAL: Use local image paths (`./file.png`) in same directory as HTML. Absolute paths or `../../` relative paths often fail with `media_load_failed` warning.**

Render:
```bash
cd project_dir
npx hyperframes render --composition composition.html --format mp4 --fps 30 --output output.mp4 --quiet
```

### Key HyperFrames Concepts for Tales Untold

1. **Frame-accurate rendering:** GSAP timeline `paused: true` = deterministic seeking
2. **Local assets only:** Copy images to project dir, use relative paths
3. **CSS Ken Burns:** `transform: scale()` + `translate()` in GSAP is pixel-perfect and faster than MoviePy
4. **Vignette/film grain:** Pure CSS overlays, captured by headless Chrome
5. **Shader transitions:** Built-in WebGL transitions between scenes

### HyperFrames + Tales Untold Workflow (Proposed)

1. **Generate images** (existing Fal pipeline)
2. **Copy images + generate HTML composition** (sub-agent writes HTML)
3. **HyperFrames render to MP4**
4. **Overlay narration + music in MoviePy** (audio timing is easier in Python)
5. **Upload to Drive**

### CLI Options Quick Reference

```bash
# Key flags
--composition <html_file>   # Which HTML to render
--format mp4                # Output format
--fps 30                    # Frame rate
--output <path>             # Output file
--quality looks             # Draft / looks / delivery
--workers auto              # Parallel render workers
--quiet                     # Suppress verbose logs
--debug                     # Keep intermediate artifacts
```

### Common Issues

- `[media_load_failed]` → Image path is wrong or absolute. Use `./` relative to HTML.
- `Duration unknown` → HyperFrames infers duration from GSAP timeline end. Make sure timeline covers full duration.
- Low memory → Add `--low-memory-mode` or reduce concurrent workers.
