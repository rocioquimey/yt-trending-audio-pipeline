import os
import json
from datetime import datetime
from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
REGIONS = ["AR", "MX", "BR", "CO", "CL"]


def get_trending_videos(region_code: str, max_results: int = 50) -> list:
    youtube = build("youtube", "v3", developerKey=API_KEY)
    request = youtube.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        regionCode=region_code,
        maxResults=max_results
    )
    response = request.execute()

    videos = []
    for item in response["items"]:
        videos.append({
            "video_id": item["id"],
            "url": f"https://www.youtube.com/watch?v={item['id']}",
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "region": region_code,
            "published_at": item["snippet"]["publishedAt"],
            "view_count": item["statistics"].get("viewCount", 0),
            "mode": "trending",
            "keyword": None,
            "fetched_at": datetime.utcnow().isoformat()

        })
    return videos

def get_videos_by_keyword(keyword: str, region_code: str = None, period: str = None, max_results: int = 50) -> list:
    youtube = build("youtube", "v3", developerKey=API_KEY)

    params = {
        "part": "snippet",
        "q": keyword,
        "type": "video",
        "order": "viewCount",
        "maxResults": max_results
    }

    if region_code:
        params["regionCode"] = region_code

    if period == "week":
        since = datetime.now(timezone.utc) - timedelta(days=7)
        params["publishedAfter"] = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    elif period == "month":
        since = datetime.now(timezone.utc) - timedelta(days=30)
        params["publishedAfter"] = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    elif period == "today":
        since = datetime.now(timezone.utc) - timedelta(days=1)
        params["publishedAfter"] = since.strftime("%Y-%m-%dT%H:%M:%SZ")

    request = youtube.search().list(**params)
    response = request.execute()

    video_ids = [item["id"]["videoId"] for item in response["items"]]
    stats_request = youtube.videos().list(
        part="statistics",
        id=",".join(video_ids)
    )
    stats_response = stats_request.execute()
    stats_map = {item["id"]: item["statistics"] for item in stats_response["items"]}

    videos = []
    for item in response["items"]:
        vid_id = item["id"]["videoId"]
        videos.append({
            "video_id": vid_id,
            "url": f"https://www.youtube.com/watch?v={vid_id}",
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "region": region_code,
            "published_at": item["snippet"]["publishedAt"],
            "view_count": stats_map.get(vid_id, {}).get("viewCount", 0),
            "mode": "keyword",
            "keyword": keyword,
            "period": period,
            "fetched_at": datetime.utcnow().isoformat()
        })
    return videos

def fetch_all_regions() -> list:
    all_videos = []
    for region in REGIONS:
        print(f"Fetching trending for region: {region}")
        videos = get_trending_videos(region)
        all_videos.extend(videos)
    return all_videos

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        keyword = sys.argv[1]
        region = sys.argv[2] if len(sys.argv) > 2 else None
        period = sys.argv[3] if len(sys.argv) > 3 else None
        print(f"Searching keyword: '{keyword}' region: {region or 'global'} period: {period or 'all time'}")
        videos = get_videos_by_keyword(keyword, region, period)
    else:
        print("Fetching trending videos for all LATAM regions...")
        videos = fetch_all_regions()

    print(f"\nTotal videos fetched: {len(videos)}")
    print(json.dumps(videos[0], indent=2))