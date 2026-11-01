# 1. Install the agent and local model

## 1.1 Choose the supported route

This walkthrough uses a normal, non-administrator Windows x64 account and the native source installer. Hermes Desktop bundles have a different runtime ownership model; use the manual configuration guidance for those bundles.

First read the [official installation instructions](https://hermes-agent.nousresearch.com/docs/getting-started/installation). The published Windows source installation command is:

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

This downloads and executes the official installer. If you prefer to inspect it first, download that URL to a file, read it, then run the reviewed script. Do not run random third-party installer copies. The installer handles its managed Python and other runtime tools; you do not need to pip-install Hermes into a system Python.

Open a new PowerShell window after installation and check:

```powershell
hermes --version
hermes pm doctor
```

The tested installation reported Hermes 0.22.5. Later releases may change settings or command flags. Check `--help` and the current official documentation if a command differs.

## 1.2 Repair an existing broken install only when necessary

If `hermes` reports that no dependency environment is committed, or suggests repair:

```powershell
hermes pm repair
```

Restart Hermes after repair. Do not fix its managed environment with a raw `pip install`, copy old venv directories between machines, or delete its user-data directory. See [troubleshooting](04-troubleshooting.md) if permissions or gateway elevation block it.

## 1.3 Get llama.cpp

Use the [official llama.cpp releases](https://github.com/ggml-org/llama.cpp/releases). Choose a Windows x64 build for your backend, extract the **whole archive**, and keep the DLLs beside `llama-server.exe`.

The reference setup used a Vulkan build at `C:\AI\llama.cpp`. This path is a convention, not a requirement. NVIDIA systems may use a compatible CUDA build; CPU systems can use a CPU build. Do not choose CUDA for an AMD GPU.

```powershell
& 'C:\AI\llama.cpp\llama-server.exe' --version
& 'C:\AI\llama.cpp\llama-server.exe' --list-devices
```

The reference device list identified a Radeon RX 5700 through Vulkan. If your expected GPU is absent, fix the driver/build choice before assuming GPU acceleration works.

## 1.4 Choose a model

The guide uses [InternScience Agents-A1-4B](https://huggingface.co/InternScience/Agents-A1-4B), an agent-focused model in the roughly 4B class. The choice was made under a requested 6B parameter budget. It is not a claim that this is the best model for every workload.

The default downloader uses the publisher's official Q8_0 GGUF repository:

| Item | Value |
| --- | --- |
| Repository | `InternScience/Agents-A1-4B-Q8_0-GGUF` |
| Revision | `a5d63881e0ca8eee3c0f14663a5fa2a2c55e1b54` |
| File | `Agents-A1-4B-Q8_0.gguf` |
| Size | `4482404032` bytes |
| SHA256 | `c327f66e820dae550bd230394595071c79f48c88d411b452d013ee4b5999fcea` |

Another GGUF is fine if your llama.cpp build supports its architecture, it supports structured tool calling, its real context window is at least 64K for this Hermes version, and it fits your hardware. A smaller file is not enough by itself: the earlier downloaded Qwen3-4B model in the original setup had a smaller training context and was capped below the required window.

## 1.5 Clone this guide and download the model

```powershell
git clone https://github.com/owaise-collab/hermes-local-voice-guide.git
cd hermes-local-voice-guide
$HermesData = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $env:LOCALAPPDATA 'hermes' }
$ModelFile = Join-Path $HermesData 'models\Agents-A1-4B-Q8_0.gguf'
.\scripts\Invoke-HermesPython.ps1 -Script .\scripts\download-model.py -ScriptArgs @('--output', $ModelFile)
```

The downloader resumes a `.partial` file and verifies SHA256 before renaming it to the final model path. A complete destination with the wrong checksum is not overwritten. If verification fails, remove only that failed partial file and retry.

The original download was slow on a single connection; smaller parallel HTTP ranges worked around that network condition. The reusable public downloader uses simple curl resume instead of carrying a complex network-specific range implementation. It may take longer on that same network, but it never accepts an unverified model. A download manager can also be used with the pinned URL; verify the final hash yourself.

## 1.6 Start and inspect the server

```powershell
.\scripts\Start-LocalServer.ps1 -ModelPath $ModelFile
Invoke-RestMethod http://127.0.0.1:8080/health
$ServerProps = Invoke-RestMethod http://127.0.0.1:8080/props
$ServerProps.model_path
$ServerProps.default_generation_settings.n_ctx
```

Expect healthy status, the model you selected, and `65536` context tokens. The launcher verifies actual runtime context rather than trusting the advertised model window.

The server binds to `127.0.0.1`, uses `--jinja` for chat/tool templates, and allocates one slot. It stays running after chat closes. For CPU-only use add `-GpuLayers 0`. For custom paths, port, alias, or context, pass the corresponding parameters and use the same values when configuring Hermes.

No vision projector is installed by this guide. This setup validates text and audio workflows, not image understanding.

Continue with [voice setup](02-voice.md).
