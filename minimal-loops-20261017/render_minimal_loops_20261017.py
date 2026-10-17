"""Two original typography loops. No customer assets, downloads or font distribution."""
from pathlib import Path
import array, hashlib, json, math, os, shutil, subprocess, sys, time, wave
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'preparation/assets/minimal-loops-20261017'
W, H, FPS, D, SR = 1080, 1920, 30, 6, 48000
FF = shutil.which('ffmpeg')
FONTS = {}

def font(n, bold=False):
    k = (n, bold)
    if k not in FONTS:
        FONTS[k] = ImageFont.truetype(str(Path(os.environ['WINDIR'])/'Fonts'/('seguisb.ttf' if bold else 'segoeui.ttf')), n)
    return FONTS[k]

def clamp(x): return max(0., min(1., x))
def ease(x):
    x = clamp(x)
    return x*x*(3-2*x)
def gate(t, start, end, ramp=.28): return ease((t-start)/ramp)*ease((end-t)/ramp)

def label(im, value, y, size, color, opacity=1., bold=False, left=None):
    layer = Image.new('RGBA', im.size)
    draw = ImageDraw.Draw(layer)
    lines = value.split('\n')
    for i, line in enumerate(lines):
        box = draw.textbbox((0,0), line, font=font(size,bold))
        x = left if left is not None else (W-(box[2]-box[0]))/2
        if x < 78 or x+(box[2]-box[0]) > W-78:
            raise ValueError('Text outside safe width: '+line)
        draw.text((x, y+i*size*1.16), line, fill=color, font=font(size,bold))
    if opacity < 1:
        layer.putalpha(layer.getchannel('A').point(lambda a: round(a*clamp(opacity))))
    im.alpha_composite(layer)

def bg(kind):
    im=Image.new('RGBA',(W,H))
    d=ImageDraw.Draw(im)
    top,bottom=((14,21,21),(26,35,33)) if kind=='tabs' else ((224,213,192),(245,237,222))
    for y in range(H):
        p=y/(H-1)
        d.line((0,y,W,y),fill=tuple(round(a+(b-a)*p) for a,b in zip(top,bottom))+(255,))
    return im

BACK={k:bg(k) for k in ('tabs','call')}

def frame(kind, seconds):
    t=seconds%D
    im=BACK[kind].copy()
    light=(236,233,219,255) if kind=='tabs' else (37,40,35,255)
    muted=(139,158,151,255) if kind=='tabs' else (111,108,94,255)
    accent=(203,224,127,255) if kind=='tabs' else (163,78,48,255)
    label(im,'AFTER HOURS  /  '+('01' if kind=='tabs' else '02'),183,25,muted,left=96)
    label(im,'Hx Works · Self-initiated motion study',1745,25,muted)
    a=gate(t,0,5.99,.33)
    d=ImageDraw.Draw(im)
    if kind=='tabs':
        first=gate(t,.08,2.9,.38)
        second=gate(t,2.45,5.7,.4)
        label(im,'17 tabs.\nOne thought.',430+28*(1-ease(t/.6)),106,light,first,True,left=96)
        label(im,'Pick one.',504+28*(1-ease((t-2.45)/.5)),120,light,second,True,left=96)
        merge=ease((t-2.15)/1.1)
        for i in range(17):
            appear=ease((t-.25-i*.045)/.32)
            col,row=i%3,i//3
            x=96+col*302; y=912+row*60
            x=x+(156-x)*merge; y=y+(1046-y)*merge
            ww=284+(768-284)*merge; hh=47+(166-47)*merge
            alpha=a*appear*(1-merge*.90 if i!=8 else 1)
            layer=Image.new('RGBA',im.size)
            ld=ImageDraw.Draw(layer)
            fill=tuple(accent[:3])+(round(16*alpha),)
            outline=tuple(accent[:3])+(round((55+110*(i==8))*alpha),)
            ld.rounded_rectangle((x,y,x+ww,y+hh),radius=12,fill=fill,outline=outline,width=2)
            ld.line((x+22,y+hh*.5,x+min(ww*.6,350),y+hh*.5),fill=tuple(light[:3])+(round(125*alpha),),width=3)
            im.alpha_composite(layer)
        label(im,'THE NEXT THING',1260,25,accent,second)
        label(im,'A little less noise.',1330,37,muted,second)
        for i in range(3):
            x=96+i*31
            d=ImageDraw.Draw(im)
            d.ellipse((x,342,x+9,351),fill=tuple(accent[:3])+(round(a*255),))
    else:
        first=gate(t,.08,2.65,.35)
        second=gate(t,2.35,4.35,.35)
        third=gate(t,4.05,5.75,.36)
        label(im,'A quick call.',430+24*(1-ease(t/.55)),106,light,first,True,left=96)
        label(im,'Thirty minutes\nlater.',410,96,light,second,True,left=96)
        label(im,'Back to\nyour day.',430,108,light,third,True,left=96)
        layer=Image.new('RGBA',im.size); ld=ImageDraw.Draw(layer)
        cx,cy,r=540,1090,205
        ld.ellipse((cx-r,cy-r,cx+r,cy+r),outline=tuple(muted[:3])+(round(70*a),),width=2)
        end=-90+360*ease((t-.4)/3.5)
        if end>-90:
            ld.arc((cx-r,cy-r,cx+r,cy+r),-90,end,fill=tuple(accent[:3])+(round(230*a),),width=7)
        im.alpha_composite(layer)
        label(im,'00:30' if t<2.45 else '30:00',1020,84,light,a*(1-.65*third),True)
        label(im,'A fictional workday moment.',1400,31,muted,a)
    return im.convert('RGB')

