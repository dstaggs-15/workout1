"""Build Pages data and retain changed profile versions in a committed history."""
import hashlib,json,math
from datetime import datetime,timezone,date
from pathlib import Path
try:
 from .analyze import analyze, GROUPS
except ImportError:
 from analyze import analyze, GROUPS

def profile_read(text):
 height=None;weights={}
 for line in text.splitlines():
  line=line.strip()
  if not line or line.startswith('#'):continue
  key,sep,val=line.partition('=')
  if not sep:raise ValueError('Profile lines must be key=value')
  if key.strip()=='height_inches':
   height=float(val)
   if not math.isfinite(height) or not 12<=height<=120:raise ValueError('Invalid height')
  elif key.strip()=='weigh_in':
   parts=[s.strip() for s in val.split(',')]
   if len(parts)!=3:raise ValueError('weigh_in must be date,weight,unit')
   day,value,unit=parts;date.fromisoformat(day);value=float(value)
   if unit not in ('lb','kg') or not math.isfinite(value) or value<=0:raise ValueError('Invalid weigh-in')
   lb=value*(2.2046226218 if unit=='kg' else 1)
   if lb>=1500:raise ValueError('Weight exceeds supported range')
   weights[day]={'date':day,'weight_lb':lb,'note':'Source profile','source':'profile'}
  else:raise ValueError('Unknown profile field: '+key)
 return {'height_inches':height,'weights':sorted(weights.values(),key=lambda w:w['date'])}

def build(root):
 root=Path(root);source=root/'source';web=root/'web';web.mkdir(exist_ok=True)
 text=(source/'profile.txt').read_text();profile=profile_read(text)
 digest=hashlib.sha256(text.encode()).hexdigest();history_path=source/'history/profile_history.json'
 history=json.loads(history_path.read_text()) if history_path.exists() else []
 if not history or history[-1]['sha256']!=digest:
  history.append({'saved_at':datetime.now(timezone.utc).isoformat(),'sha256':digest,'text':text,'profile':dict(profile)})
 history_path.parent.mkdir(parents=True,exist_ok=True);history_path.write_text(json.dumps(history,indent=2)+'\n')
 profile['history']=history;(web/'profile.json').write_text(json.dumps(profile))
 overrides_path=source/'muscle_overrides.json';overrides=json.loads(overrides_path.read_text()) if overrides_path.exists() else {}
 if any(v not in GROUPS for v in overrides.values()):raise ValueError('Invalid muscle override')
 report=analyze(sorted(source.glob('*.csv')),overrides)
 (web/'report.json').write_text(json.dumps(report,ensure_ascii=False))
 print('Pages report and profile built; profile history retained.')
if __name__=='__main__':build(Path(__file__).resolve().parents[1])
