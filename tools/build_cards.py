"""Generates the profile cards as static SVGs with fonts embedded.
Run: python3 build_cards.py   (needs only the 3 .woff2 files next to it, in fonts/)"""
import base64, html, pathlib
H = pathlib.Path(__file__).parent
OUT = H / "cards"; OUT.mkdir(exist_ok=True)
def b64(n): return base64.b64encode((H/"fonts"/n).read_bytes()).decode()
FONTS = f"""
@font-face{{font-family:'IS';src:url(data:font/woff2;base64,{b64('is-reg.woff2')}) format('woff2');}}
@font-face{{font-family:'IS';font-style:italic;src:url(data:font/woff2;base64,{b64('is-it.woff2')}) format('woff2');}}
@font-face{{font-family:'GM';src:url(data:font/woff2;base64,{b64('gm.woff2')}) format('woff2');}}"""
PAPER,BORDER,INK,MUTED="#F5F4F0","#E4E2DA","#141413","#5C5B56"
BLUE,RED,YEL="#234BFF","#EE3625","#FFC700"
SANS="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
BASE=f"""{FONTS}
.serif{{font-family:'IS',Georgia,serif}} .mono{{font-family:'GM',Menlo,monospace}} .sans{{font-family:{SANS}}}
@keyframes rise{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
.rise{{animation:rise .8s cubic-bezier(.22,1,.36,1) both}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}"""
def esc(s): return html.escape(s)
def svg(w,h,body,extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">'
            f'<style>{BASE}{extra}</style>'
            f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="18" fill="{PAPER}" stroke="{BORDER}"/>{body}</svg>')
def lines(items,x,y,size,lh,cls,fill,anchor="start"):
    return "".join(f'<text x="{x}" y="{y+i*lh}" font-size="{size}" class="{cls}" fill="{fill}">{esc(t)}</text>' for i,t in enumerate(items))

# HERO
hero=(f'<circle cx="52" cy="54" r="5" fill="{BLUE}" style="animation:pulse 2.4s infinite"/>'
 f'<text x="68" y="59" font-size="13" class="mono" fill="{MUTED}">Python &amp; DevOps · Final-year B.Tech CSE (Data Science)</text>'
 f'<text x="48" y="152" font-size="92" class="serif rise" fill="{INK}" style="animation-delay:.1s">Saurav</text>'
 f'<text x="48" y="238" font-size="92" class="serif rise" font-style="italic" fill="{BLUE}" style="animation-delay:.3s">Chaudhary</text>'
 + lines(["I build Python tools and","backend services, and I automate","testing and deployment with","Docker and CI."],520,112,19,28,"sans",INK)
 + f'<text x="520" y="246" font-size="14" class="mono" fill="{BLUE}">github.com/saurav-0080 ↗</text>')
(OUT/"hero.svg").write_text(svg(880,290,hero),encoding="utf-8")

# TILES (combined into one strip so GitHub cannot wrap them)
TILES=[]
def tile(fn,label,color,num,suffix,text,href_hint,ink=None,delay=0):
    ink=ink or "#FFFFFF"
    body=(f'<rect x=".5" y=".5" width="279" height="223" rx="18" fill="{color}"/>'
     f'<text x="26" y="40" font-size="13" class="mono" fill="{ink}">{label}</text>'
     f'<text x="26" y="112" font-size="72" class="serif rise" fill="{ink}" style="animation-delay:{delay}s">{num}</text>'
     f'<text x="26" y="136" font-size="15" class="mono" fill="{ink}">{suffix}</text>'
     + lines(text,26,164,12.5,17,"sans",ink)
     + f'<text x="254" y="40" font-size="16" class="mono" fill="{ink}">{href_hint}</text>')
    TILES.append(body)
tile("build.svg","BUILD",BLUE,"88+","tests in FileFlux",["Python file organizer with dedup,","undo, CLI, Docker and CI. Docker","and testing on ORCA (SIH)."],"↗",delay=.5)
tile("create.svg","SHIP",RED,"3","tools",["Docker, Jenkins, Selenium:","containers, CI and test","automation."],"",delay=.65)
tile("learn.svg","LEARN",YEL,"17","weeks, Python backend",["B.Tech CSE (Data Science), 2027.","Now: async Python, building","Shadow Proxy."],"",ink=INK,delay=.8)

# REPO CARD
repo=(f'<text x="26" y="46" font-size="30" class="serif" fill="{INK}">FileFlux</text>'
 f'<text x="404" y="42" font-size="12" class="mono" fill="{MUTED}" text-anchor="end">v1.0.1</text>'
 + lines(["Python file organizer: SHA-256 dedup,","undo, CLI + GUI, SQLite, Docker, CI."],26,78,14,21,"sans",MUTED)
 + f'<circle cx="32" cy="136" r="6" fill="#3572A5"/><text x="46" y="141" font-size="12" class="mono" fill="{INK}">Python</text>'
 f'<text x="130" y="141" font-size="12" class="mono" fill="{MUTED}">88+ tests</text>')
(OUT/"repo_1.svg").write_text(svg(430,168,repo),encoding="utf-8")
print("done:", sorted(p.name for p in OUT.iterdir()))

strip="".join(f'<g transform="translate({i*300},0)">{b}</g>' for i,b in enumerate(TILES))
(OUT/"tiles.svg").write_text(
 f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 224" width="880" height="224" role="img" aria-label="Build: 88+ tests in FileFlux. Ship: Docker, Jenkins, Selenium. Learn: Python backend roadmap.">'
 f'<style>{BASE}</style>{strip}</svg>',encoding="utf-8")
print("tiles.svg written")
