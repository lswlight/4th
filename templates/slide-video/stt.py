"""무료 받아쓰기 (faster-whisper small). 사용: python3 stt.py 파일 [out.json]  → 문장·단어 시각"""
import sys, json, subprocess, numpy as np
from faster_whisper import WhisperModel
import os
M=os.path.expanduser('~/.cache/slide-video/whisper')   # 처음 한 번 모델(약 500MB)을 받는다
raw=subprocess.run(['ffmpeg','-v','error','-i',sys.argv[1],'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout
a=np.frombuffer(raw,np.float32)
m=WhisperModel('small',device='cpu',compute_type='int8',download_root=M)
segs,_=m.transcribe(a,language='ko',word_timestamps=True,vad_filter=True)
out=[dict(start=round(s.start,2),end=round(s.end,2),text=s.text.strip(),words=[(round(w.start,2),round(w.end,2),w.word) for w in s.words]) for s in segs]
if len(sys.argv)>2: json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
for s in out: print(f"{s['start']:7.2f}-{s['end']:7.2f} {s['text']}")
