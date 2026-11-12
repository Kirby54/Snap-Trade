#!/usr/bin/env python3
"""Offline repository contract checks; standard library only."""
import ast
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/snap-and-trade'


def validate(root=ROOT):
    errors = []
    skill = root / 'skills/snap-and-trade'
    text = (skill / 'SKILL.md').read_text(encoding='utf-8')
    description = re.search(r'^description: >-\n(.*?)\nargument-hint:', text, re.M | re.S)
    if description is None or not 1 <= len(' '.join(description[1].split())) <= 1024:
        errors.append('skill description missing or exceeds 1024 characters')
    if not re.search(r'^name: snap-and-trade$', text, re.M):
        errors.append('skill name does not match directory')
    for ref in re.findall(r'`(references/[^`<>]+\.md)`', text):
        if not (skill / ref).is_file():
            errors.append(f'missing skill reference: {ref}')
    for script in set(re.findall(r'`([a-z][a-z0-9_]*\.py)`', text)):
        if not (skill / 'scripts' / script).is_file():
            errors.append(f'missing module script: {script}')
    for path in root.rglob('*.py'):
        if '.git' not in path.parts:
            try:
                ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
            except SyntaxError as exc:
                errors.append(str(exc))
    plugin = json.loads((root / '.claude-plugin/plugin.json').read_text(encoding='utf-8'))
    market = json.loads((root / '.claude-plugin/marketplace.json').read_text(encoding='utf-8'))
    if plugin['name'] != 'snap-and-trade' or market['plugins'][0]['name'] != plugin['name']:
        errors.append('plugin and marketplace names disagree')
    version = plugin['version']
    if f'version-{version}-blue' not in (root / 'README.md').read_text(encoding='utf-8'):
        errors.append('README version badge disagrees with plugin')
    if f'## {version}' not in (root / 'CHANGELOG.md').read_text(encoding='utf-8'):
        errors.append('release missing from changelog')
    for path in (skill / 'scripts').glob('*.example.json'):
        json.loads(path.read_text(encoding='utf-8'))
    # Local Markdown links must resolve (external links and anchors are excluded).
    for path in root.rglob('*.md'):
        if '.git' in path.parts:
            continue
        for target in re.findall(r'\]\(([^\s)]+)\)', path.read_text(encoding='utf-8')):
            if '://' in target or target.startswith('#'):
                continue
            if not (path.parent / target.split('#')[0]).exists():
                errors.append(f'{path.relative_to(root)}: missing link {target}')
    return errors


if __name__ == '__main__':
    problems = validate()
    print('\n'.join(problems) if problems else 'Repository contracts OK')
    sys.exit(bool(problems))
