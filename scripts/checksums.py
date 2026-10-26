"""Write SHA-256 hashes for release packages."""
import hashlib
import sys
from pathlib import Path
folder=Path(sys.argv[1] if len(sys.argv)>1 else 'dist')
lines=[]
for path in sorted(folder.glob('*.zip')):
    lines.append(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+path.name)
(folder/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
