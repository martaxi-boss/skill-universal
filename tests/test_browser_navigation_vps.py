"""Real Ferrari-private Playwright navigation QA: passing site and fake link.

Runs only when the owned Chromium and Node are available. All test artefacts
and browser state live in the Ferrari project; no external network or daemon.
This is also exercised by the protected VPS release precheck, not merely mocked.
"""
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from engine import professional_tools

SOURCE = Path(__file__).resolve().parents[1] / "engine/browser_check.js"


class BrowserNavigationVpsTests(unittest.TestCase):
    def test_real_chromium_accepts_real_links_and_rejects_placeholder(self):
        if not professional_tools.browser_available():
            self.skipTest("Ferrari-private Chromium is not installed in this environment")
        home = professional_tools.HOME
        private = home / ".runtime"
        if not private.is_dir() or private.is_symlink():
            self.fail("Ferrari browser is available but private state directory is missing")
        node = professional_tools.NODE
        self.assertTrue(node.is_file() and node.resolve().is_relative_to(home.resolve()))
        with TemporaryDirectory(prefix=".browser-navigation-qa-", dir=private) as tmp:
            temp=Path(tmp)
            dist=temp/"dist"
            dist.mkdir(mode=0o700)
            html=(
                '<!doctype html><html lang="pt"><head><title>Navegacao Ferrari</title>'
                '<meta name="viewport" content="width=device-width, initial-scale=1">'
                '</head><body><h1>Ferrari Web QA</h1>'
                '<nav><a href="#destino">Detalhes</a>'
                '<a href="sobre.html">Sobre</a></nav>'
                '<section id="destino">Destino de navegacao verificado</section>'
                '</body></html>'
            )
            (dist/"index.html").write_text(html,encoding="utf-8")
            (dist/"sobre.html").write_text(
                '<html lang="pt"><head><title>Sobre Ferrari</title></head>'
                '<body><h1>Pagina sobre</h1></body></html>',encoding="utf-8")
            env=os.environ.copy()
            env.update({"PLAYWRIGHT_BROWSERS_PATH":str(professional_tools.BROWSER_CACHE),
                        "HOME":str(temp),"XDG_CACHE_HOME":str(temp),
                        "XDG_CONFIG_HOME":str(temp),"XDG_DATA_HOME":str(temp),
                        "XDG_RUNTIME_DIR":str(temp)})
            for label,expected,contents in (
                ("real","clear",html),
                ("fake","findings",html.replace('href="#destino"','href="#"')),
            ):
                (dist/"index.html").write_text(contents,encoding="utf-8")
                png=temp/(label+"-screenshot.png")
                report=temp/(label+"-browser.json")
                result=subprocess.run(
                    [str(node),str(SOURCE),str(dist),str(png),str(report)],
                    cwd=temp,env=env,shell=False,
                    capture_output=True,text=True,timeout=85,check=False)
                self.assertTrue(report.is_file(),result.stderr[:1200])
                data=json.loads(report.read_text("utf-8"))
                self.assertEqual(data["navigation"]["status"],expected,data)
                if label=="real":
                    self.assertEqual(result.returncode,0,result.stderr[:1300])
                    self.assertEqual(data["status"],"passed")
                    self.assertEqual(data["navigation"]["links_total"],2)
                    self.assertEqual(data["navigation"]["internal_files_verified"],1)
                    self.assertEqual(data["navigation"]["fragments_verified"],1)
                    self.assertEqual(data["mobile"]["horizontal_overflow_px"],0)
                    self.assertTrue(png.is_file())
                    self.assertTrue((temp/"browser-mobile.png").is_file())
                else:
                    self.assertNotEqual(result.returncode,0)
                    self.assertEqual(data["status"],"failed_navigation")
                    self.assertIn("Browser quality gate failed_navigation:",result.stderr)
                    self.assertIn("Non-functional link destination:",result.stderr)
                    self.assertTrue(any("Non-functional link destination" in x
                                        for x in data["navigation"]["findings"]))


if __name__=="__main__":
    unittest.main()
