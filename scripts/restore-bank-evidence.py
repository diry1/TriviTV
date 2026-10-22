"""Restore archived bank evidence locally. No API or network access."""
from pathlib import Path
import gzip,shutil,tarfile
root=Path(__file__).resolve().parents[1]/'question-bank'
for archive in root.rglob('responses.tar.gz'):
    with tarfile.open(archive,'r:gz') as tar:tar.extractall(archive.parent,filter='data')
    print('Restored',archive.relative_to(root))
for archive in root.rglob('audit.json.gz'):
    with gzip.open(archive,'rb') as src,archive.with_suffix('').open('wb') as dst:shutil.copyfileobj(src,dst)
    print('Restored',archive.relative_to(root))
