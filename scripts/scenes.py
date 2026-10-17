"""Route by explicit purpose or strong filename/header evidence, never curve shape."""
from pathlib import Path
import csv
import re

PROFILES={
 'general':{'theme':'paper','template':'line'},
 'spectrum':{'theme':'user:blue-magenta','template':'spectrum'},
 'red-cyan-spectrum':{'theme':'user:red-cyan','template':'spectrum'},
 'chromatography':{'theme':'user:red-cyan','template':'spectrum'},
 'mass-spectrum':{'theme':'user:peach-teal','template':'sticks'},
 'electrochemistry':{'theme':'user:mist-blue-rose','template':'line'},
 'bio-timecourse':{'theme':'user:peach-teal','template':'line'},
}
RULES=[
 ('mass-spectrum',r'\bmass[ _-]?spec|\bm/z\b|质谱'),
 ('chromatography',r'\bgc\b|chromatogra|retention[ _-]?time|色谱|保留时间'),
 ('red-cyan-spectrum',r'\bepr\b|\besr\b|\bnmr\b|uv[ _-]?vis|核磁|紫外|漫反射'),
 ('spectrum',r'\bxanes\b|\bexafs\b|\bftir\b|\bco[ _-]?ir\b|\bftir\b|\braman\b|wavenumber|wave[ _-]?number|\bspectrum\b|\bspectra\b|光谱|红外|拉曼'),
 ('electrochemistry',r'voltamm|\blsv\b|\bco2er\b|current[ _-]?density|faradaic|\brhe\b|电化学|极化|法拉第'),
 ('bio-timecourse',r'\bod600\b|glucose|methanogen|growth|生长|葡萄糖|甲烷'),
]


def select_scene(task,config_path,data_override=None):
    explicit=task.get('purpose','auto')
    if explicit in PROFILES:
        return explicit,{'source':'explicit-purpose','matched':explicit}
    data=task.get('data',{});value=data_override or data.get('path')
    path=Path(value).expanduser() if value else None
    if path is not None and not path.is_absolute():path=(Path.cwd() if data_override else config_path.parent)/path
    headers=[]
    if path is not None and path.is_file():
        with path.open(encoding='utf-8-sig',newline='') as file:headers=next(csv.reader(file),[])
    # Underscores are token separators; directory names do not supply evidence.
    evidence=' '.join([str(explicit) if explicit!='auto' else '',path.stem if path else '',*headers,str(data.get('x','')),str(data.get('y',''))]).replace('_',' ')
    for purpose,pattern in RULES:
        match=re.search(pattern,evidence,re.I)
        if match:return purpose,{'source':'filename-or-header','matched':match.group(0)}
    return 'general',{'source':'visual-fallback','matched':None,'reason':'Borrow the general paper style; no scientific domain or statistical meaning is inferred.'}
