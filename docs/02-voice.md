# 2. Give Hermes speech and listening

## 2.1 Start with Windows devices

Before changing AI settings, connect your microphone and speakers or headset. In Windows **Settings → System → Sound**, choose the intended input and output devices. Speak and check the input meter.

A 3.5 mm desktop microphone normally needs the microphone input, often pink, rather than the green headphone output. A four-pole headset used with separate desktop headphone/microphone jacks may need a suitable splitter. Bluetooth speech input usually appears through a hands-free endpoint; reconnecting or changing profiles can change the default device. A headset being connected for playback does not prove its microphone is available.

Do not open Windows security/privacy dialogs through an automated workaround. If Windows asks you to grant microphone permission, review and make that choice yourself. The scripts do not change privacy settings.

## 2.2 Install native speech support through Hermes

```powershell
hermes pm install --extra voice --extra piper
```

In the tested source install, `voice` provided sounddevice, numpy, and supported Faster-Whisper dependencies; `piper` provided local Piper speech. The `all` extra did not already include every voice feature. Use Hermes PM instead of mutating its environment with pip.

Restart Hermes after its dependency environment changes. The public helper resolves the currently selected environment; it does not assume a particular install ID or generation directory.

## 2.3 Apply the setup kit

From this repository:

```powershell
.\scripts\Configure-Hermes.ps1 -DryRun
.\scripts\Configure-Hermes.ps1
```

The first command previews the affected areas without writing user data or installing dependencies. The second installs speech extras, backs up configuration/SOUL/skills, merges local settings, and copies the two bundled skills.

If you already installed the extras, `-SkipDependencies` skips that package-manager step. For a non-default layout:

```powershell
.\scripts\Configure-Hermes.ps1 -HermesHome 'D:\HermesData' -HermesSource 'D:\Code\hermes-agent' -Port 8081
```

Use the same endpoint, alias, and context in the server launcher. The configurator deliberately clears main and delegated model fallback chains and resets the listed text auxiliaries to `main`; inspect the dry-run summary and backup before using it with an existing advanced routing setup. It preserves unrelated configuration and existing SOUL text.

## Manual configuration

If you prefer editing YAML, merge [the example fragment](../config/hermes-local.example.yaml) into your active `config.yaml`. It is not a replacement for an entire user configuration. Keep only one top-level block for each key: duplicate `stt:`, `tts:`, or `model:` blocks can be rejected or accidentally override settings.

The essential speech settings are:

```yaml
stt:
  enabled: true
  provider: local
  language: en
  local:
    model: base
    device: cpu
    compute_type: int8
    vad: true

tts:
  provider: piper
  piper:
    voice: en_US-lessac-medium
    use_cuda: false

voice:
  record_key: ctrl+b
  auto_tts: true
  silence_duration: 2.0
  stop_phrases: [stop, goodbye hermes]
```

CPU speech avoids competing with the local LLM for GPU memory. `vad` reduces silence-related hallucinations; it does not guarantee perfect recognition. `language: en` is an English hint. Change it to the intended supported language or use automatic detection if appropriate. A different language also needs an appropriate TTS voice; recognition language and speech voice are separate settings.

Piper's selected voice and Whisper's `base` model download on first use. Piper's cache lives under the Hermes home; Faster-Whisper normally uses the Hugging Face cache. The first use therefore requires internet even when later inference is local.

For signed Desktop installations, use the built-in provider setup UI and supported dependency management. Do not point the source-runtime helper at an app bundle or use pip inside it. Check the official [voice](https://hermes-agent.nousresearch.com/docs/user-guide/features/voice-mode) and [TTS](https://hermes-agent.nousresearch.com/docs/user-guide/features/tts) documentation for your installed version.

## 2.4 Check devices and speech independently

```powershell
$HermesData = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $env:LOCALAPPDATA 'hermes' }
$VoiceChecks = Join-Path $HermesData 'runtime\voice-guide-checks'
.\scripts\Invoke-HermesPython.ps1 -Script .\scripts\check-audio.py
.\scripts\Invoke-HermesPython.ps1 -Script .\scripts\verify-voice.py -ScriptArgs @('--output-dir', $VoiceChecks, '--capture-microphone', '--play')
```

The device check records nothing. The verification synthesizes a known sentence, transcribes it locally, optionally opens the microphone for one second without saving that capture, and optionally plays the sentence. Expect every requested check to be `true`.

This distinguishes microphone access from speech recognition accuracy. The synthetic roundtrip validates STT/TTS; a real listening test is still needed to check your voice and surroundings.

## 2.5 Talk to Hermes

Start the server and chat:

```powershell
.\scripts\Start-Hermes.ps1
```

Inside Hermes, enter `/voice on`, then press **Ctrl+B**. A beep signals capture. Speak naturally and pause; after about two seconds of silence, Hermes transcribes and answers. With `auto_tts: true`, the reply is spoken and the voice loop can continue automatically.

| Control | Meaning |
| --- | --- |
| `/voice on` | Enable the interactive voice feature |
| Ctrl+B | Start recording; during recording, end the continuous loop |
| Say exactly `stop` | End the current voice conversation |
| `/voice tts` | Toggle spoken output while voice mode is enabled |
| `/voice status` | Inspect the current mode and requirements |
| `/voice off` | Disable voice mode |

If you connected a microphone after Hermes started, restart the client so its audio library refreshes device state. There is no always-on wake word in this setup; that is a separate Hermes feature.

Continue with [skills and agents](03-skills-and-agents.md).
