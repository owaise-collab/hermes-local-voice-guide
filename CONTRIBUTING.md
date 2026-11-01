# Contributing

Keep the guide reproducible and honest about what was tested. Reproduce a reported failure before changing a workaround. Include OS, architecture, Hermes version, llama.cpp build/backend, and a redacted error; do not attach raw user configuration, credentials, microphone recordings, or private transcripts.

The configuration tests use temporary directories. Run them through the selected Hermes runtime on a native Windows source install:

```powershell
.\scripts\Invoke-HermesPython.ps1 -Script .\tests\test_configure.py
.\scripts\Invoke-HermesPython.ps1 -Script .\tests\check_repository.py
```

For a separate contributor environment, use Python 3.11+ and install `requirements-test.txt` into that isolated environment, then run the two Python files. This is a test environment for this repository, not a way to mutate Hermes's venv.

Parse changed PowerShell scripts on Windows and exercise them against the supported source layout. Use `Configure-Hermes.ps1 -DryRun` before any real configuration change. Do not test against an active user home when a temporary directory can exercise the behavior.

Hardware checks are opt-in: `check-audio.py` does not record, `verify-voice.py --capture-microphone` briefly opens input without retaining it, and `listen-test.py` intentionally transcribes speech. Do not add background listening or cloud audio uploads to a troubleshooting command.

When adding another platform, document and run the full installation/runtime/audio test on that platform. Parser checks or mocked devices are insufficient evidence for a working microphone/GPU stack.
