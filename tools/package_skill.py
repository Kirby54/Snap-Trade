#!/usr/bin/env python3
"""Build a reproducible, installable skill ZIP and SHA-256 checksum (stdlib only)."""
import argparse
import hashlib
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def build(output, root=ROOT):
    skill=root/'skills/snap-and-trade'
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    files=[(p,p.relative_to(skill.parent).as_posix()) for p in sorted(skill.rglob('*'))
           if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    files.append((root/'LICENSE','snap-and-trade/LICENSE'))
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for path,name in files:
            info=zipfile.ZipInfo(name,date_time=(2020,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            z.writestr(info,path.read_bytes())
    digest=hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix('.zip.sha256').write_text(f'{digest}  {output.name}\n',encoding='ascii')
    return digest


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',default='dist/snap-and-trade.zip')
    a=p.parse_args();print(build(a.output))
