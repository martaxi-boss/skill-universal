"""Read-only discovery of open-source candidates via GitHub's public API.

No paid providers, no arbitrary URLs, no source execution, no auto-installs.
All results still need manual license/Ubuntu/runtime verification.
"""
from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ENDPOINT = "https://api.github.com/search/repositories"
FREE_LICENSES = frozenset({
    "mit", "apache-2.0", "bsd-2-clause", "bsd-3-clause", "gpl-2.0",
    "gpl-3.0", "lgpl-2.1", "lgpl-3.0", "mpl-2.0", "agpl-3.0",
    "unlicense", "isc", "epl-2.0"
})

def discover(query: str, minimum_stars: int = 100, limit: int = 15,
             github_token: str | None = None) -> dict:
    """Search only GitHub source metadata. Unknown licenses are excluded."""
    if not isinstance(query, str):
        raise ValueError("Search query must be text")
    query = " ".join(query.strip().split())
    if not query or len(query) > 130 or re.search(r"[\x00-\x1f]", query):
        raise ValueError("Query must contain 1-130 printable characters")
    if re.search(r"\b(crack|keygen|serial\s*key|pirat|license\s*bypass)\b", query, re.I):
        raise ValueError("Search for free licensed replacements, not cracked binaries")
    if type(minimum_stars) is not int or minimum_stars < 0:
        raise ValueError("minimum_stars must be nonnegative")
    if type(limit) is not int or not 1 <= limit <= 30:
        raise ValueError("limit must be 1-30")
    # Fixed public endpoint. User input is only an encoded search parameter.
    term = query + " archived:false fork:false"
    params = urllib.parse.urlencode({
        "q": term, "sort": "stars", "order": "desc",
        "per_page": min(100, limit * 4),
    })
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "motor-ferrari-ubuntu-discovery",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = github_token or os.getenv("FERRARI_GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(ENDPOINT + "?" + params, headers=headers)
    # Python urllib verifies HTTPS certificates through its default SSL context.
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            raw = response.read(3_000_000)
        payload = json.loads(raw)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError("GitHub discovery unavailable: " + str(exc)[:220]) from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise RuntimeError("Invalid GitHub search response")
    found = []
    for repo in payload["items"]:
        if not isinstance(repo, dict):
            continue
        if repo.get("archived") or repo.get("fork"):
            continue
        license_info = repo.get("license") or {}
        spdx = license_info.get("spdx_id", "")
        if not isinstance(spdx, str) or spdx.lower() not in FREE_LICENSES:
            continue
        stars = repo.get("stargazers_count", 0)
        if not isinstance(stars, int) or stars < minimum_stars:
            continue
        full_name = repo.get("full_name", "")
        html_url = repo.get("html_url", "")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", full_name):
            continue
        if html_url != "https://github.com/" + full_name:
            continue
        found.append({
            "repository": full_name, "url": html_url, "stars": stars,
            "spdx_license": spdx, "last_push": repo.get("pushed_at"),
            "description": str(repo.get("description") or "")[:240],
            "ubuntu_compatibility": "unverified_candidate",
            "install_status": "NOT_INSTALLED",
            "source_code_reviewed": False, "automatic_install_allowed": False,
        })
        if len(found) >= limit:
            break
    return {
        "query": query, "results": found,
        "searched_at": datetime.now(timezone.utc).isoformat(),
        "provider": "public GitHub REST search",
        "license_filter": "known_free_spdx_ids_only",
        "note": "Stars and repository metadata do not prove Ubuntu support, quality or safety."
    }
