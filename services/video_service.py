from moviepy import ImageSequenceClip, AudioFileClip, concatenate_videoclips
from moviepy.video import fx as vfx
from PIL import Image
import numpy as np
import os
import json
import random
import tempfile
import shutil
import subprocess

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

VIDEO_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
    "config_video.json"
)

DEFAULT_FPS = 24


def load_video_config() -> dict:
    if os.path.exists(VIDEO_CONFIG_PATH):
        with open(VIDEO_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "video_settings": {"fps": DEFAULT_FPS, "transition_duration": 0.5},
        "effects": {"ken_burns": {"enabled": True}}
    }


def calculate_image_timings(audio_path: str, num_images: int, config: dict) -> list:
    with AudioFileClip(audio_path) as audio:
        total_duration = audio.duration
    
    transition_duration = config.get("video_settings", {}).get("transition_duration", 0.5)
    total_transition_time = transition_duration * (num_images - 1)
    available_time = total_duration - total_transition_time
    base_duration = available_time / num_images
    
    return [base_duration] * num_images


def generate_effect_frames(img_path: str, effect_type: str, duration: float, fps: int = 24, output_folder: str = None):
    img = Image.open(img_path)
    
    if img.width != img.height:
        min_side = min(img.width, img.height)
        left = (img.width - min_side) // 2
        top = (img.height - min_side) // 2
        img = img.crop((left, top, left + min_side, top + min_side))
    
    img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
    
    total_frames = int(fps * duration)
    
    if output_folder is None:
        output_folder = tempfile.mkdtemp(prefix='clip_frames_')
    else:
        os.makedirs(output_folder, exist_ok=True)
    
    BASE_SCALE = 1920 / 1024
    TARGET_W, TARGET_H = 1080, 1920
    
    frame_paths = []
    
    for i in range(total_frames):
        progress = i / (total_frames - 1) if total_frames > 1 else 0
        
        if effect_type == "zoom_in":
            scale = BASE_SCALE + (BASE_SCALE * 0.5 * progress)
        elif effect_type == "zoom_out":
            scale = (BASE_SCALE * 1.5) - (BASE_SCALE * 0.5 * progress)
            scale = max(scale, BASE_SCALE)
        else:
            scale = BASE_SCALE * 1.3
        
        if effect_type == "pan_left":
            pan_x, pan_y = -200 * progress, 0
        elif effect_type == "pan_right":
            pan_x, pan_y = 200 * progress, 0
        elif effect_type == "pan_up":
            pan_x, pan_y = 0, -200 * progress
        elif effect_type == "pan_down":
            pan_x, pan_y = 0, 200 * progress
        else:
            pan_x, pan_y = 0, 0
        
        new_w = int(1024 * scale)
        new_h = int(1024 * scale)
        scaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        left = (new_w - TARGET_W) // 2 + int(pan_x)
        top = (new_h - TARGET_H) // 2 + int(pan_y)
        left = max(0, min(left, new_w - TARGET_W))
        top = max(0, min(top, new_h - TARGET_H))
        
        cropped = scaled.crop((left, top, left + TARGET_W, top + TARGET_H))
        
        frame_path = os.path.join(output_folder, f'frame_{i:04d}.jpg')
        cropped.save(frame_path, quality=85)
        frame_paths.append(frame_path)
        
        if i % 50 == 0:
            import gc
            gc.collect()
    
    return frame_paths, output_folder


def apply_effects_to_clip(img_path: str, duration: float, effects_config: dict, 
                          transition_duration: float = 0.5, seed: int = None, fps: int = 24):
    if seed is not None:
        random.seed(seed)
    
    ken_burns = effects_config.get("ken_burns", {})
    ken_burns_enabled = ken_burns.get("enabled", True)
    
    if ken_burns_enabled:
        effect_types = ["zoom_in", "zoom_out", "pan_left", "pan_right", "pan_up", "pan_down"]
        effect_type = random.choice(effect_types)
        print(f"      -> Effect: {effect_type}")
    else:
        effect_type = "static"
        print(f"      -> Effect: static")
    
    temp_folder = tempfile.mkdtemp(prefix=f'clip_{seed}_')
    
    if effect_type == "static":
        img = Image.open(img_path)
        if img.width != img.height:
            min_side = min(img.width, img.height)
            left = (img.width - min_side) // 2
            top = (img.height - min_side) // 2
            img = img.crop((left, top, left + min_side, top + min_side))
        img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
        
        from moviepy import ImageClip
        clip = ImageClip(np.array(img), duration=duration)
        shutil.rmtree(temp_folder, ignore_errors=True)
    else:
        frame_paths, temp_folder = generate_effect_frames(img_path, effect_type, duration=duration, fps=fps, output_folder=temp_folder)
        print(f"      OK: {len(frame_paths)} frames on disk")
        
        clip = ImageSequenceClip(frame_paths, fps=fps)
        clip._temp_folder = temp_folder
    
    if transition_duration > 0:
        clip = clip.with_effects([
            vfx.FadeIn(transition_duration),
            vfx.FadeOut(transition_duration)
        ])
        print(f"      -> Fade: {transition_duration}s")
    
    return clip


