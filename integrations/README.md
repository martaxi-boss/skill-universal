# Connecting clients

## Codex
Copy `integrations/AGENTS.md` to the root of an independent checkout as `AGENTS.md` (or keep it in the supplied repo and instruct Codex to read it). Put `skill/motor-universal-linux/SKILL.md` in the Codex Skill path supported by the installed client. Configure the MCP via the local Codex CLI where supported; run `python3 -m integrations.mcp_server` from this repository root.

## ChatGPT
Import `skill.zip` in the ChatGPT Skills area, if available. It cannot automatically SSH into a VPS. A trusted remote MCP endpoint, or a separately authorized GitHub Actions dispatch and SSH bridge in the **new** repository, must exist before real VPS commands can run. Local stdio MCP by itself is not a remote endpoint.

## Other hosts
Use a client-specific skill adapter pointing to the **same** `SKILL.md` and the standard MCP tools `motor_health`, `motor_catalog`, `motor_providers`, `motor_plan`, `motor_execute`. Test the host's support before announcing integration. API and filesystem permissions depend on that host.

## Deployment status
At delivery of this archive only the local Python CLI has been exercised. The remote bridge, SSH, installed tools on the target VPS and authentication remain unconfigured and unverified.