"""List Windows audio devices; no recording and no playback."""
import json
import sounddevice as sd

devices = list(sd.query_devices())
inputs = [device for device in devices if device['max_input_channels'] > 0]
outputs = [device for device in devices if device['max_output_channels'] > 0]
print(json.dumps({'default_input_output': list(sd.default.device), 'inputs': inputs, 'outputs': outputs}, indent=2))
if not inputs:
    raise SystemExit('No recording input. Connect/enable a microphone in Windows, then restart Hermes.')
try:
    mic = sd.query_devices(None, 'input')
    sd.check_input_settings(channels=1, dtype='int16', samplerate=int(mic['default_samplerate']))
    print(f"Default microphone can be opened: {mic['name']}")
except Exception as exc:
    raise SystemExit(f'Select a working default microphone in Windows Sound settings: {exc}')
