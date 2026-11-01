# Platforms and requirements

## Tested path

The script-assisted path targets a native Windows x64 **source installation** of Hermes. It was derived from a working Windows setup with Hermes 0.22.5, managed Python 3.14.9, llama.cpp build 11960 (`8642541b2`), AMD Radeon RX 5700 8 GB using Vulkan, Faster-Whisper 1.2.1, sounddevice 0.5.5, and Piper 1.8.0.

You need a working microphone, an output device, storage for several gigabytes of model weights and runtime packages, and enough RAM/VRAM for your selected context and model. The pinned GGUF is 4,482,404,032 bytes. Piper and Whisper add their own downloaded model files. Allow extra disk space for package-manager generations and backups.

The original install was repaired and reconfigured on an existing machine. We did not wipe Windows or certify a completely clean machine installation. The fresh-install steps use the official installer and the same package-manager interfaces; they should be verified on your machine with the included checks.

## Other Windows configurations

| Configuration | Guidance |
| --- | --- |
| NVIDIA GPU | Choose an official compatible CUDA llama.cpp build; verify device detection. Not tested by this guide. |
| AMD GPU | The reference setup used Vulkan, not CUDA. Driver and model-kernel compatibility still matter. |
| CPU only | Use `-GpuLayers 0`; provide enough system RAM and expect lower speed. Not benchmarked here. |
| Windows ARM64 | The tested local Faster-Whisper/Piper extras are platform-gated. Do not assume this kit works unchanged. Use the official provider support matrix. |
| Signed Hermes Desktop/MSIX | Configure providers through Hermes UI/manual YAML. Do not inject packages into a signed payload using pip or these source-runtime helpers. |
| Custom source directory/profile | Pass explicit `-HermesHome` and `-HermesSource`, and verify the selected runtime. Only the default source layout was exercised end to end. |

The scripts use PowerShell syntax compatible with Windows PowerShell 5.1 and were checked with the installed PowerShell parser. Hardware validation happened on Windows; a Linux CI job is not a substitute for that test.

## Linux and macOS

The architecture and configuration concepts carry over, but the PowerShell launchers are Windows-specific. Install Hermes through its official platform instructions, use a compatible llama.cpp backend, and configure local STT/TTS in Hermes. Audio system dependencies and package availability differ. The complete Linux/macOS workflow has not been verified here.

Local Faster-Whisper is excluded by the tested Hermes dependency markers on native Windows ARM64 and Intel macOS. Do not force the install by editing markers. See the [official platform matrix](https://hermes-agent.nousresearch.com/docs/getting-started/platform-support) and [voice documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/voice-mode).
