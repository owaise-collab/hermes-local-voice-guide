"""Test speech synthesis/transcription, with explicit optional hardware checks."""
import argparse
import json
from pathlib import Path
import wave


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--capture-microphone', action='store_true', help='Briefly open the default microphone; no microphone recording is saved.')
    parser.add_argument('--play', action='store_true', help='Play the synthetic test sentence.')
    args = parser.parse_args()
    from tools.tts_tool import text_to_speech_tool
    from tools.transcription_tools import transcribe_audio
    import numpy as np
    import sounddevice as sd
    out = args.output_dir.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    report = {'checks': {}, 'scope': 'synthetic speech roundtrip; hardware checks only when requested'}
    report_path = out / 'voice-check.json'

    def save():
        report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')

    text = 'Hello. I am Hermes. My local voice is ready. I can listen and help you finish tasks.'
    print('Synthesizing locally. First use may download a Piper voice.', flush=True)
    speech = json.loads(text_to_speech_tool(text, output_path=str(out / 'voice-check.wav')))
    if not speech.get('success'):
        report['error'] = speech
        save()
        raise SystemExit('Speech generation failed; see the local report.')
    path = Path(speech['file_path'])
    with wave.open(str(path), 'rb') as audio:
        report['speech_duration_seconds'] = audio.getnframes() / audio.getframerate()
    report['checks']['speech_generation'] = report['speech_duration_seconds'] > 0
    print('Transcribing locally. First use may download the Whisper model.', flush=True)
    result = transcribe_audio(str(path))
    transcript = str(result.get('transcript', result.get('transcription', result.get('text', '')))).lower()
    report['checks']['speech_roundtrip'] = bool(result.get('success')) and all(word in transcript for word in ('local','voice','listen','tasks'))
    if not result.get('success'):
        report['stt_error'] = result
    if args.capture_microphone:
        try:
            mic = sd.query_devices(None, 'input')
            rate = int(mic['default_samplerate'])
            print('Opening the default microphone for one second; audio is not saved.', flush=True)
            data = sd.rec(rate, samplerate=rate, channels=1, dtype='int16')
            sd.wait()
            report['checks']['microphone_capture'] = True
            report['microphone_peak'] = int(np.abs(data.astype(np.int32)).max())
        except Exception as exc:
            report['checks']['microphone_capture'] = False
            report['microphone_error'] = str(exc)
    if args.play:
        from tools.voice_mode import play_audio_file
        report['checks']['speaker_playback'] = bool(play_audio_file(str(path)))
    save()
    print(json.dumps(report['checks']), flush=True)
    print(f'Local report: {report_path}', flush=True)
    if not all(report['checks'].values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
