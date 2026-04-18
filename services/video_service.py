from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
from moviepy.video import fx as vfx
import os
import json
import random
from pathlib import Path

# Импортируем конфиг из корня
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Загружаем конфиг видео
VIDEO_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
    "config_video.json"
)

def load_video_config() -> dict:
    """Загружает настройки видео из конфига"""
    if os.path.exists(VIDEO_CONFIG_PATH):
        with open(VIDEO_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "video_settings": {"fps": 30, "transition_duration": 0.5},
        "effects": {"ken_burns": {"enabled": True, "zoom_speed": 0.1}},
        "timing": {"first_image_multiplier": 1.2, "last_image_multiplier": 1.2}
    }


def calculate_image_timings(audio_path: str, num_images: int, config: dict) -> list:
    """Рассчитывает длительность показа каждой картинки с вариациями"""
    
    with AudioFileClip(audio_path) as audio:
        total_duration = audio.duration
    
    transition_duration = config.get("video_settings", {}).get("transition_duration", 0.5)
    timing_config = config.get("timing", {})
    
    total_transition_time = transition_duration * (num_images - 1)
    available_time = total_duration - total_transition_time
    
    # Базовое время
    base_duration = available_time / num_images
    
    # Создаём тайминги с вариациями
    timings = []
    for i in range(num_images):
        if i == 0:
            multiplier = timing_config.get("first_image_multiplier", 1.2)
        elif i == num_images - 1:
            multiplier = timing_config.get("last_image_multiplier", 1.2)
        else:
            multiplier = timing_config.get("middle_images_multiplier", 0.9)
        
        duration = base_duration * multiplier
        
        # Ограничиваем мин/макс
        min_dur = timing_config.get("min_image_duration", 3.0)
        max_dur = timing_config.get("max_image_duration", 15.0)
        duration = max(min_dur, min(max_dur, duration))
        
        timings.append(duration)
    
    # Корректируем чтобы совпадало с аудио
    total = sum(timings) + total_transition_time
    if total != total_duration:
        diff = (total_duration - total) / num_images
        timings = [t + diff for t in timings]
    
    print(f"🎬 Расчёт тайминга:")
    print(f"   Длительность аудио: {total_duration:.1f} сек")
    print(f"   Количество картинок: {num_images}")
    for i, t in enumerate(timings):
        print(f"   [{i+1}] {t:.1f} сек")
    print(f"   Переходы: {transition_duration} сек")
    
    return timings


def apply_effects_to_clip(clip, effects_config: dict, transition_duration: float = 0.5, seed: int = None, ):
    """
    Применяет эффекты к клипу.
    
    Args:
        clip: ImageClip
        effects_config: Настройки эффектов из конфига
        seed: Seed для случайности (чтобы одинаковые картинки = одинаковые эффекты)
    
    Returns:
        Клип с эффектами
    """
    
    if seed is not None:
        random.seed(seed)
    
    ken_burns = effects_config.get("ken_burns", {})
    rotation = effects_config.get("rotation", {})
    
    # === КЕН БЁРНС (ЗУМ) — безопасная версия ===
    if ken_burns.get("enabled", True):
        directions = ken_burns.get("directions", ["zoom_in", "zoom_out", "none"])
        direction = random.choice(directions)
        
        if direction == "zoom_in":
            # Плавное увеличение от 1.0 до 1.1 (максимум 10%)
            start_scale = 1.0
            end_scale = 1.5
            clip = clip.with_effects([
                vfx.Resize(lambda t: start_scale + (end_scale - start_scale) * (t / clip.duration))
            ])
        elif direction == "zoom_out":
            # Плавное уменьшение от 1.1 до 1.0
            start_scale = 1.5
            end_scale = 1.0
            clip = clip.with_effects([
                vfx.Resize(lambda t: start_scale - (start_scale - end_scale) * (t / clip.duration))
            ])
        # else "none" — без зума
    
    # === МИКРО-ВРАЩЕНИЕ ===
    if rotation.get("enabled", True):
        if random.random() < rotation.get("probability", 0.3):
            max_angle = rotation.get("max_angle", 2)
            angle = random.uniform(-max_angle, max_angle)
            clip = clip.with_effects([vfx.Rotate(angle)])
    
    # === FADE ПЕРЕХОДЫ ===
    if transition_duration > 0:
        clip = clip.with_effects([
            vfx.FadeIn(transition_duration),
            vfx.FadeOut(transition_duration)
        ])
    
    return clip


