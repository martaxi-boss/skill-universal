"""Ferrari F11 PDAL must never claim a format PASS without real LAS roundtrip."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1]/"install/vps-f11-pdal-las-certify.py"
spec = importlib.util.spec_from_file_location("f11_pdal_las", SRC)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class PdalLasTests(unittest.TestCase):
    def test_guards_against_global_operations(self):
        s = SRC.read_text()
        for forbidden in ("apt-get ", "sudo ", "pip install", "git reset", "shell=True"):
            self.assertNotIn(forbidden,s)
        self.assertEqual(m.CURRENT_SHA,"205c6f0e970259c79fa2111b6670c2fe1672fb27")
        self.assertEqual(m.FALLBACK_SHA,"7bf6dcecf15da26502c5969b5eee54d5e116fc32")
        self.assertEqual(len(m.POINTS),5)

    def test_real_las_header_synthetic_parser(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"cloud.las"
            b=bytearray(227)
            b[:4]=b"LASF"
            import struct
            struct.pack_into("<H",b,94,227)
            struct.pack_into("<I",b,96,227)
            struct.pack_into("<I",b,107,5)
            p.write_bytes(b)
            report=m.las_header(p)
            self.assertEqual(report["point_count"],5)
            with p.open("r+b") as fh:
                fh.seek(107)
                fh.write(struct.pack("<I",4))
            with self.assertRaisesRegex(RuntimeError,"POINT_COUNT"):
                m.las_header(p)

    def test_csv_coordinates_are_validated(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"roundtrip.csv"
            p.write_text("X,Y,Z\\n"+"".join(f"{a},{b},{c}\\n" for a,b,c in m.POINTS))
            self.assertEqual(m.verify_csv(p),5)
            p.write_text("X,Y,Z\\n"+ "0,0,0\\n"*5)
            with self.assertRaisesRegex(RuntimeError,"COORDINATES"):
                m.verify_csv(p)

    def test_pipeline_is_typed_and_explicit(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"p.json"
            m.pipeline(f,[{"type":"readers.text","filename":"/private/test.txt"},
                          {"type":"writers.las","filename":"/private/test.las"}])
            x=json.loads(f.read_text())
            self.assertEqual(len(x["pipeline"]),2)
            self.assertEqual(x["pipeline"][1]["type"],"writers.las")

    def test_driver_failure_cannot_be_pass(self):
        with tempfile.TemporaryDirectory() as d, \\
             patch.object(m,"RUNTIME",Path(d)), \\
             patch.object(m,"guard",return_value=Path("/private/pdal")), \\
             patch.object(m,"run",return_value={"exit_code":1,"timed_out":False,
                                                "stdout_tail":"","stderr_tail":"missing"}):
            x=m.certify()
            self.assertEqual(x["status"],"partial_blocked")
            self.assertFalse(x["full_pdal_formats_certified"])
            self.assertFalse(x["optional_hdf_icebridge_formats_certified"])
            self.assertTrue(x["test_artifacts_removed"])
            self.assertEqual(list(Path(d).iterdir()),[])

if __name__=="__main__":
    unittest.main()
