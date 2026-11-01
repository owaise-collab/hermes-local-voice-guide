"""Record a short, explicit live listening test and transcribe locally."""
import argparse
import json
from pathlib import Path
import wave


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=15)
    parser.add_argument('--keep-audio', action='store_true', help='Retain the microphone recording; default is to delete it after transcription.')
    args = parser.parse_args()
    if not 1 <= args.seconds <= 60:
        parser.error('--seconds must be between 1 and 60')
    import sounddevice as sd
    from tools.transcription_tools import transcribe_audio
    from tools.voice_mode import play_beep
    mic = sd.query_devices(None, 'input')
    rate = int(mic['default_samplerate'])
    out = args.output_dir.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    path = out / 'microphone-test.wav'
    print(f'Recording {args.seconds} seconds. Say: Hello Hermes, what is two plus two?', flush=True)
    play_beep()
    data = sd.rec(rate * args.seconds, samplerate=rate, channels=1, dtype='int16')
    sd.wait()
    with wave.open(str(path), 'wb') as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(rate)
        stream.writeframes(data.tobytes())
    try:
        result = transcribe_audio(str(path))
        transcript = str(result.get('transcript', result.get('text', ''))).strip()
        result['nonempty_transcript'] = bool(transcript)
        (out / 'live-transcript.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result), flush=True)
        if not result.get('success') or not transcript:
            raise SystemExit('No recognized speech. Check the microphone, level, and language setting.')
    finally:
        if not args.keep_audio:
            path.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
