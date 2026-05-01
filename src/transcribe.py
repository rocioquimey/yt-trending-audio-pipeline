import os
from pathlib import Path
from faster_whisper import WhisperModel

AUDIO_DIR = Path("data/audio")
model = WhisperModel("small", device="cpu", compute_type="int8")


def transcribe_audio(audio_path: str) -> dict:
    try:
        segments, info = model.transcribe(audio_path, beam_size=5)
        text = " ".join([seg.text for seg in segments])
        return {
            "audio_path": audio_path,
            "language": info.language,
            "language_probability": round(info.language_probability, 3),
            "transcription": text.strip(),
            "status": "success"
        }
    except Exception as e:
        return {
            "audio_path": audio_path,
            "language": None,
            "language_probability": None,
            "transcription": None,
            "status": f"failed: {e}"
        }


def transcribe_batch(audio_paths: list) -> list:
    results = []
    for path in audio_paths:
        print(f"Transcribing: {Path(path).name}")
        result = transcribe_audio(path)
        print(f"Language: {result['language']} | {result['transcription'][:80]}...")
        results.append(result)
    return results


if __name__ == "__main__":
    mp3_files = list(AUDIO_DIR.glob("*.mp3"))
    
    if not mp3_files:
        print("No mp3 files found in data/audio/")
    else:
        print(f"Found {len(mp3_files)} audio files\n")
        results = transcribe_batch([str(f) for f in mp3_files])
        print(f"\nTranscribed {len(results)} files")
        for r in results:
            print(f"\n{Path(r['audio_path']).name}")
            print(f"  Language: {r['language']} ({r['language_probability']})")
            print(f"  Text: {r['transcription'][:150]}...")