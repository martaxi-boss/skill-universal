"""Evidence-based quality gate for Ferrari outputs, inside the existing Skill engine.

An executable returning zero only proves execution. This module checks technical
properties and explicitly refuses to call a file functional/professional merely
because it exists. Policy is supplied by the single authorized host; no LLM/API.
"""
from __future__ import annotations

from array import array
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys

from engine import tool_runtime

MEDIA_EXTENSIONS = frozenset({".mp4", ".mov", ".mkv", ".webm", ".mp3", ".m4a", ".wav", ".flac", ".ogg"})
VIDEO_EXTENSIONS = frozenset({".mp4", ".mov", ".mkv", ".webm"})
ALLOWED_KEYS = frozenset({"required_extensions", "audible_audio", "browser_evidence"})


def validate(policy):
    """Small, typed, backwards-compatible acceptance contract for a host job."""
    if policy is None:
        return None
    if not isinstance(policy, dict) or not policy or set(policy) - ALLOWED_KEYS:
        raise ValueError("Invalid Ferrari acceptance policy")
    extensions = policy.get("required_extensions", [])
    if (not isinstance(extensions, list) or len(extensions) > 12 or
            any(not isinstance(ext, str) or not re.fullmatch(r"\.[a-z0-9]{2,12}", ext)
                for ext in extensions) or
            len(set(extensions)) != len(extensions)):
        raise ValueError("Invalid required output extensions")
    for key in ("audible_audio", "browser_evidence"):
        if key in policy and type(policy[key]) is not bool:
            raise ValueError("Ferrari acceptance switch must be boolean")
    if not extensions and not policy.get("audible_audio") and not policy.get("browser_evidence"):
        raise ValueError("Acceptance policy requires a positive verification gate")
    return policy


def _owned_binary(name):
    # Never search PATH or use dependencies from other projects.
    root = tool_runtime.HOME.resolve(strict=False)
    exe = tool_runtime.executable("ffmpeg", name)
    if exe is None:
        return None
    path = Path(exe)
    if (not path.is_file() or path.is_symlink() or
            not path.resolve(strict=True).is_relative_to(root)):
        return None
    return str(path)


