"""Behavior checks for the public configurator; never touch an active Hermes home."""
import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('guide_configure', ROOT / 'scripts' / 'configure.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ConfigureTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name) / 'home'

    def run_configure(self, **kwargs):
        settings = {'model': 'example-model', 'base_url': 'http://127.0.0.1:8081/v1', 'context': 65536}
        settings.update(kwargs)
        with contextlib.redirect_stdout(io.StringIO()):
            return module.configure(self.home, **settings)

    def read_config(self):
        return YAML(typ='safe').load((self.home / 'config.yaml').read_text(encoding='utf-8'))

    def test_dry_run_writes_nothing_even_for_a_new_home(self):
        self.run_configure(dry_run=True)
        self.assertFalse(self.home.exists())

    def test_existing_settings_and_original_backup_survive(self):
        self.home.mkdir()
        original = '# keep this comment\nterminal:\n  cwd: D:/Projects\ncustom_setting: café\n'
        (self.home / 'config.yaml').write_text(original, encoding='utf-8')
        (self.home / 'SOUL.md').write_text('My own personality.\n', encoding='utf-8')
        backup = self.run_configure()
        result = self.read_config()
        self.assertEqual(result['terminal']['cwd'], 'D:/Projects')
        self.assertEqual(result['custom_setting'], 'café')
        self.assertEqual((backup / 'config.yaml').read_text(encoding='utf-8'), original)
        self.assertEqual((backup / 'SOUL.md').read_text(encoding='utf-8'), 'My own personality.\n')
        self.assertIn('# keep this comment', (self.home / 'config.yaml').read_text(encoding='utf-8'))
        self.assertTrue((self.home / 'SOUL.md').read_text(encoding='utf-8').startswith('My own personality.'))

    def test_repeat_configuration_is_idempotent(self):
        self.run_configure()
        before = self.read_config()
        self.run_configure()
        self.assertEqual(before, self.read_config())
        self.assertEqual((self.home / 'SOUL.md').read_text(encoding='utf-8').count('## Local voice guide workflow'), 1)
        self.assertEqual(len(list((self.home / 'skills').rglob('SKILL.md'))), 2)

    def test_existing_skill_is_backed_up(self):
        previous = self.home / 'skills' / 'autonomous-ai-agents' / 'find-skills' / 'SKILL.md'
        previous.parent.mkdir(parents=True)
        previous.write_text('An existing local adaptation.', encoding='utf-8')
        backup = self.run_configure()
        self.assertEqual((backup / previous.relative_to(self.home)).read_text(encoding='utf-8'), 'An existing local adaptation.')
        self.assertIn('Find Skills for Hermes', previous.read_text(encoding='utf-8'))

    def test_routes_and_text_helpers_do_not_keep_cloud_overrides(self):
        config = {
            'fallback_model': {'provider': 'cloud'},
            'fallback_providers': [{'provider': 'cloud'}],
            'auxiliary': {'compression': {'provider': 'cloud', 'model': 'cloud-model',
                'base_url': 'https://example.invalid/v1', 'api_key': 'example-placeholder'}},
        }
        result = module.merge_settings(config, model='example-model', base_url='http://localhost:8080/v1', context=65536)
        self.assertEqual(result['model']['base_url'], 'http://localhost:8080/v1')
        self.assertEqual(result['delegation']['base_url'], result['model']['base_url'])
        self.assertEqual(result['delegation']['max_concurrent_children'], 1)
        self.assertFalse(result['delegation']['subagent_auto_approve'])
        self.assertEqual(result['fallback_providers'], [])
        self.assertNotIn('fallback_model', result)
        self.assertEqual(result['auxiliary']['compression']['base_url'], '')
        self.assertEqual(result['auxiliary']['compression']['provider'], 'main')

    def test_context_below_minimum_is_rejected_without_writing(self):
        with self.assertRaises(ValueError):
            self.run_configure(context=32768)
        self.assertFalse(self.home.exists())

    def test_remote_or_credentialed_endpoint_is_rejected(self):
        for endpoint in ('https://example.invalid/v1', 'http://user:pass@localhost/v1',
                         'http://localhost/v1?key=example', 'http://localhost/not-v1'):
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                self.run_configure(base_url=endpoint)
        self.assertFalse(self.home.exists())

    def test_empty_config_is_valid(self):
        self.home.mkdir()
        (self.home / 'config.yaml').write_text('', encoding='utf-8')
        self.run_configure()
        self.assertEqual(self.read_config()['tts']['provider'], 'piper')
        self.assertEqual(self.read_config()['stt']['local']['compute_type'], 'int8')

    def test_cli_toolsets_are_merged_without_duplicates(self):
        config = {'platform_toolsets': {'cli': ['file', 'my-custom-toolset'], 'other': ['unchanged']}}
        result = module.merge_settings(config, model='local', base_url='http://127.0.0.1:8080/v1', context=65536)
        self.assertEqual(result['platform_toolsets']['cli'].count('file'), 1)
        self.assertIn('my-custom-toolset', result['platform_toolsets']['cli'])
        self.assertEqual(result['platform_toolsets']['other'], ['unchanged'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
