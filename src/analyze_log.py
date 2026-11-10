"""Analyze the recorded binary signal; never reconstruct it from an annotated MP4."""
import argparse,csv,json
from pathlib import Path

def read_flags(path):
    result=[]
    for idx,line in enumerate(Path(path).read_text(encoding='utf8').splitlines(),1):
        val=line.strip()
        if not val: continue
        if val not in ('0','1'): raise ValueError(f'Invalid flag on line {idx}: {val}')
        result.append(int(val))
    if not result: raise ValueError('Empty inference log')
    return result

def episodes(flags):
    spans=[]; start=None
    for i,flag in enumerate(list(flags)+[0]):
        if flag and start is None: start=i
        elif not flag and start is not None:
            spans.append((start,i-1));start=None
    return spans

def summarize(flags,fps):
    if fps<=0:raise ValueError('fps must be positive')
    spans=episodes(flags)
    return {'total_frames':len(flags),'flagged_frames':sum(flags),
            'flagged_percentage':100*sum(flags)/len(flags),
            'video_duration_seconds':len(flags)/fps,
            'flagged_duration_seconds':sum(flags)/fps,
            'episodes_count':len(spans),
            'episodes':[{'start_frame':a,'end_frame':b,'start_seconds':a/fps,
                         'end_seconds':(b+1)/fps,'duration_seconds':(b-a+1)/fps} for a,b in spans]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('log');ap.add_argument('--fps',type=float,required=True);ap.add_argument('--out',default='outputs');args=ap.parse_args()
    flags=read_flags(args.log);s=summarize(flags,args.fps);out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    (out/'tailgating_summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf8')
    with (out/'tailgating_timeline.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.writer(f);w.writerow(['frame','time_seconds','potential_tailgating']);w.writerows((i,round(i/args.fps,6),v) for i,v in enumerate(flags))
    with (out/'tailgating_episodes.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=['start_frame','end_frame','start_seconds','end_seconds','duration_seconds']);w.writeheader();w.writerows(s['episodes'])
    print(json.dumps(s,indent=2))
if __name__=='__main__':main()
