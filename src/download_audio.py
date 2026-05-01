import os
import yt_dlp
from pathlib import Path

AUDIO_DIR = Path("data/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def download_audio(video: dict) -> dict:
    video_id = video["video_id"]
    output_path = AUDIO_DIR / f"{video_id}.%(ext)s"


    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output_path),
        "ffmpeg_location": r"C:\Users\ramor173\yt-trending-audio-pipeline\ffmpeg-8.1-essentials_build\ffmpeg-8.1-essentials_build\bin",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }],
        "quiet": True,
        "no_warnings": True,
    }
    


    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video["url"]])
        
        audio_file = AUDIO_DIR / f"{video_id}.mp3"
        print(f"Downloaded: {video['title'][:50]}")
        
        return {**video, "audio_path": str(audio_file), "download_status": "success"}

    except Exception as e:
        print(f"Failed: {video['title'][:50]} — {e}")
        return {**video, "audio_path": None, "download_status": "failed"}


def download_batch(videos: list, max_videos: int = 5) -> list:
    results = []
    for video in videos[:max_videos]:
        result = download_audio(video)
        results.append(result)
    return results


if __name__ == "__main__":
    from fetch_trending import fetch_all_regions
    
    print("Fetching trending videos...")
    videos = fetch_all_regions()
    
    print(f"\nDownloading audio for first 3 videos...")
    results = download_batch(videos, max_videos=3)
    
    success = [r for r in results if r["download_status"] == "success"]
    print(f"\nDownloaded {len(success)}/{len(results)} successfully")