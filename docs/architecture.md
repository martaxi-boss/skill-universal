> **NOTA DE HIGIENIZAÇÃO (03/11/2026): documentação histórica ou de procedimento, não fotografia atual da VPS.** Para release, contagens, REA próprio, Apktool 3.0.3 e pendências reais, consultar primeiro [BOOTSTRAP.md](../BOOTSTRAP.md), confirmado pelos runs [#41671631900](https://github.com/martaxi-boss/VPS/actions/runs/41671631900) e [#41672372249](https://github.com/martaxi-boss/VPS/actions/runs/41672372249). Referências nesta página a instalações pendentes, versões antigas ou ligação não certificada descrevem etapas passadas; não executar instalações automaticamente.

# Capabilities and staged realization

| Task | Tool candidates | Current implementation | Caveat |
|---|---|---|---|
| Professional site | Original responsive HTML template; optional Vite/Astro/Next/Tailwind/shadcn | Working editable HTML | Not a production full-stack app |
| Social creative | Original SVG template; Inkscape/ImageMagick/Blender/FFmpeg candidates | Working editable SVG | No prompt-to-photo model in CPU-only prototype |
| APK/native analysis | file, binutils, apktool, JADX, Ghidra, REA | Basic file hash/type, ZIP listing, ELF header | Actual decompiler needs independent installation and tests |
| Video/sound | FFmpeg, SoX, eSpeak, optional Piper | Installed-tool detection only | Production timeline, audio voices and render not implemented |
| Documents/data | LibreOffice, Pandoc, Poppler, Tesseract, SQLite, PostgreSQL clients | Inventory only | No claims of file conversions or DB operations |
| Agent orchestration | Ruflo and host model | Candidate inventory only | Ruflo requires its own runtime and host credentials |
| Cloud AI | OpenRouter free, Gemini, Groq, HF, Cloudflare | Provider configuration detection | Live free tier and quotas not verified |

## Installation states

`catalogued` -> `apt available` -> `installed` -> `functional smoke tested` -> `ready for tasks`.

Never collapse all these into one 'OK'. Log version, actual binary path, host ID, test outcome and provenance.

## What 'maximum' means

Maximum **verified compatibility** with the user's Ubuntu CPU, RAM, disk, toolchain and available providers, not an unconditional install of all programs. Heavy apps and models can consume many GiB and some are GUI- or GPU-dependent. Runtime detects candidates; packages can be installed once by profile after disk assessment. Keep the engine isolated from all old projects; third-party packages get independent namespaces or venvs as appropriate.

## REA (separate upstream copy)

Source: https://github.com/morluto/rea. Its command-line distribution is `rea-agents`. Use only its Linux-compatible, freely usable providers; do not require paid Hopper or macOS. Linux Java/Ghidra, JADX and relevant CLI capabilities require individual checks. A separate copy under the new project is **not** the user's existing REA FINAL installation.

## Stable bridge contract

Request: task type + input files + output directory + user instruction.
Response: selected engine/tool, version, actual actions performed, output artifact paths, warnings and verification. A single Skill can describe this contract, but each host still needs compatible tooling and authorization.

## Future implementation packages (not shipped as working)

Dedicated installers with exact upstream hashes, genuine image-generation provider selection, web design catalog, REA installer + smoke tests, video pipeline, authenticated ChatGPT bridge, secure background job queue, and resource-aware Ruflo orchestration. These are explicit future milestones, not already functioning components.