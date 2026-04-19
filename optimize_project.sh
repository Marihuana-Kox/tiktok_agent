cat > optimize_project.sh << 'ENDSCRIPT'
#!/bin/bash

# ============================================================================
# PROJECT OPTIMIZATION & CLEANUP SCRIPT
# Для OpenAi_TikTok_agent проекта
# ============================================================================

set -e  # Остановить при ошибке

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "============================================================"
echo "🛠️  PROJECT OPTIMIZATION & CLEANUP"
echo "============================================================"
echo ""

# ============================================================================
# ЧАСТЬ 1: ОЧИСТКА ТЕСТОВЫХ ФАЙЛОВ
# ============================================================================
echo -e "${BLUE}[1/6]${NC} Очистка тестовых файлов..."

# Тестовые скрипты в корне
TEST_FILES=$(find . -maxdepth 1 -name "test_*.py" -type f 2>/dev/null | wc -l)
if [ "$TEST_FILES" -gt 0 ]; then
    rm -f test_*.py
    echo -e "   ✅ Удалено тестовых скриптов: ${TEST_FILES}"
else
    echo -e "   ℹ️  Тестовых скриптов не найдено"
fi

# Тестовые файлы в output/
OUTPUT_TEST=$(find output -maxdepth 1 -name "test_*" -type f 2>/dev/null | wc -l)
if [ "$OUTPUT_TEST" -gt 0 ]; then
    rm -f output/test_*.*
    echo -e "   ✅ Удалено тестовых файлов в output/: ${OUTPUT_TEST}"
else
    echo -e "   ℹ️  Тестовых файлов в output/ не найдено"
fi

# Временные папки с кадрами
TEMP_FOLDERS=$(find output -maxdepth 1 -name "clip_frames_*" -type d 2>/dev/null | wc -l)
if [ "$TEMP_FOLDERS" -gt 0 ]; then
    rm -rf output/clip_frames_* output/zoom_frames output/effect_frames
    echo -e "   ✅ Удалено временных папок: ${TEMP_FOLDERS}"
else
    echo -e "   ℹ️  Временных папок не найдено"
fi

# FFmpeg временные файлы
FFMPEG_TEMP=$(find . -maxdepth 1 -name "temp-*.m4a" -o -name "temp-*.mp4" 2>/dev/null | wc -l)
if [ "$FFMPEG_TEMP" -gt 0 ]; then
    rm -f temp-*.m4a temp-*.mp4
    echo -e "   ✅ Удалено FFmpeg temp файлов: ${FFMPEG_TEMP}"
else
    echo -e "   ℹ️  FFmpeg temp файлов не найдено"
fi

# Python кэш
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo -e "   ✅ Очищен Python кэш (__pycache__, *.pyc)"

echo ""

# ============================================================================
# ЧАСТЬ 2: ПРОВЕРКА НЕИСПОЛЬЗУЕМЫХ ИМПОРТОВ
# ============================================================================
echo -e "${BLUE}[2/6]${NC} Проверка неиспользуемых импортов..."

if command -v autoflake &> /dev/null; then
    UNUSED_IMPORTS=0
    for pyfile in $(find services modules -name "*.py" -type f 2>/dev/null); do
        RESULT=$(autoflake --check --remove-all-unused-imports "$pyfile" 2>&1) || true
        if [[ "$RESULT" == *"Unused imports"* ]]; then
            UNUSED_IMPORTS=$((UNUSED_IMPORTS + 1))
        fi
    done
    
    if [ "$UNUSED_IMPORTS" -gt 0 ]; then
        echo -e "   ⚠️  Найдено файлов с неиспользуемыми импортами: ${UNUSED_IMPORTS}"
        echo -e "   💡 Запусти: ${YELLOW}autoflake --in-place --remove-all-unused-imports -r services modules${NC}"
    else
        echo -e "   ✅ Неиспользуемых импортов не найдено"
    fi
else
    echo -e "   ℹ️  autoflake не установлен. Для проверки:"
    echo -e "      ${YELLOW}pip install autoflake${NC}"
fi

echo ""

# ============================================================================
# ЧАСТЬ 3: ФОРМАТИРОВАНИЕ КОДА (отступы, пробелы)
# ============================================================================
echo -e "${BLUE}[3/6]${NC} Проверка форматирования кода..."

if command -v black &> /dev/null; then
    echo -e "   ℹ️  Black найден. Запуск форматирования..."
    black --line-length 100 services/ modules/ 2>/dev/null || true
    echo -e "   ✅ Код отформатирован (black)"
else
    echo -e "   ℹ️  Black не установлен. Для форматирования:"
    echo -e "      ${YELLOW}pip install black${NC}"
    echo -e "      ${YELLOW}black --line-length 100 services/ modules/${NC}"
fi

echo ""

# ============================================================================
# ЧАСТЬ 4: ПРОВЕРКА СТИЛЯ КОДА (PEP 8)
# ============================================================================
echo -e "${BLUE}[4/6]${NC} Проверка стиля кода (PEP 8)..."

