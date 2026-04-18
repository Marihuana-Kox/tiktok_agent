import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# API ключи
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Модель для текста
TEXT_MODEL = "gpt-4o-mini"
# TEXT_MODEL = "gpt-3.5-turbo"
# Максимальное количество токенов
MAX_TOKENS = 1500  # Увеличили с 800, чтобы хватило на 300 слов
# Параметры контента
TEXT_MIN_WORDS = 250
TEXT_MAX_WORDS = 450

# Настройки озвучки
VOICE_MODEL = "tts-1"      # или "tts-1-hd" для лучшего качества
VOICE_NAME = "onyx"        # alloy, echo, fable, onyx, nova, shimmer
VOICE_SPEED = 1.1          # 0.25 - 4.0 (1.1-1.2 оптимально для TikTok)

# Настройки Silero TTS
SILERO_SPEAKER = "xenia"           # Рекомендованный голос
SILERO_SAMPLE_RATE = 48000         # Качество (48000 = CD quality)

# Выбор сервиса: "openai", "elevenlabs", или "silero"
# Бесплатно (локально):
# VOICE_SERVICE = "silero"
# Платно (качество):
VOICE_SERVICE = "openai"
# Выбор сервиса
# VOICE_SERVICE = "elevenlabs"  # ← Было "openai" или "silero"

# Настройки ElevenLabs
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE = "Antoni"              # Рекомендованный голос
ELEVENLABS_MODEL = "eleven_multilingual_v2"  # Поддерживает русский
ELEVENLABS_STABILITY = 0.75              # 0.0-1.0 (стабильность)
ELEVENLABS_SIMILARITY = 0.75             # 0.0-1.0 (похожесть на оригинал)

# Настройки DALL-E
DALL_E_MODEL = "dall-e-3"
DALL_E_SIZE = "1024x1792"  # 9:16 для TikTok
DALL_E_QUALITY = "standard"  # "standard" или "hd"
DALL_E_STYLE = "vivid"  # "vivid" или "natural"

# Пути к папкам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

PATHS = {
    "output": OUTPUT_DIR,
    "scripts": os.path.join(OUTPUT_DIR, "scripts"),      # Для старых файлов
    "audio": os.path.join(OUTPUT_DIR, "audio"),          # Для старых файлов
    "images": os.path.join(OUTPUT_DIR, "images"),        # Для старых файлов
    "videos": os.path.join(OUTPUT_DIR, "videos")         # Для старых файлов
}