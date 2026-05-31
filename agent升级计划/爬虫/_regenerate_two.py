"""临时脚本：重新生成角度图和套装图"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / '生图'))
from image_gen import generate
import json

out_dir = Path(r'..\产品卖点主图和信息生成\Chevy-Silverado_1999-2014_Door-Handle').resolve()
ref_img = out_dir / 'ref_ebay_4handles.webp'

angle_prompt = (
    'Professional product photography of exactly four individual chrome exterior door handles '
    'arranged in a single horizontal row on a pure white seamless background. '
    'Only four handles total — count them: handle 1 front left, handle 2 front right, '
    'handle 3 rear left, handle 4 rear right. Each handle shown from a side profile angle '
    'revealing both the front face and the back mounting side with clip attachment points. '
    'NO other objects, NO extra items. Studio lighting, natural soft shadows. '
    'NO logos, NO brand names, NO text, NO watermarks.'
)

print('Regenerating angle (多视角图)...')
angle_path = generate(prompt=angle_prompt, model='fast', size='1:1', output_dir=str(out_dir))
print(f'Angle saved: {angle_path}')

kit_prompt = (
    'Professional product photography, exactly 4 individual exterior door handles '
    '(front left, front right, rear left, rear right) arranged in a 2x2 grid layout '
    'on a dark gray textured surface. All 4 handles must be fully visible, each positioned '
    'to show its unique orientation. Above the handles, the mounting hardware and clips '
    'are visible. Studio top-down lighting with soft shadows. Clean commercial catalog style. '
    'NO logos, NO brand names, NO text, NO watermarks.'
)

print('Regenerating kit (套装展示图)...')
kit_path = generate(prompt=kit_prompt, model='fast', size='1:1',
                    reference_image=str(ref_img), strength=0.5, output_dir=str(out_dir))
print(f'Kit saved: {kit_path}')

# update image_batch.json
batch_file = out_dir / 'image_batch.json'
batch = json.loads(batch_file.read_text(encoding='utf-8'))
batch['angle']['path'] = Path(angle_path).name
batch['angle']['regenerated'] = True
batch['kit']['path'] = Path(kit_path).name
batch['kit']['regenerated'] = True
batch_file.write_text(json.dumps(batch, ensure_ascii=False, indent=2), encoding='utf-8')
print('Updated image_batch.json')
print('Done!')
