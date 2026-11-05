"""Krita's existing Ubuntu Xvfb backend is used only in its own Ferrari job."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import subprocess
import unittest

from engine import tool_runtime


class KritaVirtualDisplayTests(unittest.TestCase):
    def test_krita_export_runs_under_temporary_xvfb_display(self):
        with TemporaryDirectory() as d:
            root=Path(d)
            src=root/"sample.jpg"
            src.write_bytes(b"\xff\xd8\xff"+b"data")
            dst=root/"result"
            private=root/"private-cli"
            (private/"bin").mkdir(parents=True)
            for name in ("xvfb-run","Xvfb"):
                (private/"bin"/name).write_text("private fixture")
            def fake(args,**kw):
                self.assertEqual(args[:3],[str(private/"bin/xvfb-run"),"-a","/usr/bin/krita"])
                self.assertEqual(args[3],str(src))
                self.assertIn("--export",args)
                self.assertEqual(kw["env"]["QT_QPA_PLATFORM"],"xcb")
                self.assertTrue(kw["env"]["TMPDIR"].startswith(str(dst)))
                self.assertFalse(kw.get("shell",False))
                (dst/"krita-export.png").write_bytes(b"\x89PNG\r\n\x1a\n"+"Ferrari".encode())
                return subprocess.CompletedProcess(args,0,b"",b"")
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/krita"):
                with patch.object(tool_runtime,"PRIVATE_CLI_ROOT",private):
                    with patch.object(tool_runtime.subprocess,"run",side_effect=fake):
                        result=tool_runtime.invoke("krita-image-png",str(src),str(dst))
            self.assertTrue(result["confirmed"])
            self.assertEqual(result["executor"],"/usr/bin/krita")

    def test_no_xvfb_refuses_before_subprocess(self):
        with TemporaryDirectory() as d:
            root=Path(d)
            src=root/"sample.jpg"
            src.write_bytes(b"\xff\xd8\xff")
            # A private Xvfb exists on the real VPS; force a missing private
            # executor so this negative test is independent of the host.
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/krita"):
                with patch.object(tool_runtime,"PRIVATE_CLI_ROOT",root/"missing-private-cli"):
                    with patch.object(tool_runtime.subprocess,"run") as invoke:
                        with self.assertRaisesRegex(RuntimeError,"existing Xvfb virtual display"):
                            tool_runtime.invoke("krita-image-png",str(src),str(root/"out"))
                        invoke.assert_not_called()


if __name__=="__main__":
    unittest.main()
