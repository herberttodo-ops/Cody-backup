# Story Generator with Quality Scoring
# 
# Pattern: Generate batch of stories → Score each → Return best
# Useful for ensuring AI-generated content meets quality thresholds.

import os
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

class StoryGenerator:
    """Generate and score stories using async LLM."""
    
    def __init__(self, client_class, system_prompt: str):
        self.client_class = client_class
        self.system_prompt = system_prompt
    
    async def generate_best_story(
        self,
        batch_size: int = 15,
        score_threshold: float = 7.0,
        max_attempts: int = 3
    ) -> Optional[Dict]:
        """
        Generate batch, score, return best above threshold.
        Retries if quality insufficient.
        """
        async with self.client_class() as client:
            all_scored = []
            
            for attempt in range(max_attempts):
                # Generate batch
                stories = await self._generate_batch(client, batch_size)
                
                if not stories:
                    continue
                
                # Score each story
                scored = []
                for story in stories:
                    story["_score"] = await self._score_story(client, story)
                    scored.append(story)
                
                if scored:
                    scored.sort(key=lambda x: x.get("_score", 0), reverse=True)
                    all_scored.extend(scored)
                    
                    best = scored[0]
                    print(f"  Best score: {best.get('_score', 0):.1f}")
                    
                    if best.get("_score", 0) >= score_threshold:
                        best["_id"] = f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{int(best['_score'])}"
                        return best
            
            # Return best from all attempts
            if all_scored:
                all_scored.sort(key=lambda x: x.get("_score", 0), reverse=True)
                best = all_scored[0]
                best["_id"] = f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{int(best.get('_score', 0))}"
                return best
            
            return None
    
    async def _generate_batch(self, client, batch_size: int) -> List[Dict]:
        """Generate stories via LLM."""
        prompt = f"""Generate {batch_size} different stories.

Return as JSON array:
[{{"hook": "...", "twist": "...", "mood_tag": "...", "visual_prompt": "..."}}]

hook: Attention-grabbing first sentence (max 15 words)
twist: Final line revealing something unsettling (max 20 words)"""

        task_id = await client.generate_chat(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.95,
            max_tokens=3000
        )
        
        result = await client.wait_for_result(task_id, timeout=120)
        output = result.get("output", {}) or {}
        content = output.get("content", "") or result.get("text", "")
        
        # Parse JSON from response
        try:
            start = content.find('[')
            end = content.rfind(']') + 1
            if start >= 0 and end > start:
                stories = json.loads(content[start:end])
            else:
                stories = json.loads(content)
            return stories if isinstance(stories, list) else [stories]
        except json.JSONDecodeError:
            return [{"hook": content[:100], "twist": ""}]
    
    async def _score_story(self, client, story: Dict) -> float:
        """Score story on coherence, atmosphere, originality, punch."""
        prompt = f"""Score this story 1-10 on: coherence, atmosphere, originality, punch.

Hook: "{story.get('hook', '')}"
Twist: "{story.get('twist', '')}"

Return JSON: {{"coherence": N, "atmosphere": N, "originality": N, "punch": N}}"""

        task_id = await client.generate_chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        result = await client.wait_for_result(task_id, timeout=60)
        output = result.get("output", {}) or {}
        content = output.get("content", "") or result.get("text", "")
        
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            scores = json.loads(content[start:end]) if start >= 0 else json.loads(content)
            
            return sum([
                scores.get("coherence", 5),
                scores.get("atmosphere", 5),
                scores.get("originality", 5),
                scores.get("punch", 5)
            ]) / 4.0
        except Exception:
            return 5.0  # Default middle score
