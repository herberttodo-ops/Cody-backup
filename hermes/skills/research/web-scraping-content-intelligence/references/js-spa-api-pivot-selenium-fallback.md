# JS SPA Recovery: API-First Pivot with Selenium Fallback

Session: 2026-10-10 — ATG Tickets (React seating chart)

## Problem Sketch

The site is a React SPA that renders seat pricing inside an SVG chart. A plain `curl`
fetches an empty `<div id="root">`. Standard archive services (Wayback) cannot render
JS-heavy seating charts. The data exists behind authenticated GraphQL endpoints.

## API-First Pivot

Check these common SPA data sources *before* launching a real browser:

### 1. Embedded JSON in HTML (`<script type="application/json">`)
Modern SPAs embed config or initial state in the HTML shell:

```html
<script type="application/json" id="env">
{"API_ENDPOINT":"https://api.example.com","EVENT_ID":"..."}
</script>
```

### 2. CDN / Static Content Service (often UNGATED)
Hosting services like `content-service.example.com` may serve pages via S3-compatible
backends that reject unexpected HTTP methods (e.g., `POST` to a static bucket).

```bash
curl -s https://content-service.example.com/graphql
# → 405 (S3 bucket, POST not allowed)
```
This tells you the endpoint exists—but it's a static gateway, not a real GraphQL
server. Check for a `graphql` subdomain instead:

```bash
curl -s https://graphql.example.com/graphql -X POST ...
```

### 3. GraphQL Subdomain Triage
Common patterns seen in the wild:
- `https://graphql.example.com/graphql` — canonical data API
- `https://calendar-service.core.platform.example.com/graphql` — feature-specific GQL
- `https://session-service.example.com/graphql` — booking/session API

When one returns `Missing Authentication Token`, try others. Auth is often scoped
per subdomain.

### 4. CDP / Network Log via Real Browser
If API pivoting fails but individual seat prices are in the HTML (server-side rendered
for SEO/accessibility), use **Selenium with headless Chrome** to grab `page_source`:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--user-agent=Mozilla/5.0 ...")

driver = webdriver.Chrome(options=chrome_options)
driver.get(url)
# React hydration may take 5–10s
time.sleep(8)

html = driver.page_source
# Search for data attributes injected during hydration
driver.quit()
```

### 5. Post-Hydration DOM Patterns
After React/Vue hydration, look for `aria-label` attributes—they're often used for
accessibility and contain the exact pricing text:

```python
# Extract from hydrated HTML
import re
seats = re.findall(
    r'aria-label="Row ([A-Z]+), Seat (\d+), \$([\d\.]+), (Available|Sold out)"',
    html
)
```

This yielded 11 "Seat 31" matches on ATG Tickets, each with exact row, price, and
availability—after API endpoints all returned auth errors.

## Key Pitfalls

- **Do NOT rely on static curl HTML alone** for JS SPAs — you'll get an empty shell.
- **401 on GraphQL isn't always the end.** Subdomain-level auth scoping means one
  service requires a session token while another may not. Enumerate all known
  subdomains (read from the HTML shell's `<script id="env">` config block).
- **Wayback/Archive.today** will not render JS seat charts reliably. They capture
  the static HTML shell, not the post-hydration state.
- **Wait time matters.** React hydration + API calls can take 5–10s. Start with
  `time.sleep(8)` and increase if `page_source` still looks like a shell.
- **Use `--disable-blink-features=AutomationControlled`** to reduce bot detection
  that blocks Selenium from receiving data.
