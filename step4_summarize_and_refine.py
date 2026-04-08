import os
import csv
import time
import random
import sys
import json
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

def summarize_and_refine_row(row, video_info):
    """
    Use Claude to:
    1. Summarize each category's content (from long quotes to concise summaries)
    2. Generate a one-liner product description
    3. Optionally re-classify content if needed
    """
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Build the content for Claude
    categories_content = {}
    for cat in STANDARD_CATEGORIES:
        content = row.get(cat, '').strip()
        if content:
            categories_content[cat] = content
    
    if not categories_content:
        print(f"   ⚠️  No content to summarize")
        return None
    
    prompt = f"""You are analyzing a startup story video. Here is the raw content extracted from the transcript, organized by category.

Video Title: {video_info['title']}

Current Content by Category:
{json.dumps(categories_content, indent=2)}

Your tasks:
1. **Product One-Liner**: Write a single sentence (15-25 words) describing what product/business this person built. Be specific and concise.

2. **Summarize Each Category**: For each category with content, create a concise 2-3 sentence summary that captures the key points. Remove redundancy and focus on actionable insights.

3. **Re-classify if Needed** (optional): If you notice content that clearly belongs in a different category, you may move it. But don't overthink this - only do it if it's obviously misclassified.

Return JSON in this exact format:
{{
  "product_oneliner": "A clear, specific description of the product/business...",
  "categories": {{
    "Idea Generation": "Concise 2-3 sentence summary...",
    "Validation": "Concise 2-3 sentence summary...",
    ...
  }}
}}

Only include categories that have content. Keep summaries focused and actionable."""

    try:
        print(f"      → Sending to Claude API...", flush=True)
        start_time = time.time()
        
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ],
            timeout=120.0
        )
        
        elapsed = time.time() - start_time
        print(f"      → Received response in {elapsed:.1f}s, parsing...", flush=True)
        
        # Extract JSON from response
        response_text = message.content[0].text
        
        # Try to find JSON block
        json_match = re.search(r'\{[\s\S]*"product_oneliner"[\s\S]*\}', response_text)
        
        if json_match:
            json_str = json_match.group()
            result = json.loads(json_str)
            
            product_oneliner = result.get('product_oneliner', '')
            categories = result.get('categories', {})
            
            if not product_oneliner:
                print(f"   ⚠️  No product one-liner found in response")
                return None
            
            return {
                'product_oneliner': product_oneliner,
                'categories': categories
            }
        else:
            print(f"   ⚠️  Could not parse JSON from Claude response")
            print(f"      Response: {response_text[:300]}...")
            return None
            
    except (APIStatusError, APIConnectionError, APITimeoutError) as e:
        print(f"   ❌ API Error: {str(e)[:100]}")
        return None
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON Error: {str(e)[:100]}")
        return None
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)[:100]}")
        return None


def process_csv_refinement(limit=None):
    input_file = 'chapters_analysis.csv'
    output_file = 'chapters_analysis_refined.csv'
    
    # Load video URLs for metadata
    with open('video_urls.json', 'r', encoding='utf-8') as f:
        videos = json.load(f)
    video_dict = {v['video_id']: v for v in videos}
    
    # Read existing CSV
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"📊 Total videos in CSV: {len(rows)}")
    
    # Check if we have a partial output already
    processed_ids = set()
    existing_rows = []
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                processed_ids.add(row['video_id'])
                existing_rows.append(row)
        print(f"✅ Already refined: {len(processed_ids)} videos")
    
    # Filter to unprocessed rows
    rows_to_process = [r for r in rows if r['video_id'] not in processed_ids]
    
    print(f"🎯 Remaining to refine: {len(rows_to_process)}")
    if limit:
        rows_to_process = rows_to_process[:limit]
        print(f"⚙️  Limit set to: {limit} new videos")
    
    print(f"\n🚀 Starting refinement with Claude...\n")
    
    refined_rows = []
    
    for i, row in enumerate(rows_to_process, 1):
        video_id = row['video_id']
        title = row['video_title']
        video_info = video_dict.get(video_id, {'title': title})
        
        print(f"[{i}/{len(rows_to_process)}] Refining: {title[:60]}...")
        
        # Call Claude to refine
        result = summarize_and_refine_row(row, video_info)
        
        if result:
            # Build new row
            new_row = {
                'video_id': video_id,
                'video_title': title,
                'video_url': row['video_url'],
                'product_oneliner': result['product_oneliner']
            }
            
            # Add refined categories
            for cat in STANDARD_CATEGORIES:
                new_row[cat] = result['categories'].get(cat, '')
            
            refined_rows.append(new_row)
            
            print(f"   ✅ Refined! Product: {result['product_oneliner'][:60]}...")
            print(f"   📂 Categories with content: {len([c for c in result['categories'] if result['categories'][c]])}")
        else:
            print(f"   ⚠️  Skipping - will retry next time")
        
        # Rate limiting
        if i < len(rows_to_process):
            delay = random.uniform(2.0, 4.0)
            print(f"   ⏳ Cooldown: {delay:.1f}s...\n")
            time.sleep(delay)
    
    # Combine existing + new
    all_refined = existing_rows + refined_rows
    
    # Write to output
    fieldnames = ['video_id', 'video_title', 'video_url', 'product_oneliner'] + STANDARD_CATEGORIES
    
    print(f"\n💾 Writing results to {output_file}...")
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_refined)
    
    print(f"\n{'='*70}")
    print(f"🎉 Complete! Summary:")
    print(f"   📹 Total refined videos: {len(all_refined)}")
    print(f"   🆕 New videos refined: {len(refined_rows)}")
    print(f"   💾 Saved to: {output_file}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    limit = None
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print("❌ Error: Please provide a number (e.g., python step4_summarize_and_refine.py 10)")
            sys.exit(1)
    
    process_csv_refinement(limit)

