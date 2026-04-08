import json
import os
import csv
import sys
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

def get_processed_video_ids(csv_file):
    """
    Load already processed video IDs from CSV.
    Returns a set of video_ids.
    """
    if not os.path.exists(csv_file):
        return set()
    
    processed = set()
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'video_id' in row:
                    processed.add(row['video_id'])
    except Exception as e:
        print(f"⚠️  Warning: Could not read existing CSV: {e}")
        return set()
    
    return processed

def analyze_transcript_chapters(transcript_text, video_title):
    """
    Use Claude to analyze a transcript and identify chapters/topics.
    Returns a dict mapping category -> content.
    """
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    prompt = f"""Analyze this startup story and identify key topics.

Title: {video_title}

Transcript:
{transcript_text}

Identify 3-7 main topics from ONLY these standard categories:
- Idea Generation
- Validation  
- Building/Development
- Launch
- Marketing/Distribution
- Growth
- Monetization
- Challenges/Failures
- Team/Hiring
- Cost/Expenses
- Advice/Lessons

IMPORTANT: Use ONLY the exact category names listed above. Do NOT create subcategories (like "Growth - Paid Ads") or variations (like "Marketing/Distribution - Networking"). 
- If a topic is about growth strategies, use "Growth"
- If about marketing channels, use "Marketing/Distribution"
- If about building/coding, use "Building/Development"
- If about overcoming obstacles, use "Challenges/Failures"

For each topic, extract a relevant quote (100-300 words) from the transcript.

Return JSON:
{{
  "chapters": [
    {{"category": "Category Name", "content": "direct quote from transcript..."}},
    ...
  ]
}}

Keep original wording, don't summarize."""
    
    try:
        print(f"      → Sending request to Claude API...", flush=True)
        import time
        start_time = time.time()
        
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8192,
            messages=[
                {"role": "user", "content": prompt}
            ],
            timeout=120.0
        )
        
        elapsed = time.time() - start_time
        print(f"      → Received response in {elapsed:.1f}s, parsing...", flush=True)
        
        # Extract JSON from response
        response_text = message.content[0].text
        
        # Try to extract JSON - be flexible with format
        import re
        
        # Try to find JSON block (most common)
        json_match = re.search(r'\{[\s\S]*"chapters"[\s\S]*\}', response_text)
        
        if json_match:
            json_str = json_match.group()
            result = json.loads(json_str)
            chapters = result.get('chapters', [])
            
            # Convert list of chapters to dict: category -> content
            chapter_dict = {}
            for chapter in chapters:
                category = chapter.get('category', 'Unknown')
                content = chapter.get('content', '').strip()
                # If category already exists, append (shouldn't happen often)
                if category in chapter_dict:
                    chapter_dict[category] += " | " + content
                else:
                    chapter_dict[category] = content
            
            return chapter_dict
        else:
            print(f"   ⚠️  Could not parse JSON response")
            return {}
            
    except Exception as e:
        print(f"   ❌ Error analyzing transcript: {str(e)[:100]}")
        return {}