def audio(kind,path):
    events=[(.40,720,.045,.10),(.82,900,.045,.08),(1.24,1080,.045,.07),(2.60,420,.25,.08),(3.9,660,.42,.07)] if kind=='tabs' else [(.45,620,.14,.08),(.68,780,.14,.07),(2.45,330,.2,.08),(4.08,550,.38,.07)]
    data=array.array('h'); peak=0.; square=0.
    for n in range(SR*D):
        t=n/SR; v=0.
        for start,freq,length,amp in events:
            u=t-start
            if 0<=u<length:
                env=math.sin(math.pi*u/length)**2
                v+=amp*env*math.sin(2*math.pi*freq*u)*math.exp(-3*u/length)
        v*=5  # Sparse original cues: keep peaks audible without approaching clipping.
        peak=max(peak,abs(v));square+=v*v
        v=round(max(-.99,min(.99,v))*32767)
        data.extend((v,v))
    if sys.byteorder!='little': data.byteswap()
    with wave.open(str(path),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes(data.tobytes())
    return {'peak_linear':peak,'rms_linear':math.sqrt(square/(SR*D)),'sample_frames':SR*D,'events_seconds':[e[0] for e in events],'third_party_samples':False,'perceptual_listening':'Not independently verified'}

def run(args):
    return subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,shell=False)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    if not FF: raise RuntimeError('Existing ffmpeg required; no installation')
    OUT.mkdir(parents=True,exist_ok=True)
    results=[]
    for kind in ('tabs','call'):
        start=time.monotonic()
        wav=OUT/(kind+'-sound.wav'); ar=audio(kind,wav)
        silent=OUT/(kind+'-silent.mp4'); final=OUT/('hx-'+kind+'-loop.mp4')
        cmd=[FF,'-nostdin','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(silent)]
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,shell=False)
        try:
            for n in range(FPS*D):proc.stdin.write(frame(kind,n/FPS).tobytes())
            proc.stdin.close(); err=proc.stderr.read().decode(errors='replace'); code=proc.wait(timeout=90)
            if code:raise RuntimeError(err)
        except BaseException:
            if proc.poll() is None:proc.kill();proc.wait()
            raise
        run([FF,'-nostdin','-hide_banner','-loglevel','error','-y','-i',str(silent),'-i',str(wav),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','128k','-t','6','-movflags','+faststart','-metadata','title=Hx Works - '+kind+' self-initiated loop','-metadata','comment=Original code-authored fictional typography study; synthesized audio; not client/travel footage',str(final)])
        decoded=run([FF,'-nostdin','-hide_banner','-loglevel','error','-i',str(final),'-map','0:v:0','-f','framemd5','pipe:1']).stdout.decode()
        count=sum(bool(x) and not x.startswith('#') for x in decoded.splitlines())
        if count!=FPS*D:raise RuntimeError('Unexpected decoded frame count')
        stills=[]
        for t in (.7,1.8,3.2,4.7,5.9):
            p=OUT/f'{kind}-{t:.1f}.png'
            run([FF,'-nostdin','-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',str(final),'-frames:v','1',str(p)])
            stills.append(p)
        sheet=Image.new('RGB',(5*240,466),'#222222'); sd=ImageDraw.Draw(sheet)
        for i,p in enumerate(stills):
            with Image.open(p) as im:sheet.paste(im.resize((240,426),Image.Resampling.LANCZOS),(i*240,40))
            sd.text((i*240+10,8),p.stem,font=font(20),fill='white')
        sheet.save(OUT/(kind+'-contact.jpg'),quality=95)
        info=subprocess.run([FF,'-nostdin','-hide_banner','-i',str(final)],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False).stderr.decode(errors='replace')
        results.append({'file':final.name,'sha256':sha(final),'bytes':final.stat().st_size,'decoded_frames':count,'width':W,'height':H,'fps':FPS,'seconds':D,'audio':ar,'source_at_0_and_6_identical':frame(kind,0).tobytes()==frame(kind,D).tobytes(),'actual_media_header':info,'render_seconds':time.monotonic()-start})
        print(json.dumps({'rendered':final.name,'frames':count,'seconds':round(time.monotonic()-start,1)}),flush=True)
    receipt={'source_sha256':sha(Path(__file__)),'python':sys.version.split()[0],'tool_version':run([FF,'-version']).stdout.decode().splitlines()[0],'authorship':'Self-initiated code-authored fictional corporate/life typography loops, no customer or travel footage, no external assets/music/font redistribution.','outputs':results,'limitations':'Not travel-footage editing or client work. No engagement or buyer acceptance claim. Audio perceptual quality not independently verified. Actual player behavior still requires native observation.'}
    (OUT/'render-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print('Complete',flush=True)

if __name__=='__main__':main()
