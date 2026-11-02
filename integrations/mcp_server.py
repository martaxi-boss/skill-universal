"""Optional MCP bridge for compatible authenticated hosts.

Start from this repository root with:
    python3 -m pip install 'mcp>=1,<2' --no-cache-dir
    python3 -m integrations.mcp_server

This binds to stdio only; a ChatGPT plugin cannot call it directly without a
supported connection. No public server, keys, or SSH are created here.
"""
from __future__ import annotations
import json
from pathlib import Path
from engine.core import environment, inventory, plan, providers, execute
try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:
    raise SystemExit("Python MCP SDK not installed: install mcp in a separate venv") from exc

mcp = FastMCP("motor-universal-linux")

@mcp.tool()
def motor_health() -> str:
    """Inspect real installed Linux capabilities, not a fabricated pass."""
    return json.dumps(environment(), ensure_ascii=False)

@mcp.tool()
def motor_catalog(category: str = "") -> str:
    """List free local candidate programs and actually detected executables."""
    return json.dumps(inventory(category or None), ensure_ascii=False)

@mcp.tool()
def motor_providers() -> str:
    """List candidate free providers; reports configured keys without exposing them."""
    return json.dumps(providers(), ensure_ascii=False)

@mcp.tool()
def motor_plan(request: str) -> str:
    """Select tasks and installed tool candidates without making changes."""
    return json.dumps(plan(request), ensure_ascii=False)

@mcp.tool()
def motor_execute(request: str, output: str, title: str = "Projeto Criativo", input_file: str = "") -> str:
    """Execute only the bounded local website, SVG or static inspection task."""
    return json.dumps(execute(request, Path(output), title, Path(input_file) if input_file else None), ensure_ascii=False)



# Ferrari v1 tools. No model or third-party hosting SDK is required here.
from engine import ferrari as ferrari_engine

@mcp.tool()
def ferrari_doctor() -> str:
    """Inspect Ubuntu host and real detected executables. Inventory, not certification."""
    return json.dumps(ferrari_engine.doctor(), ensure_ascii=False)

@mcp.tool()
def ferrari_catalog(category: str = "") -> str:
    """List upstream free-tool candidates, GitHub metadata, and binary detection."""
    return json.dumps(ferrari_engine.inventory(category or None), ensure_ascii=False)

@mcp.tool()
def ferrari_plan(request: str) -> str:
    """Route a user request to candidates without starting tools or charging providers."""
    return json.dumps(ferrari_engine.plan(request), ensure_ascii=False)

@mcp.tool()
def ferrari_run(operation: str, output: str, input_file: str = "", title: str = "Novo Projeto", layout: str = "landing") -> str:
    """Run one supported typed Ubuntu operation; never shell commands from prompts."""
    return json.dumps(ferrari_engine.run(operation, output, input_file or None, title, layout), ensure_ascii=False)


@mcp.tool()
def ferrari_alternatives(product: str) -> str:
    """Find legitimate Ubuntu software alternatives for commercial products."""
    return json.dumps(ferrari_engine.alternatives(product), ensure_ascii=False)

@mcp.tool()
def ferrari_discover(query: str, minimum_stars: int = 100, limit: int = 15) -> str:
    """Search free licensed GitHub upstream metadata, with no installation or code execution."""
    return json.dumps(ferrari_engine.discover(query, minimum_stars, limit), ensure_ascii=False)

@mcp.tool()
def ferrari_orchestrate(plan_json: str, workspace: str,
                       execute: bool = False, max_parallel: int = 2) -> str:
    """Validate or execute a bounded Ubuntu workflow with Ferrari tools only."""
    from engine.orchestrator import orchestrate
    plan_data = json.loads(plan_json)
    return json.dumps(orchestrate(plan_data, workspace, execute, max_parallel),
                      ensure_ascii=False)

if __name__ == "__main__":
    mcp.run(transport="stdio")
