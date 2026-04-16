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
TEXT_MAX_WORDS = 350

# Пути к папкам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATHS = {
    "scripts": os.path.join(BASE_DIR, "output", "scripts"),
    "images": os.path.join(BASE_DIR, "output", "images"),
    "audio": os.path.join(BASE_DIR, "output", "audio"),
    "videos": os.path.join(BASE_DIR, "output", "videos")
}