# 4. Troubleshooting

Work from the failing layer outward. A working speaker does not prove microphone capture; a healthy llama.cpp server does not prove tool calling; a child's claim does not prove its artifact exists.

## Hermes says its dependency environment is missing

Run `hermes pm repair` under the user account that owns the source installation, then restart Hermes. The reference install needed this repair before it could run. Do not pip-install into its managed venv or replace a generation with an older directory.

If repair reports that install state is not writable, check the user, source/data paths, and permissions. A restricted automation sandbox can present a different local app-data path. Repair the actual user's install in a normal authorized shell; do not create a second accidental installation in a redirected sandbox directory.

## `gateway_elevated`: the CLI cannot reach the gateway

An older gateway may have been started as administrator. Stop it from its owning elevated shell, then restart Hermes as your normal user:

```powershell
hermes gateway stop
hermes gateway start
```

If the elevated process cannot be stopped from a normal account, return to the shell that started it. Do not indiscriminately kill all Python processes. The original setup needed a clean gateway restart after this mismatch.

After installing new speech extras or changing provider configuration, restart Hermes so it loads the selected dependency generation and fresh settings. Drain active work first.

## Hermes rejects a 32K context

The tested Hermes build enforces a 64,000-token minimum. Set the server to `--ctx-size 65536` and set `model.context_length: 65536`. Keep one slot for the reference configuration.

Check the actual `n_ctx` from `/props`. A model with a smaller native/training context may be capped by llama.cpp even when you requested 65,536. Do not merely lie in config about the available context; choose a compatible model. More context also consumes memory, so reduce model size or use another supported model if it does not fit.

## Port 8080 is occupied or the wrong model answers

Inspect `/health`, `/props`, and `/v1/models` for the intended local endpoint. The launch script refuses to reuse a port serving a different model path or alias.

Choose another port with `-Port 8081` and use that same port in `Configure-Hermes.ps1` and `Start-Hermes.ps1`. The included stop script stops only a process it started and recorded; it verifies executable path and process start time before acting.

## Native tool calls appear as ordinary text

Use a tool-capable model and its correct chat template. The reference llama.cpp command includes `--jinja`. Check model/build compatibility, then run the structured-call test in the validation guide. A model that can chat may still be a poor agent.

## Voice mode reports available, but recording fails with device `-1`

Run `check-audio.py`. If its input list is empty, there is no recording device exposed to that Python process. The reference machine initially exposed only output devices; a generic availability check was therefore insufficient.

Connect or enable a microphone, choose it as the default Windows input, and verify the Windows level meter. Then restart Hermes and the diagnostic. In the reference setup, an active headset input eventually appeared and the capture test passed.

For 3.5 mm devices, distinguish the microphone jack from headphone output and check whether a headset splitter is needed. For Bluetooth, select the hands-free microphone endpoint and confirm the headset supports/has connected that profile. Hardware, driver, and Windows privacy choices must be checked separately; changing an AI model will not create a missing input device.

## Speech recognition is wrong, empty, or hallucinates on silence

Check microphone placement, volume, background sound, and input language. Whisper `base` trades accuracy for a small CPU footprint; larger supported models can improve some tasks at higher resource cost. Keep VAD enabled and validate against real speech.

Do not treat a successful synthetic roundtrip as proof of perfect live recognition. If speech could change an important action, clarify the words before executing. The live test script fails on an empty transcript, but a nonempty transcript still needs a human accuracy check.

## TTS generates a file but no one hears it

First inspect the synthetic WAV and selected Windows output device. Run `verify-voice.py` with `--play`. A successful synthesis only proves file creation; playback through the right output is a separate check.

In interactive Hermes, enable `/voice on`; `voice.auto_tts: true` enables spoken replies when that mode starts. `/voice tts` is a toggle within voice mode, not a standalone always-on speaker command. An audio attachment from a one-shot tool call is not necessarily automatically played by every client.

## First speech use waits while models download

Piper downloads the selected voice; Faster-Whisper downloads its STT model. Wait for those initial downloads, check network access to the upstream host, and inspect Hermes logs if a transfer fails. Do not publish logs without redacting credentials, user paths, and private prompts.

Hugging Face symlink warnings on Windows are not necessarily failures: its cache can fall back to file copies. The reference STT download worked without enabling Developer Mode or running the agent as administrator. Do not weaken Windows security just to silence that warning.

## A GitHub skill URL does not install

Use the exact identifier returned by `hermes skills search`, or a direct raw `SKILL.md` HTTPS URL. The reference repository-tree URL failed, while its raw file URL succeeded. Inspect dependencies and keep the installer's scan enabled.

Use `--json --limit 5` when asking a small model to read catalog output. Do not cut a live Rich-formatted command off with a pipe that closes early; that produced a terminal-output error during testing. Re-running the bounded JSON command completed normally.

## A child finishes, but its summary is unreliable

Read its artifact and test the behavior. In the reference run, a child created the correct file but struggled with an output contract correction; the parent independently read and verified the file. Prefer concise plain-text results unless machine-readable JSON is needed.

Keep the interactive parent session open for background completion. Do not poll indefinitely, duplicate work, or claim success while a handle is still pending. Single-worker limits keep this modest GPU usable, but do not guarantee fast or correct reasoning.

## Python throws a Windows `UnicodeDecodeError`

Use explicit `encoding='utf-8'` when reading this repository's files, or run Python with `-X utf8`. `Invoke-HermesPython.ps1` does this. The original verification helper needed that correction when Windows defaulted to a legacy code page.

The configurator writes UTF-8 with explicit LF newlines. This avoids the extra blank lines that appeared when a Windows roundtrip YAML edit mixed newline conventions. Its tests verify preservation and repeatability.
