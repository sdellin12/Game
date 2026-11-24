"""Dependency-free SVG card templates and offline comparison gallery.

Design fixtures only: never imports the game engine or executes card text.
"""
import base64
import html
import json
import re
import textwrap
from pathlib import Path
ROOT = Path(__file__).resolve().parent
PALETTE = {
 'Generic':('#647784','GENERIC'), 'Red':('#ad363e','DRIVE'),
 'Orange':('#c36528','DARING'), 'White':('#687c94','DISCIPLINE'),
 'Green':('#35745b','RESILIENCE'), 'Gold':('#9b6b20','COOPERATION'),
 'Blue':('#315d91','INSIGHT'), 'Purple':('#76558d','CUNNING'),
 'Black':('#58495b','AMBITION'), 'Silver':('#566f85','INGENUITY'),
 'Teal':('#267f80','ADAPTABILITY'),
}


def esc(value):
 return html.escape(str(value), quote=True)


def rect(x,y,w,h,fill,rx=0,extra=''):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" {extra}/>'


def text(x,y,value,size=24,fill='#152b36',weight=400,extra=''):
 return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" {extra}>{esc(value)}</text>'


def wrap_lines(value, width):
 return textwrap.wrap(value, width=width, break_long_words=False, break_on_hyphens=False) or ['']


def content_lines(card):
 lines=[]
 if card.get('access_detail'):
  lines += [('access',line) for line in wrap_lines(card['access_detail'],55)]
 for ability in card['abilities']:
  if lines:
   lines.append(('space',''))
  if ability.get('label'):
   lines += [('label',line) for line in wrap_lines(ability['label'],49)]
  if ability.get('cost'):
   lines += [('cost',line) for line in wrap_lines('COST · '+ability['cost'],55)]
  lines += [('body',line) for line in wrap_lines(ability['text'],55)]
  if ability.get('timing'):
   lines += [('timing',line) for line in wrap_lines(ability['timing'],58)]
 return lines


def art(card, accent):
 """Named replaceable vector placeholder, not final generated card artwork."""
 if card.get('art_image'):
  path=(ROOT/card['art_image']).resolve()
  if not path.is_relative_to((ROOT/'art').resolve()) or path.suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):
   raise ValueError('art_image must be a PNG/JPEG/WebP inside design/cards/art')
  mime={'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp'}[path.suffix.lower()]
  uri='data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()
  return f'<image id="artwork-image" href="{uri}" width="750" height="1050" preserveAspectRatio="xMidYMid slice"/>'
 return (rect(0,0,750,1050,'#8ebbb8')+
  '<circle cx="540" cy="290" r="210" fill="#f4d98f" opacity=".25"/>'
  '<path d="M0 590 Q180 410 400 570 T750 490 V1050 H0Z" fill="#355d62"/>'
  '<path d="M0 660 Q220 520 400 660 T750 600 V1050 H0Z" fill="#1d414b"/>'
  '<g transform="translate(375 420)" stroke="#173746" stroke-width="10" stroke-linejoin="round">'
  '<path d="M-130-30 L-145-135 L-55-84 Q0-108 55-84 L145-135 L130-30 V85 Q0 155-130 85Z" fill="#d9e3da"/>'
  '<path d="M-112-52 L-120-105 L-76-78 M112-52 L120-105 L76-78" stroke="#b18748" fill="none"/>'
  '<path d="M-108 18 Q0-46 108 18 V80 Q0 130-108 80Z" fill="#eebc6e" stroke="none"/>'
  '<ellipse cx="-57" cy="0" rx="17" ry="24" fill="#173746" stroke="none"/>'
  '<ellipse cx="57" cy="0" rx="17" ry="24" fill="#173746" stroke="none"/>'
  '<path d="M-18 42 L0 55 L18 42 M0 55 V75" fill="none"/>'
  '<path d="M-40 210 L-87 155 L-80 101 M40 210 L87 155 L80 101" fill="#a9c5bd"/>'
  '<circle cy="156" r="27" fill="'+accent+'" stroke="#f8dda0"/>'
  '</g>')


