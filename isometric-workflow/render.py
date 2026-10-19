"""Original six-second isometric workflow; synthetic data, no client assets."""
from pathlib import Path
import hashlib, json, math, shutil, subprocess
from html import escape
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageStat

OUT=Path(__file__).resolve().parent
W,H,FPS,D,S=1280,720,30,6,2
BG='#101d2b'; INK='#eff5fa'; MUTED='#99aabd'; LINE='#34495e'; ACC='#77e8c4'
fonts={}
def font(n,bold=False):
    k=(n,bold)
    if k not in fonts: fonts[k]=ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),n*S)
    return fonts[k]

class Canvas:
    def __init__(self):
        self.im=Image.new('RGB',(W*S,H*S),BG); self.d=ImageDraw.Draw(self.im)
        self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', '<title>Request to record — original isometric workflow study</title>',f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    def poly(self,pts,fill):
        self.d.polygon([(round(x*S),round(y*S)) for x,y in pts],fill=fill)
        self.svg.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+f'" fill="{fill}"/>')
    def line(self,pts,fill,width=2):
        self.d.line([(round(x*S),round(y*S)) for x,y in pts],fill=fill,width=round(width*S),joint='curve')
        self.svg.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+f'" fill="none" stroke="{fill}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>')
    def circle(self,x,y,r,fill):
        self.d.ellipse(((x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S),fill=fill)
        self.svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{fill}"/>')
    def text(self,x,y,value,size=20,fill=INK,bold=False):
        box=self.d.textbbox((0,0),value,font=font(size,bold))
        assert x>=32 and y>=20 and x+(box[2]-box[0])/S<W-32 and y+size<H-20,(value,box)
        self.d.text((round(x*S),round(y*S)),value,font=font(size,bold),fill=fill)
        self.svg.append(f'<text x="{x}" y="{y+size*.94:.2f}" font-family="Segoe UI, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{fill}">{escape(value)}</text>')
    def finish(self): return self.im.resize((W,H),Image.Resampling.LANCZOS)

def diamond(c,x,y,rx,ry,z,top,left,right):
    c.poly([(x-rx,y),(x,y+ry),(x,y+ry+z),(x-rx,y+z)],left)
    c.poly([(x,y+ry),(x+rx,y),(x+rx,y+z),(x,y+ry+z)],right)
    c.poly([(x-rx,y),(x,y-ry),(x+rx,y),(x,y+ry)],top)

NODES=[(330,350,'01','Request'),(640,218,'02','Validate'),(950,350,'03','Record'),(640,482,'04','Confirm')]
def render(t):
    c=Canvas()
    c.text(62,35,'HX WORKS  /  MOTION STUDY',15,MUTED,True)
    c.text(62,67,'From request to record.',38,INK,True)
    c.text(64,121,'One route. Four clear steps.',18,MUTED)
    c.text(1005,40,'06 s  /  LOOP',15,MUTED)
    centers=[(x,y+22) for x,y,_,_ in NODES]
    c.line(centers+[centers[0]],LINE,5)
    phase=(t/D*4)%4; edge=int(phase); p=phase-edge
    a,b=centers[edge],centers[(edge+1)%4]
    # Constant-speed packet follows each same-length edge. No performance claim.
    x=a[0]+(b[0]-a[0])*p; y=a[1]+(b[1]-a[1])*p
    for i in range(8,0,-1):
        q=max(0,p-i*.013)
        c.circle(a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q,2.5,'#376f73')
    c.circle(x,y,7,ACC); c.circle(x,y,2.4,'#eefdf7')
    for i,(nx,ny,num,name) in enumerate(NODES):
        active=max(0,1-abs(phase-i))
        if i==0: active=max(active,max(0,phase-3))
        # Platform stays fixed; gentle top lift signals which step the packet leaves.
        lift=3*active
        diamond(c,nx,ny+33,92,39,9,'#192b3c','#122333','#20364a')
        diamond(c,nx,ny-lift,72,31,25,'#355267','#21394d','#294359')
        diamond(c,nx,ny-4-lift,60,26,5,ACC if active>.52 else '#c5e1df','#6da79f','#87bbb3')
        # Upright, editable vector symbols for the four distinct operations.
        cy=ny-35-lift
        if i in (0,3):
            c.poly([(nx-22,cy-38),(nx+12,cy-38),(nx+25,cy-25),(nx+25,cy+9),(nx-22,cy+9)],'#edf4f6')
            c.poly([(nx+12,cy-38),(nx+12,cy-25),(nx+25,cy-25)],'#9fb9c7')
            if i==0:
                for dy,w in [(-20,23),(-10,30),(0,18)]: c.line([(nx-12,cy+dy),(nx-12+w,cy+dy)],'#526f82',3)
            else: c.line([(nx-10,cy-13),(nx-2,cy-5),(nx+14,cy-23)],'#217a68',4)
        elif i==1:
            c.poly([(nx-28,cy-32),(nx,cy-44),(nx+28,cy-32),(nx+23,cy-4),(nx,cy+15),(nx-23,cy-4)],'#edf4f6')
            c.line([(nx-14,cy-14),(nx-3,cy-4),(nx+16,cy-26)],'#217a68',5)
        else:
            for dy in [3,-12,-27]:
                diamond(c,nx,cy+dy,34,13,8,'#edf4f6','#a7c1cf','#bfd6df')
        c.text(nx-39,ny+88,num,13,ACC,True)
        c.text(nx-13,ny+83,name,19,INK,True)
    c.line([(62,647),(1218,647)],'#2a3d50',1)
    c.circle(71,679,4,ACC)
    c.text(86,666,'Illustrative workflow',16,MUTED)
    c.text(864,666,'Self-initiated  /  Code-authored',16,MUTED)
    return c

def main():
    ff=shutil.which('ffmpeg'); assert ff
    cmd=[ff,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'workflow-loop.mp4')]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for f in range(FPS*D): proc.stdin.write(render(f/FPS).finish().tobytes())
    proc.stdin.close(); assert proc.wait()==0
    contact=Image.new('RGB',(W, H),BG)
    for i,t in enumerate([.45,1.95,3.45,4.95]):
        im=render(t).finish(); im.resize((W//2,H//2)).save(OUT/f'stage-{i+1}.png')
        contact.paste(im.resize((W//2,H//2)),((i%2)*W//2,(i//2)*H//2))
    contact.save(OUT/'contact-sheet.jpg',quality=92)
    frame=render(1.95); frame.finish().save(OUT/'poster.png')
    (OUT/'poster.svg').write_text('\n'.join(frame.svg+['</svg>']),encoding='utf-8')
    first=render(0).finish(); last=render(D-1/FPS).finish(); wrap=render(D).finish()
    qa={'width':W,'height':H,'fps':FPS,'frames':FPS*D,'duration_seconds':D,'synthetic':True,'loop_exact_endpoint_bbox':ImageChops.difference(first,wrap).getbbox(),'last_first_mean_absolute_channels':ImageStat.Stat(ImageChops.difference(first,last)).mean,'claim_limits':['Own illustrative workflow only','No After Effects or Cinema4D project','No client work or financial system claims','No full explainer, voiceover, sound or narrative capability proved']}
    qa['sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.name!='qa.json'}
    (OUT/'qa.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
    print(json.dumps(qa))
if __name__=='__main__': main()
