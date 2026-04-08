import json
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

def get_channel_id_from_handle(youtube, handle):
    """
    Get channel ID from handle like @starterstory
    """
    # Remove @ if present
    handle = handle.lstrip('@')
    
    # Try searching for the channel
    request = youtube.search().list(
        part="snippet",
        q=handle,
        type="channel",
        maxResults=1
    )
    response = request.execute()
    
    if response['items']:
        return response['items'][0]['snippet']['channelId']
    return None

def get_video_duration_seconds(youtube, video_ids):
    """
    Get video durations for a list of video IDs
    Returns dict of {video_id: duration_in_seconds}
    """
    import isodate
    
    durations = {}
    # API allows max 50 IDs per request
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        request = youtube.videos().list(
            part="contentDetails",
            id=",".join(batch)
        )
        response = request.execute()
        
        for item in response['items']:
            video_id = item['id']
            duration_iso = item['contentDetails']['duration']
            # Parse ISO 8601 duration (e.g., PT1M30S = 90 seconds)
            duration_seconds = int(isodate.parse_duration(duration_iso).total_seconds())
            durations[video_id] = duration_seconds
    
    return durations

def get_all_videos_from_channel(youtube, channel_id, exclude_shorts=True):
    """
    Get all videos from a channel using pagination
    
    Args:
        youtube: YouTube API client
        channel_id: Channel ID
        exclude_shorts: If True, filter out shorts (videos < 90 seconds)
    """
    videos = []
    next_page_token = None
    
    while True:
        # Search for videos in the channel
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            type="video",
            order="date",
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        
        # Collect video IDs from this page
        page_video_ids = []
        page_videos = []
        
        for item in response['items']:
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            page_video_ids.append(video_id)
            page_videos.append({
                'video_id': video_id,
                'title': title,
                'url': url,
                'published_at': item['snippet']['publishedAt']
            })
        
        # Get durations for this page if excluding shorts
        if exclude_shorts:
            durations = get_video_duration_seconds(youtube, page_video_ids)
            
            # Filter out shorts and short videos (< 300 seconds / 5 minutes)
            for video in page_videos:
                duration = durations.get(video['video_id'], 0)
                video['duration_seconds'] = duration
                
                if duration >= 300:  # At least 5 minutes
                    videos.append(video)
                    minutes = duration // 60
                    print(f"✅ Found: {video['title']} ({minutes}m {duration % 60}s)")
                else:
                    print(f"⏭️  Skipped short video: {video['title']} ({duration}s)")
        else:
            videos.extend(page_videos)
            for video in page_videos:
                print(f"Found: {video['title']}")
        
        # Check if there are more pages
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
        
        print(f"Fetched {len(videos)} videos so far, getting more...")
    
    return videos

def get_starter_story_videos():
    """
    Get all video URLs from Starter Story YouTube channel using YouTube Data API
    """
    print("Fetching videos from Starter Story channel using YouTube Data API...")
    
    # Load API key
    api_key = os.getenv('YOUTUBE_DATA_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_DATA_API_KEY not found in .env file")
        return []
    
    # Build YouTube API client
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # Get channel ID from handle
    print("\nStep 1: Resolving channel handle @starterstory...")
    channel_id = get_channel_id_from_handle(youtube, '@starterstory')
    
    if not channel_id:
        print("Error: Could not find channel ID for @starterstory")
        return []
    
    print(f"Found channel ID: {channel_id}")
    
    # Get all videos
    print("\nStep 2: Fetching all videos from channel...")
    videos = get_all_videos_from_channel(youtube, channel_id)
    
    print(f"\nTotal videos found: {len(videos)}")
    
    # Save to JSON
    with open('video_urls.json', 'w', encoding='utf-8') as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)
    
    print("Saved to video_urls.json")
    return videos

if __name__ == "__main__":
    videos = get_starter_story_videos()