def _audio_measure(path):
    probe = _owned_binary("ffprobe")
    decoder = _owned_binary("ffmpeg")
    if not probe or not decoder:
        raise RuntimeError("Ferrari private FFmpeg and ffprobe are required for audio acceptance")
    env = dict(os.environ)
    env["PATH"] = str(Path(decoder).parent)
    env.pop("FFREPORT", None)
    info = subprocess.run(
        [probe, "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=index,codec_name", "-of", "json", str(path)],
        capture_output=True, text=True, check=False, timeout=25, env=env)
    if info.returncode != 0:
        raise RuntimeError("Ferrari private ffprobe could not inspect audio streams")
    try:
        streams = json.loads(info.stdout).get("streams", [])
    except ValueError as exc:
        raise RuntimeError("Ferrari ffprobe returned invalid JSON") from exc
    if not streams:
        return {"audio_stream": False, "audible": False, "rms_dbfs": None,
                "claim": "No audio stream exists"}
    # Short bounded PCM probe, 8 kHz mono, 30 seconds; no external URL or shell.
    decoded = subprocess.run(
        [decoder, "-nostdin", "-hide_banner", "-loglevel", "error",
         "-i", str(path), "-map", "0:a:0", "-vn", "-t", "30",
         "-ac", "1", "-ar", "8000", "-f", "s16le", "pipe:1"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False, timeout=55, env=env)
    if decoded.returncode != 0 or len(decoded.stdout) < 800:
        raise RuntimeError("Ferrari could not decode a valid audio sample")
    samples = array("h")
    samples.frombytes(decoded.stdout[:len(decoded.stdout) // 2 * 2])
    if sys.byteorder != "little":
        samples.byteswap()
    # Use a bounded sample; the input is at most 30s and 8k frames/sec.
    rms = math.sqrt(sum(float(s) * s for s in samples) / len(samples)) / 32768.0
    rms_dbfs = 20.0 * math.log10(max(rms, 1e-10))
    return {"audio_stream": True, "audible": rms_dbfs > -52.0,
            "rms_dbfs": round(rms_dbfs, 2),
            "claim": "Audible energy measured, NOT proof of speech or voice quality"}


def inspect(files, acceptance=None):
    """Return explicit checks. Fail if a requested acceptance condition is unmet.

    In absence of acceptance, static signatures are checked, but semantic
    fulfillment is always unverified, never assumed from a successful tool.
    """
    policy = validate(acceptance)
    paths = [Path(p) for p in files]
    checks = []
    failures = []
    warnings = []
    extensions = {p.suffix.lower() for p in paths}
    for p in paths:
        if p.is_symlink() or not p.is_file() or p.stat().st_size == 0:
            failures.append("Empty or nonregular Ferrari artifact")
            continue
        ext = p.suffix.lower()
        if ext == ".pdf" and not p.open("rb").read(5) == b"%PDF-":
            failures.append("Invalid PDF signature")
        if ext == ".png":
            with p.open("rb") as handle:
                head = handle.read(24)
            if (len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n"
                    or int.from_bytes(head[16:20], "big") == 0
                    or int.from_bytes(head[20:24], "big") == 0):
                failures.append("Invalid PNG signature or dimensions")
        if ext == ".mp4":
            with p.open("rb") as handle:
                head = handle.read(12)
            if len(head) < 12 or head[4:8] != b"ftyp":
                failures.append("Invalid MP4 container header")
    checks.append({"check": "artifact-signatures", "status": "failed" if failures else "passed"})

    if policy is not None:
        for ext in policy.get("required_extensions", []):
            found = ext in extensions
            checks.append({"check": "required-extension", "extension": ext,
                           "status": "passed" if found else "failed"})
            if not found:
                failures.append("Missing required artifact extension: " + ext)
        if policy.get("audible_audio"):
            found_media = [p for p in paths if p.suffix.lower() in MEDIA_EXTENSIONS]
            if not found_media:
                failures.append("Audible audio was requested but no media was generated")
            else:
                for p in found_media:
                    try:
                        evidence = _audio_measure(p)
                        success = evidence["audible"]
                        checks.append({"check": "audible-audio", "artifact": p.name,
                                       "status": "passed" if success else "failed", **evidence})
                        if not success:
                            failures.append("Silent or missing audio in artifact: " + p.name)
                    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
                        failures.append("Audio acceptance could not be certified: " + str(exc)[:180])
        if policy.get("browser_evidence"):
            reports = [p for p in paths if p.name == "browser-check.json"]
            mobile = [p for p in paths if p.name == "browser-mobile.png"]
            desktop = [p for p in paths if p.name == "browser-screenshot.png"]
            passed = bool(reports and mobile and desktop)
            issues = []
            if passed:
                try:
                    evidence = json.loads(reports[0].read_text(encoding="utf-8"))
                    m = evidence.get("mobile", {})
                    interactions = evidence.get("interactions", {})
                    if evidence.get("status") != "passed":
                        issues.append("Playwright browser did not pass")
                    if evidence.get("viewport") != {"width": 1280, "height": 720}:
                        issues.append("Desktop viewport was not verified")
                    if type(evidence.get("body_text_chars")) is not int or evidence["body_text_chars"] < 1:
                        issues.append("Browser has no verified rendered text")
                    if evidence.get("dom_ready") not in {"complete", "interactive"}:
                        issues.append("Document did not reach DOM readiness")
                    if not isinstance(m, dict) or m.get("viewport") != {"width": 390, "height": 844}:
                        issues.append("Mobile 390x844 viewport is missing")
                    if not isinstance(m, dict) or m.get("viewport_meta_present") is not True:
                        issues.append("Mobile viewport metadata missing")
                    if not isinstance(m, dict) or m.get("horizontal_overflow_px") != 0:
                        issues.append("Mobile has unverified horizontal overflow")
                    if not isinstance(m, dict) or m.get("spotcheck_status") != "clear" or m.get("findings") != []:
                        issues.append("Mobile usability findings are unresolved")
                    if not isinstance(interactions, dict) or interactions.get("status") != "clear" or interactions.get("findings") != []:
                        issues.append("Keyboard and interactive usability findings are unresolved")
                    for key in ("page_errors", "console_errors", "blocked_external"):
                        if evidence.get(key) != []:
                            issues.append("Browser has unresolved " + key)
                except (OSError, ValueError, UnicodeError, TypeError, AttributeError):
                    issues.append("Browser report is malformed or unreadable")
            if not passed:
                issues.append("Real Playwright report and both viewport screenshots are required")
            checks.append({"check": "browser-evidence",
                           "status": "failed" if issues else "passed",
                           "issues": issues,
                           "note": "Verified local browser/mobile checks do NOT prove deployed website UX, geolocation, checkout or commercial content"})
            if issues:
                failures.extend(issues)
            else:
                warnings.append("Host must still inspect screenshots and test the deployed site, routing, navigation and commerce")
    elif any(ext in MEDIA_EXTENSIONS or ext in {".html", ".svg"} for ext in extensions):
        warnings.append("Output was generated; audio, usability, and editorial requirements were not requested as acceptance checks")

    return {"status": "failed" if failures else "passed" if policy is not None else "not_certified",
            "checks": checks, "failures": failures, "warnings": warnings,
            "acceptance_requested": policy is not None,
            "note": "Technical checks do not certify factual accuracy, visual design, natural speech or legal compliance"}
