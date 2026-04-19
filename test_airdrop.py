print("="*60)
print("AIRDROP TEST - Quick iOS Video")
print("="*60)

from moviepy import ImageClip, AudioFileClip
from moviepy.video import fx as vfx
from PIL import Image
import numpy as np
import subprocess
import os
import time

start_time = time.time()

# === 1. БЕРЁМ ЛЮБУЮ КАРТИНКУ ИЗ ПРОЕКТА ===
print("\n[1/5] Finding test image...")
test_img = None
for folder in os.listdir('output'):
    if folder.startswith('topic_'):
        folder_path = os.path.join('output', folder)
        for file in os.listdir(folder_path):
            if file.startswith('image_') and file.endswith('.jpg'):
                test_img = os.path.join(folder_path, file)
                break
        if test_img:
            break

if not test_img:
    print("   Creating test pattern...")
    img = Image.new('RGB', (1024, 1024), color='white')
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    for i in range(0, 512, 40):
        color = (i % 256, (i*2) % 256, (i*3) % 256)
        draw.ellipse([512-i, 512-i, 512+i, 512+i], outline=color, width=3)
    draw.ellipse([502, 502, 522, 522], fill='red')
    test_img = 'output/test_pattern.jpg'
    img.save(test_img)

print(f"   OK: {test_img}")

# === 2. СОЗДАЁМ КОРОТКИЙ КЛИП (3 секунды) ===
print("\n[2/5] Creating 3-second clip...")

img = Image.open(test_img)
if img.width != img.height:
    min_side = min(img.width, img.height)
    left = (img.width - min_side) // 2
    top = (img.height - min_side) // 2
    img = img.crop((left, top, left + min_side, top + min_side))
img = img.resize((1080, 1920), Image.Resampling.LANCZOS)

clip = ImageClip(np.array(img), duration=3)
clip = clip.with_effects([vfx.FadeIn(0.3), vfx.FadeOut(0.3)])

output_path = 'output/test_airdrop.mp4'

# БЕЗ verbose и logger (MoviePy 2.x)
clip.write_videofile(
    output_path,
    fps=24,
    codec='libx264',
    audio_codec='aac',
    temp_audiofile='temp-audio.m4a',
    remove_temp=True
)
print(f"   OK: {output_path}")

# === 3. iOS КОНВЕРТАЦИЯ ===
print("\n[3/5] Converting for iOS...")

ios_path = 'output/test_airdrop_ios.mov'

cmd = [
    'ffmpeg', '-y',
    '-i', output_path,
    '-c:v', 'libx264',
    '-profile:v', 'baseline',
    '-level', '3.0',
    '-pix_fmt', 'yuv420p',
    '-colorspace', 'bt709',
    '-color_primaries', 'bt709',
    '-color_trc', 'bt709',
    '-c:a', 'aac',
    '-b:a', '128k',
    '-ar', '44100',
    '-ac', '2',
    '-movflags', '+faststart',
    '-movflags', '+write_colr',
    '-brand', 'mp41',
    '-preset', 'medium',
    '-b:v', '3000k',
    '-g', '24',
    ios_path
]

result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode == 0:
    print(f"   OK: Conversion successful")
else:
    print(f"   Warning: {result.stderr[:100]}")

# === 4. ПРОВЕРКА ===
print("\n[4/5] Verifying...")

probe_v = subprocess.run([
    'ffprobe', '-v', 'error',
    '-select_streams', 'v:0',
    '-show_entries', 'stream=codec_name,profile,level,width,height',
    '-of', 'default=noprint_wrappers=1',
    ios_path
], capture_output=True, text=True)

probe_a = subprocess.run([
    'ffprobe', '-v', 'error',
    '-select_streams', 'a:0',
    '-show_entries', 'stream=codec_name,sample_rate,channels',
    '-of', 'default=noprint_wrappers=1',
    ios_path
], capture_output=True, text=True)

print("   Video:")
for line in probe_v.stdout.strip().split('\n'):
    if line:
        print(f"      {line}")

print("   Audio:")
for line in probe_a.stdout.strip().split('\n'):
    if line:
        print(f"      {line}")

# === 5. ГОТОВО ===
print("\n[5/5] Done!")

elapsed = time.time() - start_time
print(f"\nTotal time: {elapsed:.1f} seconds")
print(f"\nFiles:")
print(f"   - {output_path} ({os.path.getsize(output_path)/(1024*1024):.1f} MB)")
print(f"   - {ios_path} ({os.path.getsize(ios_path)/(1024*1024):.1f} MB)")

print("\nTO TEST AIRDROP:")
print(f"   1. Run: open {ios_path}")
print(f"   2. In QuickTime: Share -> AirDrop -> iPhone")
print(f"   3. Or drag file to AirDrop window")
