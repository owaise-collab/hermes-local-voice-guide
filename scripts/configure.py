"""Merge the guide's settings, preserving unrelated user configuration."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import os
import shutil
import tempfile
from urllib.parse import urlsplit

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[1]


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n',
                                     dir=path.parent, delete=False) as stream:
        stream.write(text)
        temporary = Path(stream.name)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def merge_settings(config, *, model, base_url, context):
    if context < 64000:
        raise ValueError('This tested Hermes version requires at least 64,000 context tokens.')
    endpoint = urlsplit(base_url)
    if endpoint.scheme != 'http' or endpoint.hostname not in {'localhost', '127.0.0.1', '::1'}:
        raise ValueError('This local-only setup requires an HTTP loopback endpoint.')
    if endpoint.username or endpoint.password or endpoint.query or endpoint.fragment or endpoint.path != '/v1':
        raise ValueError('Use a loopback URL ending in /v1, with no credentials, query, or fragment.')
    config.setdefault('model', {}).update(default=model, provider='llamacpp',
        base_url=base_url, api_key='local-only', context_length=context)
    config.setdefault('providers', {})['llamacpp'] = {
        'base_url': base_url, 'model': model, 'api_key': 'local-only'}
    config['fallback_providers'] = []
    config.pop('fallback_model', None)
    config.setdefault('skills', {})['creation_nudge_interval'] = 10
    config.setdefault('delegation', {}).update({
        'backend': 'default', 'max_iterations': 40, 'max_concurrent_children': 1,
        'max_spawn_depth': 1, 'subagent_auto_approve': False,
        'model': model, 'base_url': base_url, 'api_key': 'local-only',
        'api_mode': 'chat_completions', 'fallback_providers': [],
    })
    stt = config.setdefault('stt', {})
    stt.update(enabled=True, provider='local', language='en')
    stt.setdefault('local', {}).update(model='base', device='cpu', compute_type='int8', vad=True)
    config.setdefault('tts', {}).update(provider='piper', speed=1.0)
    config['tts'].setdefault('piper', {}).update(voice='en_US-lessac-medium', use_cuda=False)
    config.setdefault('voice', {}).update({
        'record_key': 'ctrl+b', 'auto_tts': True, 'beep_enabled': True,
        'max_recording_seconds': 120, 'silence_threshold': 200,
        'silence_duration': 2.0, 'stop_phrases': ['stop', 'goodbye hermes'],
    })
    for task in ('compression', 'title_generation', 'approval', 'skills_hub', 'mcp'):
        auxiliary = config.setdefault('auxiliary', {}).setdefault(task, {})
        auxiliary.update(provider='main', model='', base_url='', api_key='', fallback_chain=[])
    platforms = config.setdefault('platform_toolsets', {})
    cli = platforms.setdefault('cli', ['hermes-cli'])
    for toolset in ('skills', 'delegation', 'terminal', 'file', 'memory', 'session_search', 'tts'):
        if toolset not in cli:
            cli.append(toolset)
    return config


def configure(home, *, model, base_url, context, dry_run=False):
    home = Path(home).expanduser().resolve()
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 120
    config_path = home / 'config.yaml'
    config = yaml.load(config_path.read_text(encoding='utf-8')) if config_path.exists() else {}
    if config is None:
        config = {}
    merge_settings(config, model=model, base_url=base_url, context=context)
    import io
    output = io.StringIO()
    yaml.dump(config, output)
    # Validate all bundled input before modifying user state.
    additions = (ROOT / 'config' / 'soul-addition.md').read_text(encoding='utf-8')
    skill_files = list((ROOT / 'skills').glob('*/SKILL.md'))
    if len(skill_files) != 2:
        raise ValueError('Expected the two bundled skills; incomplete download.')
    for skill in skill_files:
        metadata = yaml.load(skill.read_text(encoding='utf-8').split('---', 2)[1])
        if metadata.get('name') != skill.parent.name:
            raise ValueError(f'Skill name mismatch: {skill.parent.name}')
    if dry_run:
        print(f'Dry run: would configure {home}; no files or dependencies changed.')
        print('Changes: local model, no model fallbacks, bounded delegation, local STT/TTS, voice, two skills, SOUL addition.')
        return None
    backup = home / 'backups' / ('local-voice-guide-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    backup.mkdir(parents=True)
    destinations = [config_path, home / 'SOUL.md'] + [home / 'skills' / 'autonomous-ai-agents' / skill.parent.name / 'SKILL.md' for skill in skill_files]
    for destination in destinations:
        if destination.exists():
            saved = backup / destination.relative_to(home)
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, saved)
    soul_path = home / 'SOUL.md'
    soul = soul_path.read_text(encoding='utf-8') if soul_path.exists() else ''
    if '## Local voice guide workflow' not in soul:
        soul += '\n\n' + additions.strip() + '\n'
    atomic_write(config_path, output.getvalue())
    atomic_write(soul_path, soul)
    for skill in skill_files:
        atomic_write(home / 'skills' / 'autonomous-ai-agents' / skill.parent.name / 'SKILL.md', skill.read_text(encoding='utf-8'))
    print(f'Configured. Backup: {backup}')
    return backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hermes-home', required=True)
    parser.add_argument('--model', default='local-hermes')
    parser.add_argument('--base-url', default='http://127.0.0.1:8080/v1')
    parser.add_argument('--context', type=int, default=65536)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    configure(args.hermes_home, model=args.model, base_url=args.base_url,
              context=args.context, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
