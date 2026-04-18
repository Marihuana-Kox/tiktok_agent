from openai import OpenAI
import os
from pathlib import Path

# Импортируем конфиг из корня
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

# Доступные голоса OpenAI TTS
AVAILABLE_VOICES = [
    "alloy",    # Нейтральный, мужской
    "echo",     # Глубокий, мужской
    "fable",    # Британский акцент
    "onyx",     # Серьёзный, мужской
    "nova",     # Энергичный, женский
    "shimmer"   # Мягкий, женский
]

def extract_voice_text(script: str) -> str:
    """Извлекает текст для озвучки из сценария"""
    
    voice_text = ""
    in_voice_section = False
    
    for line in script.split("\n"):
        # Ищем начало секции озвучки
        if "=== ТЕКСТ ДЛЯ ОЗВУЧКИ ===" in line:
            in_voice_section = True
            continue
        # Ищем конец секции (хэштеги или другая секция)
        elif "=== ХЭШТЕГИ ===" in line or "=== НАЗВАНИЕ ===" in line:
            in_voice_section = False
            continue
        # Если мы в секции озвучки и линия не пустая — добавляем
        elif in_voice_section and line.strip():
            voice_text += line + "\n"
    
    result = voice_text.strip()
    
    # Отладка: показываем сколько извлекли
    if result:
        print(f"🔍 Извлечено текста для озвучки: {len(result)} символов")
    else:
        print("⚠️ WARNING: Текст для озвучки не найден!")
        print("Проверь что в сценарии есть секция: === ТЕКСТ ДЛЯ ОЗВУЧКИ ===")
    
    return result


def generate_voice(
    text: str, 
    output_path: str, 
    voice: str = "onyx",
    speed: float = 1.0,
    model: str = "tts-1"
) -> str:
    """
    Генерирует аудио из текста.
    
    Args:
        text: текст для озвучки
        output_path: путь для сохранения файла
        voice: имя голоса (alloy, echo, fable, onyx, nova, shimmer)
        speed: скорость (0.25 - 4.0)
        model: модель (tts-1 быстрее, tts-1-hd качественнее)
    
    Returns:
        Путь к сохранённому файлу
    """
    
    print(f"🎙️ Генерация голоса: {voice}, скорость: {speed}x, модель: {model}")
    print(f"📝 Размер текста: {len(text)} символов (~{len(text.split())} слов)")
    
    # Создаём папку если нет
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
        speed=speed
    )
    
    response.stream_to_file(output_path)
    
    print(f"✅ Аудио сохранено: {output_path}")
    return output_path


def generate_voice_from_script(
    script_path: str, 
    output_path: str = None,
    voice: str = None,
    speed: float = None
) -> str:
    """
    Генерирует аудио из файла сценария.
    Извлекает ТОЛЬКО текст из секции === ТЕКСТ ДЛЯ ОЗВУЧКИ ===
    
    Args:
        script_path: путь к файлу сценария
        output_path: путь для сохранения (опционально)
        voice: имя голоса (если None — берётся из config)
        speed: скорость (если None — берётся из config)
    
    Returns:
        Путь к сохранённому файлу
    """
    
    print(f"\n📂 Чтение сценария: {script_path}")
    
    # Читаем сценарий
    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()
    
    # === ИЗВЛЕКАЕМ ТОЛЬКО ТЕКСТ ДЛЯ ОЗВУЧКИ ===
    voice_text = extract_voice_text(script)
    
    if not voice_text:
        # Если не нашли секцию — показываем что есть в файле
        print("\n⚠️ Содержимое файла:")
        print("-" * 50)
        print(script[:500])  # Первые 500 символов для отладки
        print("-" * 50)
        raise Exception("Не найден текст для озвучки в сценарии! Проверь секцию === ТЕКСТ ДЛЯ ОЗВУЧКИ ===")
    
    # Настройки по умолчанию из config
    if voice is None:
        voice = config.VOICE_NAME
    if speed is None:
        speed = config.VOICE_SPEED
    
    # Если путь не указан — генерируем автоматически
    if not output_path:
        script_name = Path(script_path).stem
        output_path = os.path.join(
            config.PATHS["audio"], 
            f"{script_name}_voice.mp3"
        )
    
    return generate_voice(voice_text, output_path, voice, speed, config.VOICE_MODEL)


def test_voices(text: str = "Привет! Это тест разных голосов."):
    """Генерирует тестовые файлы со всеми голосами"""
    
    print("🎙️ Тестирование голосов...")
    print(f"📝 Текст: {text}")
    
    for voice in AVAILABLE_VOICES:
        output_path = os.path.join(
            config.PATHS["audio"], 
            f"test_{voice}.mp3"
        )
        generate_voice(text, output_path, voice=voice)
    
    print(f"\n✅ Тест завершён!")
    print(f"📁 Файлы в: {config.PATHS['audio']}")
    print("\nПрослушай и выбери:")
    for i, voice in enumerate(AVAILABLE_VOICES, 1):
        print(f"  {i}. {voice}")