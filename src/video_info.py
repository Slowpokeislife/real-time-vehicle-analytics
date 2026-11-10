"""Inspect videos and write JSON using ffprobe, no third-party Python deps."""
import argparse
import json
from pathlib import Path
import subprocess
from fractions import Fraction

def probe_video(path):
    p=Path(path)
    if not p.is_file(): raise FileNotFoundError(str(p))
    cp=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)],capture_output=True,text=True,check=True)
    obj=json.loads(cp.stdout)
    v=next(s for s in obj['streams'] if s['codec_type']=='video')
    rate=str(v.get('avg_frame_rate') or v.get('r_frame_rate') or '0/1')
    fps=float(Fraction(rate))
    return {'file':p.name,'codec':v.get('codec_name'),'pixel_format':v.get('pix_fmt'),
            'width':int(v['width']),'height':int(v['height']),'fps':fps,
            'frames':int(v['nb_frames']) if v.get('nb_frames') else None,
            'duration_seconds':float(obj['format'].get('duration',0)),
            'bytes':p.stat().st_size}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('video');ap.add_argument('--output');args=ap.parse_args()
    data=probe_video(args.video); print(json.dumps(data,indent=2))
    if args.output:
        p=Path(args.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
