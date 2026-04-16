import json
import os

class TopicManager:
    """Управление очередью тем"""
    
    def __init__(self):
        # Путь к файлу topics.json (в корне проекта)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filepath = os.path.join(base_dir, "..", "topics.json")
        self.data = self._load_topics()
    
    def _load_topics(self) -> dict:
        """Загружает темы из файла"""
        if not os.path.exists(self.filepath):
            # Если файла нет — создаём пустую структуру
            return {"topics": [], "next_id": 1}
        
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _save_topics(self):
        """Сохраняет темы в файл"""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def add_topic(self, topic: str, notes: str = "") -> int:
        """Добавляет новую тему в очередь"""
        topic_id = self.data["next_id"]
        
        self.data["topics"].append({
            "id": topic_id,
            "topic": topic,
            "notes": notes,
            "status": "pending",
            "output_file": None
        })
        
        self.data["next_id"] += 1
        self._save_topics()
        
        print(f"✅ Тема #{topic_id} добавлена")
        return topic_id
    
    def get_pending_topics(self) -> list:
        """Возвращает список необработанных тем"""
        return [t for t in self.data["topics"] if t["status"] == "pending"]
    
    def get_topic_by_id(self, topic_id: int) -> dict:
        """Возвращает тему по ID"""
        for topic in self.data["topics"]:
            if topic["id"] == topic_id:
                return topic
        return None
    
    def mark_completed(self, topic_id: int, output_file: str):
        """Отмечает тему как выполненную"""
        for topic in self.data["topics"]:
            if topic["id"] == topic_id:
                topic["status"] = "completed"
                topic["output_file"] = output_file
                self._save_topics()
                print(f"✅ Тема #{topic_id} отмечена как выполненная")
                return
        print(f"❌ Тема #{topic_id} не найдена")
    
    def mark_failed(self, topic_id: int):
        """Отмечает тему как проваленную"""
        for topic in self.data["topics"]:
            if topic["id"] == topic_id:
                topic["status"] = "failed"
                self._save_topics()
                print(f"❌ Тема #{topic_id} отмечена как проваленная")
                return
    
    def show_stats(self):
        """Показывает статистику по темам"""
        total = len(self.data["topics"])
        pending = len(self.get_pending_topics())
        completed = sum(1 for t in self.data["topics"] if t["status"] == "completed")
        failed = sum(1 for t in self.data["topics"] if t["status"] == "failed")
        
        print(f"\n📊 СТАТИСТИКА:")
        print(f"  Всего тем: {total}")
        print(f"  В очереди: {pending}")
        print(f"  Выполнено: {completed}")
        print(f"  Провалено: {failed}")
        print()
    
    def list_all_topics(self) -> list:
        """Возвращает все темы"""
        return self.data["topics"]