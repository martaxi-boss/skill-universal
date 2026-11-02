import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from engine.core import execute, environment, inventory, plan, providers


class EngineTest(unittest.TestCase):
    def test_routes(self):
        self.assertEqual(plan('cria um site responsivo')['route'], 'website')
        self.assertEqual(plan('faz-me um criativo para o anuncio')['route'], 'creative')
        self.assertEqual(plan('descompilar esta aplicacao APK')['route'], 'reverse')
        self.assertEqual(plan('quero um relatorio PDF')['route'], 'documents')

    def test_inventory_includes_free_programs(self):
        ids = {t['id'] for t in inventory()}
        self.assertTrue({'ruflo', 'REA', 'ffmpeg', 'apktool', 'html-templates'} <= ids)
        self.assertIn('tool_count', environment())

    def test_provider_secrets_not_exposed(self):
        for p in providers():
            self.assertNotIn('key_value', p)

    def test_site_and_creative_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d)
            r = execute('fazer um site', output, 'Barbearia & Cia')
            self.assertEqual(r['status'], 'completed_local_task')
            self.assertIn('Barbearia &amp; Cia', (output / 'site/index.html').read_text())
            self.assertNotIn('{{TITLE}}', (output / 'site/index.html').read_text())
            r = execute('criar cartaz', output, '<promo & teste>')
            self.assertEqual(r['route'], 'creative')
            self.assertIn('&lt;promo &amp; teste&gt;', (output / 'creative/poster.svg').read_text())

    def test_reverse_nonexecuting(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d)
            target = output / 'sample.apk'
            with zipfile.ZipFile(target, 'w') as z:
                z.writestr('classes.dex', b'dex\n\x00')
            r = execute('descompilar um APK', output, 'APP', target)
            self.assertEqual(r['route'], 'reverse')
            data = json.loads((output / 'reverse/report.json').read_text())
            self.assertIn('classes.dex', data['zip_entries'])
            self.assertIn('nao foi executado REA', data['warning'])

    def test_no_unsafe_arbitrary_commands(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(NotImplementedError):
                execute('executar qualquer comando shell', Path(d), 'n/a')


if __name__ == '__main__':
    unittest.main()