def convert_to_ios_compatible(input_path: str):
    """
    Перекодирует видео в 100% iOS-совместимый формат через FFmpeg.
    """
    output_path = input_path.replace('.mp4', '_ios.mov')
    
    print(f"\n📱 Converting to iOS compatible format...")
    print(f"   Input: {input_path}")
    print(f"   Output: {output_path}")
    
    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
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
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        orig_size = os.path.getsize(input_path) / (1024*1024)
        new_size = os.path.getsize(output_path) / (1024*1024)
        print(f"   ✅ Success! {orig_size:.1f}MB → {new_size:.1f}MB")
        
        # Проверка видео
        probe_v = subprocess.run([
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_name,profile,level,width,height',
            '-of', 'default=noprint_wrappers=1',
            output_path
        ], capture_output=True, text=True)
        
        # Проверка аудио
        probe_a = subprocess.run([
            'ffprobe', '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'stream=codec_name,sample_rate,channels',
            '-of', 'default=noprint_wrappers=1',
            output_path
        ], capture_output=True, text=True)
        
        print(f"   📹 Video:")
        for line in probe_v.stdout.strip().split('\n'):
            if line:
                print(f"      {line}")
        
        print(f"   🎵 Audio:")
        for line in probe_a.stdout.strip().split('\n'):
            if line:
                print(f"      {line}")
        
        # Заменяем оригинал
        os.remove(input_path)
        os.rename(output_path, input_path)
        print(f"   ✅ File: {input_path}")
        
        return input_path
    else:
        print(f"   ⚠️  Warning: {result.stderr[:200]}")
        return input_path


def create_video_from_images(images: list, audio_path: str, output_path: str, config: dict = None) -> str:
    if config is None:
        config = load_video_config()
    
    print(f"\n{'='*60}")
    print(f"VIDEO MONTAGE (Memory Optimized + iOS Compatible)")
    print(f"{'='*60}")
    print(f"Images: {len(images)}")
    
    effects_config = config.get("effects", {})
    transition_duration = config.get("video_settings", {}).get("transition_duration", 0.5)
    fps = config.get("video_settings", {}).get("fps", DEFAULT_FPS)
    
    for img_path in images:
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"Image not found: {img_path}")
    
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio not found: {audio_path}")
    
    timings = calculate_image_timings(audio_path, len(images), config)
    
    clips = []
    temp_folders = []
    
    for i, (img_path, duration) in enumerate(zip(images, timings)):
        print(f"\n   [{i+1}/{len(images)}] {os.path.basename(img_path)}")
        print(f"      Duration: {duration:.1f}s")
        
        try:
            clip = apply_effects_to_clip(
                img_path=img_path,
                duration=duration,
                effects_config=effects_config,
                transition_duration=transition_duration,
                seed=i,
                fps=fps
            )
            
            if hasattr(clip, '_temp_folder'):
                temp_folders.append(clip._temp_folder)
            
            print(f"      OK: Clip {clip.size}, {clip.duration}s")
            clips.append(clip)
            
            import gc
            gc.collect()
            
        except Exception as e:
            print(f"   WARN: {e}")
            import traceback
            traceback.print_exc()
            from moviepy import ImageClip
            img = Image.open(img_path).resize((1080, 1920))
            clip = ImageClip(np.array(img), duration=duration)
            clip = clip.with_effects([vfx.FadeIn(transition_duration), vfx.FadeOut(transition_duration)])
            clips.append(clip)
    
    print("\n   Concatenating...")
    final_video = concatenate_videoclips(clips, method="compose")
    print(f"   OK: {final_video.size[0]}x{final_video.size[1]}, {final_video.duration:.1f}s")
    
    print("   Adding audio...")
    audio = AudioFileClip(audio_path)
    final_video = final_video.with_audio(audio)
    print(f"   OK: Audio {audio.duration:.1f}s")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Рендер (БЕЗ verbose и logger!)
    print(f"\n   Rendering: {output_path}")
    print("   Format: H.264 + AAC")
    print("   This may take 2-5 minutes...")
    
    final_video.write_videofile(
        output_path,
        fps=fps,
        codec='libx264',
        audio_codec='aac',
        bitrate='5000k',
        audio_bitrate='192k',
        preset='medium',
        threads=4,
        temp_audiofile='temp-audio.m4a',
        remove_temp=True
    )
    
    final_video.close()
    audio.close()
    
    print("\n   Cleaning up temp files...")
    for folder in temp_folders:
        shutil.rmtree(folder, ignore_errors=True)
    print(f"   OK: Removed {len(temp_folders)} temp folders")
    
    print(f"\n   DONE: {output_path}")
    print(f"   Size: {os.path.getsize(output_path) / (1024*1024):.1f} MB")
    
    # iOS конвертация
    output_path = convert_to_ios_compatible(output_path)
    
    print(f"\n   🎉 Video ready for AirDrop!")
    
    return output_path


def get_images_from_project(project_path: str) -> list:
    images = []
    for filename in os.listdir(project_path):
        if filename.endswith(('.jpg', '.jpeg', '.png')) and filename.startswith('image_'):
            images.append(os.path.join(project_path, filename))
    
    def extract_number(filepath):
        filename = os.path.basename(filepath)
        parts = filename.split('_')
        if len(parts) > 1 and parts[1].isdigit():
            return int(parts[1])
        return 999
    
    images.sort(key=extract_number)
    return images


def generate_video_for_topic(project_path: str, output_filename: str = "video.mp4") -> str:
    print(f"\n{'='*60}")
    print(f"GENERATING VIDEO FOR: {os.path.basename(project_path)}")
    print(f"{'='*60}")
    
    config = load_video_config()
    images = get_images_from_project(project_path)
    
    if len(images) < 3:
        raise Exception(f"Not enough images: {len(images)}")
    
    audio_path = os.path.join(project_path, "voice.mp3")
    if not os.path.exists(audio_path):
        raise Exception(f"Audio not found")
    
    output_path = os.path.join(project_path, output_filename)
    
    return create_video_from_images(
        images=images,
        audio_path=audio_path,
        output_path=output_path,
        config=config
    )