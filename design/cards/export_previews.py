"""Optional local PNG review export. SVG/HTML generation needs only Python stdlib."""
from pathlib import Path
from io import BytesIO
import resvg_py
from PIL import Image
root=Path(__file__).resolve().parent
for name in ['pup','leader','combined','pup-live','leader-live']:
    images=[]
    for style in ['standard','full-art']:
        svg=(root/'output'/f'{name}-{style}.svg').read_text(encoding='utf-8')
        data=resvg_py.svg_to_bytes(svg_string=svg)
        images.append(Image.open(BytesIO(data)).convert('RGB').resize((600,840)))
    sheet=Image.new('RGB',(1230,860),'#102631')
    for i,image in enumerate(images):
        sheet.paste(image,(i*610+10,10))
    sheet.save(root/f'preview-{name}.png')
print('Exported five local PNG review pairs')
