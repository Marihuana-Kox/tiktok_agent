def create_video_from_images(
    images: list,        # Пути к картинкам
    audio_path: str,     # Путь к voice.mp3
    output_path: str     # Куда сохранить video.mp4
) -> str:
    """
    Создаёт видео из картинок с наложенным аудио.
    Каждая картинка показывается равное время.
    """