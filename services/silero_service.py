import torch
import torchaudio
import os
from pathlib import Path

# Импортируем конфиг из корня
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Доступные голоса Silero
AVAILABLE_VOICES = {
    "aidar": "Спокойный мужской",
    "baya": "Тёплый женский",
    "kseniya": "Энергичный женский",
    "xenia": "Мягкий интеллигентный женский",
    "eugene": "Серьёзный мужской"
}

# Глобальная модель (загружается один раз)
_model = None

def get_model():
    """Загружает модель (один раз)"""
    global _model
    
    if _model is None:
        print(" Загрузка модели Silero...")
        _model, _ = torch.hub.load(
            repo_or_dir='snakers4/silero-models',
            model='silero_tts',
            language='ru',
            speaker='v5_ru'
        )
        print("✅ Модель загружена")
    
    return _model


def extract_voice_text(script: str) -> str:
    """Извлекает текст для озвучки из сценария"""
    voice_text = ""
    in_voice_section = False
    
    for line in script.split("\n"):
        if "=== ТЕКСТ ДЛЯ ОЗВУЧКИ ===" in line:
            in_voice_section = True
            continue
        elif "=== ХЭШТЕГИ ===" in line or "=== НАЗВАНИЕ ===" in line:
            in_voice_section = False
            continue
        elif in_voice_section and line.strip():
            voice_text += line + "\n"
    
    result = voice_text.strip()
    if result:
        print(f"🔍 Извлечено текста: {len(result)} символов")
    return result


def generate_voice(
    text: str, 
    output_path: str, 
    speaker: str = "xenia",
    sample_rate: int = 48000
) -> str:
    """
    Генерирует аудио через Silero.
    
    Args:
        text: текст для озвучки
        output_path: путь для сохранения
        speaker: имя голоса
        sample_rate: качество (8000/24000/48000)
    
    Returns:
        Путь к файлу
    """
    
    print(f"🎙️ Silero TTS: голос '{speaker}', качество: {sample_rate}Hz")
    print(f"📝 Текст: {len(text)} символов (~{len(text.split())} слов)")
    
    # Загружаем модель
    model = get_model()
    
    # Генерация аудио
    audio = model.apply_tts(
        text=text,
        speaker=speaker,
        sample_rate=sample_rate
    )
    
    # Сохранение
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    torchaudio.save(output_path, audio.unsqueeze(0), sample_rate)
    
    print(f"✅ Аудио сохранено: {output_path}")
    return output_path


def generate_voice_from_script(
    script_path: str, 
    output_path: str = None,
    speaker: str = None,
    sample_rate: int = None
) -> str:
    """Генерирует аудио из файла сценария"""
    
    print(f"\n📂 Чтение сценария: {script_path}")
    
    # Читаем сценарий
    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()
    
    # Извлекаем текст
    voice_text = extract_voice_text(script)
    
    if not voice_text:
        raise Exception("Не найден текст для озвучки!")
    
    # Настройки по умолчанию
    if speaker is None:
        speaker = config.SILERO_SPEAKER
    if sample_rate is None:
        sample_rate = config.SILERO_SAMPLE_RATE
    
    # Путь по умолчанию
    if not output_path:
        script_name = Path(script_path).stem
        output_path = os.path.join(
            config.PATHS["audio"], 
            f"{script_name}_voice.wav"  # WAV формат для Silero
        )
    
    return generate_voice(voice_text, output_path, speaker, sample_rate)


def test_voices(text: str = "Привет! Это тест голосов Silero для канала Загадки истории."):
    """Тестирует все голоса"""
    
    print("🎙️ Тестирование голосов Silero...")
    
    for speaker in AVAILABLE_VOICES.keys():
        output_path = os.path.join(
            config.PATHS["audio"], 
            f"test_silero_{speaker}.wav"
        )
        generate_voice(text, output_path, speaker=speaker)
    
    print(f"\n✅ Тест завершён!")
    print(f"📁 Файлы в: {config.PATHS['audio']}")