def process_transcripts(limit=None):
    """
    Process transcripts and extract chapters.
    One row per video, chapters as columns.
    """
    # Check API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ Error: ANTHROPIC_API_KEY not found in .env file")
        return
    
    # Load video metadata
    with open('video_urls.json', 'r', encoding='utf-8') as f:
        videos = json.load(f)
    
    # Create video lookup dict
    video_dict = {v['video_id']: v for v in videos}
    
    # Get list of transcript files (source of truth)
    transcript_files = []
    for f in os.listdir('transcripts'):
        if f.endswith('.txt'):
            filepath = os.path.join('transcripts', f)
            size = os.path.getsize(filepath)
            transcript_files.append((f, size))
    
    # Sort by size (smallest first for faster processing)
    transcript_files.sort(key=lambda x: x[1])
    transcript_files = [f for f, size in transcript_files]
    
    # Get already processed video IDs from CSV
    output_file = 'chapters_analysis.csv'
    processed_ids = get_processed_video_ids(output_file)
    
    print(f"📊 Total transcripts: {len(transcript_files)}")
    print(f"✅ Already processed: {len(processed_ids)}")
    print(f"🎯 Remaining to process: {len(transcript_files) - len(processed_ids)}")
    
    # Filter out already processed
    remaining_files = []
    for filename in transcript_files:
        video_id = filename[:-4]  # Remove .txt
        if video_id not in processed_ids:
            remaining_files.append(filename)
    
    if limit:
        remaining_files = remaining_files[:limit]
        print(f"⚙️  Limit set to: {limit} new videos")
    
    if not remaining_files:
        print("\n✅ All videos already processed!")
        return
    
    print(f"\n🎯 Processing {len(remaining_files)} new videos...")
    print(f"📊 Using Claude to analyze chapters...\n")
    
    # Collect all category names for CSV header
    all_categories = set()
    results = []
    
    for i, filename in enumerate(remaining_files, 1):
        video_id = filename[:-4]
        
        # Get video metadata
        video_info = video_dict.get(video_id, {})
        title = video_info.get('title', 'Unknown')
        url = video_info.get('url', '')
        
        print(f"[{i}/{len(remaining_files)}] Processing: {title[:60]}...")
        
        # Read transcript
        transcript_path = os.path.join('transcripts', filename)
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_text = f.read()
        
        print(f"   📝 Transcript length: {len(transcript_text):,} chars")
        print(f"   🤖 Analyzing with Claude... (this may take 10-30 seconds)", flush=True)
        
        # Analyze chapters
        chapter_dict = analyze_transcript_chapters(transcript_text, title)
        
        print(f"   ✓ Found {len(chapter_dict)} chapters")
        
        # Only save if we got valid results
        if chapter_dict and len(chapter_dict) > 0:
            categories = list(chapter_dict.keys())
            print(f"   📂 Categories: {', '.join(categories)}")
            all_categories.update(categories)
            
            # Build result row
            result_row = {
                'video_id': video_id,
                'video_title': title,
                'video_url': url,
            }
            result_row.update(chapter_dict)  # Add all chapter columns
            results.append(result_row)
            
            print(f"   ✅ Completed!\n")
        else:
            print(f"   ⚠️  No chapters extracted - will retry next time\n")
    
    # Write to CSV (append mode if file exists)
    print(f"💾 Writing results to {output_file}...")
    
    # Read existing data if file exists
    existing_rows = []
    if os.path.exists(output_file) and len(processed_ids) > 0:
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing_rows = list(reader)
            # Update all_categories from existing data
            for row in existing_rows:
                for key in row.keys():
                    if key not in ['video_id', 'video_title', 'video_url'] and row[key]:
                        all_categories.add(key)
    
    # Combine existing + new results
    all_rows = existing_rows + results
    
    # Define column order: video info first, then categories sorted
    base_columns = ['video_id', 'video_title', 'video_url']
    category_columns = sorted(list(all_categories))
    fieldnames = base_columns + category_columns
    
    # Write all rows
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_rows)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"🎉 Complete! Summary:")
    print(f"   📹 Total videos in CSV: {len(all_rows)}")
    print(f"   🆕 New videos processed: {len(results)}")
    print(f"   📂 Total unique categories: {len(all_categories)}")
    print(f"   💾 Saved to: {output_file}")
    print(f"{'='*70}")
    
    # Show category list
    if category_columns:
        print(f"\n📊 Categories found:")
        for cat in category_columns:
            print(f"   - {cat}")

if __name__ == "__main__":
    # Parse command line argument for limit
    limit = None
    
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print("❌ Error: Please provide a number (e.g., python step3_analyze_chapters.py 10)")
            sys.exit(1)
    
    if limit:
        print(f"📝 Processing {limit} new videos as a sample\n")
    else:
        print(f"📝 Processing all remaining videos\n")
    
    process_transcripts(limit)
