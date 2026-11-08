"""Real Prometheus adapter: rules are parsed by private promtool, not by a mock parser."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from engine import catalog_registry, ferrari, monitor_tools


RULES = """groups:
  - name: ferrari_synthetic
    rules:
      - record: ferrari_synthetic_metric
        expr: vector(1)
"""


class FerrariPrometheusRulesTests(unittest.TestCase):
    def _fixture(self, root):
        (root / ".runtime/input").mkdir(parents=True)
        tool = root / monitor_tools.PROMTOOL_RELATIVE
        tool.parent.mkdir(parents=True)
        tool.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        tool.chmod(0o700)
        rules = root / ".runtime/input/rules.yml"
        rules.write_text(RULES, encoding="utf-8")
        return tool, rules

    def test_function_is_in_the_one_universal_catalog(self):
        doc = catalog_registry.read_catalog()
        self.assertEqual(doc["counts"]["functions"], 280)
        self.assertEqual(doc["counts"]["all_catalog_entries"], 458)
        self.assertEqual(doc["counts"]["functions_base_operations"], 20)
        self.assertIn("prometheus-rule-check", ferrari.OPS)
        matches = [entry for entry in doc["functions"]
                   if entry["id"] == "operation:prometheus-rule-check"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["program"], "prometheus")
        self.assertEqual(matches[0]["invocation"],
                         {"kind": "operation", "operation": "prometheus-rule-check"})

    def test_private_binary_checks_real_rule_syntax_and_archives_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            exe, rules = self._fixture(root)
            folder = root / ".runtime/results"
            reply = subprocess.CompletedProcess(
                args=[str(exe), "check", "rules", str(rules)],
                returncode=0,
                stdout="Checking " + str(rules) + "\n  SUCCESS: 1 rules found\n",
                stderr="",
            )
            with patch.object(monitor_tools, "HOME", root), \
                 patch.object(monitor_tools.subprocess, "run", return_value=reply) as call:
                identity, artifacts = monitor_tools.check_rules(rules, folder)
            self.assertIn("promtool", identity)
            self.assertEqual(len(artifacts), 2)
            self.assertTrue(all(p.is_file() for p in artifacts))
            report = json.loads((folder / "prometheus-rules-report.json").read_text())
            self.assertEqual(report["rules_validated"], 1)
            self.assertEqual(report["input_sha256"], hashlib.sha256(RULES.encode()).hexdigest())
            self.assertFalse(report["daemon_started"])
            self.assertFalse(report["monitoring_service_certified"])
            args, kwargs = call.call_args
            self.assertEqual(args[0], [str(exe), "check", "rules", str(rules)])
            self.assertFalse(kwargs["shell"])
            self.assertLessEqual(kwargs["timeout"], 25)
            self.assertEqual(kwargs["env"]["PATH"], str(exe.parent))
            self.assertFalse(any("secret" in str(x) for x in artifacts))
            self.assertFalse(any(p.name.startswith(".promtool-check-")
                                 for p in (root / ".runtime").iterdir()))

    def test_invalid_rules_are_rejected_without_false_completed_report(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, rules = self._fixture(root)
            result = subprocess.CompletedProcess(args=[], returncode=1,
                       stdout="Checking rules\nFAILED", stderr="parse error")
            with patch.object(monitor_tools, "HOME", root), \
                 patch.object(monitor_tools.subprocess, "run", return_value=result):
                with self.assertRaisesRegex(RuntimeError, "rule validation failed"):
                    monitor_tools.check_rules(rules, root / ".runtime/result")
            self.assertFalse((root / ".runtime/result/prometheus-rules-report.json").exists())

    def test_file_type_symlink_and_project_escape_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "ferrari"
            root.mkdir()
            _, rules = self._fixture(root)
            outside = Path(temp) / "other-rules.yml"
            outside.write_text(RULES, encoding="utf-8")
            symlink = root / ".runtime/input/escape.yml"
            symlink.symlink_to(outside)
            with patch.object(monitor_tools, "HOME", root):
                with self.assertRaisesRegex(ValueError, "must be .yml"):
                    monitor_tools.check_rules(rules.with_suffix(".txt"), root / ".runtime/out")
                with self.assertRaises(ValueError):
                    monitor_tools.check_rules(symlink, root / ".runtime/out")
                with self.assertRaises(ValueError):
                    monitor_tools.check_rules(outside, root / ".runtime/out")

    def test_no_global_program_or_network_fallback(self):
        text = Path(monitor_tools.__file__).read_text(encoding="utf-8")
        self.assertIn("PROMTOOL_RELATIVE", text)
        self.assertIn("start_new_session=True", text)
        self.assertIn("stdin=subprocess.DEVNULL", text)
        self.assertNotIn("shell=True", text)
        self.assertNotIn("systemctl", text)
        self.assertNotIn("apt-get", text)
        self.assertNotIn("requests.", text)


if __name__ == "__main__":
    unittest.main()