def create_video_from_images(
    images: list,
    audio_path: str,
    output_path: str,
    config: dict = None
) -> str:
    """Создаёт видео из картинок с эффектами"""
    
    if config is None:
        config = load_video_config()
    
    print(f"\n{'='*60}")
    print(f"🎬 МОНТАЖ ВИДЕО")
    print(f"{'='*60}")
    print(f"📁 Картинки: {len(images)} шт")
    print(f"🎵 Аудио: {os.path.basename(audio_path)}")
    print(f"📐 Формат: 9:16 (1080x1920)")
    
    # Получаем настройки
    video_settings = config.get("video_settings", {})
    effects_config = config.get("effects", {})
    transition_duration = video_settings.get("transition_duration", 0.5)
    fps = video_settings.get("fps", 30)
    
    print(f"🎞️  FPS: {fps}")
    print(f"🎭 Переходы: {transition_duration} сек")
    
    # Проверяем файлы
    for img_path in images:
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"Картинка не найдена: {img_path}")
    
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Аудио не найдено: {audio_path}")
    
    # Рассчитываем тайминг
    timings = calculate_image_timings(audio_path, len(images), config)
    
    # Создаём клипы с эффектами
    clips = []
    
    for i, (img_path, duration) in enumerate(zip(images, timings)):
        print(f"   [{i+1}/{len(images)}] {os.path.basename(img_path)} → {duration:.1f} сек")
        
        # Создаём клип
        clip = ImageClip(img_path, duration=duration)
        
        # Применяем эффекты (передаём transition_duration явно!)
        clip = apply_effects_to_clip(
            clip=clip,
            effects_config=effects_config,
            transition_duration=transition_duration,
            seed=i
        )
        
        clips.append(clip)
    
    # Соединяем клипы
    print("\n🔗 Соединение клипов...")
    final_video = concatenate_videoclips(clips, method="compose")
    
    # Накладываем аудио
    print("🎵 Наложение аудио...")
    audio = AudioFileClip(audio_path)
    final_video = final_video.with_audio(audio)
    
    # Создаём папку если нет
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Рендерим видео
    print(f"💾 Рендер видео: {output_path}")
    print("⏳ Это может занять 2-5 минут...")
    
    final_video.write_videofile(
        output_path,
        fps=fps,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True
    )
    
    # Освобождаем память
    final_video.close()
    audio.close()
    
    print(f"\n✅ Видео сохранено: {output_path}")
    
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"📊 Размер файла: {file_size:.1f} MB")
    
    return output_path


def get_images_from_project(project_path: str) -> list:
    """Получает список картинок из папки проекта в правильном порядке"""
    
    images = []
    
    for filename in os.listdir(project_path):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            if filename.startswith('image_'):
                images.append(os.path.join(project_path, filename))
    
    def extract_number(filepath):
        filename = os.path.basename(filepath)
        parts = filename.split('_')
        if len(parts) > 1 and parts[1].isdigit():
            return int(parts[1])
        return 999
    
    images.sort(key=extract_number)
    
    print(f"📂 Найдено {len(images)} картинок в проекте")
    for i, img in enumerate(images, 1):
        print(f"   [{i}] {os.path.basename(img)}")
    
    return images


def generate_video_for_topic(
    project_path: str,
    output_filename: str = "video.mp4"
) -> str:
    """Генерирует видео для темы автоматически"""
    
    print(f"\n{'='*60}")
    print(f"🎬 ГЕНЕРАЦИЯ ВИДЕО ДЛЯ: {os.path.basename(project_path)}")
    print(f"{'='*60}")
    
    config = load_video_config()
    
    # Загружаем активный пресет
    preset_name = config.get("active_preset", "dynamic")
    presets = config.get("style_presets", {})
    
    if preset_name in presets:
        preset = presets[preset_name]
        print(f"🎭 Пресет: {preset_name} — {preset.get('description', '')}")
        
        # Применяем пресет к настройкам
        if "ken_burns" in preset:
            config["effects"]["ken_burns"]["enabled"] = preset["ken_burns"]
        if "rotation" in preset:
            config["effects"]["rotation"]["enabled"] = preset["rotation"]
        if "transition" in preset:
            config["video_settings"]["transition_duration"] = preset["transition"]
    
    images = get_images_from_project(project_path)
    
    if len(images) < 3:
        raise Exception(f"Недостаточно картинок для видео (найдено: {len(images)}, нужно: минимум 3)")
    
    audio_path = os.path.join(project_path, "voice.mp3")
    
    if not os.path.exists(audio_path):
        raise Exception(f"Аудио не найдено: {audio_path}")
    
    output_path = os.path.join(project_path, output_filename)
    
    return create_video_from_images(
        images=images,
        audio_path=audio_path,
        output_path=output_path,
        config=config
    )