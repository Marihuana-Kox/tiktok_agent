from moviepy import ImageClip, VideoClip
from moviepy.video import fx as vfx
import random
import numpy as np


def apply_ken_burns_effect(clip, zoom_speed=0.1, pan_speed=0.05, direction="zoom_in"):
    """
    Применяет эффект Кена Бёрнса (медленный зум/панорама).
    
    Args:
        clip: Видео клип
        zoom_speed: Скорость зума (0.0-0.2)
        pan_speed: Скорость панорамы (0.0-0.1)
        direction: "zoom_in", "zoom_out", "pan_left", "pan_right", "none"
    
    Returns:
        Клип с применённым эффектом
    """
    
    if direction == "none":
        return clip
    
    duration = clip.duration
    
    def make_frame(t):
        frame = clip.get_frame(t)
        h, w = frame.shape[:2]
        
        # Рассчитываем прогресс (0.0 - 1.0)
        progress = t / duration
        
        # Зум
        if direction in ["zoom_in", "zoom_out"]:
            scale_factor = 1.0 + (zoom_speed * progress * duration)
            if direction == "zoom_out":
                scale_factor = 1.0 / scale_factor
            
            new_h, new_w = int(h * scale_factor), int(w * scale_factor)
            
            # Центрируем
            start_y = (new_h - h) // 2
            start_x = (new_w - w) // 2
            
            # Кроп
            if direction == "zoom_in":
                # Увеличиваем - кропим центр
                crop_h = int(h / scale_factor)
                crop_w = int(w / scale_factor)
                start_y = (h - crop_h) // 2
                start_x = (w - crop_w) // 2
                frame = frame[start_y:start_y+crop_h, start_x:start_x+crop_w]
                frame = np.array(ImageClip(frame, duration=duration).resize((h, w)).get_frame(t))
            else:
                # Уменьшаем - добавляем чёрные поля (не делаем для простоты)
                pass
    
    # Для MoviePy 2.x используем with_effects
    if direction == "zoom_in":
        return clip.with_effects([vfx.MultiplySpeed(1.0)])  # Заглушка, реальный зум ниже
    
    # Простая реализация через resize
    if direction == "zoom_in":
        return clip.resize(lambda t: 1 + zoom_speed * t)
    elif direction == "zoom_out":
        return clip.resize(lambda t: 1.2 - zoom_speed * t)
    
    return clip


def apply_random_rotation(clip, max_angle=2, probability=0.3):
    """
    Применяет случайное микро-вращение для динамики.
    
    Args:
        clip: Видео клип
        max_angle: Максимальный угол в градусах
        probability: Вероятность применения (0.0-1.0)
    
    Returns:
        Клип с применённым эффектом
    """
    
    if random.random() > probability:
        return clip
    
    angle = random.uniform(-max_angle, max_angle)
    return clip.with_effects([vfx.Rotate(angle)])


def apply_color_grading(clip, contrast=1.1, saturation=1.2):
    """
    Применяет цветокоррекцию.
    
    Args:
        clip: Видео клип
        contrast: Контраст (1.0 = без изменений)
        saturation: Насыщенность (1.0 = без изменений)
    
    Returns:
        Клип с применённым эффектом
    """
    
    clip = clip.with_effects([vfx.Colorx(contrast)])
    clip = clip.with_effects([vfx.MultiplyColor(saturation)])
    return clip


def get_random_effect_sequence():
    """
    Генерирует случайную последовательность эффектов для клипа.
    
    Returns:
        Словарь с параметрами эффектов
    """
    
    directions = ["zoom_in", "zoom_out", "pan_left", "pan_right", "none"]
    
    return {
        "ken_burns_direction": random.choice(directions),
        "ken_burns_zoom": random.uniform(0.05, 0.15),
        "rotation_angle": random.uniform(-2, 2) if random.random() > 0.7 else 0,
        "transition_type": random.choice(["fade", "crossfade"])
    }