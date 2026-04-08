import json
import os
import time
import random
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_existing_transcripts():
    """
    Load existing transcripts from the transcripts/ directory.
    Returns a set of video IDs that already have transcripts.
    """
    if not os.path.exists('transcripts'):
        return set()
    
    existing = set()
    for filename in os.listdir('transcripts'):
        if filename.endswith('.txt'):
            video_id = filename[:-4]  # Remove .txt extension
            existing.add(video_id)
    
    return existing

def get_transcripts_via_api(limit=None, delay_min=2, delay_max=5):
    """
    Get transcripts using youtube-transcript.io API
    
    Args:
        limit: Maximum number of NEW videos to download (None = all remaining)
        delay_min: Minimum delay between requests in seconds (default: 2)
        delay_max: Maximum delay between requests in seconds (default: 5)
    """
    # Load API key
    api_key = os.getenv('YOUTUBE_TRANSCRIPT_IO_API_KEY')
    if not api_key:
        print("❌ Error: YOUTUBE_TRANSCRIPT_IO_API_KEY not found in .env file")
        return
    
    # Load video URLs
    with open('video_urls.json', 'r', encoding='utf-8') as f:
        videos = json.load(f)
    
    print(f"📊 Total videos in list: {len(videos)}")
    
    # Create directory for transcripts
    os.makedirs('transcripts', exist_ok=True)
    
    # Load existing transcripts from directory (SOURCE OF TRUTH)
    existing_transcripts = get_existing_transcripts()
    print(f"✅ Already downloaded: {len(existing_transcripts)} transcripts")
    print(f"🎯 Remaining to download: {len(videos) - len(existing_transcripts)}")
    
    if limit:
        print(f"⚙️  Limit set to: {limit} new downloads")
    
    print(f"⏱️  Delay between requests: {delay_min}-{delay_max} seconds")
    print()
    
    # Counter for newly downloaded videos
    new_downloads = 0
    failed_downloads = []
    
    for i, video in enumerate(videos, 1):
        video_id = video['video_id']
        title = video['title']
        transcript_file = f"transcripts/{video_id}.txt"
        
        # Skip if transcript file already exists
        if video_id in existing_transcripts:
            print(f"[{i}/{len(videos)}] ⏭️  Already exists: {title[:60]}...")
            continue
        
        # Check if we've hit the limit for new downloads
        if limit and new_downloads >= limit:
            print(f"\n✋ Reached limit of {limit} new downloads. Stopping here.")
            print(f"   Run again to download more!")
            break
        
        # Progress bar
        progress = (i / len(videos)) * 100
        print(f"\n{'='*70}")
        print(f"[{i}/{len(videos)}] ({progress:.1f}%) Processing: {title[:60]}...")
        print(f"{'='*70}")
        
        try:
            # Call youtube-transcript.io API
            print(f"   ⬇️  Fetching from youtube-transcript.io API...", end='', flush=True)
            
            url = "https://www.youtube-transcript.io/api/transcripts"
            headers = {
                "Authorization": f"Basic {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "ids": [video_id]
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            print(f" ✓")
            
            # Parse response
            data = response.json()
            
            # Extract transcript text
            print(f"   📝 Processing transcript...", end='', flush=True)
            
            # Response format: array of results for each video ID
            if isinstance(data, list) and len(data) > 0:
                result = data[0]
                if 'transcript' in result and isinstance(result['transcript'], list):
                    # Format: [{"text": "...", "offset": 0.0}, ...]
                    full_transcript = ' '.join([item['text'] for item in result['transcript']])
                elif 'text' in result:
                    full_transcript = result['text']
                else:
                    full_transcript = str(result)
            elif 'transcript' in data:
                full_transcript = ' '.join([item['text'] for item in data['transcript']])
            else:
                # Fallback
                full_transcript = str(data)
            
            print(f" ✓")
            
            # Save individual transcript
            print(f"   💾 Saving to file...", end='', flush=True)
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(full_transcript)
            print(f" ✓")
            
            # Add to existing set
            existing_transcripts.add(video_id)
            new_downloads += 1
            
            print(f"   ✅ Success! ({len(full_transcript):,} chars | {new_downloads}/{limit if limit else '∞'} done)")
            
            # Longer delay to avoid rate limiting
            delay = random.uniform(delay_min, delay_max)
            print(f"   ⏳ Cooldown: {delay:.1f}s...", end='', flush=True)
            time.sleep(delay)
            print(f" ✓")
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {e.response.status_code}"
            if e.response.status_code == 429:
                error_msg += " (Too Many Requests - Rate Limited)"
            print(f"\n   ❌ API Error: {error_msg}")
            failed_downloads.append({
                'video_id': video_id,
                'title': title,
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            })
            
            # If rate limited, wait longer
            if e.response.status_code == 429:
                wait_time = 30
                print(f"   ⏸️  Rate limited! Waiting {wait_time}s before continuing...")
                time.sleep(wait_time)
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n   ❌ Error: {error_msg[:100]}...")
            failed_downloads.append({
                'video_id': video_id,
                'title': title,
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            })
        
        # Progress update every 5 videos
        if new_downloads > 0 and new_downloads % 5 == 0:
            print(f"\n📊 Progress: {len(existing_transcripts)} total | {new_downloads} new | {len(failed_downloads)} failed\n")
    
    # Final summary
    print(f"\n{'='*70}")
    print(f"🎉 Complete! Summary:")
    print(f"   ✅ Total transcripts: {len(existing_transcripts)}/{len(videos)}")
    print(f"   🆕 New downloads: {new_downloads}")
    print(f"   ❌ Failed: {len(failed_downloads)}")
    print(f"   📁 Saved to: transcripts/ directory")
    print(f"{'='*70}")
    
    if failed_downloads:
        print(f"\n⚠️  Failed videos:")
        for fail in failed_downloads[:10]:  # Show first 10 failures
            print(f"   - {fail['title'][:60]}: {fail['error']}")
        if len(failed_downloads) > 10:
            print(f"   ... and {len(failed_downloads) - 10} more")

if __name__ == "__main__":
    # Parse command line argument for limit
    limit = None
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
            print(f"📝 Limit set to {limit} videos\n")
        except ValueError:
            print("❌ Error: Please provide a number (e.g., python step2_get_transcripts_io.py 20)")
            sys.exit(1)
    
    get_transcripts_via_api(limit)