if command -v flake8 &> /dev/null; then
    FLAKE_ERRORS=$(flake8 --count --select=E9,F63,F7,F82 --show-source services/ modules/ 2>&1 | tail -1) || true
    if [[ "$FLAKE_ERRORS" == *"0"* ]]; then
        echo -e "   ✅ Ошибок стиля не найдено"
    else
        echo -e "   ⚠️  Найдены проблемы стиля. Детали:"
        flake8 --select=E9,F63,F7,F82 --max-line-length 120 services/ modules/ 2>/dev/null || true
    fi
else
    echo -e "   ℹ️  flake8 не установлен. Для проверки:"
    echo -e "      ${YELLOW}pip install flake8${NC}"
fi

echo ""

# ============================================================================
# ЧАСТЬ 5: АНАЛИЗ ЗАВИСИМОСТЕЙ
# ============================================================================
echo -e "${BLUE}[5/6]${NC} Анализ зависимостей..."

if [ -f "requirements.txt" ]; then
    echo -e "   ℹ️  requirements.txt найден"
    
    # Проверка установленных пакетов
    INSTALLED=$(pip list --format=freeze 2>/dev/null | wc -l)
    echo -e "   ✅ Установлено пакетов: ${INSTALLED}"
    
    # Проверка критических зависимостей
    CRITICAL=("moviepy" "Pillow" "requests" "openai")
    MISSING=()
    
    for pkg in "${CRITICAL[@]}"; do
        if ! pip show "$pkg" &>/dev/null; then
            MISSING+=("$pkg")
        fi
    done
    
    if [ ${#MISSING[@]} -gt 0 ]; then
        echo -e "   ⚠️  Отсутствуют критические пакеты: ${YELLOW}${MISSING[*]}${NC}"
        echo -e "   💡 Запусти: ${YELLOW}pip install ${MISSING[*]}${NC}"
    else
        echo -e "   ✅ Все критические зависимости установлены"
    fi
else
    echo -e "   ⚠️  requirements.txt не найден"
    echo -e "   💡 Создай: ${YELLOW}pip freeze > requirements.txt${NC}"
fi

echo ""

# ============================================================================
# ЧАСТЬ 6: ПРОВЕРКА ЦЕЛОСТНОСТИ ПРОЕКТА
# ============================================================================
echo -e "${BLUE}[6/6]${NC} Проверка целостности проекта..."

# Проверка основных файлов
REQUIRED_FILES=(
    "main.py"
    "config.py"
    "config_video.json"
    "services/video_service.py"
    "services/image_service.py"
    "services/voice_service.py"
)

MISSING_FILES=()
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo -e "   ⚠️  Отсутствуют файлы: ${YELLOW}${MISSING_FILES[*]}${NC}"
else
    echo -e "   ✅ Все основные файлы на месте"
fi

# Проверка синтаксиса Python
echo -e "   ℹ️  Проверка синтаксиса Python..."
SYNTAX_ERRORS=0
for pyfile in $(find services modules -name "*.py" -type f 2>/dev/null); do
    if ! python -m py_compile "$pyfile" 2>/dev/null; then
        SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
        echo -e "   ❌ Ошибка синтаксиса: ${pyfile}"
    fi
done

if [ "$SYNTAX_ERRORS" -eq 0 ]; then
    echo -e "   ✅ Синтаксис всех файлов корректен"
else
    echo -e "   ❌ Найдено ошибок синтаксиса: ${SYNTAX_ERRORS}"
fi

echo ""

# ============================================================================
# ИТОГИ
# ============================================================================
echo "============================================================"
echo -e "${GREEN}✅ OPTIMIZATION COMPLETE${NC}"
echo "============================================================"
echo ""
echo "📊 Статистика:"
echo "   • Удалено тестовых файлов: ${TEST_FILES:-0} + ${OUTPUT_TEST:-0}"
echo "   • Удалено временных папок: ${TEMP_FOLDERS:-0}"
echo "   • Ошибок синтаксиса: ${SYNTAX_ERRORS:-0}"
echo ""
echo "📁 Структура проекта:"
du -sh . 2>/dev/null | awk '{print "   • Размер проекта: " $1}'
du -sh output/ 2>/dev/null | awk '{print "   • Размер output/: " $1}'
find output -name "topic_*" -type d 2>/dev/null | wc -l | awk '{print "   • Проектов в output/: " $1}'
echo ""
echo "💡 Рекомендации:"
echo "   1. Регулярно запускай этот скрипт (раз в неделю)"
echo "   2. Используй git для отслеживания изменений"
echo "   3. Создавай backup перед крупными изменениями"
echo ""
echo "🚀 Для запуска проекта:"
echo "   ${YELLOW}python main.py${NC}"
echo ""
ENDSCRIPT

chmod +x optimize_project.sh
echo "✅ Скрипт создан: optimize_project.sh"