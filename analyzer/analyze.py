"""Workout export analysis. No third-party dependencies; never prints private records."""
import argparse, csv, json, math, os, re, urllib.request
from datetime import datetime, timedelta, timezone
from collections import Counter, defaultdict
from pathlib import Path

GROUPS=['Chest','Back','Shoulders','Biceps','Triceps','Forearms','Quads','Hamstrings','Glutes','Calves','Core']
RULES=[('Forearms',r'wrist|farmers'),('Calves',r'calf'),('Hamstrings',r'leg curl|romanian|deadlift'),('Glutes',r'hip abduction|hip thrust|glute'),('Quads',r'squat|leg press|leg extension|lunge|box jump|hip adduction'),('Core',r'crunch|plank|leg raise|sit up|ab wheel|bicycle'),('Triceps',r'tricep|dip'),('Biceps',r'curl'),('Back',r'row|pull up|pulldown|back extension'),('Shoulders',r'raise|overhead press|arnold|face pull|rear delt'),('Chest',r'bench|chest|fly|butterfly|push up')]
def muscle(name, overrides):
    if name in overrides: return overrides[name]
    return next((m for m,p in RULES if re.search(p,name,re.I)), 'Unmapped')
def number(value):
    if value is None or str(value).strip()=='': return None
    n=float(value)
    if not math.isfinite(n) or n<0: raise ValueError('Expected a finite nonnegative number')
    return n

