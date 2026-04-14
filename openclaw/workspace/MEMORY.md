# MEMORY.md

## Current Focus

- Building businesses
- Raising funds

## Configuration Changes

**Date: April 13, 2026**
- Changed default model from Claude Haiku 4.5 → Claude Opus 4.6
- Reason: Haiku timeouts on complex tasks; Opus has better reasoning for completing work
- Impact: All future tasks/subagents will use Opus unless explicitly overridden
- Location: /home/herby/.openclaw/openclaw.json

This addresses task completion issues with dashboard debugging and complex builds.
