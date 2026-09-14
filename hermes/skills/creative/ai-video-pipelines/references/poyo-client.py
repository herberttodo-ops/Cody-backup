#!/usr/bin/env python3
"""
Poyo Async Client Reference Implementation

Unified client for Poyo AI API with async polling support.
Pattern: Submit task → Poll status → Download result.

Usage:
    async with PoyoClient() as client:
        # Submit task
        task_id = await client.generate_chat(messages=[...])
        
        # Wait for result
        result = await client.wait_for_result(task_id)
        
        # Download file if present
        if result.get("files"):
            await client.download_file(result["files"][0]["file_url"], path)
"""
import os
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, Dict, Any, Callable

POYO_BASE_URL = "https://api.poyo.ai"


class PoyoClient:
    """Unified client for Poyo AI API with async polling."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("POYO_API_KEY")
        if not self.api_key:
            raise ValueError("POYO_API_KEY not set")
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
            self.session = None
    
    # ─────────────────────────────────────────────────────────────────
    # IMAGE GENERATION
    # ─────────────────────────────────────────────────────────────────
    async def generate_image(
        self,
        prompt: str,
        model: str = "gpt-image-2",
        size: str = "1024x1536",  # 9:16 vertical
        quality: str = "high"
    ) -> str:
        """Submit image task. Returns task_id."""
        payload = {
            "model": model,
            "input": {"prompt": prompt, "size": size, "quality": quality}
        }
        result = await self._submit_task(payload)
        return result["data"]["task_id"]
    
    # ─────────────────────────────────────────────────────────────────
    # VOICE GENERATION (ElevenLabs via Poyo)
    # ─────────────────────────────────────────────────────────────────
    async def generate_voice(
        self,
        text: str,
        voice_id: str = "pNInz6obpgDQGcFmaJgB",
        model: str = "eleven_multilingual_v2",
        stability: float = 0.5,
        similarity_boost: float = 0.75
    ) -> str:
        """Submit voice task. Returns task_id."""
        payload = {
            "model": model,
            "input": {
                "text": text,
                "voice_id": voice_id,
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "use_speaker_boost": True
                }
            }
        }
        result = await self._submit_task(payload)
        return result["data"]["task_id"]
    
    # ─────────────────────────────────────────────────────────────────
    # CHAT/STORY GENERATION
    # ─────────────────────────────────────────────────────────────────
    async def generate_chat(
        self,
        messages: list,
        model: str = "gpt-4o-mini",
        temperature: float = 0.9,
        max_tokens: int = 2000
    ) -> str:
        """Submit chat task. Returns task_id."""
        payload = {
            "model": model,
            "input": {
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        }
        result = await self._submit_task(payload)
        return result["data"]["task_id"]
    
    # ─────────────────────────────────────────────────────────────────
    # TASK POLLING
    # ─────────────────────────────────────────────────────────────────
    async def wait_for_result(
        self,
        task_id: str,
        timeout: int = 300,
        poll_interval: float = 2.0,
        on_progress: Optional[Callable[[Dict], None]] = None
    ) -> Dict:
        """Poll task until complete. Returns result with file_url(s)."""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            status = await self._query_status(task_id)
            
            if on_progress:
                on_progress(status)
            
            task_status = status["data"]["status"]
            
            if task_status == "finished":
                return status["data"]
            
            if task_status in ("failed", "error"):
                raise RuntimeError(f"Task failed: {status}")
            
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Task {task_id} timed out")
            
            await asyncio.sleep(poll_interval)
    
    async def download_file(self, file_url: str, output_path: Path) -> Path:
        """Download generated file from Poyo storage."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with self.session.get(file_url) as response:
            response.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(await response.read())
        
        return output_path
    
    # ─────────────────────────────────────────────────────────────────
    # INTERNAL METHODS
    # ─────────────────────────────────────────────────────────────────
    async def _submit_task(self, payload: Dict) -> Dict:
        """POST to /api/generate/submit"""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        url = f"{POYO_BASE_URL}/api/generate/submit"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with self.session.post(url, json=payload, headers=headers) as resp:
            resp.raise_for_status()
            data = await resp.json()
            
            if data.get("code") != 200:
                raise RuntimeError(f"API error: {data}")
            
            return data
    
    async def _query_status(self, task_id: str) -> Dict:
        """GET /api/generate/status/{task_id}"""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        url = f"{POYO_BASE_URL}/api/generate/status/{task_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        async with self.session.get(url, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()


# Example usage
if __name__ == "__main__":
    async def test():
        async with PoyoClient() as client:
            task_id = await client.generate_chat(
                messages=[{"role": "user", "content": "Say hello"}],
                model="gpt-4o-mini"
            )
            print(f"Task: {task_id}")
            
            result = await client.wait_for_result(task_id)
            print(f"Result: {result}")
    
    asyncio.run(test())
