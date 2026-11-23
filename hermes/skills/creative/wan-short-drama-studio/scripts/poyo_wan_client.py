"""
POYO Wan 3.0 Video Prime client for Tales Untold video generation.

Exposes submit + poll for all three model variants:
  - wan3.0-prime-text-to-video
  - wan3.0-prime-image-to-video
  - wan3.0-prime-reference-to-video

Usage example:
    from poyo_wan_client import generate_wan_video
    url = generate_wan_video(
        model="wan3.0-prime-text-to-video",
        prompt="A paper boat drifting across a calm pond at sunrise...",
        resolution="720p",
        duration=5,
        aspect_ratio="9:16",
        audio=True,
        timeout=1800
    )
    print(f"Video ready: {url}")
"""

import os
import json
import time
import urllib.request
import urllib.error
from typing import Optional, Union, List

POYO_SUBMIT_URL = "https://api.poyo.ai/api/generate/submit"
POYO_STATUS_URL = "https://api.poyo.ai/api/generate/status"


def _get_api_key() -> str:
    key = os.environ.get("POYO_API_KEY", "")
    if not key:
        raise RuntimeError("POYO_API_KEY env var not set")
    return key


def _headers(extra: Optional[dict] = None) -> dict:
    h = {"Authorization": f"Bearer {_get_api_key()}", "Content-Type": "application/json"}
    if extra:
        h.update(extra)
    return h


def _http_request(
    url: str,
    method: str = "GET",
    data: Optional[bytes] = None,
    headers: Optional[dict] = None,
    timeout: int = 30,
):
    """Raw HTTP request returning parsed JSON. Raises on non-2xx."""
    req = urllib.request.Request(url, method=method, data=data, headers=headers or {})
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        body = resp.read().decode()
    except urllib.error.HTTPError as e:
        body = e.read().decode()
    return json.loads(body) if body else {}


def submit_wan_video(
    model: str,
    prompt: str,
    resolution: str = "720p",
    duration: int = 5,
    aspect_ratio: str = "9:16",
    audio: bool = True,
    image_urls: Optional[List[str]] = None,
    reference_image_urls: Optional[List[str]] = None,
    reference_video_urls: Optional[List[str]] = None,
    reference_audio_urls: Optional[List[str]] = None,
    callback_url: Optional[str] = None,
) -> str:
    """
    Submit a Wan 3.0 video generation task.
    Returns the task_id string.
    Raises RuntimeError on submission failure.
    """
    if model not in (
        "wan3.0-prime-text-to-video",
        "wan3.0-prime-image-to-video",
        "wan3.0-prime-reference-to-video",
    ):
        raise ValueError(f"Unsupported model: {model}")

    inp = {
        "prompt": prompt,
        "resolution": resolution,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "audio": audio,
    }

    if image_urls:
        inp["image_urls"] = image_urls
    if reference_image_urls:
        inp["reference_image_urls"] = reference_image_urls
    if reference_video_urls:
        inp["reference_video_urls"] = reference_video_urls
    if reference_audio_urls:
        inp["reference_audio_urls"] = reference_audio_urls

    payload = {"model": model, "input": inp}
    if callback_url:
        payload["callback_url"] = callback_url

    resp = _http_request(
        POYO_SUBMIT_URL,
        method="POST",
        data=json.dumps(payload).encode(),
        headers=_headers(),
        timeout=30,
    )

    if resp.get("code") != 200:
        raise RuntimeError(
            f"POYO submit failed: code={resp.get('code')} error={resp.get('error')}"
        )

    task_id = resp.get("data", {}).get("task_id")
    if not task_id:
        raise RuntimeError(f"POYO submit returned success but no task_id: {resp}")
    return task_id


def poll_wan_task(
    task_id: str,
    interval: int = 5,
    timeout: int = 1800,
) -> str:
    """
    Poll a POYO video task until it finishes or times out.
    Returns the video file_url string.
    Raises RuntimeError on failure or timeout.
    """
    url = f"{POYO_STATUS_URL}/{task_id}"
    start = time.time()
    while True:
        if time.time() - start > timeout:
            raise RuntimeError(f"Timeout waiting for task {task_id} after {timeout}s")

        try:
            resp = _http_request(url, headers=_headers(), timeout=60)
        except (TimeoutError, OSError, ValueError):
            # transient network/parse error: keep polling until overall timeout
            time.sleep(interval)
            continue
        data = resp.get("data", {}) if resp.get("code") == 200 else {}
        status = data.get("status")

        if status == "finished":
            files = data.get("files", [])
            if not files:
                raise RuntimeError(f"Task {task_id} finished but no files returned")
            return files[0].get("file_url", "")

        if status == "failed":
            raise RuntimeError(
                f"Task {task_id} failed: {data.get('error_message', 'Unknown error')}"
            )

        time.sleep(interval)


def generate_wan_video(
    model: str,
    prompt: str = "",
    resolution: str = "720p",
    duration: int = 5,
    aspect_ratio: str = "9:16",
    audio: bool = True,
    image_urls: Optional[List[str]] = None,
    reference_image_urls: Optional[List[str]] = None,
    reference_video_urls: Optional[List[str]] = None,
    reference_audio_urls: Optional[List[str]] = None,
    callback_url: Optional[str] = None,
    poll_interval: int = 5,
    timeout: int = 1800,
) -> str:
    """
    One-shot: submit + poll until video is ready. Returns file URL.
    """
    task_id = submit_wan_video(
        model=model,
        prompt=prompt,
        resolution=resolution,
        duration=duration,
        aspect_ratio=aspect_ratio,
        audio=audio,
        image_urls=image_urls,
        reference_image_urls=reference_image_urls,
        reference_video_urls=reference_video_urls,
        reference_audio_urls=reference_audio_urls,
        callback_url=callback_url,
    )
    return poll_wan_task(task_id, interval=poll_interval, timeout=timeout)


# ___LONG_STRING___
# Example usage (run this module directly to test)
# ___LONG_STRING___
if __name__ == "__main__":
    import sys
    import os

    # Load key from .env if present
    env_path = os.path.expanduser("~/.openclaw/workspace/tales-untold/.env")
    if os.path.exists(env_path) and not os.environ.get("POYO_API_KEY"):
        for line in open(env_path):
            if line.startswith("POYO_API_KEY="):
                os.environ["POYO_API_KEY"] = line.split("=", 1)[1].strip()
                break

    if not os.environ.get("POYO_API_KEY"):
        print("ERROR: POYO_API_KEY not set. Export it or put it in .env", file=sys.stderr)
        sys.exit(1)

    print("Testing wan3.0-prime-text-to-video ...")
    try:
        video_url = generate_wan_video(
            model="wan3.0-prime-text-to-video",
            prompt="A paper boat drifting across a calm pond at sunrise, gentle ripples",
            resolution="480p",
            duration=2,
            aspect_ratio="16:9",
            audio=True,
            timeout=1800,
        )
        print(f"Success! Video URL: {video_url}")
    except Exception as e:
        print(f"Failed: {e}", file=sys.stderr)
        sys.exit(1)