def analyze(paths, overrides=None):
    overrides=overrides or {}; sets=[]; seen=set(); blank=duplicates=0; errors=[]
    for path in paths:
        with open(path,encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f)
            required={'start_time','exercise_title','set_index','set_type','reps'}
            if not required.issubset(reader.fieldnames or []): raise ValueError(f'{Path(path).name}: missing required export columns')
            for line,r in enumerate(reader,2):
                if not any(str(v or '').strip() for v in r.values()): blank+=1;continue
                try:
                    start=datetime.strptime(r['start_time'],'%b %d, %Y, %I:%M %p')
                    end=datetime.strptime(r['end_time'],'%b %d, %Y, %I:%M %p') if r.get('end_time') else start
                    if end<start: raise ValueError('Workout ends before it starts')
                    name=r['exercise_title'].strip()
                    if not name: raise ValueError('Exercise name missing')
                    weight=number(r.get('weight_lbs')); reps=number(r.get('reps')); rpe=number(r.get('rpe'))
                    if rpe is not None and not 0<=rpe<=10: raise ValueError('RPE outside 0–10')
                    key=(r['start_time'],name,r.get('set_index'),r.get('set_type'),r.get('weight_lbs'),r.get('reps'),r.get('duration_seconds'),r.get('distance_miles'),r.get('rpe'))
                    if key in seen: duplicates+=1;continue
                    seen.add(key)
                    m=muscle(name,overrides)
                    assisted='assisted' in name.lower()
                    volume=(weight or 0)*(reps or 0) if not assisted else 0
                    e1rm=weight*(1+reps/30) if weight and reps and reps<=12 and not assisted else None
                    sets.append(dict(date=start.date().isoformat(),session=start.isoformat(),title=r.get('title','Workout'),minutes=(end-start).total_seconds()/60,exercise=name,muscle=m,type=r.get('set_type','normal'),weight=weight,reps=reps,rpe=rpe,volume=round(volume,2),e1rm=round(e1rm,2) if e1rm else None,duration=number(r.get('duration_seconds')),distance=number(r.get('distance_miles'))))
                except (ValueError,KeyError) as e: errors.append({'file':Path(path).name,'line':line,'reason':str(e)})
    if errors: raise ValueError(json.dumps({'invalid_rows':errors[:30],'total_invalid':len(errors)}))
    sets.sort(key=lambda x:(x['session'],x['exercise']))
    if not sets: raise ValueError('No valid workout sets found')
    work=[s for s in sets if s['type'].lower() not in ('warmup','warm-up')]
    weeks=defaultdict(lambda:dict(sets=0,reps=0,volume=0,minutes=0,sessions=set(),muscles=Counter()))
    sessions={}; exercises=defaultdict(list)
    for s in work:
        d=datetime.fromisoformat(s['date']); week=(d-timedelta(days=d.weekday())).date().isoformat(); w=weeks[week]
        w['sets']+=1;w['reps']+=s['reps'] or 0;w['volume']+=s['volume'];w['muscles'][s['muscle']]+=1
        if s['session'] not in w['sessions']: w['minutes']+=s['minutes'];w['sessions'].add(s['session'])
        sessions[s['session']]={'date':s['date'],'title':s['title'],'minutes':s['minutes']};exercises[s['exercise']].append(s)
    first=datetime.fromisoformat(min(weeks));last=datetime.fromisoformat(max(weeks));d=first
    while d<=last: weeks[d.date().isoformat()];d+=timedelta(days=7)
    weekly=[dict(week=k,**{key:(len(val) if key=='sessions' else dict(val) if key=='muscles' else round(val,2)) for key,val in w.items()}) for k,w in sorted(weeks.items())]
    exercise_stats=[]
    for name,rows in exercises.items():
        by=defaultdict(list)
        for s in rows: by[s['session']].append(s)
        history=[dict(date=ss[0]['date'],sets=len(ss),volume=round(sum(s['volume'] for s in ss),2),weight=max((s['weight'] or 0 for s in ss)),e1rm=max((s['e1rm'] or 0 for s in ss)),reps=sum(s['reps'] or 0 for s in ss)) for _,ss in sorted(by.items())]
        valid=[x for x in history if x['e1rm']>0]; baseline=valid[:3];recent=valid[-3:]
        change=None
        if len(valid)>=6:
            a=sum(x['e1rm'] for x in baseline)/len(baseline);b=sum(x['e1rm'] for x in recent)/len(recent);change=round((b/a-1)*100,1)
        exercise_stats.append(dict(name=name,muscle=rows[0]['muscle'],sets=len(rows),sessions=len(by),best_weight=max((s['weight'] or 0 for s in rows)),best_e1rm=max((s['e1rm'] or 0 for s in rows)),change=change,history=history))
    latest=datetime.fromisoformat(sets[-1]['date']);cut=(latest-timedelta(days=27)).date().isoformat();recent=[s for s in work if s['date']>=cut];counts=Counter(s['muscle'] for s in recent)
    insights=[]
    for m in GROUPS:
        n=counts[m];insights.append(dict(title=f'{m}: {n} direct sets / 28 days',tone='blue' if n else 'amber',text=f'Logged average: {n/4:.1f} direct sets/week. '+('No direct work appears in this window. Review your goal and exercise mapping before adding work.' if n==0 else 'Compare this exposure with your recovery, technique and exercise-specific trends. Secondary muscle involvement is not counted as a full set.')))
    for e in sorted(exercise_stats,key=lambda e:e['sessions'],reverse=True)[:8]:
        if e['change'] is not None:
            insights.append(dict(title=f"{e['name']}: {e['change']:+.1f}% estimated strength",tone='blue' if e['change']>=0 else 'amber',text='First 3 vs latest 3 eligible sessions, using Epley estimates on sets of 1–12 reps. '+('The log supports an upward trend.' if e['change']>2 else 'The trend is flat or down; check load/reps, consistency, technique and recovery before changing the plan.')+' This comparison cannot establish why a change occurred.'))
    return dict(schema_version=1,generated_at=datetime.now(timezone.utc).isoformat(),range={'start':sets[0]['date'],'end':sets[-1]['date']},quality={'blank_rows_skipped':blank,'duplicate_sets_skipped':duplicates,'unmapped_exercises':sorted({s['exercise'] for s in sets if s['muscle']=='Unmapped'}),'rpe_coverage':round(sum(s['rpe'] is not None for s in work)/len(work)*100,1)},summary={'sets':len(work),'workouts':len(sessions),'reps':sum(s['reps'] or 0 for s in work),'volume':round(sum(s['volume'] for s in work),2),'minutes':round(sum(s['minutes'] for s in sessions.values()))},sets=sets,weekly=weekly,exercises=sorted(exercise_stats,key=lambda e:e['sessions'],reverse=True),insights=insights,methodology=['Direct sets only; compound secondary involvement excluded. Muscle mapping is an editable heuristic.','External load × reps is logged volume, not total biomechanical work. Assisted loads excluded. Dumbbell loads use the exported value without doubling.','Bodyweight and timed sets count as sets but do not receive estimated 1RM.','Trends describe associations. Sleep, diet, technique and proximity to failure are not established by this export.','Latest week may be incomplete. Missing weeks are shown as zero.'])

def publish(report):
    url=os.environ['SUPABASE_URL'];key=os.environ['SUPABASE_SERVICE_ROLE_KEY'];owner=os.environ['WORKOUT_OWNER_ID']
    data=json.dumps({'user_id':owner,'report':report}).encode()
    req=urllib.request.Request(url+'/rest/v1/workout_reports?on_conflict=user_id',data=data,headers={'apikey':key,'Authorization':'Bearer '+key,'Content-Type':'application/json','Prefer':'resolution=merge-duplicates'},method='POST')
    with urllib.request.urlopen(req,timeout=30) as res:
        if res.status not in (200,201,204): raise RuntimeError('Report publish failed')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',default='source');p.add_argument('--output',default='private-output/report.json');p.add_argument('--publish',action='store_true');args=p.parse_args()
    overrides_path=Path(args.source)/'muscle_overrides.json'; overrides=json.loads(overrides_path.read_text()) if overrides_path.exists() else {}
    if any(v not in GROUPS for v in overrides.values()): raise ValueError('Invalid muscle override')
    report=analyze(sorted(Path(args.source).glob('*.csv')),overrides)
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False))
    if args.publish: publish(report)
    print('Analysis complete. Private output generated.')
