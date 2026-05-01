import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )


def setup_database(conn):
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS YT_TRENDING")
    cursor.execute("USE DATABASE YT_TRENDING")
    cursor.execute("CREATE SCHEMA IF NOT EXISTS PUBLIC")
    cursor.execute("USE SCHEMA PUBLIC")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TRENDING_TRANSCRIPTIONS (
            VIDEO_ID        VARCHAR,
            URL             VARCHAR,
            TITLE           VARCHAR,
            CHANNEL         VARCHAR,
            REGION          VARCHAR,
            PUBLISHED_AT    VARCHAR,
            VIEW_COUNT      NUMBER,
            MODE            VARCHAR,
            KEYWORD         VARCHAR,
            FETCHED_AT      VARCHAR,
            AUDIO_PATH      VARCHAR,
            DOWNLOAD_STATUS VARCHAR,
            LANGUAGE        VARCHAR,
            LANGUAGE_PROB   FLOAT,
            TRANSCRIPTION   VARCHAR,
            TRANSCRIPTION_STATUS VARCHAR,
            LOADED_AT       TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        )
    """)
    cursor.close()
    print("Database and table ready")


def load_records(conn, records: list):
    cursor = conn.cursor()
    cursor.execute("USE DATABASE YT_TRENDING")
    cursor.execute("USE SCHEMA PUBLIC")
    
    inserted = 0
    for r in records:
        cursor.execute("""
            INSERT INTO TRENDING_TRANSCRIPTIONS (
                VIDEO_ID, URL, TITLE, CHANNEL, REGION, PUBLISHED_AT,
                VIEW_COUNT, MODE, KEYWORD, FETCHED_AT, AUDIO_PATH,
                DOWNLOAD_STATUS, LANGUAGE, LANGUAGE_PROB, TRANSCRIPTION,
                TRANSCRIPTION_STATUS
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            r.get("video_id"), r.get("url"), r.get("title"),
            r.get("channel"), r.get("region"), r.get("published_at"),
            r.get("view_count"), r.get("mode"), r.get("keyword"),
            r.get("fetched_at"), r.get("audio_path"), r.get("download_status"),
            r.get("language"), r.get("language_probability"),
            r.get("transcription"), r.get("status")
        ))
        inserted += 1
    
    cursor.close()
    print(f"Inserted {inserted} records into Snowflake")


if __name__ == "__main__":
    from fetch_trending import fetch_all_regions
    from download_audio import download_batch
    from transcribe import transcribe_batch

    print("1. Fetching trending videos...")
    videos = fetch_all_regions()

    print("2. Downloading audio...")
    downloaded = download_batch(videos, max_videos=3)
    successful = [v for v in downloaded if v["download_status"] == "success"]

    print("3. Transcribing audio...")
    audio_paths = [v["audio_path"] for v in successful]
    transcriptions = transcribe_batch(audio_paths)

    print("4. Merging results...")
    records = []
    for video, transcription in zip(successful, transcriptions):
        record = {**video, **transcription}
        records.append(record)

    print("5. Loading to Snowflake...")
    conn = get_connection()
    setup_database(conn)
    load_records(conn, records)
    conn.close()
    print("\nPipeline complete!")