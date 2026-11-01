# 6. Validation and rollback

Run these checks in order. Stop at the first failing layer rather than changing several things at once.

## Server health and real context

```powershell
Invoke-RestMethod http://127.0.0.1:8080/health
$Props = Invoke-RestMethod http://127.0.0.1:8080/props
$Props.model_path
$Props.model_alias
$Props.default_generation_settings.n_ctx
```

Expect the model you selected, alias `local-hermes`, and an actual context of 65,536. Health alone does not validate chat templates or tool calls.

## Structured tool calling

In PowerShell:

```powershell
$Request = @{
  model = 'local-hermes'
  messages = @(@{role='user'; content='What is 17 times 23? Use the multiply tool.'})
  tools = @(@{
    type='function'
    function=@{
      name='multiply'
      description='Multiply two integers'
      parameters=@{
        type='object'
        properties=@{a=@{type='integer'}; b=@{type='integer'}}
        required=@('a','b')
      }
    }
  })
  max_tokens=256
  temperature=0.1
}
$Reply = Invoke-RestMethod 'http://127.0.0.1:8080/v1/chat/completions' -Method Post -ContentType 'application/json' -Body ($Request | ConvertTo-Json -Depth 12) -TimeoutSec 120
$Reply.choices[0].message.tool_calls | ConvertTo-Json -Depth 6
```

Expect a structured `multiply` call with arguments 17 and 23. This checks formatting and tool selection; it does not execute the multiplication tool.

## Hermes terminal and skill checks

```powershell
hermes chat --cli --oneshot -Q -t terminal --max-turns 3 --run-budget 120 -q 'Use the terminal tool to run echo HERMES_LOCAL_OK, then report the output.'
hermes skills search find-skills --limit 3 --json
hermes chat --cli --oneshot -Q -t skills --max-turns 5 --run-budget 180 -q 'Read the installed find-skills skill using skill_view. Name its GitHub source and native Hermes install command. Do not install anything.'
```

Check actual tool execution, not just the final prose. The source should be Vercel's repository and the install command should use `hermes skills install`.

## Speech roundtrip and hardware checks

```powershell
$HermesData = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $env:LOCALAPPDATA 'hermes' }
$Checks = Join-Path $HermesData 'runtime\voice-guide-checks'
.\scripts\Invoke-HermesPython.ps1 -Script .\scripts\check-audio.py
.\scripts\Invoke-HermesPython.ps1 -Script .\scripts\verify-voice.py -ScriptArgs @('--output-dir', $Checks, '--capture-microphone', '--play')
```

The synthetic WAV is local. The optional one-second capture is not saved or transcribed. A nonzero peak suggests an input signal, but does not prove recognizable speech. Speaker playback success means the software playback call succeeded; confirm you actually heard it through the intended device.

## Live listening test

Use native `/voice on` and Ctrl+B for the most representative test. Say a simple question, verify Hermes's transcription and answer, and confirm you hear the reply.

For a separate diagnostic:

```powershell
.\scripts\Invoke-HermesPython.ps1 -Script .\scripts\listen-test.py -ScriptArgs @('--output-dir', $Checks, '--seconds', '15')
```

After the beep, speak the displayed phrase. The script transcribes locally, writes `live-transcript.json`, and deletes its temporary recording by default. Add `--keep-audio` only when you intentionally want to retain that recording. A transcript can contain private speech; do not commit or upload it as a bug report without reviewing it.

## Test a real child agent

Start an interactive Hermes session and keep it open. Substitute a harmless test path in your own local workspace:

> Call delegate_task once. Give the child the goal of using write_file to create D:/Scratch/hermes-agent-check.txt containing HERMES_AGENT_OK. Context: this is a local setup test; modify only that file; return a short plain-text summary, without an output schema. After its completion arrives, read the file yourself and verify its contents. Do not create the file in the parent.

Verify the child actually ran, completion was delivered, and the parent read the file. An acknowledgment that work is pending is not the final result. Whitespace/newline differences should be reported rather than hidden.

## Public kit regression checks

These tests use temporary directories and do not write your active config:

```powershell
.\scripts\Invoke-HermesPython.ps1 -Script .\tests\test_configure.py
```

They validate settings preservation, local routing, dry-run behavior, idempotence, backups, invalid context/endpoint rejection, and portable bundled skill metadata. Hardware and LLM tests are manual/operational because a hosted CI runner cannot stand in for your microphone and GPU.

## Reference validation record

The original Windows configuration completed the following checks on November 1, 2026:

| Check | Result | Scope |
| --- | --- | --- |
| Official GGUF size/SHA256 | Passed | Pinned model artifact |
| Local server identity and 65,536 context | Passed | Actual `/props` response |
| Native structured function call | Passed | Correct tool and integer arguments |
| Hermes terminal command | Passed | Real echo output |
| GitHub skill install/scan and model skill retrieval | Passed | Retrieved content at that time |
| Public skills search | Passed | Vercel catalog entry returned |
| Child-agent file creation and parent verification | Passed | One real child, then independent read |
| Piper generation and synthetic Whisper roundtrip | Passed | CPU speech engines |
| Microphone capture and live transcription | Passed | The selected Windows headset input |
| Speaker playback and Hermes-generated spoken reply | Passed | Selected output device |

The public helpers were generalized from that setup and are separately checked; the regression suite and diagnostic rerun are not a clean-machine certification. No original recordings, personal transcripts, application logs, session IDs, or user-data snapshots are included as evidence.

## Roll back configuration

The configurator prints a backup directory under `<HermesHome>/backups/local-voice-guide-<timestamp>`. Close/drain active Hermes work first. Restore the backed-up `config.yaml` and `SOUL.md`, then restart Hermes. Restore any backed-up skill files; if a bundled skill did not exist before installation, remove only that new skill folder if you no longer want it.

The backups do not uninstall package-manager extras or erase downloaded models. Leaving those files installed does not force voice mode on. Use the official Hermes package-management instructions for dependency changes; do not manually edit its selected venv.

## Stop the model server

```powershell
.\scripts\Stop-LocalServer.ps1
```

This stops only a guide-owned process with a matching executable path and start time. If the launcher reused an already running server, there may be no guide process record; stop that server through the method that originally launched it. Do not kill every Python or llama process on the computer.
