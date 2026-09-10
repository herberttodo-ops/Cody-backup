#!/usr/bin/env python3
"""
Batch regenerate all OptiRFP social media images with Ideogram V4.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from ideogram_logo_compositor import generate_optirfp_post_with_logo

# Define all the OptiRFP posts to regenerate
# Format: (headline, topic, description)
OPTIRFP_POSTS = [
    # Copy-paste topic
    ("80% of losing RFPs are copy-pasted", "copy-paste", "copy_paste_trap"),
    ("The copy-paste trap is real", "copy-paste", "copypaste_trap"),
    ("Your template is hurting you", "copy-paste", "template_hurting"),
    
    # Mirror language topic
    ("Mirror their language. Win the deal.", "mirror-language", "mirror_language"),
    ("Speak their words, not yours", "mirror-language", "speak_their_words"),
    ("Client vocabulary = winning bids", "mirror-language", "client_vocabulary"),
    
    # Specificity topic
    ("Vague claims kill proposals", "specificity", "vague_claims"),
    ("Specificity wins. Generics lose.", "specificity", "specificity_wins"),
    ("Details close deals", "specificity", "details_close"),
    
    # Page-one topic
    ("Page one determines everything", "page-one", "page_one_matters"),
    ("Your first page is your only page", "page-one", "first_page_only"),
    ("Hook them on page one", "page-one", "hook_page_one"),
    
    # Workflow topic
    ("Stop recycling. Start winning.", "workflow", "stop_recycling"),
    ("Effort ≠ Results", "workflow", "effort_not_results"),
    ("Work smarter, not harder", "workflow", "work_smarter"),
    
    # AI-automation topic
    ("AI doesn't write. It amplifies.", "ai-automation", "ai_amplifies"),
    ("Automation + Expertise = Wins", "ai-automation", "automation_expertise"),
    ("Let AI handle the grind", "ai-automation", "ai_handle_grind"),
    
    # Winning topic
    ("Winners plan. Losers hope.", "winning", "winners_plan"),
    ("Strategy beats hustle", "winning", "strategy_beats_hustle"),
    ("The winning formula isn't luck", "winning", "winning_formula"),
    
    # So-what topic
    ("So what? Answer that first.", "so-what", "so_what_first"),
    ("Value first. Features second.", "so-what", "value_first"),
    ("They don't care what you do", "so-what", "they_dont_care"),
]


def regenerate_all():
    """Regenerate all OptiRFP social images."""
    
    results = []
    
    print("=" * 70)
    print("OPTIRFP SOCIAL IMAGE REGENERATION BATCH")
    print(f"Total posts to generate: {len(OPTIRFP_POSTS)}")
    print("=" * 70)
    
    for i, (headline, topic, description) in enumerate(OPTIRFP_POSTS, 1):
        print(f"\n[{i}/{len(OPTIRFP_POSTS)}] Generating: {description}")
        print(f"    Headline: {headline}")
        print(f"    Topic: {topic}")
        print("-" * 50)
        
        try:
            result = generate_optirfp_post_with_logo(
                headline=headline,
                topic=topic,
                aspect_ratio="square"
            )
            
            results.append({
                "headline": headline,
                "topic": topic,
                "description": description,
                "final_path": result["final_path"],
                "success": True
            })
            
            print(f"    ✓ Success: {result['final_path']}")
            
        except Exception as e:
            print(f"    ✗ Failed: {e}")
            results.append({
                "headline": headline,
                "topic": topic,
                "description": description,
                "error": str(e),
                "success": False
            })
    
    # Summary
    print("\n" + "=" * 70)
    print("REGENERATION COMPLETE")
    print("=" * 70)
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"\nSuccessful: {len(successful)}/{len(results)}")
    print(f"Failed: {len(failed)}/{len(results)}")
    
    if failed:
        print("\nFailed items:")
        for r in failed:
            print(f"  - {r['description']}: {r['headline']}")
    
    print(f"\nAll images saved to: ~/.hermes/generated_images/")
    
    # Write summary file
    summary_path = Path.home() / ".hermes" / "generated_images" / "regeneration_summary.txt"
    with open(summary_path, "w") as f:
        f.write("OPTIRFP IMAGE REGENERATION SUMMARY\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total: {len(results)}\n")
        f.write(f"Successful: {len(successful)}\n")
        f.write(f"Failed: {len(failed)}\n\n")
        
        f.write("GENERATED FILES:\n")
        f.write("-" * 70 + "\n")
        for r in successful:
            f.write(f"\n[{r['topic']}] {r['headline']}\n")
            f.write(f"  File: {r['final_path']}\n")
    
    print(f"\nSummary saved to: {summary_path}")
    
    return results


if __name__ == "__main__":
    regenerate_all()
