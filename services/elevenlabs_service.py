from elevenlabs.client import ElevenLabs
import os
from pathlib import Path

# Импортируем конфиг из корня
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Инициализация клиента
client = None
if config.ELEVENLABS_API_KEY:
    client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)

# Доступные голоса (имя: voice_id)
# Получи актуальные voice_id на: https://elevenlabs.io/app/voice-library
AVAILABLE_VOICES = {
    "VASKO": "Vl27Cllkuw8BhyPqus2n",
    "Adam": "pNInz6obpgDQGcFmaJgB",
    "Antoni": "ErXwobaYiN019PkySvjV",
    "Arnold": "VR6AewLTigWG4xSOukaG",
    "Bella": "EXAVITQu4vr4xnSDxMaL",
    "Domi": "AZnzlk1XvdvUeBnXmlld",
    "Josh": "TxGEqnHWrfWFTfGW9XjX",
    "Rachel": "21m00Tcm4TlvDq8ikWAM",
    "Sam": "yoZ06aMxZJJ28mfd3POQ"
}

# Рекомендованные для твоего канала
RECOMMENDED_VOICES = ["VASKO", "Antoni", "Josh", "Rachel"]


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
    voice_name: str = "Antoni",
    model_id: str = "eleven_multilingual_v2",
    output_format: str = "mp3_44100_128"
) -> str:
    """Генерирует аудио через ElevenLabs API v2"""
    
    print(f"🎙️ ElevenLabs: голос '{voice_name}', модель: {model_id}")
    print(f"📝 Текст: {len(text)} символов (~{len(text.split())} слов)")
    
    if not client:
        raise Exception("ElevenLabs API ключ не настроен!")
    
    # Получаем voice_id из имени
    voice_id = AVAILABLE_VOICES.get(voice_name, voice_name)
    
    # Создаём папку если нет
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Генерация через новый API
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=model_id,
        output_format=output_format
    )
    
    # Сохранение
    with open(output_path, "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)
    
    print(f"✅ Аудио сохранено: {output_path}")
    return output_path


def generate_voice_from_script(
    script_path: str, 
    output_path: str = None,
    voice_name: str = None,
) -> str:
    """Генерирует аудио из файла сценария"""
    
    print(f"\n📂 Чтение сценария: {script_path}")
    
    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()
    
    voice_text = extract_voice_text(script)
    
    if not voice_text:
        raise Exception("Не найден текст для озвучки!")
    
    if voice_name is None:
        voice_name = config.ELEVENLABS_VOICE
    
    if not output_path:
        script_name = Path(script_path).stem
        output_path = os.path.join(
            config.PATHS["audio"], 
            f"{script_name}_voice.mp3"
        )
    
    return generate_voice(
        voice_text, 
        output_path, 
        voice_name,
        model_id=config.ELEVENLABS_MODEL
    )


def test_voices(text: str = "Привет! В 1736 году? Это тест голосов ElevenLabs для канала Загадки истории."):
    """Тестирует рекомендованные голоса"""
    
    print("🎙️ Тестирование голосов ElevenLabs...")
    print(f"📝 Текст: {text}\n")
    
    for voice_name in RECOMMENDED_VOICES:
        output_path = os.path.join(
            config.PATHS["audio"], 
            f"test_elevenlabs_{voice_name}.mp3"
        )
        generate_voice(text, output_path, voice_name=voice_name)
    
    print(f"\n✅ Тест завершён!")
    print(f"📁 Файлы в: {config.PATHS['audio']}")