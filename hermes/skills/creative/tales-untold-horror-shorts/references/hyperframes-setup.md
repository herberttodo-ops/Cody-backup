# HyperFrames Setup for Tales Untold

## Installation

```bash
# Install Bun (required)
curl -fsSL https://bun.sh/install | bash
export PATH="$HOME/.bun/bin:$PATH"

# Clone and build
git clone https://github.com/heygen-com/hyperframes.git
cd hyperframes
bun install
bun run build
bun link
```

## Render Command

```bash
npx hyperframes render --composition composition.html --format mp4 --fps 30 --quality looks --output output.mp4
```

## CSS Effects Reference

### Vignette (Heavy)
```css
.vignette {
  position: absolute; inset: 0;
  background: radial-gradient(
    ellipse at 50% 38%,
    transparent 0%,
    transparent 12%,
    rgba(0,0,0,0.6) 35%,
    rgba(0,0,0,0.95) 60%,
    rgba(0,0,0,0.98) 100%
  );
  z-index: 5;
}
```

### Film Grain (SUBTLE — ask user before adding)
```css
.grain {
  position: absolute; inset: 0;
  opacity: 0.10;  /* Reduced from 0.38 — grain is now optional per user preference */
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='5' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  z-index: 6;
}
```

## CRITICAL: HyperFrames Timeline Registration

HyperFrames requires **BOTH** `data-composition-id` and `data-duration` on the root element:

```html
<div id="comp" data-composition-id="tales-untold" data-duration="58">
```

Without `data-duration`, render fails with "Composition has zero duration".

Also register `window.__timelines` for GSAP:
```javascript
const tl = gsap.timeline();
if (typeof window !== 'undefined') window.__timelines = [tl];
```

**Duration:** Get this from Whisper transcript `segments[-1]['end']`. Do NOT guess. Add 2-3s for CTA.

---

## POYO API Key — Shell Mangling Warning

**Never** pass `POYO_API_KEY` through shell commands — the shell truncates/redacts long keys. Always use Python `os.environ.get()` directly, or read from `.env` in Python.

```python
# CORRECT
import os
API_KEY = os.environ.get("POYO_API_KEY")  # Set in env BEFORE Python starts

# CORRECT fallback
with open(".env") as f:
    for line in f:
        if line.startswith("POYO_API_KEY="):
            API_KEY = line.split("=", 1)[1].strip()
            break
```

POYO response format changed — `task_id` is now in `result["data"]["task_id"]` not `result["task_id"]`:
```python
result = r.json()
if "data" in result and "task_id" in result["data"]:
    task_id = result["data"]["task_id"]
```
