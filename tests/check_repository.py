"""Check documentation links, Python syntax, example YAML, and publication scope."""
import ast
from pathlib import Path
import re
from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[1]
errors = []
for path in ROOT.rglob('*'):
    relative = path.relative_to(ROOT)
    if '.git' in relative.parts or '__pycache__' in relative.parts or not path.is_file():
        continue
    if path.suffix.lower() in {'.wav','.mp3','.ogg','.gguf','.onnx','.db','.exe','.dll'} or path.name in {'.env','auth.json','config.yaml'}:
        errors.append(f'User state/binary must not be published: {relative}')
    if path.suffix == '.py':
        ast.parse(path.read_text(encoding='utf-8'), filename=str(relative))
    if path.suffix == '.md':
        text = path.read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if '://' in target or target.startswith('#'):
                continue
            target = target.split('#', 1)[0]
            if target and not (path.parent / target).resolve().exists():
                errors.append(f'Broken relative link in {relative}: {target}')
    if path.stat().st_size > 500_000:
        errors.append(f'Unexpectedly large guide file: {relative}')

YAML(typ='safe').load((ROOT / 'config' / 'hermes-local.example.yaml').read_text(encoding='utf-8'))
for skill in (ROOT / 'skills').glob('*/SKILL.md'):
    metadata = YAML(typ='safe').load(skill.read_text(encoding='utf-8').split('---', 2)[1])
    if metadata['name'] != skill.parent.name:
        errors.append(f'Skill metadata mismatch: {skill.relative_to(ROOT)}')
if errors:
    raise SystemExit('\n'.join(errors))
print('Relative links, Python syntax, example YAML, skill metadata, and publication scope passed.')