def render(card, style):
 if style not in ('standard','full-art'):
  raise ValueError('unsupported style')
 if not re.fullmatch(r'[a-z][a-z0-9-]*',card['id']):
  raise ValueError('card id must be a safe lowercase filename slug')
 accent,identity=PALETTE[card['color']]
 title_lines=wrap_lines(card['name'],28) if len(card['name'])>27 else [card['name']]
 if len(title_lines)>2 or any(len(line)>28 for line in title_lines):
  raise ValueError('name exceeds two-line title capacity')
 title_svg=''.join(text(45,62+i*33,line,30,'#fff4d8',700,extra='font-family="Georgia"') for i,line in enumerate(title_lines)) if len(title_lines)>1 else text(45,78,card['name'],36,'#fff4d8',700,extra='font-family="Georgia"')
 lines=content_lines(card)
 if any(len(value)>62 for _,value in lines):
  raise ValueError('unbreakable text exceeds template width')
 line_heights={'access':25,'label':28,'cost':25,'body':27,'timing':24,'space':12}
 needed=sum(line_heights[k] for k,_ in lines)
 panel_h=max(185,needed+70+(28 if card['traits'] else 0))
 if panel_h>470:
  raise ValueError(f"{card['id']}: rules exceed v1 capacity; edit wording/template, never silently shrink")
 panel_y=930-panel_h
 result=['<svg xmlns="http://www.w3.org/2000/svg" width="750" height="1050" viewBox="0 0 750 1050" role="img" aria-labelledby="card-title card-description">',
  f'<title id="card-title">{esc(card["name"])} — {esc(style)}</title>',
  f'<desc id="card-description">{esc(card["type"])}. {esc(card["color"])}. Design example, not balanced game content.</desc>',
  '<defs><linearGradient id="sky" x2="0" y2="1"><stop stop-color="#8ebbb8"/><stop offset="1" stop-color="#173e49"/></linearGradient>'
  '<linearGradient id="shade" x2="0" y2="1"><stop stop-color="#102832" stop-opacity=".94"/><stop offset=".5" stop-color="#102832" stop-opacity=".1"/><stop offset="1" stop-color="#102832" stop-opacity=".92"/></linearGradient>'
  '<clipPath id="trim"><rect width="750" height="1050" rx="36"/></clipPath>'
  f'<clipPath id="art-window"><rect x="30" y="166" width="690" height="{panel_y-186}" rx="17"/></clipPath></defs>',
  '<g font-family="Arial" clip-path="url(#trim)">']
 result += [rect(0,0,750,1050,'#132f3c')]
 if style=='full-art':
  result += ['<g id="artwork" data-slot="artwork">'+art(card,accent)+'</g>',rect(0,0,750,1050,'#102832',extra='opacity=".22"')]
 else:
  result += [rect(16,16,718,1018,'#e5d9bc',26),rect(25,25,700,1000,'#f6f0df',22),
   '<g id="artwork" data-slot="artwork" clip-path="url(#art-window)">',
   f'<g transform="translate(0 105) scale(1 {(panel_y-186)/650:.5f})">'+art(card,accent)+'</g></g>']
 result += [rect(13,13,724,1024,'none',29,'stroke="'+accent+'" stroke-width="10"'),
  rect(25,25,700,125,'#132f3c',20),rect(25,149,700,6,accent),
  '<g id="identity" data-slot="name-color-type">',
  title_svg,
  text(45,119 if len(title_lines)>1 else 112,card['type'].upper(),18,'#cadbd7',700,extra='letter-spacing="1.1"'),
  text(46,143,(card['color'].upper() if card['color']=='Generic' else card['color'].upper()+' · '+identity),15,'#fff1cc',700),'</g>',
  '<g id="access-cost" data-slot="access">',
  rect(605,35,103,103,accent,18,'stroke="#f0d79d" stroke-width="2"'),
  text(656,59,card['access_label'],14,'#fff4d8',700,extra='text-anchor="middle"'),
  text(656,110,card['access'],36 if len(card['access'])<3 else 23,'#ffffff',700,extra='text-anchor="middle"'),'</g>',
  rect(155,panel_y-52,440,29,'#173441',10),
  text(375,panel_y-32,'ILLUSTRATION PLACEHOLDER · REPLACEABLE ART',12,'#eff2de',700,extra='text-anchor="middle" letter-spacing="1.3"'),
  '<g id="rules-panel" data-slot="traits-abilities">',rect(30,panel_y,690,panel_h,'#f7f1df',18,'stroke="'+accent+'" stroke-width="2"')]
 y=panel_y+31
 if card['traits']:
  result += [text(52,y,' · '.join(card['traits']).upper(),17,accent,700,extra='letter-spacing="1.2"')]
  y+=32
 if not lines:
  if card.get('flavor'):
   result += [text(52,y+25,card['flavor'],22,'#52686a',400,extra='font-style="italic"')]
 else:
  for kind,value in lines:
   if kind!='space':
    result += [text(52,y,value,20 if kind in ('cost','timing','access') else 23,
                    accent if kind=='label' else '#19343d',700 if kind in ('label','cost') else 400)]
   y+=line_heights[kind]
 result += ['</g>','<g id="live-status" data-slot="statuses">']
 sy=185
 for status in card.get('statuses',[]):
  width=min(660,len(status)*12+30)
  result += [rect(44,sy,width,34,'#173441',9,'stroke="#efd9a2"'),text(58,sy+24,status,17,'#fff2ce',700)]
  sy+=42
 if card.get('attachments'):
  result += [rect(44,panel_y-83,610,32,'#173441',9),text(58,panel_y-60,'UPGRADE · '+', '.join(card['attachments']),18,'#fff2ce',700)]
 result += ['</g>','<g id="stats" data-slot="creature-stats">']
 if 'attack' in card:
  for x,label,value in [(34,'ATK',card['attack']),(566,'HP',card['health'])]:
   result += [rect(x,944,150,72,'#173441',16,'stroke="#d6b86b" stroke-width="2"'),text(x+20,971,label,15,'#e7d8b8',700),text(x+76,1003,value,34,'#ffffff',700,extra='text-anchor="middle"')]
 result += ['</g>',text(375,978,'THE CRUCIBLE',19,'#fff2ce' if style=='full-art' else '#36535a',700,extra='text-anchor="middle" letter-spacing="2"'),
  text(375,1005,'ILLUSTRATIVE CONTENT · '+card['id'].upper(),11,'#dfdfcb' if style=='full-art' else '#52686a',700,extra='text-anchor="middle" letter-spacing="1"')]
 if card.get('base_note'):
  result += [text(375,1030,card['base_note'],12,'#f2e6c6' if style=='full-art' else '#36535a',400,extra='text-anchor="middle"')]
 result += ['</g></svg>']
 return '\n'.join(result)


