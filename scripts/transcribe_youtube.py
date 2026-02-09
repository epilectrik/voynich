#!/usr/bin/env python3
"""Transcribe a YouTube video using yt-dlp + OpenAI Whisper.

Usage:
    python scripts/transcribe_youtube.py URL [--language LANG] [--model MODEL] [--output FILE]

Examples:
    python scripts/transcribe_youtube.py https://www.youtube.com/watch?v=abc123
    python scripts/transcribe_youtube.py https://www.youtube.com/watch?v=abc123 --language ru
    python scripts/transcribe_youtube.py https://www.youtube.com/watch?v=abc123 --language ru --model large
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCES_DIR = Path(__file__).resolve().parent.parent / "sources"


def get_video_info(url):
    """Get video title and metadata via yt-dlp."""
    result = subprocess.run(
        ["yt-dlp", "--dump-json", "--no-download", url],
        capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        print(f"Error getting video info: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def download_audio(url, output_path):
    """Download audio from YouTube video."""
    result = subprocess.run(
        [
            "yt-dlp",
            "-x", "--audio-format", "wav",
            "--audio-quality", "0",
            "-o", str(output_path),
            url,
        ],
        capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        print(f"Error downloading audio: {result.stderr}", file=sys.stderr)
        sys.exit(1)


def transcribe_audio(audio_path, model_name="medium", language=None):
    """Transcribe audio file using Whisper."""
    import whisper

    print(f"Loading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)

    print("Transcribing...")
    options = {}
    if language:
        options["language"] = language

    result = model.transcribe(str(audio_path), **options)
    return result["text"]


def sanitize_filename(title):
    """Convert video title to a safe filename."""
    clean = re.sub(r'[<>:"/\\|?*]', '', title)
    clean = re.sub(r'\s+', '_', clean.strip())
    clean = clean[:80]  # truncate
    return clean.lower()


def main():
    parser = argparse.ArgumentParser(description="Transcribe a YouTube video")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--language", "-l", help="Language code (e.g., ru, en, de)")
    parser.add_argument("--model", "-m", default="medium",
                        help="Whisper model size (tiny/base/small/medium/large)")
    parser.add_argument("--output", "-o", help="Output file path (default: auto)")
    args = parser.parse_args()

    # Get video metadata
    print(f"Fetching video info...")
    info = get_video_info(args.url)
    title = info.get("title", "Unknown Video")
    print(f"Title: {title}")

    # Download audio to temp file
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = Path(tmpdir) / "audio.wav"
        print("Downloading audio...")
        download_audio(args.url, audio_path)

        # Find the actual output file (yt-dlp may add extension)
        wav_files = list(Path(tmpdir).glob("audio*"))
        if not wav_files:
            print("Error: No audio file found after download", file=sys.stderr)
            sys.exit(1)
        actual_audio = wav_files[0]
        print(f"Audio downloaded: {actual_audio.name}")

        # Transcribe
        text = transcribe_audio(actual_audio, args.model, args.language)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        SOURCES_DIR.mkdir(exist_ok=True)
        filename = sanitize_filename(title) + "_transcript.txt"
        output_path = SOURCES_DIR / filename

    # Write output matching existing format
    lang_note = f" (language: {args.language})" if args.language else ""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"{title}\n")
        f.write(f"Source: {args.url}\n")
        f.write(f"Model: whisper-{args.model}{lang_note}\n")
        f.write("=" * 60 + "\n\n")
        f.write(text.strip() + "\n")

    print(f"\nTranscript saved to: {output_path}")
    print(f"Length: {len(text.split())} words")


if __name__ == "__main__":
    main()
