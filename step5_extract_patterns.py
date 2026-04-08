import os
import csv
import json
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic, APIStatusError, APIConnectionError, APITimeoutError

load_dotenv()

# Standard categories
STANDARD_CATEGORIES = [
    'Idea Generation',
    'Validation',
    'Building/Development',
    'Launch',
    'Marketing/Distribution',
    'Growth',
    'Monetization',
    'Challenges/Failures',
    'Team/Hiring',
    'Cost/Expenses',
    'Advice/Lessons'
]

def extract_patterns_for_category(category, all_content):
    """
    Use Claude to analyze all videos for a single category and extract patterns.
    One-shot approach: send all content at once.
    """
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Build the content list for this category
    content_list = []
    for video_id, video_title, content in all_content:
        if content.strip():
            content_list.append(f"[{video_id}] {video_title}: {content}")
    
    if not content_list:
        print(f"   ⚠️  No content found for this category")
        return None
    
    print(f"   📊 Analyzing {len(content_list)} videos with content...")
    
    # Build prompt
    prompt = f"""You are analyzing {len(content_list)} startup stories for the category: **{category}**

Here is the content from all videos for this category:

{chr(10).join(content_list[:100])}  

{"... (truncated for length)" if len(content_list) > 100 else ""}

Your task:
1. **Identify 5-7 Common Patterns**: What are the recurring strategies, approaches, or themes across these stories?
2. **Extract Keywords**: What specific tools, platforms, channels, or methods are frequently mentioned? (e.g., Reddit, TikTok, Shopify, Twitter, SEO, etc.)

For patterns:
- Each pattern should represent a distinct strategy or approach
- Count how many videos mention this pattern (approximately)
- Provide 2-3 video IDs as examples

For keywords:
- Extract specific, actionable keywords (tools, platforms, tactics)
- Count approximate frequency across all videos
- Focus on concrete nouns (Reddit, Shopify) not generic terms (online, marketing)

Return JSON in this exact format:
{{
  "patterns": [
    {{
      "name": "Pattern name (concise, 3-8 words)",
      "description": "1-2 sentence explanation of this pattern",
      "count": 45,
      "examples": ["video_id_1", "video_id_2", "video_id_3"]
    }},
    ...
  ],
  "keywords": {{
    "Reddit": 28,
    "TikTok": 15,
    "SEO": 22,
    ...
  }}
}}

Focus on quality over quantity. Only include patterns that appear in at least 5+ videos."""

    try:
        print(f"   → Sending to Claude API...", flush=True)
        start_time = time.time()
        
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8192,
            messages=[
                {"role": "user", "content": prompt}
            ],
            timeout=180.0  # 3 minutes for large context
        )
        
        elapsed = time.time() - start_time
        print(f"   → Received response in {elapsed:.1f}s, parsing...", flush=True)
        
        # Extract JSON from response
        response_text = message.content[0].text
        
        # Try to find JSON block
        json_match = re.search(r'\{[\s\S]*"patterns"[\s\S]*\}', response_text)
        
        if json_match:
            json_str = json_match.group()
            result = json.loads(json_str)
            
            patterns = result.get('patterns', [])
            keywords = result.get('keywords', {})
            
            print(f"   ✅ Found {len(patterns)} patterns, {len(keywords)} keywords")
            
            return {
                'patterns': patterns,
                'keywords': keywords
            }
        else:
            print(f"   ⚠️  Could not parse JSON from response")
            print(f"      Response: {response_text[:500]}...")
            return None
            
    except (APIStatusError, APIConnectionError, APITimeoutError) as e:
        print(f"   ❌ API Error: {str(e)[:150]}")
        return None
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON Error: {str(e)[:150]}")
        print(f"      Response text: {response_text[:500]}...")
        return None
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)[:150]}")
        return None


def process_pattern_extraction(test_category=None):
    """
    Process all categories to extract patterns.
    If test_category is provided, only process that one category.
    """
    input_file = 'chapters_analysis_refined.csv'
    output_file = 'patterns_analysis.json'
    
    # Read refined CSV
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found")
        print(f"   Please run step4_summarize_and_refine.py first")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"📊 Loaded {len(rows)} refined videos")
    
    # Load existing results if available
    all_results = {}
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            all_results = json.load(f)
        print(f"✅ Loaded existing results for {len(all_results)} categories")
    
    # Determine which categories to process
    if test_category:
        if test_category not in STANDARD_CATEGORIES:
            print(f"❌ Error: '{test_category}' is not a valid category")
            print(f"   Valid categories: {', '.join(STANDARD_CATEGORIES)}")
            return
        categories_to_process = [test_category]
        print(f"\n🧪 TEST MODE: Processing only '{test_category}'\n")
    else:
        # Skip categories that already have results
        categories_to_process = [c for c in STANDARD_CATEGORIES if c not in all_results]
        print(f"🎯 Categories to process: {len(categories_to_process)}")
        if len(all_results) > 0:
            print(f"   Already completed: {', '.join(all_results.keys())}")
        print()
    
    if not categories_to_process:
        print("✅ All categories already processed!")
        return
    
    # Process each category
    for i, category in enumerate(categories_to_process, 1):
        print(f"[{i}/{len(categories_to_process)}] Processing: {category}")
        
        # Gather all content for this category
        all_content = []
        for row in rows:
            video_id = row['video_id']
            video_title = row['video_title']
            content = row.get(category, '').strip()
            all_content.append((video_id, video_title, content))
        
        # Extract patterns
        result = extract_patterns_for_category(category, all_content)
        
        if result:
            all_results[category] = result
            
            # Save immediately after each category
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            
            print(f"   💾 Saved results")
        else:
            print(f"   ⚠️  Skipped - will retry next time")
        
        # Rate limiting between categories
        if i < len(categories_to_process):
            delay = 3.0
            print(f"   ⏳ Cooldown: {delay:.1f}s...\n")
            time.sleep(delay)
    
    print(f"\n{'='*70}")
    print(f"🎉 Complete! Summary:")
    print(f"   📂 Categories analyzed: {len(all_results)}/{len(STANDARD_CATEGORIES)}")
    print(f"   💾 Saved to: {output_file}")
    print(f"{'='*70}\n")
    
    # Print summary
    print("📊 Pattern Summary:\n")
    for category, data in all_results.items():
        patterns = data.get('patterns', [])
        keywords = data.get('keywords', {})
        print(f"  {category}:")
        print(f"    - {len(patterns)} patterns")
        print(f"    - {len(keywords)} keywords")
        if patterns:
            top_pattern = patterns[0]
            print(f"    - Top pattern: {top_pattern['name']} ({top_pattern.get('count', 0)} videos)")
        print()


if __name__ == "__main__":
    import sys
    
    # Check if test mode (single category)
    if len(sys.argv) > 1:
        test_category = sys.argv[1]
        process_pattern_extraction(test_category=test_category)
    else:
        process_pattern_extraction()