def main():
 cards=json.loads((ROOT/'fixtures.json').read_text(encoding='utf-8'))['cards']
 if len({c['id'] for c in cards})!=len(cards):
  raise ValueError('duplicate fixture IDs')
 out=ROOT/'output';out.mkdir(exist_ok=True)
 for card in cards:
  for style in ('standard','full-art'):
   (out/f'{card["id"]}-{style}.svg').write_text(render(card,style),encoding='utf-8')
 for style in ('standard','full-art'):
  (ROOT/f'{style}.svg').write_text(render(cards[0],style),encoding='utf-8')
 options=''.join(f'<option value="{esc(c["id"])}">{esc(c["name"])} ({esc(c["type"])})</option>' for c in cards)
 sections=''.join(f'<section data-card="{esc(c["id"])}"><h2>{esc(c["name"])}</h2><p>{esc(c["art"])}</p><div class="pair">'+''.join(f'<figure><figcaption>{label}</figcaption><a href="output/{esc(c["id"])}-{style}.svg"><img src="output/{esc(c["id"])}-{style}.svg" alt="{esc(c["name"])} · {label}"></a></figure>' for style,label in [('standard','Standard'),('full-art','Full art')])+'</div></section>' for c in cards)
 page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>The Crucible · Card templates</title><style>
 *{box-sizing:border-box}body{margin:0;background:#102631;color:#f4ebd6;font:16px 'Segoe UI',sans-serif}main{max-width:1160px;margin:auto;padding:40px 24px}header{border-bottom:1px solid #547075;padding-bottom:24px}.eyebrow{color:#d4b56f;letter-spacing:3px;font-size:12px}h1{font:42px Georgia,serif;margin:12px 0}p{line-height:1.6;color:#bdcdcb}select,button{font:inherit;padding:10px;border:1px solid #698488;border-radius:6px;background:#183b47;color:#fff}button{margin-left:10px;cursor:pointer}.pair{display:grid;grid-template-columns:1fr 1fr;gap:30px;max-width:950px;margin:auto}figure{margin:0}figcaption{font-size:12px;text-transform:uppercase;letter-spacing:2px;color:#d8be7f;margin:16px 0}img{width:100%;border-radius:24px;box-shadow:0 18px 45px #0006}section h2{margin-top:30px}footer{margin-top:36px;color:#bdcdcb}@media(max-width:650px){.pair{grid-template-columns:1fr}h1{font-size:32px}button{margin:10px 0}}
 </style><main><header><div class="eyebrow">THE CRUCIBLE / DESIGN SYSTEM V1</div><h1>One card. Two treatments.</h1><p>Editable SVG templates. Identical information, separate artwork treatment. Click a card to inspect at full size. Artwork is a replaceable vector placeholder; card examples are not balance-tested.</p><label for="sample">Content example </label><select id="sample">'''+options+'''</select><button id="all">View all examples</button></header>'''+sections+'''<footer>750 × 1050 reference artboards · No network assets · Gameplay text rendered separately from artwork</footer></main><script>
 const select=document.getElementById('sample');function show(){document.querySelectorAll('section').forEach(s=>s.hidden=s.dataset.card!==select.value)}select.addEventListener('change',show);document.getElementById('all').addEventListener('click',()=>document.querySelectorAll('section').forEach(s=>s.hidden=false));show();</script></html>'''
 (ROOT/'preview.html').write_text(page,encoding='utf-8')
 print(f'Rendered {len(cards)} shared fixtures in both styles: {out}')


if __name__=='__main__':
 main()
