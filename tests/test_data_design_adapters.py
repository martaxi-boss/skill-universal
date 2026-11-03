"""First Ferrari programme-integration phase: typed design and data tools."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import subprocess
import unittest
from unittest.mock import patch

from engine import data_profiles, tool_runtime


class FerrariDataDesignAdapters(unittest.TestCase):
    def test_ferrari_has_typed_actions_with_explicit_input_formats(self):
        manifest = tool_runtime.specs()
        expected = {
            "inkscape-svg-png": ("inkscape", ".svg", "inkscape.png"),
            "typst-compile-pdf": ("typst", ".typ", "typst-document.pdf"),
            "duckdb-csv-profile": ("duckdb", ".csv", "duckdb-profile.json"),
            "polars-csv-profile": ("polars", ".csv", "polars-profile.json"),
        }
        for name, (tool, ext, artifact) in expected.items():
            with self.subTest(name=name):
                item = manifest[name]
                self.assertEqual((item["tool"], item["extensions"], item["artifact"]),
                                 (tool, [ext], artifact))
                self.assertEqual(item["mode"], "file")
                self.assertIn("{input}", item["args"])
                self.assertIn("{output}", item["args"])

    def test_private_python_venv_required_for_duckdb_and_polars(self):
        with TemporaryDirectory() as folder:
            root = Path(folder) / "motor-ferrari"
            with patch.object(tool_runtime, "HOME", root):
                for library in ("duckdb", "polars"):
                    base = root / ".runtime/venvs/extended" / library
                    interpreter = base / "bin/python"
                    package = base / "lib/python3.12/site-packages" / library
                    package.mkdir(parents=True)
                    interpreter.parent.mkdir(parents=True)
                    interpreter.write_text("fake interpreter")
                    (base / "pyvenv.cfg").write_text("home = /usr/bin")
                    self.assertEqual(tool_runtime.executable(library, "python"),
                                     str(interpreter))
                    (base / "pyvenv.cfg").unlink()
                    self.assertIsNone(tool_runtime.executable(library, "python"))

    def test_fake_duckdb_csv_profile_reads_schema_counts_and_rows(self):
        class Relation:
            columns = ["country", "score"]
            types = ["VARCHAR", "BIGINT"]
            def aggregate(self, expr):
                if expr != "count(*)":
                    raise AssertionError("Unexpected query")
                return SimpleNamespace(fetchall=lambda: [(2,)])
            def limit(self, n):
                if n != 5: raise AssertionError("Bad sample size")
                return self
            def fetchall(self): return [("Portugal", 7), ("Espanha", 9)]
        fake_db = SimpleNamespace(__version__="2.0.0",
                                  connect=lambda **kw: SimpleNamespace(
                                    read_csv=lambda path: Relation(),
                                    close=lambda: None))
        with TemporaryDirectory() as folder, patch.object(
                data_profiles.importlib, "import_module", return_value=fake_db):
            src = Path(folder) / "scores.csv"
            src.write_text("country,score\nPortugal,7\nEspanha,9\n")
            result = data_profiles.profile("duckdb", src)
        self.assertEqual(result["rows"], 2)
        self.assertEqual(result["executor"], "duckdb")
        self.assertEqual(result["sample"][0], {"country": "Portugal", "score": 7})
        self.assertEqual(result["columns"][1]["type"], "BIGINT")

    def test_fake_polars_csv_profile_reads_schema_counts_and_rows(self):
        class Table:
            height = 2
            schema = {"country": "String", "score": "Int64"}
            def head(self, n):
                if n != 5: raise AssertionError("Bad sample size")
                return self
            def to_dicts(self):
                return [{"country": "Portugal", "score": 7},
                        {"country": "Espanha", "score": 9}]
        fake_polars = SimpleNamespace(__version__="1.28.0",
                                      read_csv=lambda path: Table())
        with TemporaryDirectory() as folder, patch.object(
                data_profiles.importlib, "import_module", return_value=fake_polars):
            src = Path(folder) / "scores.csv"
            src.write_text("country,score\nPortugal,7\nEspanha,9\n")
            result = data_profiles.profile("polars", src)
        self.assertEqual(result["rows"], 2)
        self.assertEqual(result["sample_size"], 2)
        self.assertEqual(result["columns"][0]["name"], "country")

    def test_invocation_is_not_shell_and_uses_private_python_environment(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            csv = root / "input.csv"
            csv.write_text("city,score\nFaro,10\n")
            dest = root / "result"
            def simulated(args, **kw):
                self.assertFalse(kw.get("shell", False))
                self.assertEqual(args[1:4], ["-m", "engine.data_profiles", "duckdb"])
                self.assertEqual(args[4], str(csv))
                self.assertEqual(args[5], str(dest / "duckdb-profile.json"))
                self.assertEqual(kw["cwd"], str(tool_runtime.ROOT))
                self.assertEqual(kw["env"]["PYTHONNOUSERSITE"], "1")
                Path(args[5]).write_text('{"executor":"duckdb","rows":1}')
                return subprocess.CompletedProcess(args, 0, b"", b"")
            with patch.object(tool_runtime, "executable",
                              return_value="/fake/private-duckdb/bin/python"):
                with patch.object(tool_runtime.subprocess, "run", side_effect=simulated):
                    result = tool_runtime.invoke("duckdb-csv-profile", str(csv), str(dest))
            self.assertTrue(result["confirmed"])
            self.assertEqual(result["tool"], "duckdb")
            self.assertEqual(json.loads((dest / "duckdb-profile.json").read_text())["rows"], 1)

    def test_design_conversions_run_with_non_shell_commands(self):
        for action, extension, magic in (
                ("inkscape-svg-png", ".svg", b"\x89PNG\r\n\x1a\n"),
                ("typst-compile-pdf", ".typ", b"%PDF-1.7")):
            with self.subTest(action=action), TemporaryDirectory() as folder:
                root = Path(folder)
                src = root / ("sample" + extension)
                src.write_text("#set page(width: 4cm, height: 4cm)\n" if extension == ".typ"
                               else '<svg xmlns="http://www.w3.org/2000/svg"/>')
                dest = root / "output"
                spec = tool_runtime.specs()[action]
                def simulated(args, **kw):
                    self.assertFalse(kw.get("shell", False))
                    self.assertEqual(args[0], "/usr/bin/mock")
                    self.assertIn(str(src), args)
                    self.assertIn(str(dest / spec["artifact"]), args)
                    (dest / spec["artifact"]).write_bytes(magic + b"\x00" * 64)
                    return subprocess.CompletedProcess(args, 0, b"", b"")
                with patch.object(tool_runtime, "executable", return_value="/usr/bin/mock"):
                    with patch.object(tool_runtime.subprocess, "run", side_effect=simulated):
                        result = tool_runtime.invoke(action, str(src), str(dest))
                self.assertTrue(result["confirmed"])
                self.assertGreater((dest / spec["artifact"]).stat().st_size, 10)

    def test_auto_routes_only_matching_action(self):
        with patch.object(tool_runtime, "executable", return_value="/usr/bin/mock"):
            choices = [
                ("inkscape svg para png", "/tmp/source.svg", "inkscape-svg-png"),
                ("compilar typst", "/tmp/source.typ", "typst-compile-pdf"),
                ("duckdb csv", "/tmp/input.csv", "duckdb-csv-profile"),
                ("polars csv", "/tmp/input.csv", "polars-csv-profile"),
            ]
            for text, source, expected in choices:
                with self.subTest(text=text):
                    proposal = tool_runtime.auto(text, source)
                    self.assertEqual(proposal["selected"]["action"], expected)
            self.assertFalse(tool_runtime.route("duckdb csv", "/tmp/input.txt")["suggestions"])

    def test_vps_smoke_calls_each_real_installed_adapter(self):
        smoke=(Path(__file__).resolve().parents[1] /
               "install/vps-tool-runtime-smoke.sh").read_text()
        self.assertIn('assert x["registered_actions"]==31', smoke)
        self.assertIn('assert x["callable_actions"]>=31', smoke)
        for action in ("duckdb-csv-profile", "polars-csv-profile",
                       "inkscape-svg-png", "typst-compile-pdf"):
            self.assertIn("--action " + action, smoke)
        for proof in ("FERRARI_DUCKDB_CSV_REAL=PASS", "FERRARI_POLARS_CSV_REAL=PASS",
                      "FERRARI_INKSCAPE_SVG_PNG_REAL=PASS", "FERRARI_TYPST_PDF_REAL=PASS"):
            self.assertIn(proof, smoke)
        self.assertNotIn("rea-final-runtime", smoke)

    def test_missing_library_fails_without_disabling_other_tools(self):
        with TemporaryDirectory() as folder:
            src = Path(folder) / "data.csv"
            src.write_text("name\nPortugal\n")
            with patch.object(data_profiles.importlib, "import_module",
                              side_effect=ModuleNotFoundError("duckdb")):
                with self.assertRaises(ModuleNotFoundError):
                    data_profiles.profile("duckdb", src)
            self.assertFalse((Path(folder) / "output.json").exists())


if __name__ == "__main__":
    unittest.main()
