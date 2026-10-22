from pathlib import Path
import json, hashlib, shutil, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'assets-v1'
for d in ['avatars','modes','icons','panels','backgrounds','brand','art']:(OUT/d).mkdir(parents=True,exist_ok=True)
P={'cream':'#F6E7C8','navy':'#1B233F','teal':'#16A6A4','coral':'#F06D5F','mango':'#F5B940','lavender':'#A88BEB'}
PLAYERS=['#6599D1','#D99B63','#79AE84','#A18BC5','#CD87AA','#C5B56C','#70B8BF','#C6C8CE']
N=P['navy']
def svg(name,body,w=256,h=256):
    (OUT/name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>',encoding='utf8')
def path(d,fill,stroke=N,sw=5):return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"/>'
def rect(x,y,w,h,c,r=12,sw=5):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{c}" stroke="{N}" stroke-width="{sw}"/>'
def poly(points,c):return f'<polygon points="{points}" fill="{c}" stroke="{N}" stroke-width="5" stroke-linejoin="round"/>'
def circle(x,y,r,c,sw=5):return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" stroke="{N}" stroke-width="{sw}"/>'
def star(x,y,s,c):return f'<g transform="translate({x} {y}) scale({s})">'+path('M0 -22L7 -8L23 -5L12 6L15 23L0 15L-15 23L-12 6L-23 -5L-7 -8Z',c,sw=3)+'</g>'
def tile(x,y,s,c):return path(f'M{x} {y}l{s} -{s/2}l{s} {s/2}l-{s} {s/2}Z',c,sw=3)
def base():return '<ellipse cx="128" cy="225" rx="98" ry="15" fill="#1B233F" opacity=".16"/>'

# Editable illustrations: text-free so localization stays in the game UI.
b=base()+rect(55,46,146,153,P['navy'],23)+rect(47,36,146,153,P['teal'],23)
b+=path('M94 84C94 49 154 47 158 80C162 103 129 108 127 128L127 136',P['teal'],P['cream'],14)+circle(127,156,7,P['cream'],0)
for x,y,c,a in [(21,173,'coral',-12),(78,185,'lavender',-4),(137,184,'mango',7),(190,171,'teal',14)]:
    b+=f'<g transform="rotate({a} {x+22} {y+22})">'+rect(x,y+5,44,44,N,8)+rect(x,y,44,44,P[c],8)+path(f'M{x+11} {y+17}h22M{x+11} {y+28}h15','none',N,4)+'</g>'
b+=star(32,64,.75,P['mango'])+star(218,100,.55,P['coral']);svg('modes/trivia.svg',b)
b=base()
for x,y,w,c in [(25,189,207,'lavender'),(43,155,171,'teal'),(61,121,135,'coral'),(79,87,99,'mango')]:
    b+=rect(x,y,w,32,N,7)+rect(x,y-7,w,32,P[c],7)+path(f'M{x+14} {y+2}h{w-28}','none',P['cream'],3)
b+=path('M111 39H145L142 63Q128 82 114 63Z',P['mango'])+path('M111 44H99Q96 63 114 63M145 44H157Q160 63 142 63','none',P['mango'],6)+path('M128 76V87M112 88H144','none',N,6)+star(48,80,.7,P['lavender'])+star(208,105,.6,P['mango']);svg('modes/millionaire.svg',b)
b=base()
for x,y,c,a in [(38,54,'teal',-17),(91,54,'coral',16),(68,53,'lavender',0)]:
    b+=f'<g transform="rotate({a} {x+58} {y+73})">'+rect(x,y+7,116,151,N,16)+rect(x,y,116,151,P[c],16)+rect(x+12,y+14,92,119,N,10,3)+path(f'M{x+42} {y+60}C{x+42} {y+37} {x+80} {y+37} {x+80} {y+59}C{x+80} {y+73} {x+60} {y+75} {x+60} {y+87}','none',P['cream'],8)+circle(x+60,y+103,4,P['cream'],0)+'</g>'
b+=star(30,171,.55,P['mango'])+star(221,60,.6,P['coral']);svg('modes/imposter.svg',b)
b=base()+poly('21,108 128,53 236,108 236,157 128,214 21,157',N)+poly('21,101 128,46 236,101 128,158',P['cream'])
for row in range(5):
    for col in range(5):
        x=42+(col+row)*17.2;y=104+(row-col)*8.6
        c=P['teal'] if col+row<4 else P['coral']
        b+=tile(x,y,15.7,c)
b+=path('M132 125V40','none',P['cream'],7)+path('M135 42L180 50L166 63L135 62Z',P['mango'],sw=4)+star(39,49,.6,P['lavender']);svg('modes/turf.svg',b)

# Minimal original whole-animal drawings. The same geometry also ships in one color.
names=['lion','bat','turtle','fox','owl','whale','rabbit','deer']
for i,name in enumerate(names):
    source=ET.fromstring((ROOT/'animals'/f'{name}.svg').read_text())
    group=list(source)[1]
    shape=''.join(ET.tostring(e,encoding='unicode').replace('ns0:','').replace(':ns0','') for e in group)
    mono=f'<g fill="{N}" color="{N}" transform="translate(6 6) scale(2.44)">{shape}</g>'
    svg(f'avatars/{name}.svg',mono)
    badge=rect(7,15,242,233,N,44)+rect(7,7,242,233,PLAYERS[i],44)
    badge+=f'<g fill="{N}" color="{N}" transform="translate(24 24) scale(2.08)">{shape}</g>'
    svg(f'avatars/{name}-badge.svg',badge)

icons={
'play':'M29 20L79 50L29 80Z','pause':'M29 23H40V77H29ZM60 23H71V77H60Z',
'next':'M22 24L61 50L22 76ZM72 24V76','back':'M57 24L30 50L57 76M31 50H83',
'check':'M23 51L42 70L79 29','cross':'M29 29L71 71M71 29L29 71',
'lock':'M31 43V31C31 7 69 7 69 31V43M25 43H75V82H25Z',
'hourglass':'M28 16H72L68 31L54 49L68 68L72 84H28L32 68L46 49L32 31Z',
'volume':'M16 41H31L52 24V76L31 59H16ZM66 36Q80 50 66 64M77 25Q101 50 77 75',
'mute':'M16 41H31L52 24V76L31 59H16ZM68 38L88 62M88 38L68 62',
'phone':'M31 10H69Q77 10 77 18V82Q77 90 69 90H31Q23 90 23 82V18Q23 10 31 10ZM44 79H56',
'remote':'M41 8H59Q71 8 71 20V80Q71 92 59 92H41Q29 92 29 80V20Q29 8 41 8ZM43 27H57M50 20V34M43 48H57M43 64H57',
'flag':'M25 87V13L78 23L64 44L25 39','settings':'M42 13H58L62 25L73 29L84 25L92 39L83 49L84 61L89 72L76 82L64 77L54 83L47 93L32 88L31 75L21 68L8 67L8 51L19 44L23 32L21 20L35 13ZM39 50A13 13 0 1 0 65 50A13 13 0 1 0 39 50',
'trophy':'M31 15H69L66 48Q50 70 34 48ZM31 23H15Q12 46 35 47M69 23H85Q88 46 65 47M50 62V81M32 84H68',
'reveal':'M18 29H82V78H18ZM28 18H71M40 12H60M35 48H65M35 59H56'
}
for name,d in icons.items():svg(f'icons/{name}.svg',f'<g transform="translate(8 8) scale(2.4)">'+path(d,'none',N,7)+'</g>')

for name,c,pressed in [('default','teal',False),('focus','mango',False),('pressed','teal',True),('locked','lavender',False),('correct','teal',False),('incorrect','coral',False),('disabled','navy',False)]:
    y=10 if pressed else 3
    body=path('M19 11H301L317 27V77L301 93H19L3 77V27Z',N,sw=3)
    body+=path(f'M19 {y}H301L317 {y+16}V{y+66}L301 {y+82}H19L3 {y+66}V{y+16}Z',P[c],sw=3)
    body+=path(f'M23 {y+7}H296L307 {y+18}','none',P['cream'],2)
    if name=='focus':body=path('M18 1H302L319 18V78L302 95H18L1 78V18Z',P['cream'],sw=2)+body
    if name=='disabled':body=f'<g opacity=".5">{body}</g>'
    svg(f'panels/button-{name}.svg',body,320,96)
svg('panels/question.svg',path('M27 9H613L631 27V183L613 201H27L9 183V27Z',N)+path('M27 3H613L631 21V173L613 191H27L9 173V21Z',P['cream'])+path('M34 12H605','none','#FFFFFF',2),640,210)
svg('panels/tile.svg',rect(4,10,88,85,N,15,3)+rect(4,3,88,85,P['teal'],15,3)+path('M19 12H77','none',P['cream'],2),100,100)
svg('panels/tile-cooldown.svg',rect(4,10,88,85,N,15,3)+rect(4,3,88,85,P['navy'],15,3)+''.join(path(f'M{x} 86L{x+60} 6','none','#A88BEB',3) for x in [-30,-10,10,30])+f'<g transform="translate(28 25) scale(.44)">{path(icons["hourglass"],P["cream"],P["navy"],5)}</g>',100,100)

for name,top,edge in [('menu',P['lavender'],P['navy']),('trivia','#263C57',P['navy']),('millionaire','#544179',P['navy']),('imposter','#633851',P['navy']),('turf','#22585F',P['navy'])]:
    body=f'<defs><linearGradient id="g" x2="0" y2="1"><stop stop-color="{top}"/><stop offset="1" stop-color="{edge}"/></linearGradient><radialGradient id="r"><stop stop-color="{P["teal"]}" stop-opacity=".15"/><stop offset="1" stop-color="{P["teal"]}" stop-opacity="0"/></radialGradient></defs><rect width="1920" height="1080" fill="url(#g)"/><ellipse cx="960" cy="650" rx="900" ry="480" fill="url(#r)"/>'
    body+=f'<path d="M0 920L240 1040L0 1080ZM1920 820L1700 980L1920 1080Z" fill="{P["navy"]}" opacity=".18"/>'
    svg(f'backgrounds/{name}.svg',body,1920,1080)

for name,c in [('navy',P['navy']),('cream',P['cream'])]:
    b='<g font-family="Arial,sans-serif" font-weight="900" font-size="116" letter-spacing="-5">'
    b+=f'<text x="39" y="144" fill="{P["lavender"]}">TriviTV</text><text x="34" y="133" fill="{c}">TriviTV</text></g>'
    b+=star(468,49,.8,P['mango'])+star(18,73,.45,P['coral'])
    svg(f'brand/wordmark-{name}.svg',b,520,180)
svg('brand/app-mark.svg',rect(4,12,248,240,N,45)+rect(4,4,248,240,P['teal'],45)+path('M50 62H206V100H148V192H108V100H50Z',P['cream'],sw=6)+star(209,195,.65,P['mango']))
svg('brand/decorations.svg',star(49,47,1,P['mango'])+star(140,68,.7,P['coral'])+star(212,38,.45,P['cream'])+rect(83,146,37,37,P['teal'],6,3)+rect(160,173,32,32,P['lavender'],6,3)+circle(42,200,14,P['mango'],3))

tokens={'theme':P,'players':[{'slot':i+1,'animal':a,'color':PLAYERS[i]} for i,a in enumerate(names)],'playerIdentity':'Always pair color with animal and player number. Player colors are independent of mode colors.','fontFamily':'Segoe UI, Arial, sans-serif','radii':{'button':16,'panel':24},'outline':N,'reference':'Screenshot 2026-10-21 160320.png; first playful Canva direction','version':1}
(OUT/'tokens.json').write_text(json.dumps(tokens,indent=2),encoding='utf8')
(OUT/'theme.css').write_text('''/* TriviTV playful arcade asset theme; opt in with class arcade. */
:root{--cream:#F6E7C8;--navy:#1B233F;--teal:#16A6A4;--coral:#F06D5F;--mango:#F5B940;--lavender:#A88BEB;--p1:#6599D1;--p2:#D99B63;--p3:#79AE84;--p4:#A18BC5;--p5:#CD87AA;--p6:#C5B56C;--p7:#70B8BF;--p8:#C6C8CE}
.arcade{font-family:'Segoe UI',Arial,sans-serif;color:var(--cream);background:var(--navy)}
.arcade button,.arcade .button{font:inherit;font-weight:800;font-size:1rem;border:3px solid var(--navy);border-radius:16px;background:var(--teal);color:var(--navy);padding:14px 23px;box-shadow:0 6px 0 var(--navy),inset 0 2px 0 #ffffff55;cursor:pointer;transition:transform 100ms ease,box-shadow 100ms ease}
.arcade button:focus-visible,.arcade .is-focus{outline:3px solid var(--cream);outline-offset:3px;background:var(--mango)}
.arcade button:active,.arcade .is-pressed{transform:translateY(4px);box-shadow:0 2px 0 var(--navy),inset 0 2px 0 #ffffff33}
.arcade .is-correct{background:var(--teal)}.arcade .is-incorrect{background:var(--coral)}.arcade .is-locked{background:var(--lavender)}.arcade button:disabled{background:#596179;color:#E0E3EA;cursor:default;transform:none;box-shadow:none}
.arcade .panel{border:3px solid var(--navy);border-radius:24px;background:var(--cream);color:var(--navy);padding:24px;box-shadow:0 8px 0 #12192e}
.arcade .animal{width:48px;height:48px;object-fit:contain}.arcade .mode-symbol{width:112px;height:112px;object-fit:contain}
.arcade .control-icon{display:inline-block;width:1.5em;height:1.5em;background:currentColor;mask:var(--icon) center/contain no-repeat;-webkit-mask:var(--icon) center/contain no-repeat}
@media(prefers-reduced-motion:reduce){.arcade *{transition:none!important}}
''',encoding='utf8')
print(f'Built {len(list(OUT.rglob("*.svg")))} SVG assets, tokens and CSS at {OUT}')
