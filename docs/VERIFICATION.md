# Public kit verification

Verified on Windows on November 1, 2026, using the existing working Hermes source installation described in this guide.

| Public kit check | Result |
| --- | --- |
| Nine configuration behavior tests using temporary homes | Passed |
| Relative documentation links | Passed |
| Python syntax and bundled skill metadata | Passed |
| Example YAML parsing | Passed |
| Six PowerShell scripts parsed without errors | Passed |
| Runtime discovery through Hermes PM interfaces | Passed |
| Configurator dry run against the active source layout | Passed; no config changes |
| Server launcher recognizing the existing correct local model | Passed |
| Public voice diagnostic generating and transcribing synthetic speech | Passed |
| Downloader recognizing the existing pinned GGUF by SHA256 | Passed; no re-download or overwrite |
| Publication scan for personal absolute paths, live credential patterns, binaries, and user-state files | Passed |

The hardware microphone/live-transcription, child-agent, and spoken-reply checks were completed in the underlying setup before the public kit was generalized. See the [reference validation record](06-validation-and-rollback.md#reference-validation-record).

We have not certified a fresh Windows installation, every GPU/driver, another OS, a different model, or a signed Desktop bundle using these source helpers. The download script's pinned artifact was verified in the original setup; a fresh multi-gigabyte download is not part of the lightweight regression suite. There is no hosted CI claim for microphone/GPU behavior.
