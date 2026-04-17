# 🤖 TikTok AI Agent

Автоматическая генерация контента для TikTok/YouTube в нише "Загадки истории".

## 🚀 Возможности

- ✅ Анализ вирусных тем
- ✅ Сбор фактов через OpenAI API
- ✅ Создание плана статьи
- ✅ Генерация текста в стиле автора
- ✅ Пакетная обработка тем (очередь)
- ✅ Гибкая система промптов

## 📁 Структура проекта
tiktok_agent/
├── main.py # Главный файл запуска
├── config.py # Настройки API и пути
├── requirements.txt # Зависимости
├── .env # Ключи API (не загружать в Git!)
├── author_style.json # Стиль автора (шаблон в repo)
├── topics.json # Очередь тем (не загружать в Git!)
├── modules/ # Модули агента
│ ├── research_module.py
│ ├── plan_module.py
│ ├── write_module.py
│ ├── text_generator.py
│ ├── prompt_loader.py
│ ├── author_loader.py
│ └── topic_manager.py
├── prompts/ # Промпты для разных стилей
│ ├── prompt_conspiracy.txt
│ ├── prompt_facts.txt
│ └── prompt_mystery.txt
└── output/ # Результат генерации
├── scripts/
├── images/
├── audio/
└── videos/

## ⚙️ Установка

```bash
# 1. Клонируй репозиторий
git clone https://github.com/твой_username/tiktok_agent.git
cd tiktok_agent

# 2. Создай виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# 3. Установи зависимости
pip install -r requirements.txt

# 4. Создай файл .env с ключом
cp .env.example .env
# Открой .env и вставь свой OPENAI_API_KEY

# 5. Запусти
python main.py

python main.py
# Выбери пункт 3 "Добавить новую тему"
python main.py
# Выбери пункт 1 "Обработать все темы по очереди
Настроить стиль автора:
Открой author_style.json и измени параметры под себя.
OPENAI_API_KEY="sk-твой_ключ_здесь"
TEXT_MODEL="gpt-4o-mini"
MAX_TOKENS=2000
Агент показывает:
Количество тем в очереди
Выполнено / Провалено
Слов в каждом тексте
## Темы, название, короткое описание и стиль статьи, статус "pending" будет изменен после обработки,
## если надо повторить написание статьи то этот статус надо вернуть в состояние "pending"
topics.json
id: 2 (автоматически следующий)
topic: "Сигирия в Шри-Ланке"
angle: Удивлённый стиль + подозрение на ошибку историков
notes: Инженерный проект, вода, сады, 1500 лет назад
status: pending (готова к обработке)
output_file: null (будет заполнен после генерации)
next_id: 3 (для следующей темы)
